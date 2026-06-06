@echo off
chcp 65001
echo ======================
echo  一键上传代码到GitHub
echo ======================
:: 激活 Conda 环境，然后执行命令
call D:\py\anaconda3\Scripts\activate.bat pytorch_env

git add .
git commit -m "生成 D00 带框预览图，方便后续筛选RDD中有效图和框数据，新建review_D00_bad文件夹存储不合格的D00图和框数据，后续人工审核并删除不合格的数据。"
git push

echo.
echo 执行完毕！按任意键关闭窗口...
pause