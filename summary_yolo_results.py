# import os
# import csv
# import pandas as pd

# # 训练结果根目录
# root_path = "runs/"
# save_excel_name = "YOLO训练结果汇总.xlsx"

# # 要提取的指标
# collect = []

# # 遍历所有训练文件夹
# for folder in os.listdir(root_path):
#     folder_path = os.path.join(root_path, folder)
#     if not os.path.isdir(folder_path):
#         continue
    
#     csv_path = os.path.join(folder_path, "results.csv")
#     if not os.path.exists(csv_path):
#         continue

#     # 读每一次训练的最后一行（最佳结果）
#     with open(csv_path, "r", encoding="utf-8") as f:
#         reader = list(csv.DictReader(f))
#         if not reader:
#             continue
#         last_epoch = reader[-1]

#     # 提取关键指标（适配 YOLO11/YOLOv8 通用字段）
#     row = {
#         "训练目录": folder,
#         "精确率P": round(float(last_epoch["metrics/precision"]), 4),
#         "召回率R": round(float(last_epoch["metrics/recall"]), 4),
#         "mAP@0.5": round(float(last_epoch["metrics/mAP50"]), 4),
#         "mAP@0.5:0.95": round(float(last_epoch["metrics/mAP50-95"]), 4)
#     }
#     collect.append(row)

# # 保存成Excel
# df = pd.DataFrame(collect)
# df.to_excel(save_excel_name, index=False)
# print(f"✅ 汇总完成，已保存到：{save_excel_name}")
# print("\n汇总结果：")
# print(df)
import pandas as pd
from pathlib import Path

# 自动递归查找 runs 下面所有 results.csv
ROOT = Path("runs")
SAVE_EXCEL_NAME = "YOLO训练结果汇总_best.xlsx"

records = []


def find_column(columns, include_keywords, exclude_keywords=None):
    """
    根据关键词自动匹配 YOLO results.csv 中的列名。
    兼容：
    metrics/mAP50(B)
    metrics/mAP50-95(B)
    metrics/precision(B)
    metrics/recall(B)
    以及没有 (B) 的旧字段。
    """
    exclude_keywords = exclude_keywords or []

    for col in columns:
        clean = col.replace(" ", "")

        if all(k in clean for k in include_keywords) and not any(k in clean for k in exclude_keywords):
            return col

    return None


def main():
    result_files = list(ROOT.rglob("results.csv"))

    if not result_files:
        print("没有找到 results.csv，请检查 runs 目录。")
        return

    for csv_path in result_files:
        df = pd.read_csv(csv_path)

        # 去掉列名前后的空格
        df.columns = [c.strip() for c in df.columns]

        precision_col = find_column(df.columns, ["metrics/precision"])
        recall_col = find_column(df.columns, ["metrics/recall"])
        map50_col = find_column(df.columns, ["metrics/mAP50"], exclude_keywords=["95"])
        map5095_col = find_column(df.columns, ["metrics/mAP50-95"])

        if map5095_col is None:
            print(f"跳过：{csv_path}，原因：找不到 mAP50-95 列")
            continue

        # 以 mAP@0.5:0.95 最高的 epoch 作为最佳结果
        best_idx = df[map5095_col].idxmax()
        best_row = df.loc[best_idx]

        run_name = csv_path.parent.name
        run_path = str(csv_path.parent)

        record = {
            "训练目录": run_name,
            "路径": run_path,
            "最佳epoch": int(best_row["epoch"]) if "epoch" in df.columns else int(best_idx + 1),
            "Precision": round(float(best_row[precision_col]), 4) if precision_col else None,
            "Recall": round(float(best_row[recall_col]), 4) if recall_col else None,
            "mAP@0.5": round(float(best_row[map50_col]), 4) if map50_col else None,
            "mAP@0.5:0.95": round(float(best_row[map5095_col]), 4),
        }

        records.append(record)

    if not records:
        print("没有成功提取任何训练结果。")
        return

    out_df = pd.DataFrame(records)

    # 按 mAP@0.5:0.95 从高到低排序
    out_df = out_df.sort_values(by="mAP@0.5:0.95", ascending=False)

    out_df.to_excel(SAVE_EXCEL_NAME, index=False)

    print("✅ 汇总完成")
    print(f"已保存到：{SAVE_EXCEL_NAME}")
    print()
    print(out_df)


if __name__ == "__main__":
    main()