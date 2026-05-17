from ultralytics import YOLO

if __name__ == '__main__':
    
    model = YOLO('yolo11-NBE.yaml').load('yolo11n.pt') 
    
    # 开始第三次消融实验
    results = model.train(
        data='road.yaml',          
        epochs=150,                
        imgsz=640,                 
        batch=16,                  
        optimizer='SGD',           
        lr0=0.01,                  
        momentum=0.937,            
        weight_decay=0.0005,       
        device=0,                  
        workers=4,                 
        # 换一个专属的输出文件夹，防止覆盖baseline 数据
        name='ablation_NBE', 
        patience=30                
    )