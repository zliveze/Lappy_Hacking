import os
import sys
import json
import requests
import sqlite3
from typing import Dict, Optional
import platform
import logging
import re

# Setup logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Config giống bản gốc
class Config:
    NAME_LOWER = "cursor"
    NAME_CAPITALIZE = "Cursor"
    BASE_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

class UsageManager:
    """Usage Manager - SAO CHÉP TỪ BẢN GỐC"""

    @staticmethod
    def get_proxy():
        """get proxy"""
        proxy = os.environ.get("HTTP_PROXY") or os.environ.get("HTTPS_PROXY")
        if proxy:
            return {"http": proxy, "https": proxy}
        return None

    @staticmethod
    def get_usage(token: str) -> Optional[Dict]:
        if not token:
            logger.error("No token provided for usage API")
            return None

        url = f"https://www.{Config.NAME_LOWER}.com/api/usage"
        headers = Config.BASE_HEADERS.copy()
        headers.update({"Cookie": f"Workos{Config.NAME_CAPITALIZE}SessionToken=user_01OOOOOOOOOOOOOOOOOOOOOOOO%3A%3A{token}"})

        logger.info(f"Calling usage API: {url}")
        logger.info(f"Token length: {len(token)}")

        try:
            proxies = UsageManager.get_proxy()
            response = requests.get(url, headers=headers, timeout=10, proxies=proxies)

            logger.info(f"Usage API response status: {response.status_code}")

            if response.status_code == 401:
                logger.error("Usage API returned 401 - Token may be invalid or expired")
                return None
            elif response.status_code == 403:
                logger.error("Usage API returned 403 - Access forbidden")
                return None

            response.raise_for_status()
            data = response.json()

            logger.info(f"Usage API response keys: {list(data.keys())}")

            # get Premium usage and limit
            gpt4_data = data.get("gpt-4", {})
            premium_usage = gpt4_data.get("numRequestsTotal", 0)
            max_premium_usage = gpt4_data.get("maxRequestUsage", 999)

            # get Basic usage, but set limit to "No Limit"
            gpt35_data = data.get("gpt-3.5-turbo", {})
            basic_usage = gpt35_data.get("numRequestsTotal", 0)

            logger.info(f"Premium usage: {premium_usage}/{max_premium_usage}")
            logger.info(f"Basic usage: {basic_usage}")

            return {
                'premium_usage': premium_usage,
                'max_premium_usage': max_premium_usage,
                'basic_usage': basic_usage,
                'max_basic_usage': "No Limit"  # set Basic limit to "No Limit"
            }
        except requests.RequestException as e:
            logger.error(f"Get usage info failed (RequestException): {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response text: {e.response.text[:200]}")
            return None
        except Exception as e:
            logger.error(f"Get usage info failed (Exception): {str(e)}")
            return None

    @staticmethod
    def get_stripe_profile(token: str) -> Optional[Dict]:
        if not token:
            logger.error("No token provided for subscription API")
            return None

        url = f"https://api2.{Config.NAME_LOWER}.sh/auth/full_stripe_profile"
        headers = Config.BASE_HEADERS.copy()
        headers.update({"Authorization": f"Bearer {token}"})

        logger.info(f"Calling subscription API: {url}")
        logger.info(f"Token length: {len(token)}")

        try:
            proxies = UsageManager.get_proxy()
            response = requests.get(url, headers=headers, timeout=10, proxies=proxies)

            logger.info(f"Subscription API response status: {response.status_code}")

            if response.status_code == 401:
                logger.error("Subscription API returned 401 - Token may be invalid or expired")
                return None
            elif response.status_code == 403:
                logger.error("Subscription API returned 403 - Access forbidden")
                return None

            response.raise_for_status()
            data = response.json()

            logger.info(f"Subscription API response keys: {list(data.keys())}")

            if 'membershipType' in data:
                logger.info(f"Membership type: {data['membershipType']}")
            if 'subscriptionStatus' in data:
                logger.info(f"Subscription status: {data['subscriptionStatus']}")
            if 'daysRemainingOnTrial' in data:
                logger.info(f"Days remaining: {data['daysRemainingOnTrial']}")

            return data

        except requests.RequestException as e:
            logger.error(f"Get subscription info failed (RequestException): {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response text: {e.response.text[:200]}")
            return None
        except Exception as e:
            logger.error(f"Get subscription info failed (Exception): {str(e)}")
            return None

