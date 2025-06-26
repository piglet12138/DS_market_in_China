@echo off
echo ========================================
echo 数据分析师岗位分析看板安装脚本
echo ========================================
echo.

echo 正在检查Python环境...
python --version
if %errorlevel% neq 0 (
    echo 错误：未找到Python环境，请先安装Python 3.7+
    pause
    exit /b 1
)

echo.
echo 正在安装依赖包...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo 错误：依赖包安装失败
    pause
    exit /b 1
)

echo.
echo 安装完成！
echo.
echo 启动方式：
echo 1. 运行 python run_dashboard.py
echo 2. 或运行 streamlit run DS_interactive_dashboard.py
echo.
echo 按任意键退出...
pause > nul 