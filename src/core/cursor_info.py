# core/cursor_info.py - Lấy thông tin tài khoản và sử dụng Cursor
import json
import sqlite3
import requests
from .utils import get_cursor_paths, read_json_file, check_file_exists

class CursorAccountInfo:
    def __init__(self):
        self.cursor_paths = get_cursor_paths()
        self.token = None
        self.account_info = None
        self.usage_info = None
    
    def get_token_from_storage(self):
        """Lấy token từ storage.json"""
        try:
            storage_path = self.cursor_paths.get('storage_path')
            if not storage_path or not check_file_exists(storage_path):
                return None
            
            data = read_json_file(storage_path)
            if not data:
                return None
            
            # Tìm token trong các key có thể
            possible_keys = [
                'cursorAuth/accessToken',
                'accessToken',
                'token',
                'authToken',
                'cursor_token'
            ]
            
            for key in possible_keys:
                if key in data and data[key]:
                    return data[key]
            
            # Tìm trong các key chứa 'token'
            for key, value in data.items():
                if 'token' in key.lower() and isinstance(value, str) and len(value) > 20:
                    return value
            
            return None
        except Exception as e:
            print(f"Lỗi lấy token từ storage: {str(e)}")
            return None
    
    def get_token_from_sqlite(self):
        """Lấy token từ SQLite database (giống bản gốc)"""
        try:
            sqlite_path = self.cursor_paths.get('sqlite_path')
            if not sqlite_path or not check_file_exists(sqlite_path):
                return None

            conn = sqlite3.connect(sqlite_path)
            cursor = conn.cursor()

            # Query theo cách của bản gốc
            cursor.execute("SELECT value FROM ItemTable WHERE key LIKE '%token%'")
            rows = cursor.fetchall()
            conn.close()

            for row in rows:
                try:
                    value = row[0]
                    if isinstance(value, str) and len(value) > 20:
                        return value
                    # Thử parse JSON
                    data = json.loads(value)
                    if isinstance(data, dict) and 'token' in data:
                        return data['token']
                except:
                    continue

            return None
        except Exception as e:
            print(f"Lỗi lấy token từ SQLite: {str(e)}")
            return None
    
    def get_token(self):
        """Lấy token từ các nguồn"""
        if self.token:
            return self.token
        
        # Thử lấy từ storage trước
        token = self.get_token_from_storage()
        if token:
            self.token = token
            return token
        
        # Thử lấy từ SQLite
        token = self.get_token_from_sqlite()
        if token:
            self.token = token
            return token
        
        return None
    
    def get_account_info_from_api(self):
        """Lấy thông tin tài khoản từ API"""
        try:
            token = self.get_token()
            if not token:
                return None
            
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json',
                'User-Agent': 'Cursor/1.0'
            }
            
            # Thử các endpoint có thể
            endpoints = [
                'https://api2.cursor.sh/auth/profile',
                'https://www.cursor.com/api/auth/profile',
                'https://api.cursor.com/user/profile'
            ]
            
            for endpoint in endpoints:
                try:
                    response = requests.get(endpoint, headers=headers, timeout=10)
                    if response.status_code == 200:
                        return response.json()
                except:
                    continue
            
            return None
        except Exception as e:
            print(f"Lỗi lấy thông tin tài khoản từ API: {str(e)}")
            return None
    
    def get_usage_info_from_api(self):
        """Lấy thông tin sử dụng từ API"""
        try:
            token = self.get_token()
            if not token:
                return None
            
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json',
                'User-Agent': 'Cursor/1.0'
            }
            
            # Thử các endpoint có thể
            endpoints = [
                'https://www.cursor.com/api/usage',
                'https://api2.cursor.sh/usage',
                'https://api.cursor.com/usage'
            ]
            
            for endpoint in endpoints:
                try:
                    response = requests.get(endpoint, headers=headers, timeout=10)
                    if response.status_code == 200:
                        return response.json()
                except:
                    continue
            
            return None
        except Exception as e:
            print(f"Lỗi lấy thông tin sử dụng từ API: {str(e)}")
            return None
    
    def parse_account_info(self, raw_data):
        """Parse thông tin tài khoản"""
        try:
            if not raw_data:
                return None
            
            account_info = {
                'email': 'Không tìm thấy',
                'type': 'Free',
                'days': 0,
                'subscription_status': 'inactive'
            }
            
            # Lấy email
            if 'email' in raw_data:
                account_info['email'] = raw_data['email']
            elif 'user' in raw_data and 'email' in raw_data['user']:
                account_info['email'] = raw_data['user']['email']
            
            # Lấy loại tài khoản
            if 'subscription' in raw_data:
                sub = raw_data['subscription']
                if 'plan' in sub:
                    plan_name = sub['plan'].get('name', 'Free')
                    account_info['type'] = plan_name
                
                if 'status' in sub:
                    account_info['subscription_status'] = sub['status']
            
            # Lấy số ngày còn lại
            if 'daysRemainingOnTrial' in raw_data:
                account_info['days'] = raw_data['daysRemainingOnTrial']
            elif 'trial' in raw_data and 'daysRemaining' in raw_data['trial']:
                account_info['days'] = raw_data['trial']['daysRemaining']
            
            return account_info
        except Exception as e:
            print(f"Lỗi parse thông tin tài khoản: {str(e)}")
            return None
    
    def parse_usage_info(self, raw_data):
        """Parse thông tin sử dụng"""
        try:
            if not raw_data:
                return None
            
            usage_info = {
                'fast_used': 0,
                'fast_limit': 'Không giới hạn',
                'slow_used': 0,
                'slow_limit': 'Không giới hạn'
            }
            
            # Parse GPT-4 (Fast Response)
            if 'gpt-4' in raw_data:
                gpt4_data = raw_data['gpt-4']
                usage_info['fast_used'] = gpt4_data.get('numRequestsTotal', 0)
                usage_info['fast_limit'] = gpt4_data.get('maxRequestUsage', 'Không giới hạn')
            
            # Parse GPT-3.5 (Slow Response)
            if 'gpt-3.5-turbo' in raw_data:
                gpt35_data = raw_data['gpt-3.5-turbo']
                usage_info['slow_used'] = gpt35_data.get('numRequestsTotal', 0)
                usage_info['slow_limit'] = gpt35_data.get('maxRequestUsage', 'Không giới hạn')
            
            return usage_info
        except Exception as e:
            print(f"Lỗi parse thông tin sử dụng: {str(e)}")
            return None
    
    def get_email_from_storage(self):
        """Lấy email từ storage.json (giống bản gốc)"""
        try:
            storage_path = self.cursor_paths.get('storage_path')
            if not storage_path or not check_file_exists(storage_path):
                return None

            data = read_json_file(storage_path)
            if not data:
                return None

            # Tìm email theo thứ tự ưu tiên (giống bản gốc)
            if 'cursorAuth/cachedEmail' in data:
                return data['cursorAuth/cachedEmail']

            # Tìm trong các key khác chứa email
            for key in data:
                if 'email' in key.lower() and isinstance(data[key], str) and '@' in data[key]:
                    return data[key]

            return None
        except Exception as e:
            print(f"Lỗi lấy email từ storage: {str(e)}")
            return None

    def get_email_from_sqlite(self):
        """Lấy email từ SQLite (giống bản gốc)"""
        try:
            sqlite_path = self.cursor_paths.get('sqlite_path')
            if not sqlite_path or not check_file_exists(sqlite_path):
                return None

            conn = sqlite3.connect(sqlite_path)
            cursor = conn.cursor()

            # Query records chứa email hoặc cursorAuth
            cursor.execute("SELECT value FROM ItemTable WHERE key LIKE '%email%' OR key LIKE '%cursorAuth%'")
            rows = cursor.fetchall()
            conn.close()

            for row in rows:
                try:
                    value = row[0]
                    # Nếu là string và chứa @, có thể là email
                    if isinstance(value, str) and '@' in value:
                        return value

                    # Thử parse JSON
                    try:
                        data = json.loads(value)
                        if isinstance(data, dict):
                            # Kiểm tra field email
                            if 'email' in data:
                                return data['email']
                            # Kiểm tra field cachedEmail
                            if 'cachedEmail' in data:
                                return data['cachedEmail']
                    except:
                        pass
                except:
                    continue

            return None
        except Exception as e:
            print(f"Lỗi lấy email từ SQLite: {str(e)}")
            return None

    def get_account_info_from_local(self):
        """Lấy thông tin tài khoản từ local storage (cải thiện)"""
        try:
            account_info = {
                'email': 'Không tìm thấy',
                'type': 'Free',
                'days': 0,
                'subscription_status': 'inactive'
            }

            # Lấy email từ storage trước
            email = self.get_email_from_storage()

            # Nếu không có, thử từ SQLite
            if not email:
                email = self.get_email_from_sqlite()

            if email:
                account_info['email'] = email

            # Thử lấy thông tin subscription từ storage
            storage_path = self.cursor_paths.get('storage_path')
            if storage_path and check_file_exists(storage_path):
                data = read_json_file(storage_path)
                if data:
                    # Tìm thông tin subscription
                    sub_keys = ['subscription', 'plan', 'membership', 'cursorAuth/subscription']
                    for key in sub_keys:
                        if key in data and data[key]:
                            sub_data = data[key]
                            if isinstance(sub_data, dict):
                                if 'type' in sub_data:
                                    account_info['type'] = sub_data['type']
                                if 'status' in sub_data:
                                    account_info['subscription_status'] = sub_data['status']
                                if 'plan' in sub_data:
                                    account_info['type'] = sub_data['plan']
                            elif isinstance(sub_data, str):
                                account_info['type'] = sub_data
                            break

                    # Tìm thông tin trial
                    trial_keys = ['trial', 'daysRemaining', 'trialDaysRemaining']
                    for key in trial_keys:
                        if key in data and isinstance(data[key], (int, float)):
                            account_info['days'] = int(data[key])
                            break

            return account_info
        except Exception as e:
            print(f"Lỗi lấy thông tin tài khoản từ local: {str(e)}")
            return None

