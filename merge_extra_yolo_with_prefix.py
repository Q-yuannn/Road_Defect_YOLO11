from pathlib import Path
import shutil

# 这三个目录改成你实际存放 patel_cracks / patel_potholes / pothole_dataset 的位置
SOURCE_DIRS = [
    Path("filtered_extra_data/道路坑洼裂缝/patel_cracks"),
    Path("filtered_extra_data/道路坑洼裂缝/patel_potholes"),
    Path("filtered_extra_data/道路坑洼裂缝/pothole_dataset"),
]

# 合并后的输出目录
OUT_IMG_DIR = Path("raw_data_balanced/extra_yolo/images")
OUT_LAB_DIR = Path("raw_data_balanced/extra_yolo/labels")

IMG_EXTS = [".jpg", ".jpeg", ".png", ".bmp", ".JPG", ".JPEG", ".PNG", ".BMP"]

OUT_IMG_DIR.mkdir(parents=True, exist_ok=True)
OUT_LAB_DIR.mkdir(parents=True, exist_ok=True)


def find_image(folder, stem):
    for ext in IMG_EXTS:
        p = folder / f"{stem}{ext}"
        if p.exists():
            return p
    return None


def main():
    total = 0
    skipped = 0

    for src_dir in SOURCE_DIRS:
        if not src_dir.exists():
            print(f"路径不存在，跳过：{src_dir}")
            continue

        prefix = src_dir.name
        txt_files = list(src_dir.glob("*.txt"))

        print(f"\n处理：{src_dir}")
        print(f"发现 txt 标签数量：{len(txt_files)}")

        for txt_path in txt_files:
            stem = txt_path.stem
            img_path = find_image(src_dir, stem)

            if img_path is None:
                print(f"找不到对应图片，跳过：{txt_path.name}")
                skipped += 1
                continue

            new_stem = f"{prefix}_{stem}"
            new_img_name = new_stem + img_path.suffix.lower()
            new_txt_name = new_stem + ".txt"

            shutil.copy2(img_path, OUT_IMG_DIR / new_img_name)
            shutil.copy2(txt_path, OUT_LAB_DIR / new_txt_name)

            total += 1

    print("\n========== 合并完成 ==========")
    print(f"成功复制图片+标签：{total}")
    print(f"跳过：{skipped}")
    print(f"图片输出目录：{OUT_IMG_DIR}")
    print(f"标签输出目录：{OUT_LAB_DIR}")


if __name__ == "__main__":
    main()