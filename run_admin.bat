@echo off
chcp 65001 >nul
title Lappy Lab 4.1 - Admin Mode

:: Kiểm tra quyền admin
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Đang chạy với quyền Administrator
    goto :run_app
) else (
    echo ⚠️  Cần quyền Administrator để chạy ứng dụng
    echo 🔄 Đang yêu cầu quyền Administrator...
    
    :: Chạy lại với quyền admin
    powershell -Command "Start-Process cmd -ArgumentList '/c cd /d \"%~dp0\" && \"%~f0\"' -Verb RunAs"
    exit /b
)

:run_app
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                        LAPPY LAB 4.1                        ║
echo ║                   Cursor Management Tool                     ║
echo ║                     Admin Mode                               ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

:: Chuyển đến thư mục script
cd /d "%~dp0"

:: Kiểm tra Python
echo [1/3] Kiểm tra Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python chưa được cài đặt!
    echo Vui lòng cài đặt Python 3.8+ từ: https://python.org
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION% đã được cài đặt

:: Kiểm tra dependencies
echo.
echo [2/3] Kiểm tra dependencies...
python -c "import tkinter, colorama, requests, psutil" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Một số dependencies chưa được cài đặt
    echo 🔄 Đang cài đặt dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Lỗi cài đặt dependencies!
        pause
        exit /b 1
    )
)
echo ✅ Dependencies đã sẵn sàng

:: Chạy ứng dụng
echo.
echo [3/3] Khởi động ứng dụng...
echo 🚀 Đang khởi động Lappy Lab với quyền Administrator...
echo.
echo Chọn chế độ chạy:
echo [1] Chạy với cửa sổ CMD (mặc định)
echo [2] Chạy ẩn cửa sổ CMD
echo.
set /p choice="Nhập lựa chọn (1 hoặc 2, Enter = 1): "

if "%choice%"=="2" (
    echo 🔇 Chạy ở chế độ ẩn...
    pythonw main.pyw
    if errorlevel 1 (
        echo ⚠️  Không thể chạy với pythonw, thử python...
        python main.pyw
    )
) else (
    echo 🖥️  Chạy với cửa sổ CMD...
    python main.py
)

:: Xử lý kết thúc
echo.
if errorlevel 1 (
    echo ❌ Ứng dụng đã thoát với lỗi
) else (
    echo ✅ Ứng dụng đã thoát bình thường
)

echo.
echo 👋 Cảm ơn bạn đã sử dụng Lappy Lab 4.1!
pause
