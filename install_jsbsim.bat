@echo off
REM JSBSim 安装脚本（Windows）
chcp 65001 >nul
echo ============================================
echo JSBSim 飞行动力学引擎安装工具
echo ============================================
echo.

REM 检查是否有项目 Python
if exist "bin\python\python.exe" (
    echo 发现项目 Python: bin\python\python.exe
    echo.
    echo 正在升级 pip...
    bin\python\python.exe -m pip install --upgrade pip
    echo.
    echo 正在安装 JSBSim...
    bin\python\python.exe -m pip install jsbsim
    echo.
    echo ============================================
    if errorlevel 1 (
        echo ❌ 安装失败！
        echo.
        echo 常见问题：
        echo 1. 网络连接问题 - 检查网络
        echo 2. 缺少 C++ 编译器 - 安装 VC++ Redistributable
        echo 3. 权限问题 - 以管理员身份运行
        echo.
        echo 尝试指定版本：
        echo   bin\python\python.exe -m pip install jsbsim==1.1.13
    ) else (
        echo ✅ 安装完成！
        echo ============================================
        echo.
        echo 测试 JSBSim:
        echo   python test_jsbsim_simple.py
        echo.
        echo 启用方法：
        echo 1. 运行程序: cd source ^&^& python main.py
        echo 2. 按 F12 打开设置
        echo 3. 勾选 'Use JSBSim (Restart Required)'
        echo 4. 选择飞机型号（F-16）
        echo 5. 重启程序或重新创建飞机
    )
    echo.
) else (
    echo 未找到项目 Python: bin\python\python.exe
    echo 尝试使用系统 Python...
    echo.
    python --version >nul 2>&1
    if errorlevel 1 (
        echo ❌ 系统中也没有 Python！
        echo.
        echo 请先安装 Python:
        echo   https://www.python.org/downloads/
    ) else (
        echo 正在升级 pip...
        python -m pip install --upgrade pip
        echo.
        echo 正在安装 JSBSim...
        python -m pip install jsbsim
        echo.
        echo ============================================
        if errorlevel 1 (
            echo ❌ 安装失败！
            echo.
            echo 尝试指定版本：
            echo   python -m pip install jsbsim==1.1.13
        ) else (
            echo ✅ 安装完成！
            echo ============================================
        )
    )
)

echo.
pause

