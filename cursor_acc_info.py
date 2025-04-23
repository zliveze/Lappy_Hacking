import os
import sys
import json
import sqlite3
import requests
import platform
from colorama import Fore, Style, init
from utils import get_cursor_paths
from config import EMOJI, get_config

# Khởi tạo colorama
init()

# Emoji cho thông tin tài khoản
ACCOUNT_EMOJI = {
    "USER": "👤",
    "EMAIL": "📧",
    "PLAN": "🔰",
    "TIME": "⏱️",
    "USAGE": "📊",
    "PREMIUM": "⭐",
    "BASIC": "🔄",
    "WARNING": "⚠️",
    "INFO": "ℹ️",
    "ERROR": "❌",
    "SUCCESS": "✅"
}

# Màu sắc Windows 95/XP (sao chép từ gui.py)
RETRO_COLORS = {
    "win95_bg": "#D4D0C8",           # Xám cơ bản của Win95 (đã cập nhật)
    "win95_btn": "#D4D0C8",          # Nút Win95 (đã cập nhật)
    "win95_btn_shadow": "#808080",   # Bóng nút Win95
    "win95_btn_highlight": "#ffffff", # Viền sáng Win95
    "win95_titlebar": "#000080",     # Thanh tiêu đề xanh đậm Win95
    "win95_titlebar_text": "#ffffff", # Chữ thanh tiêu đề Win95
    "win95_menu": "#D4D0C8",         # Menu Win95 (đã cập nhật)
    "win95_text": "#000000",         # Chữ Win95
    
    "xp_blue": "#245EDC",            # Xanh dương Windows XP
    "xp_green": "#36A546",           # Xanh lá Windows XP
    "xp_gradient_start": "#2A60DF",  # Bắt đầu gradient thanh tiêu đề XP
    "xp_gradient_end": "#0F3BBF",    # Kết thúc gradient thanh tiêu đề XP
    "xp_btn": "#ECE9D8",             # Nút XP
    "xp_btn_hover": "#B6CAE4",       # Nút XP khi hover
    "xp_menu": "#F1F1F1",            # Menu XP
    "xp_text": "#000000",            # Chữ XP
    "xp_text_light": "#FFFFFF",      # Chữ sáng XP
    "xp_window_frame": "#0054E3"     # Viền cửa sổ XP
}

class Config:
    """Cấu hình"""
    NAME_LOWER = "cursor"
    NAME_CAPITALIZE = "Cursor"
    BASE_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

class UsageManager:
    """Quản lý thông tin sử dụng"""

    @staticmethod
    def get_proxy():
        """Lấy proxy"""
        proxy = os.environ.get("HTTP_PROXY") or os.environ.get("HTTPS_PROXY")
        if proxy:
            return {"http": proxy, "https": proxy}
        return None

    @staticmethod
    def get_usage(token):
        """Lấy thông tin sử dụng"""
        url = f"https://www.{Config.NAME_LOWER}.com/api/usage"
        headers = Config.BASE_HEADERS.copy()
        headers.update({"Cookie": f"Workos{Config.NAME_CAPITALIZE}SessionToken=user_01OOOOOOOOOOOOOOOOOOOOOOOO%3A%3A{token}"})
        try:
            proxies = UsageManager.get_proxy()
            response = requests.get(url, headers=headers, timeout=10, proxies=proxies)
            response.raise_for_status()
            data = response.json()

            # Lấy thông tin sử dụng Premium và giới hạn
            gpt4_data = data.get("gpt-4", {})
            premium_usage = gpt4_data.get("numRequestsTotal", 0)
            max_premium_usage = gpt4_data.get("maxRequestUsage", 999)

            # Lấy thông tin sử dụng Basic, nhưng đặt giới hạn là "Không giới hạn"
            gpt35_data = data.get("gpt-3.5-turbo", {})
            basic_usage = gpt35_data.get("numRequestsTotal", 0)

            return {
                'premium_usage': premium_usage,
                'max_premium_usage': max_premium_usage,
                'basic_usage': basic_usage,
                'max_basic_usage': "Không giới hạn"
            }
        except Exception:
            return None

    @staticmethod
    def get_stripe_profile(token):
        """Lấy thông tin đăng ký của người dùng"""
        url = f"https://api2.{Config.NAME_LOWER}.sh/auth/full_stripe_profile"
        headers = Config.BASE_HEADERS.copy()
        headers.update({"Authorization": f"Bearer {token}"})
        try:
            proxies = UsageManager.get_proxy()
            response = requests.get(url, headers=headers, timeout=10, proxies=proxies)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

