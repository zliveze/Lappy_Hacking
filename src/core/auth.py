# src/core/auth.py - Lấy thông tin xác thực và tài khoản Cursor
import os
import json
import requests
import sqlite3
import re
from .utils import get_cursor_paths, check_file_exists

BASE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

def _get_token_from_storage(storage_path):
    """Lấy token từ storage.json"""
    if not check_file_exists(storage_path):
        return None
    try:
        with open(storage_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if 'cursorAuth/accessToken' in data:
                return data['cursorAuth/accessToken']
            for key, value in data.items():
                if 'token' in key.lower() and isinstance(value, str) and len(value) > 50:
                    return value
    except Exception:
        return None
    return None

def _get_token_from_sqlite(sqlite_path):
    """Lấy token từ state.vscdb"""
    if not check_file_exists(sqlite_path):
        return None
    try:
        conn = sqlite3.connect(sqlite_path)
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM ItemTable WHERE key LIKE '%token%'")
        rows = cursor.fetchall()
        conn.close()
        for row in rows:
            value = row[0]
            if isinstance(value, str) and len(value) > 50:
                # Check if it's a simple token string
                if not value.startswith('{'):
                    return value
                # Try to parse JSON if it's a stringified object
                try:
                    data = json.loads(value)
                    if isinstance(data, dict) and 'token' in data:
                        return data['token']
                except:
                    continue
    except Exception:
        return None
    return None

def _get_token_from_session(session_path):
    """Lấy token từ Session Storage"""
    if not session_path or not os.path.exists(session_path):
        return None
    try:
        for filename in os.listdir(session_path):
            if filename.endswith('.log'):
                filepath = os.path.join(session_path, filename)
                with open(filepath, 'rb') as f:
                    content = f.read().decode('utf-8', errors='ignore')
                    # Tìm token bằng regex, ưu tiên token dài
                    tokens = re.findall(r'"token":"([^"]+)"', content)
                    if tokens:
                        # Trả về token dài nhất tìm thấy
                        return max(tokens, key=len)
    except Exception:
        return None
    return None

def get_auth_token():
    """
    Lấy token xác thực từ nhiều nguồn khác nhau.
    Thứ tự ưu tiên: storage.json -> state.vscdb -> session storage
    """
    paths = get_cursor_paths()
    if not paths:
        return None

    # 1. Thử từ storage.json
    storage_path = paths.get('storage_path')
    if storage_path:
        token = _get_token_from_storage(storage_path)
        if token:
            return token

    # 2. Thử từ state.vscdb
    sqlite_path = paths.get('sqlite_path')
    if sqlite_path:
        token = _get_token_from_sqlite(sqlite_path)
        if token:
            return token

    # 3. Thử từ Session Storage
    session_path = paths.get('session_storage_path')
    if session_path:
        token = _get_token_from_session(session_path)
        if token:
            return token

    return None

def get_email():
    """Lấy email người dùng từ storage hoặc sqlite"""
    paths = get_cursor_paths()
    if not paths:
        return None

    # Thử từ storage.json
    storage_path = paths.get('storage_path')
    if storage_path and check_file_exists(storage_path):
        try:
            with open(storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'cursorAuth/cachedEmail' in data:
                    return data['cursorAuth/cachedEmail']
                for key, value in data.items():
                    if 'email' in key.lower() and isinstance(value, str) and '@' in value:
                        return value
        except:
            pass

    # Thử từ state.vscdb
    sqlite_path = paths.get('sqlite_path')
    if sqlite_path and check_file_exists(sqlite_path):
        try:
            conn = sqlite3.connect(sqlite_path)
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM ItemTable WHERE key LIKE '%email%' OR key LIKE '%cursorAuth%'")
            rows = cursor.fetchall()
            conn.close()
            for row in rows:
                value = row[0]
                if isinstance(value, str) and '@' in value:
                    return value
        except:
            pass
    
    return None


def get_api_usage(token):
    """Lấy thông tin sử dụng từ API - SAO CHÉP 1:1 TỪ BẢN GỐC"""
    if not token:
        return None
    url = "https://www.cursor.com/api/usage"
    headers = BASE_HEADERS.copy()
    headers.update({"Cookie": f"WorkosCursorSessionToken=user_01OOOOOOOOOOOOOOOOOOOOOOOO%3A%3A{token}"})
    try:
        proxies = get_proxy()
        response = requests.get(url, headers=headers, timeout=10, proxies=proxies)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Get usage info failed: {str(e)}")
        return None

def get_proxy():
    """get proxy - SAO CHÉP TỪ BẢN GỐC"""
    proxy = os.environ.get("HTTP_PROXY") or os.environ.get("HTTPS_PROXY")
    if proxy:
        return {"http": proxy, "https": proxy}
    return None

def get_stripe_profile(token):
    """Lấy thông tin gói cước từ API - SAO CHÉP 1:1 TỪ BẢN GỐC"""
    if not token:
        return None
    url = "https://api2.cursor.sh/auth/full_stripe_profile"
    headers = BASE_HEADERS.copy()
    headers.update({"Authorization": f"Bearer {token}"})
    try:
        proxies = get_proxy()
        response = requests.get(url, headers=headers, timeout=10, proxies=proxies)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Get subscription info failed: {str(e)}")
        return None
