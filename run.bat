@echo off
echo Starting File Server...

:: 检查 Python 虚拟环境是否存在
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate
    echo Installing development dependencies...
    pip install -r requirements-dev.txt
) else (
    call venv\Scripts\activate
)

:: 启动服务器
echo Starting server...
if "%~1"=="" (
    python file_server.py
) else (
    python file_server.py --dir "%~1"
)
