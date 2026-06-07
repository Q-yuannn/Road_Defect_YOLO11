from pathlib import Path
import shutil

# 只写你自己标注错的补充数据标签目录
# 不要写 RDD2022 或 RDD2022_filtered 的 labels 路径
LABEL_DIRS = [
    Path("filtered_extra_data/道路坑洼裂缝/patel_cracks"),
    Path("filtered_extra_data/道路坑洼裂缝/patel_potholes"),
    Path("filtered_extra_data/道路坑洼裂缝/pothole_dataset"),
]

# 错误类别 -> 正确类别
# 你之前把 D20 标成 0，把 D40 标成 1
# 所以要改成：0 -> 2, 1 -> 3
ID_MAP = {
    0: 2,
    1: 3,
}


def fix_one_txt(txt_path):
    # 先备份一次，避免改错无法恢复
    backup_path = txt_path.with_suffix(".txt.bak")
    if not backup_path.exists():
        shutil.copy2(txt_path, backup_path)

    new_lines = []
    changed = False

    with open(txt_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()

        if not line:
            continue

        parts = line.split()

        if len(parts) != 5:
            print(f"格式异常，跳过这一行：{txt_path} -> {line}")
            continue

        old_id = int(float(parts[0]))
        new_id = ID_MAP.get(old_id, old_id)

        if new_id != old_id:
            changed = True

        parts[0] = str(new_id)
        new_lines.append(" ".join(parts))

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines))

    return changed


def main():
    total_txt = 0
    changed_txt = 0

    for label_dir in LABEL_DIRS:
        if not label_dir.exists():
            print(f"路径不存在，跳过：{label_dir}")
            continue

        txt_files = list(label_dir.rglob("*.txt"))

        print(f"\n处理目录：{label_dir}")
        print(f"发现 txt 数量：{len(txt_files)}")

        for txt_path in txt_files:
            # 跳过备份文件
            if txt_path.name.endswith(".txt.bak"):
                continue

            total_txt += 1

            changed = fix_one_txt(txt_path)

            if changed:
                changed_txt += 1

    print("\n========== 修正完成 ==========")
    print(f"处理 txt 文件数：{total_txt}")
    print(f"发生类别修改的 txt 文件数：{changed_txt}")
    print("每个 txt 已自动生成 .txt.bak 备份")


if __name__ == "__main__":
    main()