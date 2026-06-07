from pathlib import Path
from collections import Counter, defaultdict

CLASS_NAMES = {
    0: "D00",
    1: "D10",
    2: "D20",
    3: "D40",
}

CHECK_DIRS = {
    "old_RDD_train": Path("datasets/RDD2022/labels/train"),
    "old_RDD_val": Path("datasets/RDD2022/labels/val"),

    "filtered_RDD_train": Path("datasets/RDD2022_filtered/labels/train"),
    "filtered_RDD_val": Path("datasets/RDD2022_filtered/labels/val"),

    "extra_yolo": Path("raw_data_balanced/extra_yolo/labels"),

    "final_train": Path("datasets/RoadDefect_Balanced_811/labels/train"),
    "final_val": Path("datasets/RoadDefect_Balanced_811/labels/val"),
    "final_test": Path("datasets/RoadDefect_Balanced_811/labels/test"),
}


def count_labels(label_dir):
    counter = Counter()
    invalid = Counter()
    txt_count = 0

    if not label_dir.exists():
        return counter, invalid, txt_count

    for txt_path in label_dir.rglob("*.txt"):
        if txt_path.name.endswith(".bak"):
            continue

        txt_count += 1

        with open(txt_path, "r", encoding="utf-8") as f:
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
                else:
                    invalid[cls_id] += 1

    return counter, invalid, txt_count


def print_counter(name, counter, invalid, txt_count):
    total = sum(counter.values())

    print(f"\n========== {name} ==========")
    print(f"txt 文件数: {txt_count}")
    print(f"有效框总数: {total}")

    for cls_id, cls_name in CLASS_NAMES.items():
        num = counter[cls_id]
        ratio = num / total * 100 if total > 0 else 0
        print(f"{cls_id} ({cls_name}): {num} ({ratio:.2f}%)")

    if invalid:
        print("发现非法类别编号：")
        for k, v in invalid.items():
            print(f"  class {k}: {v} 个框")


def main():
    all_results = {}

    for name, label_dir in CHECK_DIRS.items():
        counter, invalid, txt_count = count_labels(label_dir)
        all_results[name] = counter
        print_counter(name, counter, invalid, txt_count)

    print("\n========== 对比提醒 ==========")
    old_rdd = all_results["old_RDD_train"] + all_results["old_RDD_val"]
    filtered_rdd = all_results["filtered_RDD_train"] + all_results["filtered_RDD_val"]
    extra = all_results["extra_yolo"]
    final_all = all_results["final_train"] + all_results["final_val"] + all_results["final_test"]

    print("\nold RDD 总计：")
    for i, n in CLASS_NAMES.items():
        print(f"  {n}: {old_rdd[i]}")

    print("\nfiltered RDD 总计：")
    for i, n in CLASS_NAMES.items():
        print(f"  {n}: {filtered_rdd[i]}")

    print("\nextra_yolo 总计：")
    for i, n in CLASS_NAMES.items():
        print(f"  {n}: {extra[i]}")

    print("\nfinal 8:1:1 总计：")
    for i, n in CLASS_NAMES.items():
        print(f"  {n}: {final_all[i]}")

    print("\n理论上 final 应该大约等于 filtered RDD + extra_yolo。")
    print("如果 final 明显更大，说明合并时混入了重复数据或旧数据。")
    print("如果 extra_yolo 里还有 D00/D10，而你确认只标了 D20/D40，说明补充数据标签仍有问题。")
    print("如果 filtered RDD 的 D00 没比 old RDD 少，说明 review_D00_bad 没有真正筛掉样本。")


if __name__ == "__main__":
    main()