# Global instance
_cursor_account_info = None

def get_cursor_account_info():
    """Lấy instance của CursorAccountInfo"""
    global _cursor_account_info
    if _cursor_account_info is None:
        _cursor_account_info = CursorAccountInfo()
    return _cursor_account_info

def debug_cursor_data():
    """Debug thông tin Cursor để kiểm tra"""
    try:
        cursor_info = get_cursor_account_info()

        print("=== DEBUG CURSOR DATA ===")

        # Kiểm tra paths
        print(f"Cursor paths: {cursor_info.cursor_paths}")

        # Kiểm tra storage.json
        storage_path = cursor_info.cursor_paths.get('storage_path')
        if storage_path and check_file_exists(storage_path):
            print(f"Storage path exists: {storage_path}")
            data = read_json_file(storage_path)
            if data:
                print(f"Storage keys count: {len(data)}")
                # In ra một số key quan trọng
                important_keys = [key for key in data.keys() if any(keyword in key.lower() for keyword in ['email', 'token', 'auth', 'user', 'subscription'])]
                print(f"Important keys: {important_keys[:10]}")  # Chỉ in 10 key đầu
            else:
                print("Storage data is empty")
        else:
            print(f"Storage path not found: {storage_path}")

        # Kiểm tra SQLite
        sqlite_path = cursor_info.cursor_paths.get('sqlite_path')
        if sqlite_path and check_file_exists(sqlite_path):
            print(f"SQLite path exists: {sqlite_path}")
            try:
                conn = sqlite3.connect(sqlite_path)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                print(f"SQLite tables: {[t[0] for t in tables]}")
                conn.close()
            except Exception as e:
                print(f"SQLite error: {e}")
        else:
            print(f"SQLite path not found: {sqlite_path}")

        print("=== END DEBUG ===")

    except Exception as e:
        print(f"Debug error: {str(e)}")

