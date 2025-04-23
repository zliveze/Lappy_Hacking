@echo off
echo ===== BUILD WITH RESOURCE =====

REM Cai dat PyInstaller
pip install pyinstaller

REM Build ung dung voi resource
echo Dang build ung dung voi resource...
pyinstaller --onefile --windowed --uac-admin --add-data "public\images\icon.ico;public\images" --resource=resource.rc --name=LappyLab main.py

if %ERRORLEVEL% neq 0 (
    echo Build that bai!
) else (
    echo Build thanh cong!
    echo File thuc thi: %CD%\dist\LappyLab.exe
)

echo ===== BUILD DONE =====
pause
