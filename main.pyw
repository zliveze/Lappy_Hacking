# main.pyw - Lappy Lab 4.1 Entry Point (No Console Window)
import sys
import os
import ctypes

# Ẩn console window ngay từ đầu
if sys.platform == "win32":
    import ctypes.wintypes
    kernel32 = ctypes.windll.kernel32
    user32 = ctypes.windll.user32

    # Lấy handle của console window hiện tại
    console_window = kernel32.GetConsoleWindow()
    if console_window:
        # Ẩn console window
        user32.ShowWindow(console_window, 0)  # SW_HIDE

# Thêm thư mục src vào Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def is_admin():
    """Kiểm tra xem có quyền admin không"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """Chạy lại script với quyền admin mà không hiển thị console"""
    if is_admin():
        return True
    else:
        try:
            # Lấy đường dẫn Python và script hiện tại
            python_exe = sys.executable
            script_path = os.path.abspath(__file__)

            # Ưu tiên sử dụng pythonw.exe để ẩn console hoàn toàn
            pythonw_exe = python_exe.replace('python.exe', 'pythonw.exe')
            if not os.path.exists(pythonw_exe):
                # Nếu không có pythonw.exe, tìm trong cùng thư mục
                python_dir = os.path.dirname(python_exe)
                pythonw_exe = os.path.join(python_dir, 'pythonw.exe')
                if not os.path.exists(pythonw_exe):
                    pythonw_exe = python_exe  # Fallback cuối cùng

            # Chạy lại với quyền admin và ẩn hoàn toàn
            ctypes.windll.shell32.ShellExecuteW(
                None,
                "runas",
                pythonw_exe,
                f'"{script_path}"',
                None,
                0  # SW_HIDE - ẩn cửa sổ hoàn toàn
            )
            return False
        except Exception:
            # Nếu có lỗi, vẫn tiếp tục chạy nhưng ẩn console
            return True

def main():
    """Entry point chính của ứng dụng"""
    # Kiểm tra và yêu cầu quyền admin nếu cần
    if not run_as_admin():
        sys.exit(0)

    try:
        from gui.main_window import LappyLabApp
        from core.config import setup_config

        # Khởi tạo config
        setup_config()

        # Tạo và chạy app
        app = LappyLabApp()
        app.run()

    except Exception as e:
        # Hiển thị lỗi bằng messagebox nếu có thể
        try:
            import tkinter.messagebox as messagebox
            messagebox.showerror("Lỗi", f"Lỗi khởi tạo ứng dụng: {str(e)}")
        except:
            # Nếu không thể hiển thị messagebox, ghi vào file log
            try:
                with open('error.log', 'w', encoding='utf-8') as f:
                    f.write(f"Lỗi khởi tạo ứng dụng: {str(e)}\n")
                    import traceback
                    traceback.print_exc(file=f)
            except:
                pass

if __name__ == "__main__":
    main()
