import os
import sys
import json
import sqlite3
import hashlib
import base64
import requests
import platform
import time
import struct
from colorama import Fore, Style, init
from utils import get_cursor_paths
from config import EMOJI, get_config

# Khởi tạo colorama
init()

def get_token_from_database():
    """Lấy token từ cơ sở dữ liệu SQLite"""
    try:
        paths = get_cursor_paths()
        sqlite_path = paths.get('sqlite_path', '')

        if not sqlite_path or not os.path.exists(sqlite_path):
            print(f"{Fore.RED}{EMOJI['ERROR']} Không tìm thấy file SQLite.{Style.RESET_ALL}")
            return None

        # Kết nối đến cơ sở dữ liệu
        conn = sqlite3.connect(sqlite_path)
        cursor = conn.cursor()

        # Truy vấn token
        cursor.execute("SELECT value FROM ItemTable WHERE key = 'cursor.token'")
        result = cursor.fetchone()

        # Đóng kết nối
        conn.close()

        if result:
            token = json.loads(result[0])
            return token
        else:
            print(f"{Fore.YELLOW}{EMOJI['WARNING']} Không tìm thấy token trong cơ sở dữ liệu.{Style.RESET_ALL}")
            return None
    except Exception as e:
        print(f"{Fore.RED}{EMOJI['ERROR']} Lỗi khi lấy token từ cơ sở dữ liệu: {str(e)}{Style.RESET_ALL}")
        return None

def generate_hashed64_hex(input_str, salt=''):
    """Tạo hash SHA-256 của input + salt và trả về dạng hex"""
    hash_obj = hashlib.sha256()
    hash_obj.update((input_str + salt).encode('utf-8'))
    return hash_obj.hexdigest()

def obfuscate_bytes(byte_array):
    """Làm rối byte sử dụng thuật toán từ utils.js"""
    t = 165
    for r in range(len(byte_array)):
        byte_array[r] = ((byte_array[r] ^ t) + (r % 256)) & 0xFF
        t = byte_array[r]
    return byte_array

def generate_cursor_checksum(token):
    """Tạo checksum cho Cursor API sử dụng thuật toán chính xác"""
    try:
        # Làm sạch token
        clean_token = token.strip()

        # Tạo machineId và macMachineId
        machine_id = generate_hashed64_hex(clean_token, 'machineId')
        mac_machine_id = generate_hashed64_hex(clean_token, 'macMachineId')

        # Lấy timestamp và chuyển thành mảng byte
        timestamp = int(time.time() * 1000) // 1000000
        byte_array = bytearray(struct.pack('>Q', timestamp)[-6:])  # Lấy 6 byte cuối

        # Làm rối byte và mã hóa base64
        obfuscated_bytes = obfuscate_bytes(byte_array)
        encoded_checksum = base64.b64encode(obfuscated_bytes).decode('utf-8')

        # Kết hợp checksum cuối cùng
        return f"{encoded_checksum}{machine_id}/{mac_machine_id}"
    except Exception as e:
        print(f"{Fore.RED}{EMOJI['ERROR']} Lỗi khi tạo checksum: {str(e)}{Style.RESET_ALL}")
        return ""

def refresh_token(token):
    """Làm mới token sử dụng API của máy chủ Trung Quốc"""
    try:
        # Đảm bảo token được mã hóa URL đúng cách
        if '%3A%3A' not in token and '::' in token:
            # Thay thế :: bằng phiên bản mã hóa URL nếu cần
            token = token.replace('::', '%3A%3A')

        # Gửi yêu cầu đến máy chủ làm mới
        url = f"https://token.cursorpro.com.cn/reftoken?token={token}"

        print(f"{Fore.CYAN}{EMOJI['INFO']} Đang làm mới token...{Style.RESET_ALL}")

        response = requests.get(url, timeout=30)

        if response.status_code == 200:
            try:
                data = response.json()
                if 'token' in data and data['token']:
                    print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Đã làm mới token thành công!{Style.RESET_ALL}")
                    return data['token']
            except:
                pass
    except:
        pass

    # Trả về token gốc nếu làm mới thất bại
    return token.split('%3A%3A')[-1] if '%3A%3A' in token else token.split('::')[-1] if '::' in token else token

