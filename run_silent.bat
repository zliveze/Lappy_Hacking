@echo off
chcp 65001 >nul

:: Kiểm tra quyền admin
net session >nul 2>&1
if %errorLevel% == 0 (
    goto :run_app
) else (
    :: Chạy lại với quyền admin (ẩn hoàn toàn cửa sổ)
    powershell -WindowStyle Hidden -Command "Start-Process '%~f0' -Verb RunAs -WindowStyle Hidden"
    exit /b
)

:run_app
:: Chuyển đến thư mục script
cd /d "%~dp0"

:: Ưu tiên chạy với pythonw.exe (không hiển thị console)
where pythonw >nul 2>&1
if %errorLevel% == 0 (
    pythonw main.pyw
) else (
    :: Nếu không có pythonw, sử dụng PowerShell để ẩn cửa sổ
    powershell -WindowStyle Hidden -Command "python main.pyw"
)

exit /b