def get_token_from_session(session_path):
    """Lấy token từ session"""
    if not session_path or not os.path.exists(session_path):
        return None

    try:
        # Thử tìm tất cả các file session có thể
        import re
        for file in os.listdir(session_path):
            if file.endswith('.log'):
                file_path = os.path.join(session_path, file)
                try:
                    with open(file_path, 'rb') as f:
                        content = f.read().decode('utf-8', errors='ignore')
                        # Tìm mẫu token
                        token_match = re.search(r'"token":"([^"]+)"', content)
                        if token_match:
                            return token_match.group(1)
                except:
                    continue
    except Exception as e:
        print(f"Lỗi khi lấy token từ session: {str(e)}")

    return None

def get_token():
    """Lấy token Cursor"""
    paths = get_cursor_paths()
    if not paths:
        return None

    # Thử lấy token từ cơ sở dữ liệu SQLite
    token = get_token_from_sqlite(paths.get('sqlite_path', ''))
    if token:
        return token

    # Thử lấy token từ file storage.json
    token = get_token_from_storage(paths.get('storage_path', ''))
    if token:
        return token

    # Thử lấy token từ session
    session_path = os.path.join(os.path.dirname(paths.get('storage_path', '')), "Session Storage")
    token = get_token_from_session(session_path)
    if token:
        return token

    return None

def get_token_from_storage(storage_path):
    """Lấy token từ file storage.json"""
    if not storage_path or not os.path.exists(storage_path):
        return None

    try:
        with open(storage_path, 'r', encoding='utf-8', errors='ignore') as f:
            data = json.load(f)

            # Thử lấy accessToken
            if 'cursorAuth/accessToken' in data:
                return data['cursorAuth/accessToken']

            # Thử lấy cursor.token
            if 'cursor.token' in data:
                return data['cursor.token']

            # Thử các khóa khác có thể
            for key in data:
                if 'token' in key.lower() and isinstance(data[key], str) and len(data[key]) > 20:
                    return data[key]
    except Exception as e:
        print(f"Lỗi khi lấy token từ storage.json: {str(e)}")

    return None

def get_token_from_sqlite(sqlite_path):
    """Lấy token từ cơ sở dữ liệu SQLite"""
    if not sqlite_path or not os.path.exists(sqlite_path):
        return None

    try:
        conn = sqlite3.connect(sqlite_path)
        cursor = conn.cursor()

        # Thử lấy từ cursorAuth/accessToken
        cursor.execute("SELECT value FROM ItemTable WHERE key = 'cursorAuth/accessToken'")
        result = cursor.fetchone()
        if result:
            try:
                return json.loads(result[0])
            except:
                return result[0] if isinstance(result[0], str) else None

        # Thử lấy từ cursor.token
        cursor.execute("SELECT value FROM ItemTable WHERE key = 'cursor.token'")
        result = cursor.fetchone()
        if result:
            try:
                return json.loads(result[0])
            except:
                return result[0] if isinstance(result[0], str) else None

        # Thử tìm tất cả các key chứa token
        cursor.execute("SELECT key, value FROM ItemTable WHERE key LIKE '%token%'")
        rows = cursor.fetchall()
        conn.close()

        for row in rows:
            try:
                key, value = row
                if isinstance(value, str) and len(value) > 20:
                    return value

                # Thử phân tích JSON
                try:
                    data = json.loads(value)
                    if isinstance(data, dict) and 'token' in data:
                        return data['token']
                except:
                    pass
            except:
                continue
    except Exception as e:
        print(f"Lỗi khi lấy token từ SQLite: {str(e)}")

    return None

