@echo off
chcp 65001 >nul

:: Kiểm tra quyền admin
net session >nul 2>&1
if %errorLevel% == 0 (
    goto :run_app
) else (
    :: Chạy lại với quyền admin (ẩn cửa sổ)
    powershell -WindowStyle Hidden -Command "Start-Process '%~f0' -Verb RunAs -WindowStyle Hidden"
    exit /b
)

:run_app
:: Chuyển đến thư mục script
cd /d "%~dp0"

:: Chạy ứng dụng với pythonw.exe (không hiển thị console)
pythonw main.pyw

:: Nếu pythonw không có, thử python
if errorlevel 1 (
    python main.pyw
)

exit /b
