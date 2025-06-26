#!/bin/bash

echo "========================================"
echo "数据分析师岗位分析看板安装脚本"
echo "========================================"
echo

echo "正在检查Python环境..."
python3 --version
if [ $? -ne 0 ]; then
    echo "错误：未找到Python环境，请先安装Python 3.7+"
    exit 1
fi

echo
echo "正在安装依赖包..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "错误：依赖包安装失败"
    exit 1
fi

echo
echo "安装完成！"
echo
echo "启动方式："
echo "1. 运行 python3 run_dashboard.py"
echo "2. 或运行 streamlit run DS_interactive_dashboard.py"
echo 