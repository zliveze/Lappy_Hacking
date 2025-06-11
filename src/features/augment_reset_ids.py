# features/augment_reset_ids.py - Reset IDs cho JetBrains và VSCode
import os
import json
from pathlib import Path

try:
    from .augment_utils import (
        get_jetbrains_config_dir,
        get_vscode_files,
        get_jetbrains_id_files,
        get_vscode_keys,
        generate_new_uuid,
        generate_sha256_hash,
        lock_file,
        unlock_file,
        get_file_info
    )
except ImportError:
    # Fallback nếu không import được
    def get_jetbrains_config_dir():
        return None
    def get_vscode_files():
        return []
    def get_jetbrains_id_files():
        return []
    def get_vscode_keys():
        return []
    def generate_new_uuid():
        import uuid
        return str(uuid.uuid4())
    def generate_sha256_hash():
        import uuid
        import hashlib
        return hashlib.sha256(uuid.uuid4().bytes).hexdigest()
    def lock_file(path):
        return True, "OK"
    def unlock_file(path):
        return True, "OK"
    def get_file_info(path):
        return None

def reset_jetbrains_ids():
    """Reset JetBrains IDs"""
    try:
        jetbrains_dir = get_jetbrains_config_dir()
        if not jetbrains_dir:
            return False, "Không tìm thấy thư mục JetBrains config"
        
        id_files = get_jetbrains_id_files()
        results = []
        success_count = 0
        
        for file_name in id_files:
            file_path = jetbrains_dir / file_name
            
            try:
                # Đọc UUID cũ nếu có
                old_uuid = ""
                if file_path.exists():
                    try:
                        old_uuid = file_path.read_text().strip()
                    except:
                        old_uuid = "Không đọc được"
                
                # Mở khóa file nếu bị khóa
                if file_path.exists():
                    unlock_file(file_path)
                    
                # Tạo UUID mới
                new_uuid = generate_new_uuid()
                
                # Ghi UUID mới
                file_path.write_text(new_uuid)
                
                # Khóa file
                lock_result, lock_msg = lock_file(file_path)
                
                results.append(f"✅ {file_name}:")
                if old_uuid:
                    results.append(f"   Old: {old_uuid}")
                results.append(f"   New: {new_uuid}")
                if lock_result:
                    results.append(f"   🔒 Đã khóa file")
                else:
                    results.append(f"   ⚠️ Không thể khóa file: {lock_msg}")
                results.append("")
                
                success_count += 1
                
            except Exception as e:
                results.append(f"❌ {file_name}: Lỗi - {str(e)}")
                results.append("")
        
        if success_count > 0:
            message = f"Đã reset {success_count}/{len(id_files)} JetBrains ID files:\n\n" + "\n".join(results)
            return True, message
        else:
            return False, "Không thể reset bất kỳ JetBrains ID file nào:\n\n" + "\n".join(results)
            
    except Exception as e:
        return False, f"Lỗi reset JetBrains IDs: {str(e)}"

def reset_vscode_ids(specific_ide=None):
    """Reset VSCode IDs

    Args:
        specific_ide: IDE cụ thể cần reset (cursor, windsurf, vscode, etc.)
    """
    try:
        vscode_files = get_vscode_files(specific_ide=specific_ide)
        if not vscode_files:
            ide_name = specific_ide if specific_ide else "VSCode installations"
            return False, f"Không tìm thấy {ide_name}"

        vscode_keys = get_vscode_keys()
        results = []
        success_count = 0

        if specific_ide:
            results.append(f"🎯 Đang reset {specific_ide.upper()} IDs...")
        else:
            results.append("🎯 Đang reset tất cả VSCode variant IDs...")
        results.append("")

        for vscode_path in vscode_files:
            try:
                results.append(f"📁 Đang xử lý: {vscode_path}")
                
                # Xử lý storage.json nếu có
                storage_json = vscode_path / "storage.json"
                if storage_json.exists():
                    success = update_storage_json(storage_json, vscode_keys, results)
                    if success:
                        success_count += 1
                
                # Xử lý machineId file nếu đây là file ID
                if vscode_path.is_file() and vscode_path.name == "machineId":
                    success = update_id_file(vscode_path, results)
                    if success:
                        success_count += 1
                        
                results.append("")
                
            except Exception as e:
                results.append(f"❌ Lỗi xử lý {vscode_path}: {str(e)}")
                results.append("")
        
        if success_count > 0:
            message = f"Đã reset {success_count} VSCode locations:\n\n" + "\n".join(results)
            return True, message
        else:
            return False, "Không thể reset bất kỳ VSCode ID nào:\n\n" + "\n".join(results)
            
    except Exception as e:
        return False, f"Lỗi reset VSCode IDs: {str(e)}"

