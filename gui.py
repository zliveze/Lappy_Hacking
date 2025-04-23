import os
import sys
import platform
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import customtkinter as ctk
from PIL import Image, ImageTk
import threading
import io
import datetime
import base64
from colorama import Fore, Style, init, AnsiToWin32
from utils import get_windows_version, get_computer_name, get_release_date, is_admin, run_as_admin
from config import EMOJI, get_config
from cursor_acc_info import display_account_info_frame

# Thử import icon từ base64
try:
    from icon_base64 import get_icon_data
    HAS_ICON_BASE64 = True
    print("Successfully imported icon_base64 module.")
except ImportError:
    HAS_ICON_BASE64 = False
    print("Could not import icon_base64 module.")

# Khởi tạo colorama
init()

# --- DEBUGGING ---
import sys
import os
print("--- Debugging Resource Paths ---")
print(f"Script path (__file__): {os.path.abspath(__file__)}")
print(f"Running from EXE: {hasattr(sys, '_MEIPASS')}")
if hasattr(sys, '_MEIPASS'):
    print(f"MEIPASS path: {sys._MEIPASS}")
    expected_dir = os.path.join(sys._MEIPASS, "public", "images")
    print(f"Expected image directory in MEIPASS: {expected_dir}")
    print(f"Expected dir exists: {os.path.exists(expected_dir)}")
    if os.path.exists(expected_dir):
        print(f"Contents of expected dir: {os.listdir(expected_dir)}")
    else:
        # Check MEIPASS root if specific dir not found
        try:
            print(f"Contents of MEIPASS root: {os.listdir(sys._MEIPASS)}")
        except FileNotFoundError:
            print("MEIPASS root not found or inaccessible.")
else:
    print("Not running from MEIPASS.")
print("--- End Debugging ---")
# --- END DEBUGGING ---

# Đường dẫn đến thư mục hiện tại
def get_resource_path(relative_path):
    """Lấy đường dẫn tài nguyên, hoạt động cả trong file .py và .exe"""
    try:
        # PyInstaller tạo một thư mục tạm thời và lưu đường dẫn trong _MEIPASS
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, relative_path)
    except Exception as e:
        print(f"Lỗi khi lấy đường dẫn tài nguyên: {str(e)}")
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)

# Đường dẫn đến thư mục hiện tại
current_dir = os.path.dirname(os.path.abspath(__file__))

# Đường dẫn đến thư mục public
public_dir = os.path.join(current_dir, "public")

# Đường dẫn đến thư mục images
images_dir = os.path.join(public_dir, "images")

# Đường dẫn đến file icon
icon_path = get_resource_path(os.path.join("public", "images", "icon.ico"))
# Đường dẫn đến file icon.jpg
icon_jpg_path = get_resource_path(os.path.join("public", "images", "icon.jpg"))