def get_token_from_config():
    """get path info from config - SỬ DỤNG UTILS TỪ LAPPY HACKING"""
    try:
        from core.utils import get_cursor_paths
        paths = get_cursor_paths()
        if paths:
            # Add session storage path based on OS
            system = platform.system()
            if system == "Windows":
                session_path = os.path.join(os.getenv("APPDATA", ""), "Cursor", "Session Storage")
            elif system == "Darwin":  # macOS
                session_path = os.path.expanduser("~/Library/Application Support/Cursor/Session Storage")
            elif system == "Linux":
                session_path = os.path.expanduser("~/.config/Cursor/Session Storage")
            else:
                session_path = ""

            return {
                'storage_path': paths.get('storage_path', ''),
                'sqlite_path': paths.get('sqlite_path', ''),
                'session_path': session_path
            }
    except Exception as e:
        logger.error(f"Get config path failed: {str(e)}")

    return None

def get_token_from_storage(storage_path):
    if not os.path.exists(storage_path):
        return None

    try:
        with open(storage_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

            # try to get accessToken first
            if 'cursorAuth/accessToken' in data:
                token = data['cursorAuth/accessToken']
                # Handle Buffer format
                if isinstance(token, dict) and token.get('type') == 'Buffer':
                    # Convert Buffer to string
                    buffer_data = token.get('data', [])
                    if buffer_data:
                        try:
                            token_str = ''.join(chr(b) for b in buffer_data if 32 <= b <= 126)
                            if len(token_str) > 20:
                                logger.info(f"Converted Buffer token to string: {token_str[:20]}...")
                                return token_str
                        except:
                            pass
                elif isinstance(token, str) and len(token) > 20:
                    return token

            # try other possible keys
            for key in data:
                if 'token' in key.lower():
                    token = data[key]
                    if isinstance(token, str) and len(token) > 20:
                        return token
                    elif isinstance(token, dict) and token.get('type') == 'Buffer':
                        buffer_data = token.get('data', [])
                        if buffer_data:
                            try:
                                token_str = ''.join(chr(b) for b in buffer_data if 32 <= b <= 126)
                                if len(token_str) > 20:
                                    return token_str
                            except:
                                continue

    except Exception as e:
        logger.error(f"get token from storage.json failed: {str(e)}")

    return None

def get_token_from_sqlite(sqlite_path):
    if not os.path.exists(sqlite_path):
        return None

    try:
        conn = sqlite3.connect(sqlite_path)
        cursor = conn.cursor()

        # Try multiple queries to find token
        queries = [
            "SELECT value FROM ItemTable WHERE key LIKE '%token%'",
            "SELECT value FROM ItemTable WHERE key LIKE '%cursorAuth%'",
            "SELECT value FROM ItemTable WHERE key LIKE '%accessToken%'",
            "SELECT value FROM ItemTable WHERE value LIKE '%token%'"
        ]

        for query in queries:
            try:
                cursor.execute(query)
                rows = cursor.fetchall()

                for row in rows:
                    try:
                        value = row[0]

                        # Direct string token
                        if isinstance(value, str) and len(value) > 20:
                            # Check if it looks like a token (alphanumeric + some special chars)
                            if re.match(r'^[a-zA-Z0-9._-]+$', value):
                                conn.close()
                                return value

                        # Try to parse as JSON
                        try:
                            data = json.loads(value)
                            if isinstance(data, dict):
                                # Look for token field
                                if 'token' in data:
                                    token = data['token']
                                    if isinstance(token, str) and len(token) > 20:
                                        conn.close()
                                        return token

                                # Look for accessToken field
                                if 'accessToken' in data:
                                    token = data['accessToken']
                                    if isinstance(token, str) and len(token) > 20:
                                        conn.close()
                                        return token

                                # Handle Buffer format
                                for key in data:
                                    if 'token' in key.lower():
                                        token = data[key]
                                        if isinstance(token, dict) and token.get('type') == 'Buffer':
                                            buffer_data = token.get('data', [])
                                            if buffer_data:
                                                try:
                                                    token_str = ''.join(chr(b) for b in buffer_data if 32 <= b <= 126)
                                                    if len(token_str) > 20:
                                                        conn.close()
                                                        return token_str
                                                except:
                                                    continue
                        except:
                            continue

                    except:
                        continue
            except:
                continue

        conn.close()

    except Exception as e:
        logger.error(f"get token from sqlite failed: {str(e)}")

    return None

def get_token_from_session(session_path):
    if not os.path.exists(session_path):
        return None

    try:
        # try to find all possible session files
        for file in os.listdir(session_path):
            if file.endswith('.log'):
                file_path = os.path.join(session_path, file)
                try:
                    with open(file_path, 'rb') as f:
                        content = f.read().decode('utf-8', errors='ignore')
                        # find token pattern
                        token_match = re.search(r'"token":"([^"]+)"', content)
                        if token_match:
                            return token_match.group(1)
                except:
                    continue
    except Exception as e:
        logger.error(f"get token from session failed: {str(e)}")

    return None

def get_token():
    # get path from config
    paths = get_token_from_config()
    if not paths:
        return None

    # try to get token from different locations
    token = get_token_from_storage(paths['storage_path'])
    if token:
        return token

    token = get_token_from_sqlite(paths['sqlite_path'])
    if token:
        return token

    token = get_token_from_session(paths['session_path'])
    if token:
        return token

    return None

def format_subscription_type(subscription_data: Dict) -> str:
    if not subscription_data:
        return "Free"

    # handle new API response format
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

    # compatible with old API response format
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

def get_email_from_storage(storage_path):
    if not os.path.exists(storage_path):
        return None

    try:
        with open(storage_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # try to get email
            if 'cursorAuth/cachedEmail' in data:
                return data['cursorAuth/cachedEmail']

            # try other possible keys
            for key in data:
                if 'email' in key.lower() and isinstance(data[key], str) and '@' in data[key]:
                    return data[key]
    except Exception as e:
        logger.error(f"get email from storage.json failed: {str(e)}")

    return None

def get_email_from_sqlite(sqlite_path):
    if not os.path.exists(sqlite_path):
        return None

    try:
        conn = sqlite3.connect(sqlite_path)
        cursor = conn.cursor()
        # try to query records containing email
        cursor.execute("SELECT value FROM ItemTable WHERE key LIKE '%email%' OR key LIKE '%cursorAuth%'")
        rows = cursor.fetchall()
        conn.close()

        for row in rows:
            try:
                value = row[0]
                # if it's a string and contains @, it might be an email
                if isinstance(value, str) and '@' in value:
                    return value

                # try to parse JSON
                try:
                    data = json.loads(value)
                    if isinstance(data, dict):
                        # check if there's an email field
                        if 'email' in data:
                            return data['email']
                        # check if there's a cachedEmail field
                        if 'cachedEmail' in data:
                            return data['cachedEmail']
                except:
                    pass
            except:
                continue
    except Exception as e:
        logger.error(f"get email from sqlite failed: {str(e)}")

    return None

def get_email():
    paths = get_token_from_config()
    if not paths:
        return None

    # get email info - try multiple sources
    email = get_email_from_storage(paths['storage_path'])

    # if not found in storage, try from sqlite
    if not email:
        email = get_email_from_sqlite(paths['sqlite_path'])

    return email

def get_usage_info(token: str) -> Optional[Dict]:
    url = f"https://www.{Config.NAME_LOWER}.com/api/usage"
    headers = Config.BASE_HEADERS.copy()
    headers.update({"Cookie": f"Workos{Config.NAME_CAPITALIZE}SessionToken=user_01OOOOOOOOOOOOOOOOOOOOOOOO%3A%3A{token}"})
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        # get Premium usage and limit
        gpt4_data = data.get("gpt-4", {})
        premium_usage = gpt4_data.get("numRequestsTotal", 0)
        max_premium_usage = gpt4_data.get("maxRequestUsage", 999)

        # get Basic usage, but set limit to "No Limit"
        gpt35_data = data.get("gpt-3.5-turbo", {})
        basic_usage = gpt35_data.get("numRequestsTotal", 0)

        return {
            'premium_usage': premium_usage,
            'max_premium_usage': max_premium_usage,
            'basic_usage': basic_usage,
            'max_basic_usage': "No Limit"  # set Basic limit to "No Limit"
        }
    except requests.RequestException as e:
        logger.error(f"Get usage info failed: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Get usage info failed: {str(e)}")
        return None

def _format_usage(usage_data):
    if not usage_data:
        return "N/A", "N/A"

    # Fast Response (GPT-4)
    premium_usage = usage_data.get('premium_usage', 0)
    max_premium_usage = usage_data.get('max_premium_usage', "No Limit")

    if isinstance(max_premium_usage, str) and max_premium_usage == "No Limit":
        fast_response = f"{premium_usage}/{max_premium_usage}"
    else:
        fast_response = f"{premium_usage}/{max_premium_usage}"

    # Slow Response (GPT-3.5)
    basic_usage = usage_data.get('basic_usage', 0)
    max_basic_usage = usage_data.get('max_basic_usage', "No Limit")
    slow_response = f"{basic_usage}/{max_basic_usage}"

    return fast_response, slow_response

def show_account_info():
    output = []

    # get token
    token = get_token()
    if not token:
        return False, "❌ Không tìm thấy token xác thực. Vui lòng đăng nhập vào Cursor."

    # get path info
    paths = get_token_from_config()
    if not paths:
        return False, "❌ Không tìm thấy cấu hình. Vui lòng kiểm tra Cursor."

    # get email info - try multiple sources
    email = get_email_from_storage(paths['storage_path'])

    # if not found in storage, try from sqlite
    if not email:
        email = get_email_from_sqlite(paths['sqlite_path'])

    # get subscription info
    try:
        subscription_info = UsageManager.get_stripe_profile(token)
    except Exception as e:
        logger.error(f"Get subscription info failed: {str(e)}")
        subscription_info = None

    # if not found in storage and sqlite, try from subscription info
    if not email and subscription_info:
        # try to get email from subscription info
        if 'customer' in subscription_info and 'email' in subscription_info['customer']:
            email = subscription_info['customer']['email']

    # get usage info - silently handle errors
    try:
        usage_info = UsageManager.get_usage(token)
    except Exception as e:
        logger.error(f"Get usage info failed: {str(e)}")
        usage_info = None

    # Prepare left and right info
    left_info = []
    right_info = []

    # Left side shows account info
    if email:
        left_info.append(f"📧 Email: {email}")
    else:
        left_info.append("⚠️ Email not found")

    # Show subscription type
    if subscription_info:
        subscription_type = format_subscription_type(subscription_info)
        left_info.append(f"🔑 Subscription: {subscription_type}")

        # Show remaining trial days
        days_remaining = subscription_info.get("daysRemainingOnTrial")
        if days_remaining is not None and days_remaining > 0:
            left_info.append(f"⏰ Remaining Pro Trial: {days_remaining} days")
    else:
        left_info.append("⚠️ Subscription information not found")

    # Right side shows usage info - only if available
    if usage_info:
        right_info.append("📊 Usage Statistics:")

        # Premium usage
        premium_usage = usage_info.get('premium_usage', 0)
        max_premium_usage = usage_info.get('max_premium_usage', "No Limit")

        # make sure the value is not None
        if premium_usage is None:
            premium_usage = 0

        # handle "No Limit" case
        if isinstance(max_premium_usage, str) and max_premium_usage == "No Limit":
            premium_display = f"{premium_usage}/{max_premium_usage}"
        else:
            # calculate percentage when the value is a number
            if max_premium_usage is None or max_premium_usage == 0:
                max_premium_usage = 999
            premium_display = f"{premium_usage}/{max_premium_usage}"

        right_info.append(f"⭐ Fast Response: {premium_display}")

        # Slow Response
        basic_usage = usage_info.get('basic_usage', 0)
        max_basic_usage = usage_info.get('max_basic_usage', "No Limit")

        # make sure the value is not None
        if basic_usage is None:
            basic_usage = 0

        # handle "No Limit" case
        if isinstance(max_basic_usage, str) and max_basic_usage == "No Limit":
            basic_display = f"{basic_usage}/{max_basic_usage}"
        else:
            # calculate percentage when the value is a number
            if max_basic_usage is None or max_basic_usage == 0:
                max_basic_usage = 999
            basic_display = f"{basic_usage}/{max_basic_usage}"

        right_info.append(f"📝 Slow Response: {basic_display}")

    # Create output in box format similar to original
    output.append("=" * 70)
    output.append("CURSOR ACCOUNT INFORMATION")
    output.append("=" * 70)

    # Calculate the maximum display width of left info
    max_left_width = 0
    for item in left_info:
        max_left_width = max(max_left_width, len(item))

    # Set the starting position of right info
    fixed_spacing = 4  # Fixed spacing
    right_start = max_left_width + fixed_spacing

    # Print info
    max_rows = max(len(left_info), len(right_info))

    for i in range(max_rows):
        line = ""
        # Print left info
        if i < len(left_info):
            left_item = left_info[i]
            line += left_item
            # Calculate spaces needed
            spaces = right_start - len(left_item)
        else:
            # If left side has no items, print only spaces
            spaces = right_start

        # Print right info
        if i < len(right_info):
            line += ' ' * spaces + right_info[i]

        output.append(line)

    output.append("=" * 70)

    return True, "\n".join(output)

# Đổi tên hàm chính để phù hợp
def show_config():
    """Hàm chính được gọi từ main.py"""
    return show_account_info()
