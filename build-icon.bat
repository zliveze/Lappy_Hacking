@echo off
echo ===== BUILD WITH ICON =====

REM Kiem tra icon
echo Kiem tra icon...
if not exist "public\images\icon.ico" (
    echo Khong tim thay file icon.ico!
    goto :end
) else (
    echo Tim thay file icon.ico tai: %CD%\public\images\icon.ico
)

REM Cai dat PyInstaller
pip install pyinstaller

REM Build ung dung
echo Dang build ung dung voi icon...
pyinstaller --onefile --windowed --icon="%CD%\public\images\icon.ico" --uac-admin --add-data "%CD%\public\images;public\images" --name=LappyLab main.py

if %ERRORLEVEL% neq 0 (
    echo Build that bai!
) else (
    echo Build thanh cong!
    echo File thuc thi: %CD%\dist\LappyLab.exe
)

:end
echo ===== BUILD DONE =====
pause
