@echo off
echo ===== BUILD WITH BASE64 ICON =====

REM Kiem tra Python
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [LOI] Khong tim thay Python. Vui long cai dat Python 3.6 tro len.
    goto :end
)

REM Kiem tra PyInstaller
python -c "import PyInstaller" >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [THONG BAO] Dang cai dat PyInstaller...
    pip install pyinstaller
    if %ERRORLEVEL% neq 0 (
        echo [LOI] Khong the cai dat PyInstaller.
        goto :end
    )
)

REM Kiem tra cac thu vien can thiet
echo [THONG BAO] Dang kiem tra va cai dat cac thu vien can thiet...
pip install -r requirements.txt

REM Chay script chuyen doi icon thanh base64
echo [THONG BAO] Dang chuyen doi icon thanh base64...
python convert_icon.py

REM Kiem tra thu muc dist va xoa neu ton tai
if exist dist (
    echo [THONG BAO] Dang xoa thu muc dist cu...
    rmdir /s /q dist
)

REM Kiem tra thu muc build va xoa neu ton tai
if exist build (
    echo [THONG BAO] Dang xoa thu muc build cu...
    rmdir /s /q build
)

REM Build ung dung
echo [THONG BAO] Dang build ung dung...
pyinstaller --onefile --windowed --uac-admin --name=LappyLab main.py

if %ERRORLEVEL% neq 0 (
    echo [LOI] Qua trinh build that bai.
    goto :end
)

echo.
echo [THANH CONG] Da build ung dung thanh cong!
echo File thuc thi nam tai: %CD%\dist\LappyLab.exe

REM Kiem tra xem file exe da duoc tao chua
if exist dist\LappyLab.exe (
    echo [THONG BAO] Dang tao shortcut tren Desktop...
    powershell "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\Lappy Lab 4.0.lnk'); $Shortcut.TargetPath = '%CD%\dist\LappyLab.exe'; $Shortcut.Save()"
) else (
    echo [CANH BAO] Khong tim thay file LappyLab.exe trong thu muc dist
)

:end
echo.
echo ===== KET THUC QUA TRINH BUILD =====
pause
