from cx_Freeze import setup, Executable
import sys
import os

# Đường dẫn đến các files và folders cần include
files = [
    os.path.join(os.getcwd(), 'app/'),
    os.path.join(os.getcwd(), 'public/'),
]

# Các thư viện cần thiết
packages = ['tkinter', 'Pillow', 'json', 'uuid', 'hashlib', 'requests', 'packaging']

# Cấu hình build
build_exe_options = {
    "packages": packages,
    "include_files": files,
    "include_msvcr": True,  # Bao gồm runtime Microsoft C++ nếu cần
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
            script="main.py",  # Đường dẫn file script chính
            base=base,
            icon=os.path.join(os.getcwd(), 'public', 'image', 'icon.ico'),
            target_name="Lappy_Hacking.exe"
        )
    ]
)
