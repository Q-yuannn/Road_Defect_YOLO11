import os
import random
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path
from collections import Counter, defaultdict

# =========================
# 配置区
# =========================
RAW_IMAGES_DIR = Path("raw_data/images")
RAW_XMLS_DIR = Path("raw_data/xmls")

# 注意：不要再输出到 datasets/RDD2022，避免覆盖你的原始 RDD2022 数据源
OUT_DIR = Path("datasets/RoadDefect_3sets_YOLO")

SEED = 42
TRAIN_RATIO = 0.8
VAL_RATIO = 0.1
TEST_RATIO = 0.1

CLASSES = ["D00", "D10", "D20", "D40"]

# 标签统一映射
LABEL_MAP = {
    # RDD2022 原始标签
    "D00": "D00",
    "D10": "D10",
    "D20": "D20",
    "D40": "D40",

    # 英文标签兼容
    "LongitudinalCrack": "D00",
    "longitudinalcrack": "D00",
    "longitudinal_crack": "D00",

    "TransverseCrack": "D10",
    "transversecrack": "D10",
    "transverse_crack": "D10",

    "AlligatorCrack": "D20",
    "alligatorcrack": "D20",
    "alligator_crack": "D20",

    # Patel Cracks 通常可以统一成复杂裂纹 D20
    "Crack": "D20",
    "crack": "D20",
    "Cracks": "D20",
    "cracks": "D20",

    # 坑洞类
    "Pothole": "D40",
    "pothole": "D40",
    "Potholes": "D40",
    "potholes": "D40",
}

IGNORE_LABELS = {
    "Repair",
    "repair",
    "Patch",
    "patch",
    "Surface_Defects",
    "surface_defects",
    "SurfaceDefects",
    "surface defects",
}

IMG_EXTS = [".jpg", ".jpeg", ".png", ".bmp", ".JPG", ".JPEG", ".PNG", ".BMP"]


def find_image_by_stem(stem):
    for ext in IMG_EXTS:
        p = RAW_IMAGES_DIR / f"{stem}{ext}"
        if p.exists():
            return p
    return None


def convert_box(size, box):
    img_w, img_h = size
    xmin, xmax, ymin, ymax = box

    xmin = max(0, min(xmin, img_w - 1))
    xmax = max(0, min(xmax, img_w - 1))
    ymin = max(0, min(ymin, img_h - 1))
    ymax = max(0, min(ymax, img_h - 1))

    if xmax <= xmin or ymax <= ymin:
        return None

    x_center = ((xmin + xmax) / 2.0) / img_w
    y_center = ((ymin + ymax) / 2.0) / img_h
    w = (xmax - xmin) / img_w
    h = (ymax - ymin) / img_h

    return x_center, y_center, w, h


def parse_xml(xml_path):
    try:
        tree = ET.parse(xml_path)
    except Exception as e:
        print(f"⚠️ XML 解析失败：{xml_path}, 错误：{e}")
        return [], []

    root = tree.getroot()

    size = root.find("size")
    if size is None:
        print(f"⚠️ XML 缺少 size：{xml_path}")
        return [], []

    img_w = int(float(size.find("width").text))
    img_h = int(float(size.find("height").text))

    labels = []
    skipped = []

    for obj in root.iter("object"):
        name_node = obj.find("name")
        if name_node is None:
            continue

        raw_cls = name_node.text.strip()

        if raw_cls in IGNORE_LABELS:
            skipped.append(raw_cls)
            continue

        if raw_cls not in LABEL_MAP:
            skipped.append(raw_cls)
            continue

        cls = LABEL_MAP[raw_cls]
        cls_id = CLASSES.index(cls)

        xmlbox = obj.find("bndbox")
        if xmlbox is None:
            continue

        xmin = float(xmlbox.find("xmin").text)
        xmax = float(xmlbox.find("xmax").text)
        ymin = float(xmlbox.find("ymin").text)
        ymax = float(xmlbox.find("ymax").text)

        yolo_box = convert_box((img_w, img_h), (xmin, xmax, ymin, ymax))
        if yolo_box is None:
            continue

        labels.append((cls_id, *yolo_box))

    return labels, skipped


