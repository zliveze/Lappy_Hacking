import os
import sys
import platform
import tempfile
import subprocess
from colorama import Fore, Style, init
from config import EMOJI

# Khởi tạo colorama
init()

def create_admin_script(script_content, script_name="admin_task.ps1"):
    """Tạo script PowerShell để chạy với quyền admin"""
    try:
        # Tạo thư mục tạm thời nếu cần
        temp_dir = tempfile.gettempdir()
        script_path = os.path.join(temp_dir, script_name)
        
        # Ghi nội dung script
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script_content)
        
        print(f"{Fore.GREEN}{EMOJI['INFO']} Đã tạo script tại: {script_path}{Style.RESET_ALL}")
        return script_path
    except Exception as e:
        print(f"{Fore.RED}{EMOJI['ERROR']} Lỗi khi tạo script: {str(e)}{Style.RESET_ALL}")
        return None

def run_as_admin_powershell(script_path):
    """Chạy script PowerShell với quyền admin"""
    try:
        if platform.system() != "Windows":
            print(f"{Fore.RED}{EMOJI['ERROR']} Chức năng này chỉ hỗ trợ Windows.{Style.RESET_ALL}")
            return False
        
        # Tạo lệnh PowerShell để chạy script với quyền admin
        command = f'Start-Process powershell -ArgumentList "-ExecutionPolicy Bypass -File \"{script_path}\"" -Verb RunAs -Wait'
        
        # Tạo script tạm thời để chạy lệnh trên
        launcher_script = os.path.join(tempfile.gettempdir(), "launch_admin.ps1")
        with open(launcher_script, "w", encoding="utf-8") as f:
            f.write(command)
        
        # Chạy script launcher
        print(f"{Fore.CYAN}{EMOJI['INFO']} Đang yêu cầu quyền admin để thực hiện thay đổi...{Style.RESET_ALL}")
        result = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", launcher_script], 
                               capture_output=True, text=True)
        
        # Xóa script launcher
        try:
            os.remove(launcher_script)
        except:
            pass
        
        if result.returncode == 0:
            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Đã thực hiện thay đổi với quyền admin.{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}{EMOJI['ERROR']} Lỗi khi chạy script với quyền admin: {result.stderr}{Style.RESET_ALL}")
            return False
    except Exception as e:
        print(f"{Fore.RED}{EMOJI['ERROR']} Lỗi khi chạy script với quyền admin: {str(e)}{Style.RESET_ALL}")
        return False

def create_disable_auto_update_script(update_yml_path, updater_path=None):
    """Tạo script PowerShell để vô hiệu hóa tự động cập nhật"""
    script = f"""
# Script để vô hiệu hóa tự động cập nhật Cursor
Write-Host "Đang vô hiệu hóa tự động cập nhật Cursor..." -ForegroundColor Cyan

# Tạo backup nếu file tồn tại
if (Test-Path "{update_yml_path}") {{
    $backupPath = "{update_yml_path}.backup"
    Copy-Item -Path "{update_yml_path}" -Destination $backupPath -Force
    Write-Host "Đã tạo backup tại: $backupPath" -ForegroundColor Green
}}

# Tạo nội dung YAML
$yamlContent = @"
autoUpdater:
  autoDownload: false
  autoInstallOnAppQuit: false
"@

# Ghi nội dung vào file
Set-Content -Path "{update_yml_path}" -Value $yamlContent -Force
Write-Host "Đã vô hiệu hóa tự động cập nhật trong file app-update.yml" -ForegroundColor Green

"""

    # Thêm phần vô hiệu hóa thư mục updater nếu có
    if updater_path:
        script += f"""
# Vô hiệu hóa thư mục updater
if (Test-Path "{updater_path}") {{
    $disabledPath = "{updater_path}.disabled"
    
    # Xóa thư mục disabled cũ nếu tồn tại
    if (Test-Path $disabledPath) {{
        Remove-Item -Path $disabledPath -Recurse -Force
    }}
    
    # Đổi tên thư mục
    Rename-Item -Path "{updater_path}" -NewName "$disabledPath" -Force
    Write-Host "Đã vô hiệu hóa thư mục cursor-updater" -ForegroundColor Green
}}
"""

    script += """
Write-Host "Hoàn tất vô hiệu hóa tự động cập nhật!" -ForegroundColor Green
Write-Host "Nhấn Enter để đóng cửa sổ này..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
"""

    return script