def get_email_from_storage(storage_path):
    """Lấy email từ file storage.json"""
    if not storage_path or not os.path.exists(storage_path):
        return None

    try:
        with open(storage_path, 'r', encoding='utf-8', errors='ignore') as f:
            data = json.load(f)

            # Kiểm tra các khóa có thể chứa email
            for key in data:
                if 'email' in key.lower():
                    value = data[key]
                    if isinstance(value, str) and '@' in value:
                        return value
    except Exception:
        pass

    return None

def get_email_from_sqlite(sqlite_path):
    """Lấy email từ cơ sở dữ liệu SQLite"""
    if not sqlite_path or not os.path.exists(sqlite_path):
        return None

    try:
        conn = sqlite3.connect(sqlite_path)
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM ItemTable WHERE key LIKE '%email%' OR key LIKE '%cursorAuth%'")
        rows = cursor.fetchall()
        conn.close()

        for row in rows:
            try:
                value = row[0]
                # Nếu là chuỗi và chứa @, có thể là email
                if isinstance(value, str) and '@' in value:
                    return value

                # Thử phân tích JSON
                try:
                    data = json.loads(value)
                    if isinstance(data, dict):
                        # Kiểm tra xem có trường email không
                        if 'email' in data:
                            return data['email']
                        # Kiểm tra xem có trường cachedEmail không
                        if 'cachedEmail' in data:
                            return data['cachedEmail']
                except:
                    pass
            except:
                continue
    except Exception:
        pass

    return None

def format_subscription_type(subscription_data):
    """Định dạng loại đăng ký"""
    if not subscription_data:
        return "Free"

    # Xử lý định dạng phản hồi API mới
    if "membershipType" in subscription_data:
        membership_type = subscription_data.get("membershipType", "").lower()
        subscription_status = subscription_data.get("subscriptionStatus", "").lower()

        if subscription_status == "active":
            if membership_type == "pro":
                return "Pro"
            elif membership_type == "free_trial":
                return "Free Trial"
            elif membership_type == "pro_trial":
                return "Pro Trial"
            elif membership_type == "team":
                return "Team"
            elif membership_type == "enterprise":
                return "Enterprise"
            elif membership_type:
                return membership_type.capitalize()
            else:
                return "Active Subscription"
        elif subscription_status:
            return f"{membership_type.capitalize()} ({subscription_status})"

    # Tương thích với định dạng phản hồi API cũ
    subscription = subscription_data.get("subscription")
    if subscription:
        plan = subscription.get("plan", {}).get("nickname", "Unknown")
        status = subscription.get("status", "unknown")

        if status == "active":
            if "pro" in plan.lower():
                return "Pro"
            elif "pro_trial" in plan.lower():
                return "Pro Trial"
            elif "free_trial" in plan.lower():
                return "Free Trial"
            elif "team" in plan.lower():
                return "Team"
            elif "enterprise" in plan.lower():
                return "Enterprise"
            else:
                return plan
        else:
            return f"{plan} ({status})"

    return "Free"

