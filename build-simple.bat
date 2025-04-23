@echo off
echo ===== SIMPLE BUILD LAPPY LAB 4.0 =====

REM Cai dat PyInstaller
pip install pyinstaller

REM Build ung dung
pyinstaller --onefile --windowed --icon="%CD%\public\images\icon.ico" --uac-admin --name=LappyLab main.py

echo ===== BUILD DONE =====
pause
