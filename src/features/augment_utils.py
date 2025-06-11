# features/augment_utils.py - Utilities cho Augment Code VIP
import os
import platform
import json
import base64
from pathlib import Path
import uuid
import hashlib

def get_config_dirs():
    """Lấy các thư mục config dựa trên hệ điều hành"""
    system = platform.system().lower()
    
    if system == "windows":
        config_dirs = [
            Path(os.environ.get("APPDATA", "")),
            Path(os.environ.get("LOCALAPPDATA", "")),
            Path.home()
        ]
    elif system == "darwin":  # macOS
        config_dirs = [
            Path.home() / "Library" / "Application Support",
            Path.home() / "Library" / "Preferences",
            Path.home()
        ]
    else:  # Linux
        config_dirs = [
            Path.home() / ".config",
            Path.home() / ".local" / "share",
            Path.home()
        ]
    
    return [d for d in config_dirs if d.exists()]

def check_jetbrains_installation():
    """Kiểm tra xem có JetBrains IDEs được cài đặt không"""
    try:
        config_dirs = get_config_dirs()

        for config_dir in config_dirs:
            jetbrains_dir = config_dir / "JetBrains"
            if jetbrains_dir.exists():
                # Kiểm tra xem thư mục có chứa IDE thực sự không
                try:
                    contents = list(jetbrains_dir.iterdir())
                    if not contents:
                        continue  # Thư mục rỗng, không có IDE

                    # Tìm các thư mục IDE thực tế
                    ide_patterns = [
                        "intellijidea", "pycharm", "webstorm", "phpstorm",
                        "rubymine", "clion", "datagrip", "rider", "goland",
                        "androidstudio", "idea"
                    ]

                    for item in contents:
                        if item.is_dir():
                            item_name_lower = item.name.lower()
                            for pattern in ide_patterns:
                                if pattern in item_name_lower:
                                    # Kiểm tra thêm xem thư mục IDE có files thực tế
                                    try:
                                        ide_contents = list(item.iterdir())
                                        if ide_contents:  # Có files trong thư mục IDE
                                            return True
                                    except:
                                        continue

                except PermissionError:
                    continue
                except Exception:
                    continue

        return False
    except Exception:
        return False

def check_vscode_installation(specific_ide=None):
    """Kiểm tra xem có VSCode/Augment được cài đặt không

    Args:
        specific_ide: IDE cụ thể cần kiểm tra (cursor, windsurf, vscode, etc.)
    """
    try:
        config_dirs = get_config_dirs()

        # Các tên thư mục có thể có cho VSCode variants
        all_vscode_variants = {
            "cursor": ["Cursor"],
            "windsurf": ["Windsurf", ".windsurf"],
            "vscode": ["Code", "Code - Insiders"],
            "vscodium": ["VSCodium"]
        }

        # Chọn variants dựa trên specific_ide
        if specific_ide:
            ide_key = specific_ide.lower()
            if ide_key in all_vscode_variants:
                vscode_variants = all_vscode_variants[ide_key]
            else:
                return False
        else:
            # Lấy tất cả variants
            vscode_variants = []
            for variants in all_vscode_variants.values():
                vscode_variants.extend(variants)

        for config_dir in config_dirs:
            for variant in vscode_variants:
                vscode_dir = config_dir / variant
                if vscode_dir.exists():
                    # Kiểm tra xem có phải thư mục IDE thực sự không
                    try:
                        contents = list(vscode_dir.iterdir())
                        if not contents:
                            continue  # Thư mục rỗng

                        # Kiểm tra có User directory hoặc các files config
                        has_user_dir = (vscode_dir / "User").exists()
                        has_config_files = any(
                            item.name.lower() in ["user", "logs", "extensions", "crashdumps"]
                            for item in contents if item.is_dir()
                        )

                        if has_user_dir or has_config_files:
                            return True

                    except PermissionError:
                        # Nếu không có quyền đọc, coi như có IDE
                        return True
                    except Exception:
                        continue

        return False
    except Exception:
        return False

def get_installed_ides():
    """Lấy danh sách các IDE đã cài đặt"""
    installed = {}

    ide_types = {
        "cursor": "Cursor",
        "windsurf": "Windsurf",
        "vscode": "Visual Studio Code",
        "vscodium": "VSCodium"
    }

    for ide_key, ide_name in ide_types.items():
        installed[ide_key] = {
            "name": ide_name,
            "installed": check_vscode_installation(ide_key)
        }

    # Kiểm tra JetBrains
    installed["jetbrains"] = {
        "name": "JetBrains IDEs",
        "installed": check_jetbrains_installation()
    }

    return installed

def get_jetbrains_config_dir():
    """Lấy thư mục config JetBrains"""
    config_dirs = get_config_dirs()
    
    for config_dir in config_dirs:
        jetbrains_dir = config_dir / "JetBrains"
        if jetbrains_dir.exists():
            return jetbrains_dir
            
    return None

