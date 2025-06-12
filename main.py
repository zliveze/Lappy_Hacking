# main.py - Lappy Lab 4.1 Entry Point (Console Version)
import sys
import os
import ctypes

# Thêm thư mục src vào Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def is_admin():
    """Kiểm tra xem có quyền admin không"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """Chạy lại script với quyền admin"""
    if is_admin():
        return True
    else:
        try:
            # Lấy đường dẫn Python và script hiện tại
            python_exe = sys.executable
            script_path = os.path.abspath(__file__)

            # Chạy lại với quyền admin
            ctypes.windll.shell32.ShellExecuteW(
                None,
                "runas",
                python_exe,
                f'"{script_path}"',
                None,
                1  # SW_SHOWNORMAL - hiển thị console
            )
            return False
        except Exception as e:
            print(f"Không thể chạy với quyền admin: {e}")
            return True  # Tiếp tục chạy bình thường

def main():
    """Entry point chính của ứng dụng (Console Version)"""
    print("🚀 Lappy Lab 4.1 - Console Version")
    print("💡 Để chạy không hiển thị CMD, sử dụng: start_lappy.vbs hoặc main.pyw")
    print()

    # Kiểm tra và yêu cầu quyền admin nếu cần
    if not run_as_admin():
        print("Đang khởi động lại với quyền Administrator...")
        sys.exit(0)

    print("✅ Đang chạy với quyền Administrator")

    try:
        from gui.main_window import LappyLabApp
        from core.config import setup_config

        # Khởi tạo config
        setup_config()

        # Tạo và chạy app
        app = LappyLabApp()
        app.run()

    except Exception as e:
        print(f"Lỗi khởi tạo ứng dụng: {str(e)}")
        import traceback
        traceback.print_exc()

        # Hiển thị lỗi bằng messagebox nếu có thể
        try:
            import tkinter.messagebox as messagebox
            messagebox.showerror("Lỗi", f"Lỗi khởi tạo ứng dụng: {str(e)}")
        except:
            pass

if __name__ == "__main__":
    main()