from pathlib import Path
import shutil

SRC_DATASET = Path("datasets/RDD2022")
BAD_PREVIEW_DIR = Path("review_D00_bad")
OUT_DATASET = Path("datasets/RDD2022_filtered")

IMG_EXTS = [".jpg", ".jpeg", ".png", ".bmp", ".JPG", ".JPEG", ".PNG", ".BMP"]


def parse_bad_list():
    bad = set()

    if not BAD_PREVIEW_DIR.exists():
        print(f"未找到坏图目录：{BAD_PREVIEW_DIR}")
        return bad

    for p in BAD_PREVIEW_DIR.glob("*.jpg"):
        stem = p.stem

        if "__" not in stem:
            continue

        split, img_stem = stem.split("__", 1)
        bad.add((split, img_stem))

    return bad


def find_image(img_dir, stem):
    for ext in IMG_EXTS:
        p = img_dir / f"{stem}{ext}"
        if p.exists():
            return p
    return None


def clean_out():
    if OUT_DATASET.exists():
        shutil.rmtree(OUT_DATASET)

    for split in ["train", "val"]:
        (OUT_DATASET / "images" / split).mkdir(parents=True, exist_ok=True)
        (OUT_DATASET / "labels" / split).mkdir(parents=True, exist_ok=True)


def copy_filtered():
    bad = parse_bad_list()
    print(f"坏样本数量：{len(bad)}")

    clean_out()

    total = 0
    kept = 0
    removed = 0

    for split in ["train", "val"]:
        src_img_dir = SRC_DATASET / "images" / split
        src_lab_dir = SRC_DATASET / "labels" / split

        dst_img_dir = OUT_DATASET / "images" / split
        dst_lab_dir = OUT_DATASET / "labels" / split

        for label_path in src_lab_dir.glob("*.txt"):
            stem = label_path.stem
            img_path = find_image(src_img_dir, stem)

            if img_path is None:
                continue

            total += 1

            if (split, stem) in bad:
                removed += 1
                continue

            shutil.copy2(img_path, dst_img_dir / img_path.name)
            shutil.copy2(label_path, dst_lab_dir / label_path.name)
            kept += 1

    print(f"总样本：{total}")
    print(f"保留：{kept}")
    print(f"删除：{removed}")
    print(f"筛选后数据集输出到：{OUT_DATASET}")


if __name__ == "__main__":
    copy_filtered()