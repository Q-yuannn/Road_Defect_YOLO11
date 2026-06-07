@echo off
chcp 65001
echo ======================
echo  一键上传代码到GitHub
echo ======================
:: 激活 Conda 环境，然后执行命令
call D:\py\anaconda3\Scripts\activate.bat pytorch_env

git add .
git commit -m "人工筛选RDD不合格数据，在此过程建议了查询各类框数量的代码，并创建了RDD筛选后的数据集储存在了RDD_filtered文件夹中，同时加入了其他两个小数据集的数据（主要补充了D40），并且按811的比例重新划分了数据集"
git push

echo.
echo 执行完毕！按任意键关闭窗口...
pause