from ultralytics import YOLO

if __name__ == '__main__':
    # 1. 加载官方的 YOLO11n 结构配置和预训练权重作为基线模型
    model = YOLO('yolo11n.yaml').load('yolo11n.pt') 
    
    # 2. 开始训练
    results = model.train(
        data='road.yaml',          # 指向配置文件
        epochs=100,                # 训练100轮
        imgsz=640,                 # 图像输入尺寸 (论文标准尺寸)
        batch=16,          
        optimizer='SGD',           # 优化器使用 SGD
        lr0=0.01,                  # 初始学习率 0.01
        momentum=0.937,            # 动量参数 0.937
        weight_decay=0.0005,       # 权重衰减 0.0005

        device=0,                  # 指定使用第一张显卡 (RTX 4060)
        workers=4,                 # 开启多线程数据加载加速
        name='baseline_yolo11n',   # 训练结果保存的文件夹名称
        patience=30                # 早停机制：如果 30 轮 mAP 没有提升就自动停止
    )