def display_account_info_frame(frame):
    """Hiển thị thông tin tài khoản trong frame"""
    import tkinter as tk

    # Xóa tất cả widget con trong frame
    for widget in frame.winfo_children():
        widget.destroy()

    # Lấy token
    token = get_token()
    if not token:
        label = tk.Label(
            frame,
            text="Không tìm thấy token. Vui lòng đăng nhập vào Cursor trước.",
            font=("MS Sans Serif", 8, "bold"),  # Font Win95
            fg="#800000",  # Đỏ đậm Win95
            bg=RETRO_COLORS["win95_bg"],
            padx=10,
            pady=5,
            relief=tk.FLAT
        )
        label.pack(pady=5)
        return

    # Lấy đường dẫn
    paths = get_cursor_paths()
    if not paths:
        label = tk.Label(
            frame,
            text="Không tìm thấy cấu hình.",
            font=("MS Sans Serif", 8, "bold"),  # Font Win95
            fg="#800000",  # Đỏ đậm Win95
            bg=RETRO_COLORS["win95_bg"],
            padx=10,
            pady=5,
            relief=tk.FLAT
        )
        label.pack(pady=5)
        return

    # Lấy thông tin email - thử nhiều nguồn
    email = get_email_from_storage(paths.get('storage_path', ''))

    # Nếu không tìm thấy trong storage, thử từ sqlite
    if not email:
        email = get_email_from_sqlite(paths.get('sqlite_path', ''))

    # Lấy thông tin đăng ký
    try:
        subscription_info = UsageManager.get_stripe_profile(token)
    except Exception:
        subscription_info = None

    # Nếu không tìm thấy trong storage và sqlite, thử từ thông tin đăng ký
    if not email and subscription_info:
        # Thử lấy email từ thông tin đăng ký
        if 'customer' in subscription_info and 'email' in subscription_info['customer']:
            email = subscription_info['customer']['email']

    # Lấy thông tin sử dụng - xử lý lỗi một cách im lặng
    try:
        usage_info = UsageManager.get_usage(token)
    except Exception:
        usage_info = None

    # Container frame cho cả thông tin tài khoản
    container_frame = tk.Frame(
        frame, 
        bg=RETRO_COLORS["win95_bg"],
        relief=tk.FLAT
    )
    container_frame.pack(fill=tk.X, padx=5, pady=5)
    
    # Frame cho thông tin tài khoản bên trái - Win95 style
    info_frame = tk.Frame(
        container_frame, 
        bg=RETRO_COLORS["win95_bg"],
        relief=tk.RIDGE,  # Viền kiểu Win95
        bd=1
    )
    info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

    # Tạo tiêu đề mini giống cửa sổ Win95
    title_frame = tk.Frame(
        info_frame, 
        bg=RETRO_COLORS["win95_titlebar"],
        height=18
    )
    title_frame.pack(fill=tk.X, side=tk.TOP)
    
    title_label = tk.Label(
        title_frame,
        text=" Thông tin tài khoản",
        font=("MS Sans Serif", 8, "bold"),
        bg=RETRO_COLORS["win95_titlebar"],
        fg=RETRO_COLORS["win95_titlebar_text"],
        anchor="w"
    )
    title_label.pack(side=tk.LEFT, fill=tk.Y)
    
    # Nút đóng giả - giống Windows 95
    close_button = tk.Label(
        title_frame,
        text=" × ",
        font=("MS Sans Serif", 8, "bold"),
        bg=RETRO_COLORS["win95_titlebar"],
        fg=RETRO_COLORS["win95_titlebar_text"]
    )
    close_button.pack(side=tk.RIGHT)
    
    # Frame nội dung
    content_frame = tk.Frame(
        info_frame, 
        bg=RETRO_COLORS["win95_bg"],
        padx=5,
        pady=5
    )
    content_frame.pack(fill=tk.X, side=tk.TOP)

    # Hiển thị email
    if email:
        email_frame = tk.Frame(content_frame, bg=RETRO_COLORS["win95_bg"])
        email_frame.pack(fill=tk.X, pady=2)
        
        email_icon = tk.Label(
            email_frame,
            text="📧",
            font=("MS Sans Serif", 8),
            bg=RETRO_COLORS["win95_bg"]
        )
        email_icon.pack(side=tk.LEFT, padx=(0, 5))
        
        email_label = tk.Label(
            email_frame,
            text=f"Email: {email}",
            font=("MS Sans Serif", 8),
            fg=RETRO_COLORS["win95_text"],
            bg=RETRO_COLORS["win95_bg"],
            anchor="w"
        )
        email_label.pack(side=tk.LEFT, fill=tk.X)
    else:
        email_frame = tk.Frame(content_frame, bg=RETRO_COLORS["win95_bg"])
        email_frame.pack(fill=tk.X, pady=2)
        
        email_icon = tk.Label(
            email_frame,
            text="⚠️",
            font=("MS Sans Serif", 8),
            bg=RETRO_COLORS["win95_bg"]
        )
        email_icon.pack(side=tk.LEFT, padx=(0, 5))
        
        email_label = tk.Label(
            email_frame,
            text="Email: Không tìm thấy",
            font=("MS Sans Serif", 8),
            fg="#800000",  # Đỏ đậm Win95
            bg=RETRO_COLORS["win95_bg"],
            anchor="w"
        )
        email_label.pack(side=tk.LEFT, fill=tk.X)

    # Hiển thị loại đăng ký
    plan_frame = tk.Frame(content_frame, bg=RETRO_COLORS["win95_bg"])
    plan_frame.pack(fill=tk.X, pady=2)
    
    if subscription_info:
        subscription_type = format_subscription_type(subscription_info)
        
        plan_icon = tk.Label(
            plan_frame,
            text="🔰",
            font=("MS Sans Serif", 8),
            bg=RETRO_COLORS["win95_bg"]
        )
        plan_icon.pack(side=tk.LEFT, padx=(0, 5))
        
        subscription_label = tk.Label(
            plan_frame,
            text=f"Gói: {subscription_type}",
            font=("MS Sans Serif", 8),
            fg=RETRO_COLORS["win95_text"],
            bg=RETRO_COLORS["win95_bg"],
            anchor="w"
        )
        subscription_label.pack(side=tk.LEFT, fill=tk.X)

        # Hiển thị số ngày còn lại của bản dùng thử
        days_remaining = subscription_info.get("daysRemainingOnTrial")
        if days_remaining is not None and days_remaining > 0:
            trial_frame = tk.Frame(content_frame, bg=RETRO_COLORS["win95_bg"])
            trial_frame.pack(fill=tk.X, pady=2)
            
            trial_icon = tk.Label(
                trial_frame,
                text="⏱️",
                font=("MS Sans Serif", 8),
                bg=RETRO_COLORS["win95_bg"]
            )
            trial_icon.pack(side=tk.LEFT, padx=(0, 5))
            
            trial_label = tk.Label(
                trial_frame,
                text=f"Còn lại: {days_remaining} ngày",
                font=("MS Sans Serif", 8),
                fg=RETRO_COLORS["win95_text"],
                bg=RETRO_COLORS["win95_bg"],
                anchor="w"
            )
            trial_label.pack(side=tk.LEFT, fill=tk.X)
    else:
        plan_icon = tk.Label(
            plan_frame,
            text="🔰",
            font=("MS Sans Serif", 8),
            bg=RETRO_COLORS["win95_bg"]
        )
        plan_icon.pack(side=tk.LEFT, padx=(0, 5))
        
        subscription_label = tk.Label(
            plan_frame,
            text="Gói: Free",
            font=("MS Sans Serif", 8),
            fg=RETRO_COLORS["win95_text"],
            bg=RETRO_COLORS["win95_bg"],
            anchor="w"
        )
        subscription_label.pack(side=tk.LEFT, fill=tk.X)

    # Hiển thị thông tin sử dụng ở bên phải
    if usage_info:
        # Frame thông tin sử dụng bên phải
        usage_frame = tk.Frame(
            container_frame, 
            bg=RETRO_COLORS["win95_bg"],
            relief=tk.RIDGE,  # Viền kiểu Win95
            bd=1
        )
        usage_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Tạo tiêu đề mini giống cửa sổ Win95
        usage_title_frame = tk.Frame(
            usage_frame, 
            bg=RETRO_COLORS["win95_titlebar"],
            height=18
        )
        usage_title_frame.pack(fill=tk.X, side=tk.TOP)
        
        usage_title_label = tk.Label(
            usage_title_frame,
            text=" Thông tin sử dụng",
            font=("MS Sans Serif", 8, "bold"),
            bg=RETRO_COLORS["win95_titlebar"],
            fg=RETRO_COLORS["win95_titlebar_text"],
            anchor="w"
        )
        usage_title_label.pack(side=tk.LEFT, fill=tk.Y)
        
        # Nút đóng giả - giống Windows 95
        usage_close_button = tk.Label(
            usage_title_frame,
            text=" × ",
            font=("MS Sans Serif", 8, "bold"),
            bg=RETRO_COLORS["win95_titlebar"],
            fg=RETRO_COLORS["win95_titlebar_text"]
        )
        usage_close_button.pack(side=tk.RIGHT)
        
        # Frame nội dung sử dụng
        usage_content_frame = tk.Frame(
            usage_frame, 
            bg=RETRO_COLORS["win95_bg"],
            padx=5,
            pady=5
        )
        usage_content_frame.pack(fill=tk.BOTH, expand=True)

        # Sử dụng Premium
        premium_usage = usage_info.get('premium_usage', 0)
        max_premium_usage = usage_info.get('max_premium_usage', "Không giới hạn")

        # Đảm bảo giá trị không phải None
        if premium_usage is None:
            premium_usage = 0

        # Xử lý trường hợp "Không giới hạn"
        if isinstance(max_premium_usage, str) and max_premium_usage == "Không giới hạn":
            premium_color = "#008000"  # Green
            premium_display = f"{premium_usage}/{max_premium_usage}"
        else:
            # Tính phần trăm khi giá trị là số
            if max_premium_usage is None or max_premium_usage == 0:
                max_premium_usage = 999
                premium_percentage = 0
            else:
                premium_percentage = (premium_usage / max_premium_usage) * 100

            # Chọn màu dựa trên phần trăm sử dụng
            premium_color = "#008000"  # Green
            if premium_percentage > 70:
                premium_color = "#FFA500"  # Orange
            if premium_percentage > 90:
                premium_color = "#800000"  # Đỏ đậm Win95

            premium_display = f"{premium_usage}/{max_premium_usage} ({premium_percentage:.1f}%)"

        premium_frame = tk.Frame(usage_content_frame, bg=RETRO_COLORS["win95_bg"])
        premium_frame.pack(fill=tk.X, pady=1)
        
        premium_icon = tk.Label(
            premium_frame,
            text="⭐",
            font=("MS Sans Serif", 8),
            bg=RETRO_COLORS["win95_bg"]
        )
        premium_icon.pack(side=tk.LEFT, padx=(0, 5))
        
        premium_label = tk.Label(
            premium_frame,
            text=f"Fast Response: {premium_display}",
            font=("MS Sans Serif", 8),
            fg=premium_color,
            bg=RETRO_COLORS["win95_bg"],
            anchor="w"
        )
        premium_label.pack(side=tk.LEFT, fill=tk.X)

        # Sử dụng Basic
        basic_usage = usage_info.get('basic_usage', 0)
        max_basic_usage = usage_info.get('max_basic_usage', "Không giới hạn")

        # Đảm bảo giá trị không phải None
        if basic_usage is None:
            basic_usage = 0

        # Xử lý trường hợp "Không giới hạn"
        if isinstance(max_basic_usage, str) and max_basic_usage == "Không giới hạn":
            basic_color = "#008000"  # Green
            basic_display = f"{basic_usage}/{max_basic_usage}"
        else:
            # Tính phần trăm khi giá trị là số
            if max_basic_usage is None or max_basic_usage == 0:
                max_basic_usage = 999
                basic_percentage = 0
            else:
                basic_percentage = (basic_usage / max_basic_usage) * 100

            # Chọn màu dựa trên phần trăm sử dụng
            basic_color = "#008000"  # Green
            if basic_percentage > 70:
                basic_color = "#FFA500"  # Orange
            if basic_percentage > 90:
                basic_color = "#800000"  # Đỏ đậm Win95

            basic_display = f"{basic_usage}/{max_basic_usage} ({basic_percentage:.1f}%)"

        basic_frame = tk.Frame(usage_content_frame, bg=RETRO_COLORS["win95_bg"])
        basic_frame.pack(fill=tk.X, pady=1)
        
        basic_icon = tk.Label(
            basic_frame,
            text="🔄",
            font=("MS Sans Serif", 8),
            bg=RETRO_COLORS["win95_bg"]
        )
        basic_icon.pack(side=tk.LEFT, padx=(0, 5))
        
        basic_label = tk.Label(
            basic_frame,
            text=f"Slow Response: {basic_display}",
            font=("MS Sans Serif", 8),
            fg=basic_color,
            bg=RETRO_COLORS["win95_bg"],
            anchor="w"
        )
        basic_label.pack(side=tk.LEFT, fill=tk.X)
        
        # Tạo thanh tiến trình kiểu Windows 95
        progress_frame = tk.Frame(
            usage_content_frame, 
            bg=RETRO_COLORS["win95_bg"],
            relief=tk.SUNKEN,
            bd=1,
            height=15
        )
        progress_frame.pack(fill=tk.X, pady=5)
        
        # Tính phần trăm sử dụng Premium nếu có
        if isinstance(max_premium_usage, int) and max_premium_usage > 0:
            premium_percentage = min(100, (premium_usage / max_premium_usage) * 100)
            
            # Tạo thanh tiến trình
            def update_progress(progress_frame=progress_frame, width_percent=premium_percentage):
                width = int((width_percent / 100) * progress_frame.winfo_width())
                progress_bar = tk.Frame(
                    progress_frame,
                    bg=RETRO_COLORS["win95_titlebar"],
                    height=13
                )
                progress_bar.place(x=1, y=1, width=width, height=13)
            
            # Cập nhật khi cửa sổ thay đổi kích thước
            progress_frame.bind("<Configure>", lambda e: update_progress())
            
            # Cập nhật lần đầu sau khi cửa sổ được hiển thị
            progress_frame.after(100, update_progress)

