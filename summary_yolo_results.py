import os
import csv
import pandas as pd

# 训练结果根目录
root_path = "runs/"
save_excel_name = "YOLO训练结果汇总.xlsx"

# 要提取的指标
collect = []

# 遍历所有训练文件夹
for folder in os.listdir(root_path):
    folder_path = os.path.join(root_path, folder)
    if not os.path.isdir(folder_path):
        continue
    
    csv_path = os.path.join(folder_path, "results.csv")
    if not os.path.exists(csv_path):
        continue

    # 读每一次训练的最后一行（最佳结果）
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
        if not reader:
            continue
        last_epoch = reader[-1]

    # 提取关键指标（适配 YOLO11/YOLOv8 通用字段）
    row = {
        "训练目录": folder,
        "精确率P": round(float(last_epoch["metrics/precision"]), 4),
        "召回率R": round(float(last_epoch["metrics/recall"]), 4),
        "mAP@0.5": round(float(last_epoch["metrics/mAP50"]), 4),
        "mAP@0.5:0.95": round(float(last_epoch["metrics/mAP50-95"]), 4)
    }
    collect.append(row)

# 保存成Excel
df = pd.DataFrame(collect)
df.to_excel(save_excel_name, index=False)
print(f"✅ 汇总完成，已保存到：{save_excel_name}")
print("\n汇总结果：")
print(df)