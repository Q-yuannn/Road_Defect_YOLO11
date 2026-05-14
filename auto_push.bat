@echo off
chcp 65001
echo ======================
echo  一键上传代码到GitHub
echo ======================
:: 激活 Conda 环境，然后执行命令
call D:\py\anaconda3\Scripts\activate.bat pytorch_env

git add .
git commit -m "添加A-Star-C3k2 的注册逻辑，并在 yolo11-AStar.yaml（新建，原yolo模型也有）中使用它"
git push

echo.
echo 执行完毕！按任意键关闭窗口...
pause