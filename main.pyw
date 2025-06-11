# main.pyw - Lappy Lab 4.1 Entry Point (No Console Window)
import sys
import os
import ctypes
import subprocess

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

            # Chạy lại với quyền admin (sử dụng pythonw.exe để ẩn console)
            pythonw_exe = python_exe.replace('python.exe', 'pythonw.exe')
            if not os.path.exists(pythonw_exe):
                pythonw_exe = python_exe  # Fallback nếu không tìm thấy pythonw.exe

            ctypes.windll.shell32.ShellExecuteW(
                None,
                "runas",
                pythonw_exe,
                f'"{script_path}"',
                None,
                0  # SW_HIDE - ẩn cửa sổ
            )
            return False
        except Exception as e:
            # Nếu có lỗi, thử chạy với python.exe thông thường
            try:
                ctypes.windll.shell32.ShellExecuteW(
                    None,
                    "runas",
                    python_exe,
                    f'"{script_path}"',
                    None,
                    0  # SW_HIDE - ẩn cửa sổ
                )
                return False
            except:
                return True  # Tiếp tục chạy bình thường

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
