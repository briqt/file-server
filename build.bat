@echo on
:: 清理旧的构建文件
echo Cleaning old build files...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist

:: 创建并激活虚拟环境
if not exist "venv-build" (
    echo Creating build virtual environment...
    python -m venv venv-build
)
call venv-build\Scripts\activate

:: 安装生产依赖
echo Installing production requirements...
python -m pip install -r requirements.txt

:: 构建可执行文件
echo Building executable...
python -m PyInstaller FileServer.spec --clean
if errorlevel 1 (
    echo Build failed! Check the error messages above.
    deactivate
    pause
    exit /b 1
)

:: 清理并退出
deactivate
echo Done! You can find the executable in the dist folder.
pause