def dominant_class(labels):
    counter = Counter([x[0] for x in labels])
    return counter.most_common(1)[0][0]


def clean_output_dir():
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)

    for split in ["train", "val", "test"]:
        (OUT_DIR / "images" / split).mkdir(parents=True, exist_ok=True)
        (OUT_DIR / "labels" / split).mkdir(parents=True, exist_ok=True)


def copy_record(record, split):
    img_path = record["img_path"]
    labels = record["labels"]

    img_name = img_path.name
    label_name = img_path.with_suffix(".txt").name

    dst_img = OUT_DIR / "images" / split / img_name
    dst_label = OUT_DIR / "labels" / split / label_name

    shutil.copy2(img_path, dst_img)

    with open(dst_label, "w", encoding="utf-8") as f:
        for item in labels:
            cls_id, x, y, w, h = item
            f.write(f"{cls_id} {x:.6f} {y:.6f} {w:.6f} {h:.6f}\n")


def split_stats(name, records):
    counter = Counter()

    for r in records:
        for item in r["labels"]:
            counter[CLASSES[item[0]]] += 1

    print(f"\n{name} 图片数：{len(records)}")
    for cls in CLASSES:
        print(f"  {cls}: {counter[cls]}")


def main():
    random.seed(SEED)

    if not RAW_IMAGES_DIR.exists() or not RAW_XMLS_DIR.exists():
        raise FileNotFoundError("请先确认 raw_data/images 和 raw_data/xmls 存在，并且已经运行 merge_to_raw_data.py")

    xml_files = sorted(RAW_XMLS_DIR.glob("*.xml"))

    records = []
    total_counter = Counter()
    skipped_counter = Counter()
    missing_images = 0
    empty_xml = 0

    for xml_path in xml_files:
        img_path = find_image_by_stem(xml_path.stem)

        if img_path is None:
            print(f"⚠️ 找不到对应图片：{xml_path.name}")
            missing_images += 1
            continue

        labels, skipped = parse_xml(xml_path)

        for s in skipped:
            skipped_counter[s] += 1

        if not labels:
            empty_xml += 1
            continue

        for item in labels:
            total_counter[CLASSES[item[0]]] += 1

        records.append({
            "img_path": img_path,
            "xml_path": xml_path,
            "labels": labels,
            "dom": dominant_class(labels),
        })

    print("=" * 60)
    print(f"有效图片数量：{len(records)}")
    print(f"找不到对应图片的 XML 数量：{missing_images}")
    print(f"无有效目标 XML 数量：{empty_xml}")

    print("\n总目标框统计：")
    for cls in CLASSES:
        print(f"  {cls}: {total_counter[cls]}")

    print("\n被跳过的标签：")
    if skipped_counter:
        for k, v in skipped_counter.most_common():
            print(f"  {k}: {v}")
    else:
        print("  无")
    print("=" * 60)

    # 简单分层：按每张图的主类别分组，尽量保证 train/val/test 类别比例接近
    groups = defaultdict(list)
    for r in records:
        groups[r["dom"]].append(r)

    train_records, val_records, test_records = [], [], []

    for dom, items in groups.items():
        random.shuffle(items)
        n = len(items)

        n_train = int(n * TRAIN_RATIO)
        n_val = int(n * VAL_RATIO)

        train_records.extend(items[:n_train])
        val_records.extend(items[n_train:n_train + n_val])
        test_records.extend(items[n_train + n_val:])

    random.shuffle(train_records)
    random.shuffle(val_records)
    random.shuffle(test_records)

    clean_output_dir()

    for r in train_records:
        copy_record(r, "train")
    for r in val_records:
        copy_record(r, "val")
    for r in test_records:
        copy_record(r, "test")

    split_stats("train", train_records)
    split_stats("val", val_records)
    split_stats("test", test_records)

    print("\n✅ 8:1:1 划分完成")
    print(f"输出目录：{OUT_DIR}")


if __name__ == "__main__":
    main()