def display_account_info():
    """Hiển thị thông tin tài khoản trong terminal"""
    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{ACCOUNT_EMOJI['USER']} Thông tin tài khoản Cursor{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")

    # Lấy token
    token = get_token()
    if not token:
        print(f"{Fore.RED}{ACCOUNT_EMOJI['ERROR']} Không tìm thấy token. Vui lòng đăng nhập vào Cursor trước.{Style.RESET_ALL}")
        return

    # Lấy đường dẫn
    paths = get_cursor_paths()
    if not paths:
        print(f"{Fore.RED}{ACCOUNT_EMOJI['ERROR']} Không tìm thấy cấu hình.{Style.RESET_ALL}")
        return

    # Lấy thông tin email - thử nhiều nguồn
    email = get_email_from_storage(paths['storage_path'])

    # Nếu không tìm thấy trong storage, thử từ sqlite
    if not email:
        email = get_email_from_sqlite(paths['sqlite_path'])

    # Lấy thông tin đăng ký
    try:
        subscription_info = UsageManager.get_stripe_profile(token)
    except Exception:
        subscription_info = None

    # Nếu không tìm thấy trong storage và sqlite, thử từ thông tin đăng ký
    if not email and subscription_info:
        # Thử lấy email từ thông tin đăng ký
        if 'customer' in subscription_info and 'email' in subscription_info['customer']:
            email = subscription_info['customer']['email']

    # Lấy thông tin sử dụng - xử lý lỗi một cách im lặng
    try:
        usage_info = UsageManager.get_usage(token)
    except Exception:
        usage_info = None

    # Hiển thị thông tin tài khoản
    if email:
        print(f"{Fore.GREEN}{ACCOUNT_EMOJI['EMAIL']} Email: {Fore.WHITE}{email}{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}{ACCOUNT_EMOJI['WARNING']} Email không tìm thấy{Style.RESET_ALL}")

    # Hiển thị loại đăng ký
    if subscription_info:
        subscription_type = format_subscription_type(subscription_info)
        print(f"{Fore.GREEN}{ACCOUNT_EMOJI['PLAN']} Gói: {Fore.WHITE}{subscription_type}{Style.RESET_ALL}")

        # Hiển thị số ngày còn lại của bản dùng thử
        days_remaining = subscription_info.get("daysRemainingOnTrial")
        if days_remaining is not None and days_remaining > 0:
            print(f"{Fore.GREEN}{ACCOUNT_EMOJI['TIME']} Còn lại: {Fore.WHITE}{days_remaining} ngày{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}{ACCOUNT_EMOJI['WARNING']} Không tìm thấy thông tin đăng ký{Style.RESET_ALL}")

    # Hiển thị thông tin sử dụng
    if usage_info:
        print(f"\n{Fore.GREEN}{ACCOUNT_EMOJI['USAGE']} Thống kê sử dụng:{Style.RESET_ALL}")

        # Sử dụng Premium
        premium_usage = usage_info.get('premium_usage', 0)
        max_premium_usage = usage_info.get('max_premium_usage', "Không giới hạn")

        # Đảm bảo giá trị không phải None
        if premium_usage is None:
            premium_usage = 0

        # Xử lý trường hợp "Không giới hạn"
        if isinstance(max_premium_usage, str) and max_premium_usage == "Không giới hạn":
            premium_color = Fore.GREEN  # Khi không có giới hạn, sử dụng màu xanh lá
            premium_display = f"{premium_usage}/{max_premium_usage}"
        else:
            # Tính phần trăm khi giá trị là số
            if max_premium_usage is None or max_premium_usage == 0:
                max_premium_usage = 999
                premium_percentage = 0
            else:
                premium_percentage = (premium_usage / max_premium_usage) * 100

            # Chọn màu dựa trên phần trăm sử dụng
            premium_color = Fore.GREEN
            if premium_percentage > 70:
                premium_color = Fore.YELLOW
            if premium_percentage > 90:
                premium_color = Fore.RED

            premium_display = f"{premium_usage}/{max_premium_usage} ({premium_percentage:.1f}%)"

        print(f"{Fore.BLUE}{ACCOUNT_EMOJI['PREMIUM']} Fast Response: {premium_color}{premium_display}{Style.RESET_ALL}")

        # Sử dụng Basic
        basic_usage = usage_info.get('basic_usage', 0)
        max_basic_usage = usage_info.get('max_basic_usage', "Không giới hạn")

        # Đảm bảo giá trị không phải None
        if basic_usage is None:
            basic_usage = 0

        # Xử lý trường hợp "Không giới hạn"
        if isinstance(max_basic_usage, str) and max_basic_usage == "Không giới hạn":
            basic_color = Fore.GREEN  # Khi không có giới hạn, sử dụng màu xanh lá
            basic_display = f"{basic_usage}/{max_basic_usage}"
        else:
            # Tính phần trăm khi giá trị là số
            if max_basic_usage is None or max_basic_usage == 0:
                max_basic_usage = 999
                basic_percentage = 0
            else:
                basic_percentage = (basic_usage / max_basic_usage) * 100

            # Chọn màu dựa trên phần trăm sử dụng
            basic_color = Fore.GREEN
            if basic_percentage > 70:
                basic_color = Fore.YELLOW
            if basic_percentage > 90:
                basic_color = Fore.RED

            basic_display = f"{basic_usage}/{max_basic_usage} ({basic_percentage:.1f}%)"

        print(f"{Fore.BLUE}{ACCOUNT_EMOJI['BASIC']} Slow Response: {basic_color}{basic_display}{Style.RESET_ALL}")

def run():
    """Hàm chạy chính"""
    display_account_info()

if __name__ == "__main__":
    run()
