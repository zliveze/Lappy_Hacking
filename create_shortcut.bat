@echo off
chcp 65001 >nul
title Tạo Shortcut Lappy Lab 4.1

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                    TẠO SHORTCUT DESKTOP                     ║
echo ║                      Lappy Lab 4.1                          ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

:: Lấy đường dẫn hiện tại
set "CURRENT_DIR=%~dp0"
set "BATCH_FILE=%CURRENT_DIR%run_admin.bat"
set "SILENT_BATCH_FILE=%CURRENT_DIR%run_silent.bat"
set "ICON_FILE=%CURRENT_DIR%assets\icons\app.ico"

:: Tạo shortcut trên Desktop
set "DESKTOP=%USERPROFILE%\Desktop"
set "SHORTCUT_NAME=Lappy Lab 4.1 (Admin).lnk"
set "SILENT_SHORTCUT_NAME=Lappy Lab 4.1 (Silent).lnk"

echo 🔄 Đang tạo shortcut trên Desktop...

:: Sử dụng PowerShell để tạo shortcut thông thường
powershell -Command ^
"$WshShell = New-Object -comObject WScript.Shell; ^
$Shortcut = $WshShell.CreateShortcut('%DESKTOP%\%SHORTCUT_NAME%'); ^
$Shortcut.TargetPath = '%BATCH_FILE%'; ^
$Shortcut.WorkingDirectory = '%CURRENT_DIR%'; ^
$Shortcut.Description = 'Lappy Lab 4.1 - Cursor Management Tool (Admin Mode)'; ^
if (Test-Path '%ICON_FILE%') { $Shortcut.IconLocation = '%ICON_FILE%' }; ^
$Shortcut.Save()"

echo 🔄 Đang tạo shortcut ẩn cửa sổ CMD...

:: Tạo shortcut cho chế độ ẩn
powershell -Command ^
"$WshShell = New-Object -comObject WScript.Shell; ^
$Shortcut = $WshShell.CreateShortcut('%DESKTOP%\%SILENT_SHORTCUT_NAME%'); ^
$Shortcut.TargetPath = '%SILENT_BATCH_FILE%'; ^
$Shortcut.WorkingDirectory = '%CURRENT_DIR%'; ^
$Shortcut.Description = 'Lappy Lab 4.1 - Cursor Management Tool (Silent Mode)'; ^
if (Test-Path '%ICON_FILE%') { $Shortcut.IconLocation = '%ICON_FILE%' }; ^
$Shortcut.Save()"

if exist "%DESKTOP%\%SHORTCUT_NAME%" (
    echo ✅ Đã tạo shortcut thành công!
    echo 📍 Vị trí: %DESKTOP%\%SHORTCUT_NAME%
    if exist "%DESKTOP%\%SILENT_SHORTCUT_NAME%" (
        echo 📍 Vị trí (Silent): %DESKTOP%\%SILENT_SHORTCUT_NAME%
    )
    echo.
    echo 🎯 Bây giờ bạn có thể:
    echo    1. Double-click "Lappy Lab 4.1 (Admin)" để chạy với cửa sổ CMD
    echo    2. Double-click "Lappy Lab 4.1 (Silent)" để chạy ẩn cửa sổ CMD
    echo    3. Hoặc chạy trực tiếp file: run_admin.bat
    echo    4. Hoặc chạy: python run.py (sẽ tự động yêu cầu quyền Admin)
) else (
    echo ❌ Lỗi tạo shortcut!
    echo Bạn có thể chạy trực tiếp file: run_admin.bat hoặc run_silent.bat
)

echo.
echo 💡 Lưu ý:
echo    - Shortcut "Admin" sẽ hiển thị cửa sổ CMD và cho phép xem log
echo    - Shortcut "Silent" sẽ ẩn cửa sổ CMD để chạy ngầm
echo    - Cả hai đều chạy với quyền Administrator để đảm bảo tính năng hoạt động đúng

echo.
pause