def get_vscode_files(machine_id="machineId", specific_ide=None):
    """Lấy danh sách các file/thư mục VSCode cần xử lý

    Args:
        machine_id: Tên file machine ID
        specific_ide: IDE cụ thể cần xử lý (None = tất cả)
    """
    config_dirs = get_config_dirs()
    vscode_files = []

    # Các tên thư mục có thể có cho VSCode variants
    all_vscode_variants = {
        "cursor": ["Cursor"],
        "windsurf": ["Windsurf", ".windsurf"],
        "vscode": ["Code", "Code - Insiders"],
        "vscodium": ["VSCodium"]
    }

    # Chọn variants dựa trên specific_ide
    if specific_ide:
        ide_key = specific_ide.lower()
        if ide_key in all_vscode_variants:
            vscode_variants = all_vscode_variants[ide_key]
        else:
            # Nếu không tìm thấy, tìm trong tất cả variants
            vscode_variants = []
            for variants in all_vscode_variants.values():
                if specific_ide in variants:
                    vscode_variants = variants
                    break
            if not vscode_variants:
                return []
    else:
        # Lấy tất cả variants
        vscode_variants = []
        for variants in all_vscode_variants.values():
            vscode_variants.extend(variants)
    
    # Các pattern để tìm global storage và workspace storage
    global_patterns = [
        ["User", "globalStorage"],
        ["data", "User", "globalStorage"],
        [machine_id],
        ["data", machine_id]
    ]
    
    workspace_patterns = [
        ["User", "workspaceStorage"],
        ["data", "User", "workspaceStorage"]
    ]
    
    for config_dir in config_dirs:
        for variant in vscode_variants:
            variant_dir = config_dir / variant
            if not variant_dir.exists():
                continue
                
            # Tìm global storage
            for pattern in global_patterns:
                path = variant_dir
                for segment in pattern:
                    path = path / segment
                if path.exists():
                    vscode_files.append(path)
            
            # Tìm workspace storage
            for pattern in workspace_patterns:
                workspace_base = variant_dir
                for segment in pattern:
                    workspace_base = workspace_base / segment
                    
                if workspace_base.exists():
                    try:
                        for workspace_dir in workspace_base.iterdir():
                            if workspace_dir.is_dir():
                                vscode_files.append(workspace_dir)
                    except PermissionError:
                        continue
    
    return vscode_files

def generate_new_uuid():
    """Tạo UUID mới"""
    return str(uuid.uuid4())

def generate_sha256_hash():
    """Tạo SHA256 hash từ UUID mới"""
    new_uuid = uuid.uuid4()
    return hashlib.sha256(new_uuid.bytes).hexdigest()

def decode_base64_key(encoded_key):
    """Decode base64 key"""
    try:
        return base64.b64decode(encoded_key).decode('utf-8')
    except Exception:
        return None

def lock_file(file_path):
    """Khóa file để ngăn ghi đè"""
    try:
        file_path = Path(file_path)
        if not file_path.exists():
            return False, f"File không tồn tại: {file_path}"

        # Đặt file thành read-only
        if platform.system().lower() == "windows":
            import subprocess
            subprocess.run(['attrib', '+R', str(file_path)], check=False, capture_output=True)
        else:
            os.chmod(file_path, 0o444)

        return True, f"Đã khóa file: {file_path}"
    except Exception as e:
        return False, f"Lỗi khóa file: {str(e)}"

def unlock_file(file_path):
    """Mở khóa file"""
    try:
        file_path = Path(file_path)
        if not file_path.exists():
            return False, f"File không tồn tại: {file_path}"

        # Đặt file thành writable
        if platform.system().lower() == "windows":
            import subprocess
            subprocess.run(['attrib', '-R', str(file_path)], check=False, capture_output=True)
        else:
            os.chmod(file_path, 0o644)

        return True, f"Đã mở khóa file: {file_path}"
    except Exception as e:
        return False, f"Lỗi mở khóa file: {str(e)}"

def get_jetbrains_id_files():
    """Lấy danh sách các file ID của JetBrains"""
    # Base64 encoded file names từ Augment VIP
    encoded_files = [
        "UGVybWFuZW50RGV2aWNlSWQ=",  # PermanentDeviceId
        "UGVybWFuZW50VXNlcklk"       # PermanentUserId
    ]
    
    id_files = []
    for encoded in encoded_files:
        decoded = decode_base64_key(encoded)
        if decoded:
            id_files.append(decoded)
    
    return id_files

def get_vscode_keys():
    """Lấy danh sách các key VSCode cần update"""
    # Base64 encoded keys từ Augment VIP
    encoded_keys = [
        "dGVsZW1ldHJ5Lm1hY2hpbmVJZA==",      # telemetry.machineId
        "dGVsZW1ldHJ5LmRldkRldmljZUlk",       # telemetry.devDeviceId
        "dGVsZW1ldHJ5Lm1hY01hY2hpbmVJZA==",   # telemetry.macMachineId
        "c3RvcmFnZS5zZXJ2aWNlTWFjaGluZUlk"    # storage.serviceMachineId
    ]
    
    keys = []
    for encoded in encoded_keys:
        decoded = decode_base64_key(encoded)
        if decoded:
            keys.append((encoded, decoded))
    
    return keys

def format_file_size(size_bytes):
    """Format file size thành human readable"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def get_file_info(file_path):
    """Lấy thông tin chi tiết về file"""
    try:
        file_path = Path(file_path)
        if not file_path.exists():
            return None
            
        stat = file_path.stat()
        return {
            "path": str(file_path),
            "size": stat.st_size,
            "size_formatted": format_file_size(stat.st_size),
            "permissions": oct(stat.st_mode)[-3:],
            "is_readonly": not os.access(file_path, os.W_OK)
        }
    except Exception:
        return None
