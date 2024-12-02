@echo on
echo Cleaning build directories...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist

echo Cleaning virtual environments...
if exist "venv" rmdir /s /q venv
if exist "venv-build" rmdir /s /q venv-build

echo Cleaning Python cache...
if exist "__pycache__" rmdir /s /q __pycache__
if exist "*.pyc" del /s /q *.pyc

echo Done!
pause
