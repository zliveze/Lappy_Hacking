@echo off
chcp 65001 >nul
title Lappy Lab 4.1 - Cài đặt

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                        LAPPY LAB 4.1                        ║
echo ║                   Cursor Management Tool                     ║
echo ║                     Cài đặt tự động                         ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

:: Kiểm tra Python
echo [1/4] Kiểm tra Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python chưa được cài đặt!
    echo Vui lòng cài đặt Python 3.8+ từ: https://python.org
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION% đã được cài đặt

:: Kiểm tra pip
echo.
echo [2/4] Kiểm tra pip...
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip chưa được cài đặt!
    echo Vui lòng cài đặt pip
    pause
    exit /b 1
)
echo ✅ pip đã sẵn sàng

:: Cài đặt dependencies
echo.
echo [3/4] Cài đặt dependencies...
echo Đang cài đặt các package cần thiết...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Lỗi cài đặt dependencies!
    echo Thử chạy lại với quyền Administrator
    pause
    exit /b 1
)
echo ✅ Đã cài đặt thành công tất cả dependencies

:: Kiểm tra cài đặt
echo.
echo [4/4] Kiểm tra cài đặt...
python -c "import tkinter, colorama, requests, psutil; print('✅ Tất cả module đã sẵn sàng')" 2>nul
if errorlevel 1 (
    echo ❌ Một số module chưa được cài đặt đúng
    pause
    exit /b 1
)

:: Hoàn thành
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                    CÀI ĐẶT HOÀN TẤT!                        ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo ✅ Lappy Lab 4.1 đã sẵn sàng sử dụng!
echo.
echo Cách chạy ứng dụng:
echo   1. Chạy file: run.py
echo   2. Hoặc: python main.py
echo   3. Hoặc: python run.py
echo.

:: Hỏi có muốn chạy ngay không
set /p RUN_NOW="Bạn có muốn chạy Lappy Lab ngay bây giờ? (y/N): "
if /i "%RUN_NOW%"=="y" (
    echo.
    echo 🚀 Đang khởi động Lappy Lab...
    python run.py
) else (
    echo.
    echo 👋 Cảm ơn bạn đã cài đặt Lappy Lab 4.1!
    echo Chạy "python run.py" để bắt đầu sử dụng.
)

echo.
pause
