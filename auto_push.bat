@echo off
chcp 65001
echo ======================
echo  一键上传代码到GitHub
echo ======================
:: 激活 Conda 环境，然后执行命令
call D:\py\anaconda3\Scripts\activate.bat pytorch_env

git add .
git commit -m "补充 A-Star-C3k2 的复合模块代码（与论文替换c3k2中的bottleneck一致，而不是全部替换）"
git push

echo.
echo 执行完毕！按任意键关闭窗口...
pause