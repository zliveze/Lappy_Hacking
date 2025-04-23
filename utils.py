import os
import sys
import platform
import uuid
import hashlib
import winreg
import ctypes
import datetime

def get_user_documents_path():
    """Lấy đường dẫn thư mục Documents của người dùng"""
    if platform.system() == "Windows":
        return os.path.expanduser("~\\Documents")
    else:
        return os.path.expanduser("~/Documents")

def get_windows_version():
    """Lấy thông tin phiên bản Windows"""
    if platform.system() == "Windows":
        try:
            return platform.win32_ver()[0] + " " + platform.win32_ver()[1]
        except:
            return platform.version()
    else:
        return "Không phải Windows"

def get_computer_name():
    """Lấy tên máy tính"""
    try:
        return platform.node()
    except:
        return "Unknown"

def is_admin():
    """Kiểm tra xem ứng dụng có đang chạy với quyền admin không"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def run_as_admin():
    """Chạy lại ứng dụng với quyền admin"""
    try:
        if sys.executable.endswith("pythonw.exe"):
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, '"' + os.path.abspath(sys.argv[0]) + '"', None, 1
            )
        else:
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, '"' + os.path.abspath(sys.argv[0]) + '"', None, 1
            )
        return True
    except:
        return False

def get_cursor_machine_id_path():
    """Lấy đường dẫn đến file machineId của Cursor"""
    if platform.system() == "Windows":
        return os.path.join(os.getenv("APPDATA"), "Cursor", "machineId")
    else:
        return ""

def get_cursor_paths():
    """Lấy các đường dẫn liên quan đến Cursor"""
    if platform.system() == "Windows":
        appdata = os.getenv("APPDATA")
        localappdata = os.getenv("LOCALAPPDATA", "")
        
        paths = {
            'storage_path': os.path.join(appdata, "Cursor", "User", "globalStorage", "storage.json"),
            'sqlite_path': os.path.join(appdata, "Cursor", "User", "globalStorage", "state.vscdb"),
            'machine_id_path': os.path.join(appdata, "Cursor", "machineId"),
            'cursor_path': os.path.join(localappdata, "Programs", "Cursor", "resources", "app"),
            'updater_path': os.path.join(localappdata, "cursor-updater"),
            'update_yml_path': os.path.join(localappdata, "Programs", "Cursor", "resources", "app-update.yml"),
            'product_json_path': os.path.join(localappdata, "Programs", "Cursor", "resources", "app", "product.json")
        }
        return paths
    else:
        return {}

def generate_new_machine_id():
    """Tạo machine ID mới"""
    # Tạo UUID mới
    dev_device_id = str(uuid.uuid4())

    # Tạo machineId mới (64 ký tự hex)
    machine_id = hashlib.sha256(os.urandom(32)).hexdigest()

    # Tạo macMachineId mới (128 ký tự hex)
    mac_machine_id = hashlib.sha512(os.urandom(64)).hexdigest()

    # Tạo sqmId mới
    sqm_id = "{" + str(uuid.uuid4()).upper() + "}"

    return {
        "telemetry.devDeviceId": dev_device_id,
        "telemetry.macMachineId": mac_machine_id,
        "telemetry.machineId": machine_id,
        "telemetry.sqmId": sqm_id,
        "storage.serviceMachineId": dev_device_id,
    }

def update_windows_machine_guid():
    """Cập nhật Machine GUID trong registry của Windows"""
    if platform.system() != "Windows":
        return False
        
    try:
        # Tạo GUID mới
        new_guid = "{" + str(uuid.uuid4()).upper() + "}"
        
        # Mở registry key
        key_path = r"SOFTWARE\Microsoft\Cryptography"
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE | winreg.KEY_WOW64_64KEY)
        
        # Đặt giá trị MachineGuid
        winreg.SetValueEx(key, "MachineGuid", 0, winreg.REG_SZ, new_guid)
        winreg.CloseKey(key)
        
        return True
    except PermissionError:
        print("Lỗi quyền truy cập. Vui lòng chạy với quyền admin.")
        return False
    except Exception as e:
        print(f"Lỗi khi cập nhật Machine GUID: {str(e)}")
        return False

def update_windows_machine_id():
    """Cập nhật Machine ID trong registry của Windows"""
    if platform.system() != "Windows":
        return False
        
    try:
        # Tạo GUID mới
        new_guid = "{" + str(uuid.uuid4()).upper() + "}"
        
        # Mở registry key
        key_path = r"SOFTWARE\Microsoft\SQMClient"
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE | winreg.KEY_WOW64_64KEY)
        
        # Đặt giá trị MachineId
        winreg.SetValueEx(key, "MachineId", 0, winreg.REG_SZ, new_guid)
        winreg.CloseKey(key)
        
        return True
    except PermissionError:
        print("Lỗi quyền truy cập. Vui lòng chạy với quyền admin.")
        return False
    except Exception as e:
        print(f"Lỗi khi cập nhật Machine ID: {str(e)}")
        return False

def get_release_date():
    """Lấy ngày phát hành"""
    return "23/04/2025"
