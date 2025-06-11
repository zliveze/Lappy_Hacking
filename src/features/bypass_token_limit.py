# features/bypass_token_limit.py - Bỏ qua giới hạn token Cursor
import os
import json
import platform
import re
import tempfile
import shutil
from datetime import datetime
from core.utils import get_cursor_paths, backup_file, check_file_exists, is_cursor_running, kill_cursor_processes

def get_workbench_cursor_path():
    """Lấy đường dẫn workbench.desktop.main.js"""
    try:
        cursor_paths = get_cursor_paths()
        if not cursor_paths:
            return None

        app_path = cursor_paths.get('cursor_path', '')
        if not app_path:
            return None

        # Đường dẫn workbench.desktop.main.js
        system = platform.system()
        if system == "Windows":
            workbench_path = os.path.join(app_path, "out", "vs", "workbench", "workbench.desktop.main.js")
        else:
            workbench_path = os.path.join(app_path, "out/vs/workbench/workbench.desktop.main.js")

        if check_file_exists(workbench_path):
            return workbench_path

        return None

    except Exception as e:
        print(f"Lỗi lấy đường dẫn workbench: {str(e)}")
        return None

def modify_workbench_js_for_token():
    """Chỉnh sửa workbench.desktop.main.js để bỏ qua giới hạn token"""
    try:
        workbench_path = get_workbench_cursor_path()
        if not workbench_path:
            return False, ["ℹ️ Không tìm thấy workbench.desktop.main.js"]

        # Backup file trước
        backup_path = backup_file(workbench_path)
        if not backup_path:
            return False, ["❌ Không thể tạo backup workbench.desktop.main.js"]

        # Đọc nội dung file
        with open(workbench_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Patterns để patch token limit (giống bản gốc)
        patterns = {
            # Pattern chính để bỏ qua token limit
            r'async getEffectiveTokenLimit\(e\)\{const n=e\.modelName;if\(!n\)return 2e5;':
            r'async getEffectiveTokenLimit(e){return 9000000;const n=e.modelName;if(!n)return 9e5;',

            # Pattern backup
            r'getEffectiveTokenLimit\([^)]*\)\s*\{[^}]*return\s+\d+[^}]*\}':
            r'getEffectiveTokenLimit(e){return 9000000;}',

            # Thay đổi Pro Trial thành Pro
            r'<div>Pro Trial': r'<div>Pro',

            # Ẩn notifications
            r'notifications-toasts': r'notifications-toasts hidden',

            # Thay đổi button Upgrade to Pro thành GitHub link
            r'title:"Upgrade to Pro"': r'title:"yeongpin GitHub"',

            # Thay đổi onClick cho button
            r'get onClick\(\)\{return t\.pay\}': r'get onClick(){return function(){window.open("https://github.com/yeongpin/cursor-free-vip","_blank")}}',
        }

        patched = False
        modifications = []

        for pattern, replacement in patterns.items():
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                patched = True
                modifications.append(f"Đã patch: {pattern[:30]}...")

        if patched:
            # Ghi file đã patch
            with open(workbench_path, 'w', encoding='utf-8', errors='ignore') as f:
                f.write(content)

            results = [f"✅ Đã patch workbench.desktop.main.js"]
            results.append(f"   Backup: {backup_path}")
            results.extend([f"   {mod}" for mod in modifications])
            return True, results
        else:
            return False, ["ℹ️ Không tìm thấy pattern token limit để patch"]

    except Exception as e:
        return False, [f"❌ Lỗi patch workbench.desktop.main.js: {str(e)}"]

def modify_product_json_for_token():
    """Chỉnh sửa product.json để bỏ qua giới hạn token"""
    try:
        system = platform.system()
        product_json_paths = []
        
        if system == "Windows":
            localappdata = os.getenv("LOCALAPPDATA")
            product_json_paths = [
                os.path.join(localappdata, "Programs", "Cursor", "resources", "app", "product.json")
            ]
        elif system == "Darwin":  # macOS
            product_json_paths = [
                "/Applications/Cursor.app/Contents/Resources/app/product.json"
            ]
        else:  # Linux
            home = os.path.expanduser("~")
            product_json_paths = [
                os.path.join(home, ".config", "Cursor", "resources", "app", "product.json"),
                os.path.join(home, ".config", "cursor", "resources", "app", "product.json"),
                "/opt/cursor/resources/app/product.json",
                "/usr/share/cursor/resources/app/product.json"
            ]
        
        results = []
        success_count = 0
        
        for product_json_path in product_json_paths:
            if check_file_exists(product_json_path):
                try:
                    # Backup file
                    backup_path = backup_file(product_json_path)
                    
                    # Đọc file hiện tại
                    with open(product_json_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Chỉnh sửa để bỏ qua giới hạn token
                    modifications = []
                    
                    # Tắt kiểm tra giới hạn token
                    if 'enableTokenLimit' in data:
                        data['enableTokenLimit'] = False
                        modifications.append("enableTokenLimit = False")
                    else:
                        data['enableTokenLimit'] = False
                        modifications.append("Thêm enableTokenLimit = False")
                    
                    # Tắt kiểm tra usage
                    if 'enableUsageCheck' in data:
                        data['enableUsageCheck'] = False
                        modifications.append("enableUsageCheck = False")
                    else:
                        data['enableUsageCheck'] = False
                        modifications.append("Thêm enableUsageCheck = False")
                    
                    # Đặt giới hạn token cao
                    if 'maxTokens' in data:
                        data['maxTokens'] = 999999999
                        modifications.append("maxTokens = 999999999")
                    else:
                        data['maxTokens'] = 999999999
                        modifications.append("Thêm maxTokens = 999999999")
                    
                    # Đặt giới hạn request cao
                    if 'maxRequests' in data:
                        data['maxRequests'] = 999999999
                        modifications.append("maxRequests = 999999999")
                    else:
                        data['maxRequests'] = 999999999
                        modifications.append("Thêm maxRequests = 999999999")
                    
                    # Tắt kiểm tra subscription
                    if 'enableSubscriptionCheck' in data:
                        data['enableSubscriptionCheck'] = False
                        modifications.append("enableSubscriptionCheck = False")
                    else:
                        data['enableSubscriptionCheck'] = False
                        modifications.append("Thêm enableSubscriptionCheck = False")
                    
                    # Ghi lại file
                    with open(product_json_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    
                    results.append(f"✅ Đã chỉnh sửa {product_json_path}")
                    results.append(f"   Backup: {backup_path}")
                    results.append(f"   Thay đổi: {', '.join(modifications)}")
                    success_count += 1
                    
                except Exception as e:
                    results.append(f"❌ Lỗi chỉnh sửa {product_json_path}: {str(e)}")
            else:
                results.append(f"ℹ️ File không tồn tại: {product_json_path}")
        
        return success_count > 0, results
        
    except Exception as e:
        return False, [f"❌ Lỗi modify product.json: {str(e)}"]

def modify_settings_json_for_token():
    """Chỉnh sửa settings.json để bỏ qua giới hạn token"""
    try:
        cursor_paths = get_cursor_paths()
        config_path = cursor_paths.get('config_path')
        
        if not config_path:
            return False, ["ℹ️ Không tìm thấy đường dẫn settings.json"]
        
        results = []
        
        # Tạo file settings.json nếu chưa tồn tại
        if not check_file_exists(config_path):
            # Tạo thư mục nếu cần
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            # Tạo settings mặc định
            default_settings = {
                "cursor.general.enableTokenLimit": False,
                "cursor.general.enableUsageCheck": False,
                "cursor.general.enableSubscriptionCheck": False,
                "cursor.general.maxTokens": 999999999,
                "cursor.general.maxRequests": 999999999,
                "cursor.ai.enableRateLimit": False,
                "cursor.ai.maxRequestsPerMinute": 999999999,
                "cursor.ai.maxTokensPerRequest": 999999999
            }
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(default_settings, f, indent=2, ensure_ascii=False)
            
            results.append(f"✅ Đã tạo settings.json mới: {config_path}")
            return True, results
        
        # Backup file hiện tại
        backup_path = backup_file(config_path)
        
        # Đọc settings hiện tại
        with open(config_path, 'r', encoding='utf-8') as f:
            settings = json.load(f)
        
        # Chỉnh sửa settings
        modifications = []
        
        # Tắt các giới hạn token
        token_limit_settings = {
            "cursor.general.enableTokenLimit": False,
            "cursor.general.enableUsageCheck": False,
            "cursor.general.enableSubscriptionCheck": False,
            "cursor.general.maxTokens": 999999999,
            "cursor.general.maxRequests": 999999999,
            "cursor.ai.enableRateLimit": False,
            "cursor.ai.maxRequestsPerMinute": 999999999,
            "cursor.ai.maxTokensPerRequest": 999999999
        }
        
        for key, value in token_limit_settings.items():
            if key in settings:
                if settings[key] != value:
                    settings[key] = value
                    modifications.append(f"{key} = {value}")
            else:
                settings[key] = value
                modifications.append(f"Thêm {key} = {value}")
        
        # Ghi lại settings
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
        
        results.append(f"✅ Đã chỉnh sửa settings.json")
        results.append(f"   Backup: {backup_path}")
        if modifications:
            results.append(f"   Thay đổi: {', '.join(modifications)}")
        else:
            results.append("   Không có thay đổi (đã được cấu hình)")
        
        return True, results
        
    except Exception as e:
        return False, [f"❌ Lỗi modify settings.json: {str(e)}"]

def bypass_token_limit():
    """Bỏ qua giới hạn token Cursor"""
    try:
        # Kiểm tra Cursor có đang chạy không
        if is_cursor_running():
            print("Cursor đang chạy, đang tắt...")
            killed = kill_cursor_processes()
            if killed > 0:
                print(f"Đã tắt {killed} process Cursor")
                import time
                time.sleep(2)
            else:
                return False, "Không thể tắt Cursor. Vui lòng tắt thủ công trước khi bỏ qua giới hạn token"
        
        all_results = []
        total_success = 0
        
        # 1. Chỉnh sửa product.json
        print("Đang chỉnh sửa product.json...")
        success, results = modify_product_json_for_token()
        all_results.extend([f"PRODUCT.JSON: {result}" for result in results])
        if success:
            total_success += 1
        
        # 2. Chỉnh sửa settings.json
        print("Đang chỉnh sửa settings.json...")
        success, results = modify_settings_json_for_token()
        all_results.extend([f"SETTINGS.JSON: {result}" for result in results])
        if success:
            total_success += 1

        # 3. Patch workbench.desktop.main.js (như bản gốc)
        print("Đang patch workbench.desktop.main.js...")
        success, results = modify_workbench_js_for_token()
        all_results.extend([f"WORKBENCH.JS: {result}" for result in results])
        if success:
            total_success += 1

        # Tổng kết
        if total_success > 0:
            result_message = f"Bỏ qua giới hạn token thành công ({total_success} phương pháp):\n" + "\n".join(all_results)
            result_message += "\n\n✅ Cursor sẽ không kiểm tra giới hạn token khi sử dụng."
            result_message += "\n⚠️ Lưu ý: Hiệu quả có thể khác nhau tùy phiên bản Cursor."
            return True, result_message
        else:
            result_message = f"Bỏ qua giới hạn token thất bại:\n" + "\n".join(all_results)
            return False, result_message
            
    except Exception as e:
        return False, f"Lỗi bỏ qua giới hạn token: {str(e)}"
