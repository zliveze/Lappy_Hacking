# demo_ui.py - Demo giao diện mới không cần quyền admin
import sys
import os

# Thêm thư mục src vào Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Demo giao diện mới"""
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
