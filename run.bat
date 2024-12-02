@echo off
echo Starting File Server...

:: 检查 Python 虚拟环境是否存在
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate
    echo Installing dependencies...
    pip install flask
) else (
    call venv\Scripts\activate
)

:: 启动服务器
echo Starting server...
python file_server.py
