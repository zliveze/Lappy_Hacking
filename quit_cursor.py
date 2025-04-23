import psutil
import time
from colorama import Fore, Style, init
import sys
import os

# Khởi tạo colorama
init()

# Emoji cho các thông báo
EMOJI = {
    "PROCESS": "⚙️",
    "SUCCESS": "✅",
    "ERROR": "❌",
    "INFO": "ℹ️",
    "WAIT": "⏳"
}

class CursorQuitter:
    def __init__(self, timeout=5):
        self.timeout = timeout
        
    def quit_cursor(self):
        """Đóng nhẹ nhàng các tiến trình Cursor"""
        try:
            print(f"{Fore.CYAN}{EMOJI['PROCESS']} Đang tìm kiếm tiến trình Cursor...{Style.RESET_ALL}")
            cursor_processes = []
            
            # Thu thập tất cả tiến trình Cursor
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if proc.info['name'].lower() in ['cursor.exe', 'cursor']:
                        cursor_processes.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            if not cursor_processes:
                print(f"{Fore.GREEN}{EMOJI['INFO']} Không tìm thấy tiến trình Cursor nào đang chạy.{Style.RESET_ALL}")
                return True

            # Yêu cầu nhẹ nhàng các tiến trình kết thúc
            for proc in cursor_processes:
                try:
                    if proc.is_running():
                        print(f"{Fore.YELLOW}{EMOJI['PROCESS']} Đang kết thúc tiến trình Cursor (PID: {proc.pid})...{Style.RESET_ALL}")
                        proc.terminate()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # Đợi các tiến trình kết thúc tự nhiên
            print(f"{Fore.CYAN}{EMOJI['WAIT']} Đang đợi các tiến trình kết thúc...{Style.RESET_ALL}")
            start_time = time.time()
            while time.time() - start_time < self.timeout:
                still_running = []
                for proc in cursor_processes:
                    try:
                        if proc.is_running():
                            still_running.append(proc)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                
                if not still_running:
                    print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Tất cả tiến trình Cursor đã được đóng thành công.{Style.RESET_ALL}")
                    return True
                    
                time.sleep(0.5)
                
            # Nếu các tiến trình vẫn đang chạy sau thời gian chờ
            if still_running:
                process_list = ", ".join([str(p.pid) for p in still_running])
                print(f"{Fore.RED}{EMOJI['ERROR']} Hết thời gian chờ. Các tiến trình sau vẫn đang chạy: {process_list}{Style.RESET_ALL}")
                return False
                
            return True

        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} Lỗi khi đóng Cursor: {str(e)}{Style.RESET_ALL}")
            return False

def quit_cursor(timeout=5):
    """Hàm tiện lợi để gọi trực tiếp hàm đóng Cursor"""
    quitter = CursorQuitter(timeout)
    return quitter.quit_cursor()

if __name__ == "__main__":
    quit_cursor()