def check_user_authorized(token=None):
    """Kiểm tra xem người dùng có được ủy quyền với token đã cho không"""
    try:
        print(f"{Fore.CYAN}{EMOJI['INFO']} Đang kiểm tra ủy quyền...{Style.RESET_ALL}")

        # Nếu không có token, lấy từ cơ sở dữ liệu
        if not token:
            token = get_token_from_database()
            if not token:
                return False

        # Thử làm mới token trước
        token = refresh_token(token)

        # Làm sạch token
        if token and '%3A%3A' in token:
            token = token.split('%3A%3A')[1]
        elif token and '::' in token:
            token = token.split('::')[1]

        # Xóa khoảng trắng
        token = token.strip()

        if not token or len(token) < 10:
            print(f"{Fore.RED}{EMOJI['ERROR']} Token không hợp lệ{Style.RESET_ALL}")
            return False

        print(f"{Fore.CYAN}{EMOJI['INFO']} Độ dài token: {len(token)} ký tự{Style.RESET_ALL}")

        # Thử lấy thông tin sử dụng bằng DashboardService API
        try:
            # Tạo checksum
            checksum = generate_cursor_checksum(token)

            # Tạo header cho request
            headers = {
                'accept-encoding': 'gzip',
                'authorization': f'Bearer {token}',
                'connect-protocol-version': '1',
                'content-type': 'application/proto',
                'user-agent': 'connect-es/1.6.1',
                'x-cursor-checksum': checksum,
                'x-cursor-client-version': '0.48.7',
                'x-cursor-timezone': 'Asia/Ho_Chi_Minh',
                'x-ghost-mode': 'false',
                'Host': 'api2.cursor.sh'
            }

            # Gửi request
            response = requests.get('https://api2.cursor.sh/api/v1/dashboard/usage', headers=headers)

            # Kiểm tra kết quả
            if response.status_code == 200:
                print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Người dùng đã được ủy quyền!{Style.RESET_ALL}")

                # Hiển thị thông tin tài khoản
                try:
                    data = response.json()
                    if 'user' in data:
                        user = data['user']
                        print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
                        print(f"{Fore.CYAN}{EMOJI['USER']} Thông tin tài khoản:{Style.RESET_ALL}")
                        print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
                        print(f"{Fore.GREEN}Email:{Style.RESET_ALL} {Fore.CYAN}{user.get('email', 'N/A')}{Style.RESET_ALL}")
                        print(f"{Fore.GREEN}Tên:{Style.RESET_ALL} {Fore.CYAN}{user.get('name', 'N/A')}{Style.RESET_ALL}")
                        print(f"{Fore.GREEN}ID:{Style.RESET_ALL} {Fore.CYAN}{user.get('id', 'N/A')}{Style.RESET_ALL}")

                        # Hiển thị thông tin gói
                        if 'subscription' in data:
                            subscription = data['subscription']
                            print(f"{Fore.GREEN}Gói:{Style.RESET_ALL} {Fore.CYAN}{subscription.get('plan', 'Free')}{Style.RESET_ALL}")
                            print(f"{Fore.GREEN}Trạng thái:{Style.RESET_ALL} {Fore.CYAN}{subscription.get('status', 'N/A')}{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.YELLOW}{EMOJI['WARNING']} Lỗi khi xử lý dữ liệu phản hồi: {str(e)}{Style.RESET_ALL}")

                return True
            elif response.status_code == 401 or response.status_code == 403:
                print(f"{Fore.RED}{EMOJI['ERROR']} Người dùng không được ủy quyền. Mã lỗi: {response.status_code}{Style.RESET_ALL}")
                return False
            else:
                print(f"{Fore.YELLOW}{EMOJI['WARNING']} Mã trạng thái không mong đợi: {response.status_code}{Style.RESET_ALL}")

                # Nếu token có dạng JWT hợp lệ, coi như hợp lệ
                if token.startswith('eyJ') and '.' in token and len(token) > 100:
                    print(f"{Fore.YELLOW}{EMOJI['WARNING']} Token có vẻ đúng định dạng JWT, nhưng API trả về mã trạng thái không mong đợi. Token có thể hợp lệ nhưng truy cập API bị hạn chế.{Style.RESET_ALL}")
                    return True

                return False

        except Exception as e:
            print(f"{Fore.YELLOW}{EMOJI['WARNING']} Lỗi khi kiểm tra sử dụng: {str(e)}{Style.RESET_ALL}")

            # Nếu token có dạng JWT hợp lệ, coi như hợp lệ ngay cả khi kiểm tra API thất bại
            if token.startswith('eyJ') and '.' in token and len(token) > 100:
                print(f"{Fore.YELLOW}{EMOJI['WARNING']} Token có vẻ đúng định dạng JWT, nhưng kiểm tra API thất bại. Token có thể hợp lệ nhưng truy cập API bị hạn chế.{Style.RESET_ALL}")
                return True

            return False

    except Exception as e:
        print(f"{Fore.RED}{EMOJI['ERROR']} Lỗi khi kiểm tra ủy quyền: {str(e)}{Style.RESET_ALL}")
        return False

def run():
    """Hàm chạy chính"""
    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{EMOJI['KEY']} Kiểm tra ủy quyền người dùng{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")

    # Tự động lấy token từ cơ sở dữ liệu
    print(f"{Fore.CYAN}{EMOJI['INFO']} Đang lấy token từ cơ sở dữ liệu...{Style.RESET_ALL}")
    token = get_token_from_database()

    # Nếu không tìm thấy token trong cơ sở dữ liệu, yêu cầu nhập thủ công
    if not token:
        token = input(f"{Fore.CYAN}{EMOJI['KEY']} Không tìm thấy token trong cơ sở dữ liệu. Vui lòng nhập token của bạn: {Style.RESET_ALL}").strip()

    # Kiểm tra ủy quyền
    check_user_authorized(token)

    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")

if __name__ == "__main__":
    run()