def update_storage_json(storage_json_path, vscode_keys, results):
    """Update storage.json file"""
    try:
        # Đọc storage.json hiện tại
        try:
            with open(storage_json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except:
            data = {}
        
        results.append(f"   📄 Updating storage.json")
        updated_keys = 0
        
        for encoded_key, decoded_key in vscode_keys:
            try:
                # Hiển thị giá trị cũ
                old_value = data.get(decoded_key, "Không có")
                if old_value != "Không có":
                    results.append(f"   Old {decoded_key}: {old_value}")
                
                # Tạo giá trị mới
                if encoded_key == "dGVsZW1ldHJ5LmRldkRldmljZUlk":  # telemetry.devDeviceId
                    new_value = generate_new_uuid()
                else:
                    new_value = generate_sha256_hash()
                
                # Cập nhật
                data[decoded_key] = new_value
                results.append(f"   New {decoded_key}: {new_value}")
                updated_keys += 1
                
            except Exception as e:
                results.append(f"   ❌ Lỗi update key {decoded_key}: {str(e)}")
        
        # Ghi lại file
        if updated_keys > 0:
            with open(storage_json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            results.append(f"   ✅ Đã cập nhật {updated_keys} keys trong storage.json")
            return True
        else:
            results.append(f"   ⚠️ Không có key nào được cập nhật")
            return False
            
    except Exception as e:
        results.append(f"   ❌ Lỗi update storage.json: {str(e)}")
        return False

def update_id_file(id_file_path, results):
    """Update ID file (như machineId)"""
    try:
        # Đọc giá trị cũ
        old_value = ""
        if id_file_path.exists():
            try:
                old_value = id_file_path.read_text().strip()
            except:
                old_value = "Không đọc được"
        
        # Mở khóa file nếu bị khóa
        if id_file_path.exists():
            unlock_file(id_file_path)
        
        # Tạo giá trị mới
        new_value = generate_new_uuid()
        
        # Ghi giá trị mới
        id_file_path.write_text(new_value)
        
        # Khóa file
        lock_result, lock_msg = lock_file(id_file_path)
        
        results.append(f"   📄 Updating {id_file_path.name}")
        if old_value:
            results.append(f"   Old: {old_value}")
        results.append(f"   New: {new_value}")
        if lock_result:
            results.append(f"   🔒 Đã khóa file")
        else:
            results.append(f"   ⚠️ Không thể khóa file: {lock_msg}")
        
        return True
        
    except Exception as e:
        results.append(f"   ❌ Lỗi update ID file: {str(e)}")
        return False

# Các hàm reset cho từng IDE cụ thể
def reset_cursor_ids():
    """Reset chỉ Cursor IDs"""
    return reset_vscode_ids("cursor")

def reset_windsurf_ids():
    """Reset chỉ Windsurf IDs"""
    return reset_vscode_ids("windsurf")

def reset_visual_studio_code_ids():
    """Reset chỉ Visual Studio Code IDs"""
    return reset_vscode_ids("vscode")

def reset_vscodium_ids():
    """Reset chỉ VSCodium IDs"""
    return reset_vscode_ids("vscodium")

def reset_all_ids():
    """Reset tất cả IDs (JetBrains + VSCode)"""
    try:
        results = []
        overall_success = True

        # Reset JetBrains IDs
        results.append("🔧 RESET JETBRAINS IDS:")
        results.append("=" * 50)
        jetbrains_success, jetbrains_msg = reset_jetbrains_ids()
        results.append(jetbrains_msg)
        results.append("")

        if not jetbrains_success:
            overall_success = False

        # Reset VSCode IDs
        results.append("💻 RESET ALL VSCODE VARIANTS:")
        results.append("=" * 50)
        vscode_success, vscode_msg = reset_vscode_ids()
        results.append(vscode_msg)
        results.append("")

        if not vscode_success:
            overall_success = False

        # Tổng kết
        if overall_success:
            results.append("🎉 HOÀN THÀNH: Đã reset tất cả IDs thành công!")
        else:
            results.append("⚠️ HOÀN THÀNH: Một số IDs không thể reset. Xem chi tiết ở trên.")

        return overall_success, "\n".join(results)

    except Exception as e:
        return False, f"Lỗi reset tất cả IDs: {str(e)}"

def get_available_ides_for_reset():
    """Lấy danh sách các IDE có thể reset"""
    try:
        from .augment_utils import get_installed_ides
        installed_ides = get_installed_ides()

        available = []
        for ide_key, ide_info in installed_ides.items():
            if ide_info["installed"]:
                available.append({
                    "key": ide_key,
                    "name": ide_info["name"],
                    "reset_function": f"reset_{ide_key}_ids"
                })

        return available
    except Exception:
        return []
