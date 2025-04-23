@echo off
echo ===== BAT DAU BUILD LAPPY LAB 4.0 =====
echo.

REM Cai dat PyInstaller neu chua co
python -c "import PyInstaller" >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Dang cai dat PyInstaller...
    pip install pyinstaller
)

REM Cai dat cac thu vien can thiet
echo Dang cai dat cac thu vien can thiet...
pip install -r requirements.txt

REM Xoa thu muc build va dist cu
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build

REM Build ung dung
echo Dang build ung dung...
pyinstaller --onefile --windowed --icon=public\images\icon.ico --name=LappyLab main.py

if %ERRORLEVEL% neq 0 (
    echo Build that bai!
) else (
    echo.
    echo Build thanh cong!
    echo File thuc thi: %CD%\dist\LappyLab.exe
    
    REM Tao shortcut tren Desktop
    if exist dist\LappyLab.exe (
        echo Dang tao shortcut tren Desktop...
        powershell "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\Lappy Lab 4.0.lnk'); $Shortcut.TargetPath = '%CD%\dist\LappyLab.exe'; $Shortcut.IconLocation = '%CD%\public\images\icon.ico'; $Shortcut.Save()"
    )
)

echo.
echo ===== KET THUC BUILD =====
pause
