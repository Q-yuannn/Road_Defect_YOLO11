@echo off
chcp 65001
echo ======================
echo  一键上传代码到GitHub
echo ======================
:: 激活 Conda 环境，然后执行命令
call D:\py\anaconda3\Scripts\activate.bat pytorch_env

git add .
git commit -m "纠错，没有正确注册SC_DFF_SPPF模块，导致训练时找不到该模块，现已修正并测试通过。"
git push

echo.
echo 执行完毕！按任意键关闭窗口...
pause