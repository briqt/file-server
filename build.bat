@echo on
echo Installing requirements...
python -m pip install -r requirements.txt
echo Building executable...
python -m PyInstaller FileServer.spec --clean
if errorlevel 1 (
    echo Build failed! Check the error messages above.
    pause
    exit /b 1
)
echo Done! You can find the executable in the dist folder.
pause