# Màu sắc Windows 95/XP
RETRO_COLORS = {
    "win95_bg": "#D4D0C8",           # Xám cơ bản của Win95
    "win95_btn": "#D4D0C8",          # Nút Win95
    "win95_btn_shadow": "#808080",   # Bóng nút Win95
    "win95_btn_highlight": "#ffffff", # Viền sáng Win95
    "win95_titlebar": "#000080",     # Thanh tiêu đề xanh đậm Win95
    "win95_titlebar_text": "#ffffff", # Chữ thanh tiêu đề Win95
    "win95_menu": "#D4D0C8",         # Menu Win95
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

class TextRedirector:
    """Lớp chuyển hướng đầu ra văn bản"""
    def __init__(self, text_widget, tag=""):
        self.text_widget = text_widget
        self.tag = tag
        self.buffer = ""

    def write(self, string):
        self.buffer += string
        if "\n" in self.buffer:
            lines = self.buffer.split("\n")
            self.buffer = lines[-1]
            for line in lines[:-1]:
                self.text_widget.config(state=tk.NORMAL)
                self.text_widget.insert(tk.END, line + "\n", self.tag)
                self.text_widget.see(tk.END)
                self.text_widget.config(state=tk.DISABLED)

    def flush(self):
        if self.buffer:
            self.text_widget.config(state=tk.NORMAL)
            self.text_widget.insert(tk.END, self.buffer, self.tag)
            self.text_widget.see(tk.END)
            self.text_widget.config(state=tk.DISABLED)
            self.buffer = ""

class LappyLabGUI:
    """Lớp giao diện người dùng Lappy Lab"""
    def __init__(self, root):
        self.root = root
        self.config = get_config()

        # Thiết lập cửa sổ
        self.root.title("Lappy Lab 4.0")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)

        # Thiết lập màu nền cơ bản của Windows 95
        self.root.configure(bg=RETRO_COLORS["win95_bg"])

        # --- DEBUGGING ICON PATH ---
        print(f"--- Checking Icon Path for iconbitmap ---")
        print(f"Calculated icon_path: {icon_path}")
        print(f"icon_path exists: {os.path.exists(icon_path)}")
        # --- END DEBUGGING ---

        # Thiết lập icon
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
                print("Successfully called iconbitmap.")
            except Exception as e:
                print(f"Error calling iconbitmap: {e}")
        else:
            print("Icon path does not exist, skipping iconbitmap.")

        # Tạo giao diện
        self.create_widgets()

        # Kiểm tra quyền admin
        if platform.system() == "Windows" and not is_admin():
            messagebox.showwarning(
                "Cảnh báo",
                "Ứng dụng không chạy với quyền admin. Một số chức năng có thể không hoạt động đúng."
            )

    def create_widgets(self):
        """Tạo các widget cho giao diện"""
        # Frame chính - với kiểu Windows 95
        self.main_frame = tk.Frame(self.root, bg=RETRO_COLORS["win95_bg"], relief=tk.RAISED, bd=2)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # Frame header - kiểu Windows 95 với thanh tiêu đề xanh đậm
        self.header_frame = tk.Frame(self.main_frame, bg=RETRO_COLORS["win95_titlebar"], height=60, relief=tk.RAISED, bd=1)
        self.header_frame.pack(fill=tk.X, side=tk.TOP)

        # Frame cho logo và tiêu đề
        self.logo_frame = tk.Frame(self.header_frame, bg=RETRO_COLORS["win95_titlebar"], padx=10, pady=10)
        self.logo_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Tạo icon cho logo
        try:
            # --- DEBUGGING LOGO PATHS ---
            print(f"--- Checking Icon Paths for Logo ---")
            print(f"Calculated icon_jpg_path: {icon_jpg_path}")
            print(f"icon_jpg_path exists: {os.path.exists(icon_jpg_path)}")
            print(f"Calculated icon_path (for logo fallback): {icon_path}")
            print(f"icon_path exists (for logo fallback): {os.path.exists(icon_path)}")
            print(f"Has icon_base64 module: {HAS_ICON_BASE64}")
            # --- END DEBUGGING ---

            icon_loaded = False

            # Thử sử dụng icon từ base64 nếu có
            if HAS_ICON_BASE64:
                try:
                    print("Attempting to use icon from base64...")
                    # Lấy dữ liệu base64
                    icon_data = get_icon_data()
                    # Giải mã base64
                    icon_bytes = base64.b64decode(icon_data)
                    # Tạo ảnh từ dữ liệu nhị phân
                    icon_image = Image.open(io.BytesIO(icon_bytes))
                    print("Successfully opened icon from base64 data.")
                    # Thay đổi kích thước ảnh
                    icon_image = icon_image.resize((24, 24), Image.LANCZOS)
                    # Chuyển đổi sang định dạng PhotoImage
                    icon_photo = ImageTk.PhotoImage(icon_image)

                    # Tạo label với ảnh icon
                    self.logo_label = tk.Label(
                        self.logo_frame,
                        image=icon_photo,
                        bg=RETRO_COLORS["win95_titlebar"]
                    )
                    # Lưu tham chiếu đến ảnh để tránh bị thu hồi bởi garbage collector
                    self.logo_label.image = icon_photo
                    icon_loaded = True
                    print("Successfully loaded icon from base64!")
                except Exception as e:
                    print(f"Error loading icon from base64: {str(e)}")

            # Nếu không thể sử dụng base64, thử sử dụng file icon.jpg
            if not icon_loaded and os.path.exists(icon_jpg_path):
                print(f"Attempting to use icon.jpg at: {icon_jpg_path}")
                # Tạo ảnh từ file icon.jpg
                icon_image = Image.open(icon_jpg_path)
                print("Successfully opened icon.jpg with PIL.")
                # Thay đổi kích thước ảnh
                icon_image = icon_image.resize((24, 24), Image.LANCZOS)
                # Chuyển đổi sang định dạng PhotoImage
                icon_photo = ImageTk.PhotoImage(icon_image)

                # Tạo label với ảnh icon
                self.logo_label = tk.Label(
                    self.logo_frame,
                    image=icon_photo,
                    bg=RETRO_COLORS["win95_titlebar"]
                )
                # Lưu tham chiếu đến ảnh để tránh bị thu hồi bởi garbage collector
                self.logo_label.image = icon_photo
                icon_loaded = True

            # Nếu không có icon.jpg, kiểm tra xem file icon.ico có tồn tại không
            if not icon_loaded and os.path.exists(icon_path):
                print(f"Attempting to use icon.ico at: {icon_path}")
                # Tạo ảnh từ file icon
                icon_image = Image.open(icon_path)
                print("Successfully opened icon.ico with PIL.")
                # Thay đổi kích thước ảnh
                icon_image = icon_image.resize((24, 24), Image.LANCZOS)
                # Chuyển đổi sang định dạng PhotoImage
                icon_photo = ImageTk.PhotoImage(icon_image)

                # Tạo label với ảnh icon
                self.logo_label = tk.Label(
                    self.logo_frame,
                    image=icon_photo,
                    bg=RETRO_COLORS["win95_titlebar"]
                )
                # Lưu tham chiếu đến ảnh để tránh bị thu hồi bởi garbage collector
                self.logo_label.image = icon_photo
                icon_loaded = True

            # Nếu vẫn chưa tìm thấy icon, thử tìm kiếm ở các vị trí khác
            if not icon_loaded:
                print(f"Không tìm thấy icon tại: {icon_path} hoặc {icon_jpg_path}")
                # Thử tìm kiếm icon ở các vị trí khác
                alt_paths = [
                    os.path.join(current_dir, "public", "images", "icon.jpg"),
                    os.path.join(current_dir, "public", "images", "icon.ico"),
                    os.path.join(os.path.dirname(sys.executable), "public", "images", "icon.jpg"),
                    os.path.join(os.path.dirname(sys.executable), "public", "images", "icon.ico"),
                    "public\\images\\icon.jpg",
                    "public\\images\\icon.ico",
                    "icon.jpg",
                    "icon.ico"
                ]

                for alt_path in alt_paths:
                    print(f"Thử tìm icon tại: {alt_path}")
                    if os.path.exists(alt_path):
                        print(f"Tìm thấy icon tại vị trí thay thế: {alt_path}")
                        icon_image = Image.open(alt_path)
                        icon_image = icon_image.resize((24, 24), Image.LANCZOS)
                        icon_photo = ImageTk.PhotoImage(icon_image)

                        self.logo_label = tk.Label(
                            self.logo_frame,
                            image=icon_photo,
                            bg=RETRO_COLORS["win95_titlebar"]
                        )
                        self.logo_label.image = icon_photo
                        icon_loaded = True
                        break

            # Nếu vẫn không tìm thấy icon, sử dụng ký tự thay thế
            if not icon_loaded:
                print("Không tìm thấy icon ở bất kỳ vị trí nào, sử dụng ký tự thay thế")
                self.logo_label = tk.Label(
                    self.logo_frame,
                    text="●",  # Ký tự hình tròn
                    font=("MS Sans Serif", 20, "bold"),  # Font Win95
                    bg=RETRO_COLORS["win95_titlebar"],
                    fg=RETRO_COLORS["win95_titlebar_text"]
                )
        except Exception as e:
            # Nếu có lỗi, sử dụng ký tự thay thế
            print(f"Lỗi khi tạo icon: {str(e)}")
            self.logo_label = tk.Label(
                self.logo_frame,
                text="●",  # Ký tự hình tròn
                font=("MS Sans Serif", 20, "bold"),  # Font Win95
                bg=RETRO_COLORS["win95_titlebar"],
                fg=RETRO_COLORS["win95_titlebar_text"]
            )

        self.logo_label.pack(side=tk.LEFT, padx=(0, 10))

        # Tiêu đề với font kiểu Windows 95
        self.title_label = tk.Label(
            self.logo_frame,
            text="Lappy Lab",
            font=("MS Sans Serif", 16, "bold"),  # Font Win95
            bg=RETRO_COLORS["win95_titlebar"],
            fg=RETRO_COLORS["win95_titlebar_text"]
        )
        self.title_label.pack(side=tk.LEFT)


        # Lấy thông tin hệ thống
        windows_version = get_windows_version()
        computer_name = get_computer_name()

        # Lấy ngày hiện tại
        current_date = datetime.datetime.now().strftime("%b %d, %Y")

        # Frame cho thông tin hệ thống
        self.system_frame = tk.Frame(self.header_frame, bg=RETRO_COLORS["win95_titlebar"], padx=10)
        self.system_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # Thông tin hệ thống (dữ liệu động từ máy tính) - font Win95
        self.system_info = tk.Label(
            self.system_frame,
            text=f"System: {windows_version} | PC: {computer_name}",
            font=("MS Sans Serif", 8),  # Font Win95
            bg=RETRO_COLORS["win95_titlebar"],
            fg=RETRO_COLORS["win95_titlebar_text"]
        )
        self.system_info.pack(side=tk.TOP, anchor="e")

        # Thông tin phiên bản 4.0 và ngày hiện tại - font Win95
        self.version_info = tk.Label(
            self.system_frame,
            text=f"Version 4.0 (Released: {current_date})",
            font=("MS Sans Serif", 8),  # Font Win95
            bg=RETRO_COLORS["win95_titlebar"],
            fg=RETRO_COLORS["win95_titlebar_text"]
        )
        self.version_info.pack(side=tk.TOP, anchor="e")

        # Frame cho thông tin tài khoản - kiểu Windows 95 với viền 3D
        self.account_frame = tk.Frame(
            self.main_frame,
            bg=RETRO_COLORS["win95_bg"],
            padx=5,
            pady=5,
            relief=tk.RIDGE,  # Hiệu ứng 3D kiểu Win95
            bd=2
        )
        self.account_frame.pack(fill=tk.X, side=tk.TOP, padx=10, pady=5)

        # Hiển thị thông tin tài khoản
        display_account_info_frame(self.account_frame)

        # Frame nội dung - Windows 95 style
        self.content_frame = tk.Frame(self.main_frame, bg=RETRO_COLORS["win95_bg"], relief=tk.SUNKEN, bd=1)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Frame nút
        self.button_frame = tk.Frame(self.content_frame, bg=RETRO_COLORS["win95_bg"])
        self.button_frame.pack(fill=tk.X, side=tk.TOP, pady=10)

        # Thiết lập kích thước cột đồng đều
        for col in range(3):
            self.button_frame.columnconfigure(col, weight=1)

        # Các nút chức năng - Win95 style - 2 hàng 3 cột
        self.create_button(
            self.button_frame,
            "Reset Machine ID",
            self.run_reset_machine_id,
            0, 0
        )

        self.create_button(
            self.button_frame,
            "Tắt tự động cập nhật Cursor",
            self.run_disable_auto_update,
            0, 1
        )

        self.create_button(
            self.button_frame,
            "Reset Full Cursor",
            self.run_totally_reset_cursor,
            0, 2
        )

        self.create_button(
            self.button_frame,
            "Bỏ qua kiểm tra phiên bản",
            self.run_bypass_version,
            1, 0
        )

        self.create_button(
            self.button_frame,
            "Hiển thị cấu hình",
            self.run_show_config,
            1, 1
        )

        self.create_button(
            self.button_frame,
            "Bỏ qua giới hạn token",
            self.run_bypass_token_limit,
            1, 2
        )

        # Frame log - Windows 95 style
        self.log_frame = tk.LabelFrame(
            self.content_frame,
            text="Log",
            font=("MS Sans Serif", 8, "bold"),  # Font Win95
            bg=RETRO_COLORS["win95_bg"],
            fg=RETRO_COLORS["win95_text"],
            relief=tk.RIDGE,  # Viền kiểu Windows 95
            bd=2
        )
        self.log_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Vùng log - màu DOS screen - kích thước font lớn hơn
        self.log_text = scrolledtext.ScrolledText(
            self.log_frame,
            font=("Courier New", 10),  # Font DOS - kích thước lớn hơn
            bg="#000080",  # Màu xanh đậm DOS
            fg="#FFFFFF",  # Chữ trắng DOS
            wrap=tk.WORD,
            padx=5,
            pady=5
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.log_text.config(state=tk.DISABLED)

        # Chuyển hướng đầu ra
        self.stdout_redirector = TextRedirector(self.log_text, "stdout")
        self.stderr_redirector = TextRedirector(self.log_text, "stderr")

        # Thiết lập màu cho các tag
        self.log_text.tag_configure("stdout", foreground="#FFFFFF")  # Màu DOS
        self.log_text.tag_configure("stderr", foreground="#FF0000")  # Màu lỗi DOS

        # Frame thông tin tác giả - Windows 95 style
        self.author_frame = tk.Frame(
            self.main_frame,  # Thay đổi: Đặt trong main_frame
            bg=RETRO_COLORS["win95_bg"],
            pady=2 # Giảm padding
        )
        # Pack author_frame trước status_bar
        self.author_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=(0, 2)) # Thêm padx và điều chỉnh pady

        # Thông tin tác giả
        author_info_text = "Tác giả: Nguyên kỷ | Email: Zliveze@gmail.com | Website: https://lappy-lab.vercel.app/"
        self.author_label = tk.Label(
            self.author_frame,
            text=author_info_text,
            font=("MS Sans Serif", 8),  # Font Win95
            bg=RETRO_COLORS["win95_bg"],
            fg=RETRO_COLORS["win95_text"],
            justify=tk.CENTER
        )
        self.author_label.pack()

        # Thanh trạng thái - Windows 95 style
        self.status_bar = tk.Label(
            self.main_frame, # Giữ nguyên trong main_frame
            text="Sẵn sàng",
            bd=1,
            relief=tk.SUNKEN,  # Hiệu ứng 3D kiểu Win95
            anchor=tk.W,
            bg=RETRO_COLORS["win95_bg"],
            fg=RETRO_COLORS["win95_text"],
            padx=2,
            pady=1,
            font=("MS Sans Serif", 8)  # Font Win95
        )
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=2)

    def create_button(self, parent, text, command, row, column):
        """Tạo nút với phong cách Windows 95"""
        button_frame = tk.Frame(
            parent,
            bg=RETRO_COLORS["win95_bg"],
            relief=tk.RAISED,  # Hiệu ứng nút 3D kiểu Win95
            bd=2
        )
        button_frame.grid(row=row, column=column, padx=8, pady=8, sticky="nsew")

        button = tk.Button(
            button_frame,
            text=text,
            font=("MS Sans Serif", 8),  # Font Win95
            bg=RETRO_COLORS["win95_btn"],
            fg=RETRO_COLORS["win95_text"],
            activebackground=RETRO_COLORS["win95_btn"],
            activeforeground=RETRO_COLORS["win95_text"],
            relief=tk.RAISED,  # Hiệu ứng nút Win95
            bd=1,
            padx=5,
            pady=2,
            width=20,  # Giảm độ rộng để vừa 3 cột
            height=2,
            command=command
        )
        button.pack(fill=tk.BOTH, expand=True)

        # Hiệu ứng nhấn nút kiểu Windows 95
        def on_press(event):
            button.config(relief=tk.SUNKEN)

        def on_release(event):
            button.config(relief=tk.RAISED)

        button.bind("<ButtonPress-1>", on_press)
        button.bind("<ButtonRelease-1>", on_release)

        return button

    def update_status(self, text):
        """Cập nhật thanh trạng thái"""
        self.status_bar.config(text=text)
        self.root.update_idletasks()

    def clear_log(self):
        """Xóa log"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)

    def run_in_thread(self, func):
        """Chạy hàm trong một luồng riêng biệt"""
        # Lưu stdout và stderr gốc
        old_stdout = sys.stdout
        old_stderr = sys.stderr

        # Chuyển hướng stdout và stderr
        sys.stdout = self.stdout_redirector
        sys.stderr = self.stderr_redirector

        try:
            # Chạy hàm
            func()
        finally:
            # Khôi phục stdout và stderr
            sys.stdout = old_stdout
            sys.stderr = old_stderr

            # Cập nhật trạng thái
            self.update_status("Sẵn sàng")

    def run_reset_machine_id(self):
        """Chạy chức năng Reset Machine ID"""
        self.clear_log()
        self.update_status("Đang khôi phục Machine ID...")

        def run():
            from reset_machine_id import run
            run()

        threading.Thread(target=lambda: self.run_in_thread(run)).start()

    def run_disable_auto_update(self):
        """Chạy chức năng Disable Cursor Auto-Update"""
        self.clear_log()
        self.update_status("Đang tắt tự động cập nhật Cursor...")

        def run():
            from disable_auto_update import run
            run()

        threading.Thread(target=lambda: self.run_in_thread(run)).start()

    def run_totally_reset_cursor(self):
        """Chạy chức năng Totally Reset Cursor"""
        self.clear_log()
        self.update_status("Đang khôi phục hoàn toàn Cursor...")

        def run():
            from totally_reset_cursor import run
            run()

        threading.Thread(target=lambda: self.run_in_thread(run)).start()

    def run_bypass_version(self):
        """Chạy chức năng Bypass Cursor Version Check"""
        self.clear_log()
        self.update_status("Đang bỏ qua kiểm tra phiên bản Cursor...")

        def run():
            from bypass_version import run
            run()

        threading.Thread(target=lambda: self.run_in_thread(run)).start()

    def run_show_config(self):
        """Chạy chức năng Show Config"""
        self.clear_log()
        self.update_status("Đang hiển thị cấu hình...")

        def run():
            from show_config import run
            run()

        threading.Thread(target=lambda: self.run_in_thread(run)).start()

    def run_bypass_token_limit(self):
        """Chạy chức năng Bypass Token Limit"""
        self.clear_log()
        self.update_status("Đang bỏ qua giới hạn token...")

        def run():
            from bypass_token_limit import run
            run()

        threading.Thread(target=lambda: self.run_in_thread(run)).start()

def run_gui():
    """Chạy giao diện người dùng"""
    root = tk.Tk()
    app = LappyLabGUI(root)
    root.mainloop()

if __name__ == "__main__":
    run_gui()
