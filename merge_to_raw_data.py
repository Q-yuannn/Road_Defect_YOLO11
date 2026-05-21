import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

# =========================
# 路径配置
# =========================
PROJECT_ROOT = Path(".")
DATASETS_ROOT = PROJECT_ROOT / "datasets"

OUT_IMAGES = PROJECT_ROOT / "raw_data" / "images"
OUT_XMLS = PROJECT_ROOT / "raw_data" / "xmls"

# 是否清空 raw_data/images 和 raw_data/xmls
# 第一次整理可以设为 True
# 如果你不确定 raw_data 里有没有重要文件，先设为 False，手动备份后再 True
CLEAR_RAW_DATA = False

IMG_EXTS = [".jpg", ".jpeg", ".png", ".bmp", ".JPG", ".JPEG", ".PNG", ".BMP"]


DATASET_CONFIGS = [
    {
        "name": "RDD2022",
        "root": DATASETS_ROOT / "RDD2022",
        "prefix": "rdd",
        # 只处理这些子文件夹；如果你的 XML 不在这里，可以改成 None
        "include_folders": ["RDD2022_China_Drone", "RDD2022_China_MotorBike"],
        "exclude_folders": [],
    },
    {
        "name": "Pothole_Detection_Dataset",
        "root": DATASETS_ROOT / "Pothole_Detection_Dataset",
        "prefix": "pothole",
        "include_folders": ["potholes"],
        "exclude_folders": ["normal"],
    },
    {
        "name": "Road_Defects_Images_from_Patel_Mihir",
        "root": DATASETS_ROOT / "Road_Defects_Images_from_Patel_Mihir",
        "prefix": "patel",
        "include_folders": ["Cracks", "Potholes"],
        "exclude_folders": ["Patch", "Surface_Defects"],
    },
]


def normalize_folder_name(name: str) -> str:
    return name.lower().replace(" ", "_")


def is_in_selected_folder(path: Path, root: Path, include_folders, exclude_folders):
    rel_parts = [normalize_folder_name(p) for p in path.relative_to(root).parts]

    if exclude_folders:
        exclude_norm = [normalize_folder_name(x) for x in exclude_folders]
        if any(x in rel_parts for x in exclude_norm):
            return False

    if include_folders is None:
        return True

    include_norm = [normalize_folder_name(x) for x in include_folders]
    return any(x in rel_parts for x in include_norm)


def find_image_by_stem(root: Path, stem: str):
    for ext in IMG_EXTS:
        matches = list(root.rglob(stem + ext))
        if matches:
            return matches[0]
    return None


def update_xml_filename(xml_src: Path, xml_dst: Path, new_img_name: str):
    tree = ET.parse(xml_src)
    root = tree.getroot()

    filename_node = root.find("filename")
    if filename_node is not None:
        filename_node.text = new_img_name

    path_node = root.find("path")
    if path_node is not None:
        path_node.text = str(OUT_IMAGES / new_img_name)

    tree.write(xml_dst, encoding="utf-8", xml_declaration=True)


def clear_raw_data():
    if OUT_IMAGES.exists():
        shutil.rmtree(OUT_IMAGES)
    if OUT_XMLS.exists():
        shutil.rmtree(OUT_XMLS)

    OUT_IMAGES.mkdir(parents=True, exist_ok=True)
    OUT_XMLS.mkdir(parents=True, exist_ok=True)


def ensure_out_dirs():
    OUT_IMAGES.mkdir(parents=True, exist_ok=True)
    OUT_XMLS.mkdir(parents=True, exist_ok=True)


def main():
    if CLEAR_RAW_DATA:
        clear_raw_data()
    else:
        ensure_out_dirs()

    total_pairs = 0
    total_missing = 0

    for cfg in DATASET_CONFIGS:
        name = cfg["name"]
        root = cfg["root"]
        prefix = cfg["prefix"]
        include_folders = cfg["include_folders"]
        exclude_folders = cfg["exclude_folders"]

        print("\n" + "=" * 60)
        print(f"正在处理数据集：{name}")
        print(f"路径：{root}")

        if not root.exists():
            print(f"❌ 路径不存在，跳过：{root}")
            continue

        xml_files = sorted(root.rglob("*.xml"))
        xml_files = [
            x for x in xml_files
            if is_in_selected_folder(x, root, include_folders, exclude_folders)
        ]

        print(f"筛选后 XML 数量：{len(xml_files)}")

        count = 1
        missing = 0

        for xml_path in xml_files:
            img_path = find_image_by_stem(root, xml_path.stem)

            if img_path is None:
                print(f"⚠️ 找不到对应图片，跳过 XML：{xml_path}")
                missing += 1
                continue

            new_stem = f"{prefix}_{count:06d}"
            new_img_name = new_stem + img_path.suffix.lower()
            new_xml_name = new_stem + ".xml"

            dst_img = OUT_IMAGES / new_img_name
            dst_xml = OUT_XMLS / new_xml_name

            shutil.copy2(img_path, dst_img)
            update_xml_filename(xml_path, dst_xml, new_img_name)

            count += 1
            total_pairs += 1

        total_missing += missing
        print(f"✅ {name} 完成：复制 {count - 1} 对图片/XML，缺失图片 {missing} 个")

    print("\n" + "=" * 60)
    print(f"全部完成，总共复制有效样本：{total_pairs}")
    print(f"总共缺失图片的 XML：{total_missing}")
    print(f"输出图片目录：{OUT_IMAGES}")
    print(f"输出 XML 目录：{OUT_XMLS}")
    print("=" * 60)


if __name__ == "__main__":
    main()