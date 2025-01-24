from cx_Freeze import setup, Executable
import sys
import os

# Đường dẫn đến các files và folders cần include
files = ['app/', 'public/']

# Các thư viện cần thiết
packages = ['tkinter', 'PIL', 'json', 'uuid', 'hashlib', 'requests', 'packaging']

# Cấu hình build
build_exe_options = {
    "packages": packages,
    "include_files": files,
    "include_msvcr": True,
}

# Tạo executable
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="Lappy Hacking",
    version="2.1.2",
    description="ID Generator Tool",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "main.py",
            base=base,
            icon="public/image/icon.ico",
            target_name="Lappy_Hacking.exe"
        )
    ]
) 