from pathlib import Path
import cv2

DATASET_DIR = Path("datasets/RDD2022")
OUT_DIR = Path("review_D00_preview")

IMG_EXTS = [".jpg", ".jpeg", ".png", ".bmp", ".JPG", ".JPEG", ".PNG", ".BMP"]

CLASS_NAMES = {
    0: "D00",
    1: "D10",
    2: "D20",
    3: "D40",
}


def find_image(img_dir, stem):
    for ext in IMG_EXTS:
        p = img_dir / f"{stem}{ext}"
        if p.exists():
            return p
    return None


def draw_yolo_boxes(img_path, label_path, out_path):
    img = cv2.imread(str(img_path))
    if img is None:
        return False

    h, w = img.shape[:2]

    has_d00 = False

    with open(label_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        parts = line.strip().split()
        if len(parts) != 5:
            continue

        cls_id = int(float(parts[0]))
        x, y, bw, bh = map(float, parts[1:])

        if cls_id == 0:
            has_d00 = True

        x1 = int((x - bw / 2) * w)
        y1 = int((y - bh / 2) * h)
        x2 = int((x + bw / 2) * w)
        y2 = int((y + bh / 2) * h)

        x1 = max(0, min(x1, w - 1))
        y1 = max(0, min(y1, h - 1))
        x2 = max(0, min(x2, w - 1))
        y2 = max(0, min(y2, h - 1))

        # D00 用较粗框，其他类别也画出来，方便判断是否误删
        thickness = 3 if cls_id == 0 else 2
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), thickness)
        cv2.putText(
            img,
            CLASS_NAMES.get(cls_id, str(cls_id)),
            (x1, max(y1 - 5, 15)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2,
        )

    if not has_d00:
        return False

    cv2.imwrite(str(out_path), img)
    return True


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    total = 0

    for split in ["train", "val"]:
        img_dir = DATASET_DIR / "images" / split
        lab_dir = DATASET_DIR / "labels" / split

        if not img_dir.exists() or not lab_dir.exists():
            continue

        for label_path in lab_dir.glob("*.txt"):
            img_path = find_image(img_dir, label_path.stem)
            if img_path is None:
                continue

            # 输出文件名前面加 train__ 或 val__，方便后面定位原始文件
            out_name = f"{split}__{label_path.stem}.jpg"
            out_path = OUT_DIR / out_name

            ok = draw_yolo_boxes(img_path, label_path, out_path)
            if ok:
                total += 1

    print(f"完成，共生成 D00 候选预览图：{total}")
    print(f"请打开这个文件夹人工检查：{OUT_DIR}")


if __name__ == "__main__":
    main()