@echo off
chcp 65001 >nul
title Lappy Lab 4.1 - Quick Build

echo.
echo ========================================
echo 🏗️ Lappy Lab 4.1 - Quick Build
echo ========================================
echo.

:: Kiểm tra Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python không được tìm thấy!
    echo 💡 Vui lòng cài đặt Python từ https://python.org
    pause
    exit /b 1
)

echo ✅ Python đã được tìm thấy
echo.

:: Kiểm tra PyInstaller
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo ⚠️ PyInstaller chưa được cài đặt
    echo 📦 Đang cài đặt PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo ❌ Không thể cài đặt PyInstaller
        pause
        exit /b 1
    )
    echo ✅ PyInstaller đã được cài đặt
)

echo ✅ PyInstaller đã sẵn sàng
echo.

:: Kiểm tra icon
if exist "public\image\icon.ico" (
    echo ✅ Icon tìm thấy: public\image\icon.ico
) else (
    echo ⚠️ Không tìm thấy icon
)
echo.

:: Build
echo 🔨 Bắt đầu build executable...
echo ⏳ Quá trình này có thể mất vài phút...
echo.

python build.py

echo.
echo ========================================
echo 🎉 Build hoàn tất!
echo ========================================

:: Kiểm tra kết quả
if exist "dist\LappyLab.exe" (
    echo ✅ File executable: dist\LappyLab.exe
    for %%I in ("dist\LappyLab.exe") do echo 📏 Kích thước: %%~zI bytes
    echo.
    echo 🚀 Có thể chạy file: dist\LappyLab.exe
    echo.
    set /p choice="Bạn có muốn mở thư mục dist? (y/N): "
    if /i "!choice!"=="y" (
        explorer dist
    )
) else (
    echo ❌ Build thất bại! Không tìm thấy file executable
)

echo.
pause
