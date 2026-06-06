from ultralytics import YOLO

if __name__ == '__main__':
    
    model = YOLO('yolo11-NBE.yaml').load('yolo11n.pt') 
    
    # 开始第三次消融实验
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
        name='6.5_BE_stabel(2_layers_astar&gmma=0.01)_e200', 
        patience=30                
    )