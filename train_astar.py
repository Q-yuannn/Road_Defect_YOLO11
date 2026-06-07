from ultralytics import YOLO

if __name__ == '__main__':
    # 【改动 1】：读取 A_Star_C3k2 的结构，但依然加载官方预训练权重加速收敛
    model = YOLO('yolo11-AStar.yaml').load('yolo11n.pt') 
    
    # 开始第二次消融实验
    results = model.train(
        data='road.yaml',          
        epochs=200,                
        imgsz=640,                 
        batch=16,                  
        optimizer='SGD',           
        lr0=0.01,                  
        momentum=0.9,            
        weight_decay=0.0005,       
        device=0,                  
        workers=4,                 
        seed=42,
        # 换一个专属的输出文件夹，防止覆盖baseline 数据
        name='6.6_not_stable_AStar_C3k2(all_layers)_nversion_e200', 
        patience=30                
    )