def get_account_info():
    """Lấy thông tin tài khoản (cải thiện)"""
    try:
        cursor_info = get_cursor_account_info()

        # Debug nếu cần
        # debug_cursor_data()

        # Luôn thử lấy từ local trước (vì API thường không hoạt động)
        local_info = cursor_info.get_account_info_from_local()
        if local_info and local_info.get('email') != 'Không tìm thấy':
            return local_info

        # Thử lấy từ API nếu local không có
        raw_data = cursor_info.get_account_info_from_api()
        if raw_data:
            return cursor_info.parse_account_info(raw_data)

        # Trả về thông tin local dù không đầy đủ
        return local_info
    except Exception as e:
        print(f"Lỗi lấy thông tin tài khoản: {str(e)}")
        return {
            'email': 'Lỗi khi tải',
            'type': 'Free',
            'days': 0,
            'subscription_status': 'error'
        }

def get_usage_info():
    """Lấy thông tin sử dụng (cải thiện)"""
    try:
        cursor_info = get_cursor_account_info()

        # Thử lấy từ API
        raw_data = cursor_info.get_usage_info_from_api()
        if raw_data:
            return cursor_info.parse_usage_info(raw_data)

        # Nếu không có API, trả về thông tin mặc định
        return {
            'fast_used': 'N/A',
            'fast_limit': 'N/A',
            'slow_used': 'N/A',
            'slow_limit': 'N/A'
        }
    except Exception as e:
        print(f"Lỗi lấy thông tin sử dụng: {str(e)}")
        return {
            'fast_used': 'Lỗi',
            'fast_limit': 'Lỗi',
            'slow_used': 'Lỗi',
            'slow_limit': 'Lỗi'
        }
