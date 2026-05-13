import os
import random
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

# RDD2022 核心道路缺陷类别 (D00:纵向裂缝, D10:横向裂缝, D20:网状裂缝, D40:坑洞)
CLASSES = ["D00", "D10", "D20", "D40"]

def convert_box(size, box):
    # 将绝对坐标转换为 YOLO 需要的归一化中心点坐标
    dw = 1. / size[0]
    dh = 1. / size[1]
    x = (box[0] + box[1]) / 2.0 - 1
    y = (box[2] + box[3]) / 2.0 - 1
    w = box[1] - box[0]
    h = box[3] - box[2]
    return (x * dw, y * dh, w * dw, h * dh)

def main():
    # 路径设置
    raw_images_dir = 'raw_data/images'
    raw_xmls_dir = 'raw_data/xmls'
    out_dir = 'datasets/RDD2022'
    
    # 创建 YOLO 标准目录结构
    dirs_to_make = ['images/train', 'images/val', 'labels/train', 'labels/val']
    for d in dirs_to_make:
        Path(os.path.join(out_dir, d)).mkdir(parents=True, exist_ok=True)

    # 获取所有有对应 xml 的图片
    xml_files = [f for f in os.listdir(raw_xmls_dir) if f.endswith('.xml')]
    random.shuffle(xml_files) # 随机打乱

    # 8:2 划分训练集和验证集
    split_index = int(len(xml_files) * 0.8)
    train_files = xml_files[:split_index]
    val_files = xml_files[split_index:]

    def process_files(files, split_type):
        print(f"正在处理 {split_type} 数据集...")
        for xml_file in files:
            img_name = xml_file.replace('.xml', '.jpg')
            img_path = os.path.join(raw_images_dir, img_name)
            
            # 如果图片不存在则跳过
            if not os.path.exists(img_path):
                continue
                
            # 解析 XML
            tree = ET.parse(os.path.join(raw_xmls_dir, xml_file))
            root = tree.getroot()
            size = root.find('size')
            w, h = int(size.find('width').text), int(size.find('height').text)
            
            # 写入 YOLO 格式的 txt
            txt_path = os.path.join(out_dir, f'labels/{split_type}', xml_file.replace('.xml', '.txt'))
            has_obj = False
            with open(txt_path, 'w') as out_file:
                for obj in root.iter('object'):
                    cls = obj.find('name').text
                    if cls not in CLASSES:
                        continue
                    cls_id = CLASSES.index(cls)
                    xmlbox = obj.find('bndbox')
                    b = (float(xmlbox.find('xmin').text), float(xmlbox.find('xmax').text),
                         float(xmlbox.find('ymin').text), float(xmlbox.find('ymax').text))
                    bb = convert_box((w, h), b)
                    out_file.write(f"{cls_id} {' '.join(map(str, bb))}\n")
                    has_obj = True
            
            # 只有当图片中包含目标类别时，才复制图片
            if has_obj:
                shutil.copy(img_path, os.path.join(out_dir, f'images/{split_type}', img_name))
            else:
                os.remove(txt_path) # 清理空标签

    process_files(train_files, 'train')
    process_files(val_files, 'val')
    print("🎉 数据集转换并划分完成！已经存入 datasets/RDD2022 目录。")

if __name__ == '__main__':
    main()