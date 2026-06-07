import random
import shutil
from pathlib import Path
from collections import Counter, defaultdict

# =========================
# Basic settings
# =========================

SEED = 42
random.seed(SEED)

CLASSES = ["D00", "D10", "D20", "D40"]

IMG_EXTS = [".jpg", ".jpeg", ".png", ".bmp", ".JPG", ".JPEG", ".PNG", ".BMP"]

# Output dataset
OUT_DIR = Path("datasets/RoadDefect_Balanced_811")

# Input YOLO-format data sources
# Modify these paths if your actual folders are different.
SOURCES = [
    {
        "name": "rdd_train",
        "img_dir": Path("datasets/RDD2022_filtered/images/train"),
        "lab_dir": Path("datasets/RDD2022_filtered/labels/train"),
    },
    {
        "name": "rdd_val",
        "img_dir": Path("datasets/RDD2022_filtered/images/val"),
        "lab_dir": Path("datasets/RDD2022_filtered/labels/val"),
    },
    {
        "name": "extra_labeled",
        "img_dir": Path("raw_data_balanced/extra_yolo/images"),
        "lab_dir": Path("raw_data_balanced/extra_yolo/labels"),
    },
]


def find_image_by_stem(img_dir, stem):
    """Find image file by label stem."""
    for ext in IMG_EXTS:
        p = img_dir / f"{stem}{ext}"
        if p.exists():
            return p
    return None


def read_yolo_label(txt_path):
    """
    Read YOLO label file.
    Each valid line should be:
    class_id x_center y_center width height
    """
    cls_ids = []
    valid_lines = []

    with open(txt_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            parts = line.split()
            if len(parts) != 5:
                continue

            try:
                cls_id = int(float(parts[0]))
                x, y, w, h = map(float, parts[1:])
            except ValueError:
                continue

            # Keep only valid class ids and normalized coordinates
            if cls_id not in range(len(CLASSES)):
                continue

            if not (0 <= x <= 1 and 0 <= y <= 1 and 0 < w <= 1 and 0 < h <= 1):
                continue

            cls_ids.append(cls_id)
            valid_lines.append(f"{cls_id} {x:.6f} {y:.6f} {w:.6f} {h:.6f}")

    return cls_ids, valid_lines


def dominant_class(cls_ids):
    """
    Use the most frequent class in an image as its dominant class.
    This is used for rough stratified splitting.
    """
    c = Counter(cls_ids)
    return c.most_common(1)[0][0]


def collect_records():
    """Collect all valid image-label pairs from all sources."""
    records = []
    skipped_no_image = 0
    skipped_empty_label = 0

    for src in SOURCES:
        name = src["name"]
        img_dir = src["img_dir"]
        lab_dir = src["lab_dir"]

        if not img_dir.exists() or not lab_dir.exists():
            print(f"[Skip] Source not found: {name}")
            print(f"       img_dir: {img_dir}")
            print(f"       lab_dir: {lab_dir}")
            continue

        label_files = list(lab_dir.rglob("*.txt"))
        print(f"\n[Source] {name}")
        print(f"Found label files: {len(label_files)}")

        for txt_path in label_files:
            img_path = find_image_by_stem(img_dir, txt_path.stem)

            if img_path is None:
                skipped_no_image += 1
                continue

            cls_ids, valid_lines = read_yolo_label(txt_path)

            if not valid_lines:
                skipped_empty_label += 1
                continue

            records.append({
                "source": name,
                "img_path": img_path,
                "label_path": txt_path,
                "cls_ids": cls_ids,
                "valid_lines": valid_lines,
                "dominant": dominant_class(cls_ids),
            })

    print("\n========== Collect Summary ==========")
    print(f"Valid image-label pairs: {len(records)}")
    print(f"Skipped because image missing: {skipped_no_image}")
    print(f"Skipped because label invalid/empty: {skipped_empty_label}")

    return records


def print_stats(records, title):
    """Print class box statistics."""
    counter = Counter()

    for r in records:
        for cls_id in r["cls_ids"]:
            counter[cls_id] += 1

    total_boxes = sum(counter.values())

    print(f"\n========== {title} ==========")
    print(f"Images: {len(records)}")
    print(f"Boxes : {total_boxes}")

    for cls_id, cls_name in enumerate(CLASSES):
        num = counter[cls_id]
        ratio = num / total_boxes * 100 if total_boxes > 0 else 0
        print(f"{cls_name}: {num} boxes ({ratio:.2f}%)")


def split_records(records):
    """
    Split records into train/val/test by 8:1:1.
    Stratify roughly by dominant class.
    """
    groups = defaultdict(list)

    for r in records:
        groups[r["dominant"]].append(r)

    train, val, test = [], [], []

    for cls_id, items in groups.items():
        random.shuffle(items)

        n = len(items)
        n_train = int(n * 0.8)
        n_val = int(n * 0.1)

        train.extend(items[:n_train])
        val.extend(items[n_train:n_train + n_val])
        test.extend(items[n_train + n_val:])

        print(
            f"Class {CLASSES[cls_id]} dominant images: "
            f"total={n}, train={n_train}, val={n_val}, test={n - n_train - n_val}"
        )

    random.shuffle(train)
    random.shuffle(val)
    random.shuffle(test)

    return train, val, test


def clean_output_dir():
    """Remove old output dataset and create new folders."""
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)

    for split in ["train", "val", "test"]:
        (OUT_DIR / "images" / split).mkdir(parents=True, exist_ok=True)
        (OUT_DIR / "labels" / split).mkdir(parents=True, exist_ok=True)


def save_split(records, split):
    """Copy images and write cleaned labels to output dataset."""
    img_out = OUT_DIR / "images" / split
    lab_out = OUT_DIR / "labels" / split

    for idx, r in enumerate(records, start=1):
        # Use source prefix to avoid duplicate filenames
        new_stem = f"{r['source']}_{idx:06d}"
        img_suffix = r["img_path"].suffix.lower()

        dst_img = img_out / f"{new_stem}{img_suffix}"
        dst_txt = lab_out / f"{new_stem}.txt"

        shutil.copy2(r["img_path"], dst_img)

        with open(dst_txt, "w", encoding="utf-8") as f:
            f.write("\n".join(r["valid_lines"]))


def write_yaml():
    """Write a dataset yaml file for YOLO training."""
    yaml_path = Path("road_balanced_811.yaml")

    content = """# Road defect dataset after filtering and relabeling

path: ./datasets/RoadDefect_Balanced_811

train: images/train
val: images/val
test: images/test

nc: 4

names:
  0: D00
  1: D10
  2: D20
  3: D40
"""

    with open(yaml_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"\nDataset yaml saved to: {yaml_path}")


def main():
    records = collect_records()

    if not records:
        print("No valid data found. Please check your folder paths.")
        return

    print_stats(records, "All Collected Data")

    train, val, test = split_records(records)

    clean_output_dir()

    save_split(train, "train")
    save_split(val, "val")
    save_split(test, "test")

    print_stats(train, "Train Split")
    print_stats(val, "Val Split")
    print_stats(test, "Test Split")

    write_yaml()

    print("\nDone.")
    print(f"New dataset saved to: {OUT_DIR}")
    print("Use data='road_balanced_811.yaml' in your training scripts.")


if __name__ == "__main__":
    main()