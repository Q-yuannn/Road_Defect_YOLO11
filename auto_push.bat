@echo off
chcp 65001
echo ======================
echo  一键上传代码到GitHub
echo ======================
:: 激活 Conda 环境，然后执行命令
call D:\py\anaconda3\Scripts\activate.bat pytorch_env

git add .
git commit -m "新增残差版 SPPF，不覆盖原类，方便消融实验"
git push

echo.
echo 执行完毕！按任意键关闭窗口...
pause