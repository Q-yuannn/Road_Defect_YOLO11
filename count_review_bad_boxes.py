from pathlib import Path
from collections import Counter, defaultdict

# 当前原始 YOLO 数据集
DATASET_DIR = Path("datasets/RDD2022")

# 你人工复制坏预览图的文件夹
BAD_PREVIEW_DIR = Path("review_D00_bad")

# 类别顺序必须和 road.yaml 一致
CLASS_NAMES = {
    0: "D00",
    1: "D10",
    2: "D20",
    3: "D40",
}

PREVIEW_EXTS = [".jpg", ".jpeg", ".png", ".bmp", ".JPG", ".JPEG", ".PNG", ".BMP"]


def parse_preview_name(preview_path):
    """
    预览图文件名格式应类似：
    train__xxx.jpg
    val__xxx.jpg

    返回：
    split = train / val
    stem = 原始图片和标签文件名
    """
    stem = preview_path.stem

    if "__" not in stem:
        return None, None

    split, original_stem = stem.split("__", 1)

    if split not in ["train", "val"]:
        return None, None

    return split, original_stem


def read_yolo_label(label_path):
    """
    读取 YOLO txt 标签，统计每个类别框数量。
    """
    counter = Counter()

    if not label_path.exists():
        return counter

    with open(label_path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split()

            if len(parts) < 5:
                continue

            try:
                cls_id = int(float(parts[0]))
            except ValueError:
                continue

            if cls_id in CLASS_NAMES:
                counter[cls_id] += 1

    return counter


def main():
    if not BAD_PREVIEW_DIR.exists():
        print(f"没有找到文件夹：{BAD_PREVIEW_DIR}")
        return

    preview_files = []
    for ext in PREVIEW_EXTS:
        preview_files.extend(BAD_PREVIEW_DIR.glob(f"*{ext}"))

    total_images = 0
    missing_labels = 0

    total_box_counter = Counter()
    split_image_counter = Counter()
    split_box_counter = defaultdict(Counter)

    bad_file_records = []

    for preview_path in preview_files:
        split, original_stem = parse_preview_name(preview_path)

        if split is None:
            print(f"文件名格式不符合 split__stem：{preview_path.name}")
            continue

        label_path = DATASET_DIR / "labels" / split / f"{original_stem}.txt"

        if not label_path.exists():
            missing_labels += 1
            print(f"找不到对应标签：{label_path}")
            continue

        box_counter = read_yolo_label(label_path)

        total_images += 1
        split_image_counter[split] += 1

        total_box_counter.update(box_counter)
        split_box_counter[split].update(box_counter)

        bad_file_records.append((split, original_stem, box_counter))

    print("\n========== review_D00_bad 筛选统计 ==========")
    print(f"坏图预览文件数量：{len(preview_files)}")
    print(f"成功匹配标签的图片数：{total_images}")
    print(f"找不到标签的图片数：{missing_labels}")

    print("\n按 split 统计图片数量：")
    for split in ["train", "val"]:
        print(f"  {split}: {split_image_counter[split]} 张")

    print("\n全部坏图中，各类别目标框数量：")
    total_boxes = sum(total_box_counter.values())

    for cls_id, cls_name in CLASS_NAMES.items():
        num = total_box_counter[cls_id]
        ratio = num / total_boxes * 100 if total_boxes > 0 else 0
        print(f"  {cls_name}: {num} 个框，占 {ratio:.2f}%")

    print(f"\n全部坏图中总目标框数量：{total_boxes}")

    print("\n按 split 统计各类别框数量：")
    for split in ["train", "val"]:
        print(f"\n  {split}:")
        split_total = sum(split_box_counter[split].values())
        for cls_id, cls_name in CLASS_NAMES.items():
            num = split_box_counter[split][cls_id]
            ratio = num / split_total * 100 if split_total > 0 else 0
            print(f"    {cls_name}: {num} 个框，占 {ratio:.2f}%")
        print(f"    total: {split_total} 个框")

    print("\n提示：")
    print("这些图片会在 build_filtered_by_bad_preview.py 中被排除。")
    print("如果 D00 数量很高，说明你主要筛掉的是 D00 错标/低质量样本。")
    print("如果 D20/D40 数量也不少，说明这些坏图里有多类别目标，删除时要稍微谨慎。")


if __name__ == "__main__":
    main()