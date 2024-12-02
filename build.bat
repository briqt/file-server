@echo off
:: Clean old build files
echo Cleaning old build files...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist

:: Create and activate virtual environment
if not exist "venv-build" (
    echo Creating build virtual environment...
    python -m venv venv-build
)
call venv-build\Scripts\activate

:: Install production dependencies
echo Installing production requirements...
python -m pip install -r requirements.txt

:: Build executable
echo Building executable...
python -m PyInstaller FileServer.spec --clean
if errorlevel 1 (
    echo Build failed! Check the error messages above.
    call venv-build\Scripts\deactivate
    pause
    exit /b 1
)

:: Cleanup and exit
call venv-build\Scripts\deactivate
echo Done! You can find the executable in the dist folder.
pause
