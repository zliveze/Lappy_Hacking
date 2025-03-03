import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from app.utils.id_generator import IDGenerator
from app.utils.file_manager import FileManager
from app.utils.message_box import show_message
from app.utils.settings_manager import SettingsManager
from app.utils.version_info_dialog import VersionInfoDialog
import platform
from datetime import datetime
from PIL import Image, ImageTk, ImageDraw
import requests
import re
from packaging import version
import json
import traceback
import winreg
import uuid
import ctypes
from ctypes import windll
import webbrowser
from app.components.advanced_tab import AdvancedTab

class SettingsManager:
    def __init__(self):
        self.settings_file = os.path.join(os.path.expanduser("~"), "lappy_lab_settings.json")
        self.default_settings = {
            "auto_admin": False,
            "auto_update": True,
            "auto_backup": True,
            "confirm_dangerous": True,
            "language": "vi",
            "id_backup_path": os.path.join(os.path.expanduser("~"), "id_backups"),
            "guid_backup_path": os.path.join(os.path.expanduser("~"), "guid_backups"),
            "window_size": "1200x800",
            "font_size": "normal"
        }
        self.settings = self.load_settings()

    def load_settings(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    return {**self.default_settings, **json.load(f)}
            return self.default_settings.copy()
        except Exception:
            return self.default_settings.copy()

    def save_settings(self):
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Lỗi khi lưu cài đặt: {str(e)}")

    def get_setting(self, key, default=None):
        """Lấy giá trị cài đặt với giá trị mặc định tùy chọn"""
        return self.settings.get(key, default or self.default_settings.get(key))

    def set_setting(self, key, value):
        if key in self.default_settings:
            self.settings[key] = value
            self.save_settings()

def check_for_updates():
    """Kiểm tra phiên bản mới từ GitHub"""
    try:
        # Phiên bản hiện tại
        current_version = "3.1.0"
        
        # Lấy thông tin phiên bản mới nhất từ GitHub
        response = requests.get(
            "https://api.github.com/repos/Letandat071/Lappy_Hacking/releases/latest",
            timeout=5
        )
        
        if response.status_code == 200:
            latest_release = response.json()
            latest_tag = latest_release["tag_name"]  # Ví dụ: Lappy_version_2.1.2
            
            # Trích xuất version number từ tag (lấy phần sau cùng: 2.1.2)
            version_match = re.search(r'Lappy_version_(\d+\.\d+\.\d+)$', latest_tag)
            if version_match:
                latest_version = version_match.group(1)
                if version.parse(latest_version) > version.parse(current_version):
                    message = f"Đã có phiên bản mới: {latest_version}\nPhiên bản hiện tại của bạn: {current_version}"
                    if messagebox.askyesno("Cập nhật mới", message + "\n\nBạn có muốn tải phiên bản mới không?"):
                        webbrowser.open(latest_release["html_url"])
                        
    except Exception as e:
        # Log lỗi nhưng không hiển thị cho người dùng
        print(f"Lỗi kiểm tra cập nhật: {str(e)}")

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def is_admin():
    """Kiểm tra quyền admin"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """Chạy lại ứng dụng với quyền admin nếu chưa có"""
    try:
        if sys.argv[-1] != 'asadmin':
            script = os.path.abspath(sys.argv[0])
            params = ' '.join([script] + sys.argv[1:] + ['asadmin'])
            windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
            # Đóng cửa sổ hiện tại
            sys.exit()
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể chạy với quyền admin: {str(e)}")

def get_machine_guid():
    try:
        key_path = r"SOFTWARE\Microsoft\Cryptography"
        # Mở với quyền full access
        registry_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, 
                                    winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
        value, regtype = winreg.QueryValueEx(registry_key, "MachineGuid")
        winreg.CloseKey(registry_key)
        return value
    except WindowsError as e:
        raise Exception(f"Không thể đọc MachineGuid: {str(e)}")

def set_machine_guid(new_guid):
    try:
        key_path = r"SOFTWARE\Microsoft\Cryptography"
        # Mở với quyền full access
        registry_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0,
                                    winreg.KEY_SET_VALUE | winreg.KEY_WOW64_64KEY)
        winreg.SetValueEx(registry_key, "MachineGuid", 0, winreg.REG_SZ, new_guid)
        winreg.CloseKey(registry_key)
    except WindowsError as e:
        raise Exception(f"Không thể cập nhật MachineGuid: {str(e)}")

class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Lappy Lab")
        
        # Initialize settings manager
        self.settings_manager = SettingsManager()
        
        # Áp dụng window size từ settings
        window_size = self.settings_manager.get_setting("window_size", "1200x800")
        self.geometry(window_size)
        self.minsize(1200, 800)
        self.configure(bg='#D4D0C8')
        
        # Cache cho icons để tránh load lại nhiều lần
        self._icon_cache = {}
        
        # Setup style ngay từ đầu
        self._setup_styles()
        
        # Load icons một lần duy nhất
        self._load_icons()
        
        # Initialize backend
        self.id_generator = IDGenerator()
        self.file_manager = FileManager()
        self.current_ids = None
        self.last_generated = None
        
        # Thêm biến để lưu trữ backup MachineGuid
        self.machine_guid_backup = None
        
        self.setup_ui()
        self.center_window()
        
        # Hiển thị thông báo phiên bản nếu được cấu hình
        if self.settings_manager.get_setting("show_version_info"):
            self.after(1000, lambda: VersionInfoDialog(self, self.settings_manager))
        
        # Kiểm tra cập nhật sau khi UI đã load
        self.after(2000, check_for_updates)
        
    def _setup_styles(self):
        """Setup styles một lần duy nhất khi khởi tạo"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Windows 95/XP colors
        bg_color = '#D4D0C8'
        button_bg = '#D4D0C8'
        button_pressed = '#808080'
        
        # Font families theo thứ tự ưu tiên
        default_font = ("Tahoma", "Arial", "MS Sans Serif")
        monospace_font = ("Consolas", "Courier New", "Courier")
        
        # Cấu hình styles cơ bản
        self.style.configure(".", 
                           background=bg_color,
                           font=(default_font[0], 10))
        
        self.style.configure("TFrame", background=bg_color)
        self.style.configure("TLabel", background=bg_color)
        self.style.configure("TLabelframe", background=bg_color)
        self.style.configure("TLabelframe.Label", background=bg_color)
        
        # Button style
        self.style.configure("TButton",
                           background=button_bg,
                           relief="raised",
                           font=(default_font[0], 10))
        self.style.map("TButton",
                      background=[('pressed', button_pressed),
                                ('active', button_bg)])
        
        # Notebook style
        self.style.configure("TNotebook", background=bg_color)
        self.style.configure("TNotebook.Tab", 
                           background=button_bg,
                           padding=[10, 2],
                           font=(default_font[0], 10))
        
        # Custom styles
        custom_styles = {
            "Title.TLabel": {
                "font": (default_font[0], 26, "bold"),
                "foreground": "#000080"  # Navy blue - Windows XP style
            },
            "Header.TLabel": {
                "font": (default_font[0], 16, "bold"),
                "foreground": "#003366"  # Dark blue
            },
            "Info.TLabel": {
                "font": (default_font[0], 10)
            },
            "ID.TLabel": {
                "font": (monospace_font[0], 11),
                "foreground": "#0066CC"  # Bright blue
            },
            "Action.TButton": {
                "font": (default_font[0], 10)
            },
            "Error.TLabel": {
                "font": (default_font[0], 10),
                "foreground": "#CC0000"  # Dark red
            },
            "Link.TLabel": {
                "font": (default_font[0], 10, "underline"),
                "foreground": "#0066CC"  # Bright blue
            },
            "Description.TLabel": {
                "font": (default_font[0], 10),
                "wraplength": 700,
                "justify": "left"
            },
            "Bold.TLabel": {
                "font": (default_font[0], 10, "bold")
            },
            "Status.TLabel": {
                "font": (default_font[0], 10)
            },
            "Warning.TLabel": {
                "font": (default_font[0], 10),
                "foreground": "#FF6600"  # Orange
            },
            "Subtitle.TLabel": {
                "font": (default_font[0], 10),
                "foreground": "#666666"  # Gray
            },
            "Green.TButton": {
                "font": (default_font[0], 10),
                "foreground": "white"
            },
            "Red.TButton": {
                "font": (default_font[0], 10),
                "foreground": "white"
            },
            "Blue.TButton": {
                "font": (default_font[0], 10),
                "foreground": "white"
            }
        }
        
        for style_name, config in custom_styles.items():
            self.style.configure(style_name, background=bg_color, **config)
        
        # Thêm style cho các nút màu với tone nhạt hơn
        self.style.configure("Green.TButton",
            background="#90EE90",  # Light green
            foreground="black",
            padding=5,
            font=("Segoe UI", 10)
        )
        
        self.style.configure("Red.TButton",
            background="#FFB6C1",  # Light red
            foreground="black", 
            padding=5,
            font=("Segoe UI", 10)
        )
        
        self.style.configure("Blue.TButton",
            background="#87CEEB",  # Light blue
            foreground="black",
            padding=5,
            font=("Segoe UI", 10)
        )
        
        # Thêm map cho hiệu ứng hover với màu đậm hơn một chút
        self.style.map("Green.TButton",
            background=[("active", "#7CCD7C")],  # Slightly darker when hover
            foreground=[("active", "black")]
        )
        
        self.style.map("Red.TButton",
            background=[("active", "#FF9999")],
            foreground=[("active", "black")]
        )
        
        self.style.map("Blue.TButton",
            background=[("active", "#79B4D2")],
            foreground=[("active", "black")]
        )

    def _load_icons(self):
        """Load tất cả icons một lần và cache lại"""
        try:
            # Sửa lại cách lấy đường dẫn
            if getattr(sys, 'frozen', False):
                # Nếu đang chạy từ file exe
                current_dir = sys._MEIPASS
            else:
                # Nếu đang chạy từ source
                current_dir = os.path.dirname(os.path.abspath(__file__))
            
            icon_paths = {
                "app": os.path.join(current_dir, "public", "image", "icon.jpg"),
                "cursor": os.path.join(current_dir, "public", "image", "cursor-icon.jpg"),
                "windsurf": os.path.join(current_dir, "public", "image", "windsurf-icon.png"),
                "aide": os.path.join(current_dir, "public", "image", "aide.png")
            }
            
            # Load app icon
            app_icon = Image.open(icon_paths["app"])
            self.iconphoto(True, ImageTk.PhotoImage(app_icon))
            
            # Load và cache các icon khác
            icon_size = (24, 24)
            for name, path in icon_paths.items():
                if name != "app":
                    img = Image.open(path)
                    img = img.resize(icon_size, Image.Resampling.LANCZOS)
                    self._icon_cache[name] = ImageTk.PhotoImage(img)
                    
        except Exception as e:
            print(f"Error loading icons: {e}")
            # Thêm traceback để debug
            print(traceback.format_exc())

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        
    def setup_ui(self):
        # Main container with padding
        main_container = ttk.Frame(self, padding="20")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Header Section with title and logo
        header_frame = ttk.Frame(main_container)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Left side of header with logo and title
        left_header = ttk.Frame(header_frame)
        left_header.pack(side=tk.LEFT)
        
        # Create and add round logo
        try:
            logo_size = (40, 40)
            round_logo = self.create_round_image("public/image/icon.jpg", logo_size)
            logo_label = ttk.Label(left_header, image=round_logo)
            logo_label.image = round_logo  # Keep a reference
            logo_label.pack(side=tk.LEFT, padx=(0, 15))
        except Exception as e:
            print(f"Error loading logo: {e}")
        
        # Title with modern font
        title_label = ttk.Label(left_header, text="Lappy Lab", style="Title.TLabel")
        title_label.pack(side=tk.LEFT)
        
        # System info and version on the right
        info_frame = ttk.Frame(header_frame)
        info_frame.pack(side=tk.RIGHT)
        
        # Get system information
        system_info = self.get_system_info()
        version_info = "Version 3.1.0 (Released: Mar 03, 2025)"
        
        # Add modern styling to system info
        ttk.Label(info_frame, text=system_info, style="Subtitle.TLabel").pack(anchor="e", pady=(0, 2))
        ttk.Label(info_frame, text=version_info, style="Subtitle.TLabel").pack(anchor="e")
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_container)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Main tab with more padding
        main_tab = ttk.Frame(notebook, padding="10")
        notebook.add(main_tab, text="ID Generator")
        
        # Add Advanced tab
        advanced_tab = AdvancedTab(notebook)
        notebook.add(advanced_tab, text="Advanced")
        
        # Settings tab 
        settings_tab = ttk.Frame(notebook, padding="10")
        notebook.add(settings_tab, text="Settings")
        
        # Setup all tabs
        self.setup_main_tab(main_tab)
        self.setup_settings_tab(settings_tab)
        
        # Status Bar with more spacing
        status_frame = ttk.Frame(main_container)
        status_frame.pack(fill=tk.X, pady=(20, 0))
        
        self.status_label = ttk.Label(status_frame, text="Ready", style="Info.TLabel")
        self.status_label.pack(side=tk.LEFT)
        
        self.timestamp_label = ttk.Label(status_frame, text="", style="Info.TLabel")
        self.timestamp_label.pack(side=tk.RIGHT)
        
    def get_system_info(self):
        """Get detailed system information"""
        try:
            # Get OS name and version
            if platform.system() == "Windows":
                os_name = platform.win32_ver()[0]  # e.g., "10", "11"
                os_version = platform.win32_edition() if hasattr(platform, 'win32_edition') else ""
                os_info = f"Windows {os_name} {os_version}".strip()
            elif platform.system() == "Darwin":
                os_version = platform.mac_ver()[0]
                os_info = f"macOS {os_version}"
            else:
                os_info = f"Linux {platform.release()}"
            
            # Get computer name
            if platform.system() == "Windows":
                computer_name = os.environ.get('COMPUTERNAME', 'Unknown')
            else:
                computer_name = os.uname().nodename
                
            return f"System: {os_info} | PC: {computer_name}"
            
        except Exception:
            return "System: Unknown"
    
    def setup_main_tab(self, parent):
        # Main content with better spacing
        main_content = ttk.Frame(parent)
        main_content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Quick Actions Panel
        quick_actions = ttk.LabelFrame(main_content, text="Thao tác nhanh", padding="10")
        quick_actions.pack(fill=tk.X, pady=(0, 15))
        
        # Quick actions buttons with icons - Left side
        actions_left = ttk.Frame(quick_actions)
        actions_left.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Quick fix button
        quick_fix_btn = ttk.Button(actions_left, 
                                text="⚡ Sửa lỗi nhanh",
                                command=self.quick_fix,
                                style="Action.TButton", 
                                width=20)
        quick_fix_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(actions_left, 
                text="→",
                style="Bold.TLabel").pack(side=tk.LEFT, padx=5)
        
        ttk.Label(actions_left, 
                text="Tự động tạo và lưu ID mới",
                style="Info.TLabel").pack(side=tk.LEFT, padx=5)
        
        # Status information - Right side
        status_right = ttk.Frame(quick_actions)
        status_right.pack(side=tk.RIGHT, fill=tk.Y)
        
        # App status
        app_status = ttk.Frame(status_right)
        app_status.pack(fill=tk.X, pady=2)
        ttk.Label(app_status, 
                text="🎯 Ứng dụng: ",
                style="Bold.TLabel").pack(side=tk.LEFT)
        self.app_status_label = ttk.Label(app_status,
                                      text="Cursor",
                                      style="Info.TLabel")
        self.app_status_label.pack(side=tk.LEFT)
        
        # ID status
        id_status = ttk.Frame(status_right)
        id_status.pack(fill=tk.X, pady=2)
        ttk.Label(id_status,
                text="💫 Trạng thái: ",
                style="Bold.TLabel").pack(side=tk.LEFT)
        self.quick_status_label = ttk.Label(id_status,
                                        text="Chưa tạo ID",
                                        style="Info.TLabel")
        self.quick_status_label.pack(side=tk.LEFT)
        
        # Left Panel - Controls (narrower)
        left_panel = ttk.LabelFrame(main_content, text="Bảng điều khiển", padding="15")
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        
        # Application Selection with modern styling
        select_frame = ttk.LabelFrame(left_panel, text="Chọn ứng dụng", padding="10")
        select_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.app_var = tk.StringVar(value="Cursor")
        
        # Radio buttons with icons and better spacing
        for app, icon in [("Cursor", self._icon_cache["cursor"]), ("Windsurf", self._icon_cache["windsurf"]), ("AIDE", self._icon_cache["aide"])]:
            app_frame = ttk.Frame(select_frame)
            app_frame.pack(fill=tk.X, pady=5)
            
            rb = ttk.Radiobutton(app_frame, text=app, value=app,
                               variable=self.app_var, command=self.on_app_change,
                               width=15)
            rb.pack(side=tk.LEFT)
            
            icon_label = tk.Label(app_frame, image=icon, bg='#f0f0f0')
            icon_label.pack(side=tk.LEFT)
        
        # Action Buttons with icons - Changed order as requested
        actions = [
            ("💫 Tạo ID mới", self.generate_ids),
            ("💾 Lưu ID", self.save_ids),
            ("📖 Đọc ID hiện tại", self.read_current_ids),
            ("📦 Tạo Backup", self.create_backup)
        ]
        
        for text, command in actions:
            btn = ttk.Button(left_panel, text=text, command=command,
                           style="Action.TButton", width=20)
            btn.pack(fill=tk.X, pady=5)
        
        # Right Panel - ID Information with card view
        right_panel = ttk.LabelFrame(main_content, text="Thông tin ID", padding="10")
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5,0))
        
        # Status indicator với style mới
        status_frame = ttk.Frame(right_panel)
        status_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.status_indicator = ttk.Label(status_frame, text="⭕ Chưa tạo ID",
                               style="Status.TLabel")
        self.status_indicator.pack(side=tk.LEFT)
        
        # Grid layout cho các ID cards
        grid_frame = ttk.Frame(right_panel)
        grid_frame.pack(fill=tk.BOTH, expand=True, padx=5)
        grid_frame.grid_columnconfigure(0, weight=1)
        
        # Cập nhật style cho các thành phần
        self.style.configure('TLabelframe', background='#D4D0C8')
        self.style.configure('TLabelframe.Label', background='#D4D0C8')
        self.style.configure('TFrame', background='#D4D0C8')
        self.style.configure('Card.TFrame', 
            background='#D4D0C8',
            relief='groove',  # Thêm viền dạng groove
            borderwidth=2     # Độ dày viền
        )

        # Cập nhật style cho labels
        self.style.configure('Bold.TLabel', 
            background='#D4D0C8',
            font=('Segoe UI', 9, 'bold')
        )
        self.style.configure('ID.TLabel', 
            background='#D4D0C8',
            font=('Consolas', 9),
            width=40,  # Cố định chiều rộng
            anchor='w'  # Căn lề trái
        )

        # Tiếp tục phần code hiện tại với id_types và vòng lặp...
        id_types = {
            "Machine ID": ("🔷 telemetry.machineId", "telemetry.machineId"),
            "SQM ID": ("🔶 telemetry.sqmId", "telemetry.sqmId"),
            "Device ID": ("🔴 telemetry.devDeviceId", "telemetry.devDeviceId"),
            "MAC Machine ID": ("🔵 telemetry.macMachineId", "telemetry.macMachineId")
        }

        self.id_labels = {}
        for idx, (label_text, (display_text, key)) in enumerate(id_types.items()):
            # Card frame với style cố định
            card_frame = ttk.Frame(grid_frame, style='Card.TFrame')
            card_frame.grid(row=idx, column=0, pady=3, sticky="ew")
            card_frame.grid_columnconfigure(1, weight=1)
            
            # Title với icon (cột 0)
            title_label = ttk.Label(card_frame, text=display_text,
                                  style="Bold.TLabel",
                                  width=20)  # Cố định chiều rộng title
            title_label.grid(row=0, column=0, padx=(5,0), pady=5)
            
            # ID value với monospace font và kích thước cố định (cột 1)
            id_frame = ttk.Frame(card_frame)
            id_frame.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
            id_frame.grid_columnconfigure(0, weight=1)
            
            id_label = ttk.Label(id_frame, text="Not generated",
                               style="ID.TLabel")
            id_label.grid(row=0, column=0, sticky="ew")
            self.id_labels[key] = id_label
            
            # Copy button (cột 2)
            copy_btn = ttk.Button(card_frame, text="📋",
                                command=lambda k=key: self.copy_to_clipboard(k),
                                style="Action.TButton", width=3)
            copy_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # Add separator before guide
        ttk.Separator(right_panel, orient="horizontal").pack(fill=tk.X, pady=15)
        
        # User Guide Section
        guide_frame = ttk.LabelFrame(right_panel, text="Hướng dẫn sử dụng", padding="15")
        guide_frame.pack(fill=tk.X, pady=(0, 10))
        
        guide_text = """🎯 Để sửa lỗi "Too many trial account on this machine":
- Bước 1: Dọn dẹp dữ liệu tại "Dọn Dẹp"
- Bước 2: Tạo ID mới tại "Bảng điều khiển"
- Bước 3: Lưu ID mới tại "Bảng điều khiển"

📌 Các thao tác khác:
• Xem ID hiện tại: Click "Đọc ID hiện tại"
• Sao lưu ID: Click "Tạo Backup"

💡 Tip: Click vào nút Copy bên cạnh mỗi ID để sao chép"""

        guide_label = ttk.Label(guide_frame, text=guide_text,
                              style="Description.TLabel",
                              justify="left",
                              wraplength=500,
                              font=("Segoe UI", 10))  # Increased wraplength for better readability
        guide_label.pack(fill=tk.X, pady=5)

    def setup_settings_tab(self, parent):
        # Create scrollable frame for settings content
        canvas = tk.Canvas(parent, bg='#f0f0f0')
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        # Make the scrollable frame expand to canvas width
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        # Create window inside canvas
        canvas_frame = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=canvas.winfo_width())
        
        # Update canvas window when canvas is resized
        def configure_canvas(event):
            canvas.itemconfig(canvas_frame, width=event.width)
        canvas.bind('<Configure>', configure_canvas)

        # Configure mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Bind mouse enter/leave to activate/deactivate scrolling
        def _bind_mousewheel(event): canvas.bind_all("<MouseWheel>", _on_mousewheel)
        def _unbind_mousewheel(event): canvas.unbind_all("<MouseWheel>")
        
        canvas.bind('<Enter>', _bind_mousewheel)
        canvas.bind('<Leave>', _unbind_mousewheel)

        # Pack the scrollbar and canvas
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Main settings container
        settings_frame = ttk.Frame(scrollable_frame)
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=50)

        # Application Settings Section
        app_settings_frame = ttk.LabelFrame(settings_frame, text="Application Settings", padding="15")
        app_settings_frame.pack(fill=tk.X, pady=(0, 20))

        # General Settings
        general_frame = ttk.Frame(app_settings_frame)
        general_frame.pack(fill=tk.X, pady=5)

        # Auto-start with admin rights
        self.auto_admin_var = tk.BooleanVar(value=self.settings_manager.get_setting("auto_admin", True))
        ttk.Checkbutton(general_frame, 
                       text="Tự động chạy với quyền Admin",
                       variable=self.auto_admin_var,
                       command=lambda: self.settings_manager.set_setting("auto_admin", self.auto_admin_var.get())
                       ).pack(anchor=tk.W, pady=2)

        # Auto-check for updates
        self.auto_update_var = tk.BooleanVar(value=self.settings_manager.get_setting("auto_update_check", True))
        ttk.Checkbutton(general_frame,
                       text="Tự động kiểm tra cập nhật khi khởi động",
                       variable=self.auto_update_var,
                       command=lambda: self.settings_manager.set_setting("auto_update_check", self.auto_update_var.get())
                       ).pack(anchor=tk.W, pady=2)

        # Auto-backup before changes
        self.auto_backup_var = tk.BooleanVar(value=self.settings_manager.get_setting("auto_backup", True))
        ttk.Checkbutton(general_frame,
                       text="Tự động sao lưu trước khi thay đổi",
                       variable=self.auto_backup_var,
                       command=lambda: self.settings_manager.set_setting("auto_backup", self.auto_backup_var.get())
                       ).pack(anchor=tk.W, pady=2)

        # Confirm dangerous operations
        self.confirm_dangerous_var = tk.BooleanVar(value=self.settings_manager.get_setting("confirm_dangerous", True))
        ttk.Checkbutton(general_frame,
                       text="Xác nhận trước khi thực hiện thao tác nguy hiểm",
                       variable=self.confirm_dangerous_var,
                       command=lambda: self.settings_manager.set_setting("confirm_dangerous", self.confirm_dangerous_var.get())
                       ).pack(anchor=tk.W, pady=2)

        # Backup Settings
        backup_frame = ttk.LabelFrame(app_settings_frame, text="Backup Settings", padding="10")
        backup_frame.pack(fill=tk.X, pady=10)

        # ID Backup Path
        id_backup_frame = ttk.Frame(backup_frame)
        id_backup_frame.pack(fill=tk.X, pady=5)
        ttk.Label(id_backup_frame, text="ID Backup Path:").pack(side=tk.LEFT)
        self.id_backup_path_var = tk.StringVar(value=self.settings_manager.get_setting("id_backup_path", ""))
        ttk.Entry(id_backup_frame, textvariable=self.id_backup_path_var, width=50).pack(side=tk.LEFT, padx=5)
        ttk.Button(id_backup_frame, text="Browse",
                  command=lambda: self.browse_backup_path("id")).pack(side=tk.LEFT)

        # GUID Backup Path
        guid_backup_frame = ttk.Frame(backup_frame)
        guid_backup_frame.pack(fill=tk.X, pady=5)
        ttk.Label(guid_backup_frame, text="GUID Backup Path:").pack(side=tk.LEFT)
        self.guid_backup_path_var = tk.StringVar(value=self.settings_manager.get_setting("guid_backup_path", ""))
        ttk.Entry(guid_backup_frame, textvariable=self.guid_backup_path_var, width=50).pack(side=tk.LEFT, padx=5)
        ttk.Button(guid_backup_frame, text="Browse",
                  command=lambda: self.browse_backup_path("guid")).pack(side=tk.LEFT)

        # UI Settings
        ui_frame = ttk.LabelFrame(app_settings_frame, text="UI Settings", padding="10")
        ui_frame.pack(fill=tk.X, pady=10)

        # Window Size
        size_frame = ttk.Frame(ui_frame)
        size_frame.pack(fill=tk.X, pady=5)
        ttk.Label(size_frame, text="Default Window Size:").pack(side=tk.LEFT, padx=(0, 10))
        self.window_size_var = tk.StringVar(value=self.settings_manager.get_setting("window_size", "1200x800"))
        size_combo = ttk.Combobox(size_frame,
                                textvariable=self.window_size_var,
                                values=["1200x800", "1024x768", "1366x768", "1440x900", "1920x1080"],
                                state="readonly",
                                width=15)
        size_combo.pack(side=tk.LEFT)
        size_combo.bind('<<ComboboxSelected>>',
                       lambda e: self.apply_window_size(self.window_size_var.get()))

        # Font Settings
        font_frame = ttk.Frame(ui_frame)
        font_frame.pack(fill=tk.X, pady=5)
        ttk.Label(font_frame, text="Font Size:").pack(side=tk.LEFT, padx=(0, 10))
        self.font_size_var = tk.StringVar(value=self.settings_manager.get_setting("font_size", "10"))
        font_combo = ttk.Combobox(font_frame,
                                textvariable=self.font_size_var,
                                values=["8", "9", "10", "11", "12", "14"],
                                state="readonly",
                                width=15)
        font_combo.pack(side=tk.LEFT)
        font_combo.bind('<<ComboboxSelected>>',
                       lambda e: self.apply_font_size(self.font_size_var.get()))
        
        # Registry Editor Section
        registry_frame = ttk.LabelFrame(settings_frame, text="Registry Editor", padding="10")
        registry_frame.pack(fill=tk.X, pady=(0, 10))

        # Registry Path Entry
        reg_path_frame = ttk.Frame(registry_frame)
        reg_path_frame.pack(fill=tk.X, pady=5)
        ttk.Label(reg_path_frame, text="Registry Path:").pack(side=tk.LEFT)
        self.reg_path_var = tk.StringVar(value=r"SOFTWARE\Microsoft\Cryptography")
        reg_path_entry = ttk.Entry(reg_path_frame, textvariable=self.reg_path_var, width=50)
        reg_path_entry.pack(side=tk.LEFT, padx=5)

        # Registry Value Entry
        reg_value_frame = ttk.Frame(registry_frame)
        reg_value_frame.pack(fill=tk.X, pady=5)
        ttk.Label(reg_value_frame, text="Value Name:").pack(side=tk.LEFT)
        self.reg_value_var = tk.StringVar(value="MachineGuid")
        reg_value_entry = ttk.Entry(reg_value_frame, textvariable=self.reg_value_var, width=30)
        reg_value_entry.pack(side=tk.LEFT, padx=5)

        # Registry Buttons
        reg_buttons_frame = ttk.Frame(registry_frame)
        reg_buttons_frame.pack(fill=tk.X, pady=5)
        ttk.Button(reg_buttons_frame, 
                  text="Read Registry", 
                  command=self.read_registry,
                  style="Blue.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(reg_buttons_frame, 
                  text="Edit Registry", 
                  command=self.edit_registry,
                  style="Red.TButton").pack(side=tk.LEFT, padx=5)

        # Storage Paths Section
        paths_frame = ttk.LabelFrame(settings_frame, text="Đường dẫn lưu trữ", padding="20")
        paths_frame.pack(fill=tk.X, pady=(20, 30))
        
        # Cursor Path
        cursor_frame = ttk.Frame(paths_frame)
        cursor_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(cursor_frame, text="Cursor:", width=10).pack(side=tk.LEFT)
        self.cursor_path_var = tk.StringVar(value=self.file_manager.get_storage_path("Cursor"))
        cursor_entry = ttk.Entry(cursor_frame, textvariable=self.cursor_path_var, width=50)
        cursor_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(cursor_frame, text="Browse", 
                  command=lambda: self.browse_folder("Cursor")).pack(side=tk.LEFT)
        
        # Path status for Cursor
        self.cursor_status_var = tk.StringVar()
        ttk.Label(cursor_frame, textvariable=self.cursor_status_var, 
                 foreground="green" if self.file_manager.path_exists("Cursor") else "red").pack(side=tk.LEFT, padx=5)
        
        # Windsurf Path
        windsurf_frame = ttk.Frame(paths_frame)
        windsurf_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(windsurf_frame, text="Windsurf:", width=10).pack(side=tk.LEFT)
        self.windsurf_path_var = tk.StringVar(value=self.file_manager.get_storage_path("Windsurf"))
        windsurf_entry = ttk.Entry(windsurf_frame, textvariable=self.windsurf_path_var, width=50)
        windsurf_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(windsurf_frame, text="Browse", 
                  command=lambda: self.browse_folder("Windsurf")).pack(side=tk.LEFT)
        
        # Path status for Windsurf
        self.windsurf_status_var = tk.StringVar()
        ttk.Label(windsurf_frame, textvariable=self.windsurf_status_var,
                 foreground="green" if self.file_manager.path_exists("Windsurf") else "red").pack(side=tk.LEFT, padx=5)
        
        # AIDE Path
        aide_frame = ttk.Frame(paths_frame)
        aide_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(aide_frame, text="AIDE:", width=10).pack(side=tk.LEFT)
        self.aide_path_var = tk.StringVar(value=self.file_manager.get_storage_path("AIDE"))
        aide_entry = ttk.Entry(aide_frame, textvariable=self.aide_path_var, width=50)
        aide_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(aide_frame, text="Browse", 
                  command=lambda: self.browse_folder("AIDE")).pack(side=tk.LEFT)
        
        # Path status for AIDE
        self.aide_status_var = tk.StringVar()
        ttk.Label(aide_frame, textvariable=self.aide_status_var,
                 foreground="green" if self.file_manager.path_exists("AIDE") else "red").pack(side=tk.LEFT, padx=5)
        
        # Update status indicators
        self.update_path_status()
        
        # About Section
        about_frame = ttk.LabelFrame(settings_frame, text="About Project", padding="20")
        about_frame.pack(fill=tk.X, pady=(0, 30))
        
        # Avatar and Project Title
        header_frame = ttk.Frame(about_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Create round avatar
        avatar_size = (100, 100)
        round_avatar = self.create_round_image("public/image/icon.jpg", avatar_size)
        avatar_label = ttk.Label(header_frame, image=round_avatar)
        avatar_label.image = round_avatar  # Keep a reference
        avatar_label.pack(pady=(0, 10))

        # Developer info frame
        dev_frame = ttk.Frame(header_frame)
        dev_frame.pack(pady=(0, 5))
        
        ttk.Label(dev_frame, 
                 text="Developed by:", 
                 font=("Segoe UI", 11)).pack(side=tk.LEFT, padx=(0, 5))
        
        name_label = ttk.Label(dev_frame, 
                             text="@Nguyenky", 
                             style="Link.TLabel",
                             cursor="hand2")
        name_label.pack(side=tk.LEFT)
        name_label.bind("<Button-1>", lambda e: self.open_website("https://lappy-lab.vercel.app"))

        # Website with modern styling
        web_frame = ttk.Frame(header_frame)
        web_frame.pack(pady=(5, 15))
        
        ttk.Label(web_frame, 
                text="Official website:", 
                font=("Segoe UI", 11)).pack(side=tk.LEFT, padx=(0, 5))
                
        website_label = ttk.Label(web_frame, 
                                text="https://lappy-lab.vercel.app/",
                                style="Link.TLabel",
                                cursor="hand2")
        website_label.pack(side=tk.LEFT)
        website_label.bind("<Button-1>", lambda e: self.open_website("https://lappy-lab.vercel.app/"))
        
        # Separator after profile
        ttk.Separator(about_frame, orient="horizontal").pack(fill=tk.X, pady=20)
        
        # Project description
        description = (
            "Công cụ Chỉnh sửa ID cho Cursor IDE được thiết kế nhằm hỗ trợ người dùng quản lý và "
            "sửa lỗi liên quan đến định danh (ID) trong ứng dụng Cursor IDE. Đây là một giải pháp "
            "đơn giản nhưng hiệu quả, giúp tối ưu hóa trải nghiệm người dùng, đặc biệt khi các "
            "tài khoản Cursor gặp vấn đề về định danh hoặc khi cần cập nhật các ID không hợp lệ.\n\n"
            "Đặc biệt công cụ này giúp giải quyết các lỗi phổ biến như:\n"
            "• You've reached your trial request limit\n"
            "• Too many trail account on this machine\n"
            "--------------------------------------------------------------------------------------\n"
            "#Update Version 3.0\n"
            "• Fix Cursor 0.45 trở lên\n"
            "Lưu ý thận trọng khi sử dụng công cụ này, nếu có vấn đề hãy liên hệ tôi để được hỗ trợ"
            
        )
        desc_label = ttk.Label(about_frame, text=description, wraplength=700, 
                             justify="left", style="Description.TLabel")
        desc_label.pack(pady=10)
        
        # Technology section with icon
        tech_frame = ttk.Frame(about_frame)
        tech_frame.pack(fill=tk.X, pady=10)
        python_icon = "🐍"  # Python icon
        ttk.Label(tech_frame, text=python_icon, font=("Segoe UI", 24)).pack(side=tk.LEFT, padx=5)
        ttk.Label(tech_frame, text="Python", font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT, padx=5)
        
        # Author section with modern layout
        author_frame = ttk.Frame(about_frame)
        author_frame.pack(fill=tk.X, pady=10)
        
        # Developer info with icon
        dev_frame = ttk.Frame(author_frame)
        dev_frame.pack(side=tk.LEFT, padx=20)
        dev_icon = "👨‍💻"  # Developer icon
        ttk.Label(dev_frame, text=dev_icon, font=("Segoe UI", 11)).pack(side=tk.LEFT, padx=5)
        ttk.Label(dev_frame, text="Developed by", font=("Segoe UI", 11)).pack(side=tk.LEFT, padx=5)
        author_label = ttk.Label(dev_frame, text="@Nguyenky", style="Link.TLabel", cursor="hand2")
        author_label.pack(side=tk.LEFT, padx=5)
        author_label.bind("<Button-1>", lambda e: self.open_website("https://lappy-lab.vercel.app/"))
        
        # Website with icon
        web_frame = ttk.Frame(author_frame)
        web_frame.pack(side=tk.RIGHT, padx=20)
        web_icon = "🌐"  # Website icon
        ttk.Label(web_frame, text=web_icon, font=("Segoe UI", 11)).pack(side=tk.LEFT, padx=5)
        ttk.Label(web_frame, text="Official website:", font=("Segoe UI", 11)).pack(side=tk.LEFT, padx=5)
        website_label = ttk.Label(web_frame, text="https://lappy-lab.vercel.app/",
                                style="Link.TLabel", cursor="hand2")
        website_label.pack(side=tk.LEFT, padx=5)
        website_label.bind("<Button-1>", lambda e: self.open_website("https://lappy-lab.vercel.app/"))
    
    def create_round_image(self, image_path, size):
        # Open and resize image using resource path
        img = Image.open(resource_path(image_path))
        img = img.resize(size, Image.Resampling.LANCZOS)
        
        # Create a round mask
        mask = Image.new('L', size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size[0], size[1]), fill=255)
        
        # Apply mask to create round image
        output = Image.new('RGBA', size, (0, 0, 0, 0))
        output.paste(img, (0, 0))
        output.putalpha(mask)
        
        return ImageTk.PhotoImage(output)

    def browse_folder(self, app_name):
        from tkinter import filedialog
        folder_path = filedialog.askdirectory(title=f"Select storage folder for {app_name}")
        if folder_path:
            self.file_manager.set_custom_path(app_name, folder_path)
            if app_name == "Cursor":
                self.cursor_path_var.set(self.file_manager.get_storage_path(app_name))
            elif app_name == "Windsurf":
                self.windsurf_path_var.set(self.file_manager.get_storage_path(app_name))
            else:
                self.aide_path_var.set(self.file_manager.get_storage_path(app_name))
            self.update_path_status()
    
    def update_path_status(self):
        # Update Cursor status
        cursor_exists = self.file_manager.path_exists("Cursor")
        self.cursor_status_var.set("✓ Found" if cursor_exists else "✗ Not found")
        
        # Update Windsurf status
        windsurf_exists = self.file_manager.path_exists("Windsurf")
        self.windsurf_status_var.set("✓ Found" if windsurf_exists else "✗ Not found")
        
        # Update AIDE status
        aide_exists = self.file_manager.path_exists("AIDE")
        self.aide_status_var.set("✓ Found" if aide_exists else "✗ Not found")
    
    def on_app_change(self):
        self.current_ids = None
        # Update app status label
        self.app_status_label.config(text=self.app_var.get())
        
        # Reset status indicators
        self.status_indicator.config(text="⭕ Chưa tạo ID")
        self.quick_status_label.config(text="Chưa tạo ID")
        
        # Try to read existing IDs when app changes
        try:
            self.file_manager.set_app(self.app_var.get())
            self.read_current_ids()
        except Exception:
            # Reset labels if reading fails
            for label in self.id_labels.values():
                label.config(text="Not generated")
        self.update_status("Application changed - Current IDs loaded if available")

    def generate_ids(self):
        try:
            app_name = self.app_var.get()
            self.current_ids = self.id_generator.generate_ids(app_name)
            self.last_generated = datetime.now()
            
            # Update labels
            for key, label in self.id_labels.items():
                if key in self.current_ids:
                    label.config(text=self.current_ids[key])
                else:
                    label.config(text="N/A")
            
            # Update status indicators
            self.status_indicator.config(text="✅ Đã tạo ID mới")
            self.quick_status_label.config(text="Đã tạo ID mới")
            self.update_status("IDs generated successfully")
            self.update_timestamp()
            
        except Exception as e:
            show_message(self, "Error", str(e), "error")
            self.status_indicator.config(text="❌ Lỗi khi tạo ID")
            self.quick_status_label.config(text="Lỗi khi tạo ID")
            self.update_status("Error generating IDs")
    
    def save_ids(self):
        try:
            if not self.current_ids:
                raise ValueError("Vui lòng tạo ID mới trước khi lưu!")
            
            # Lấy đường dẫn chính xác
            storage_path = self.file_manager.get_storage_path(self.app_var.get())
            print(f"[SAVE] Đang lưu tới: {storage_path}")
            
            # Thực hiện lưu
            if self.file_manager.save_ids(self.current_ids):
                # Xác minh kết quả
                if not os.path.exists(storage_path):
                    raise FileNotFoundError("Không tìm thấy file sau khi lưu")
                
                with open(storage_path, 'r', encoding='utf-8') as f:
                    saved_data = json.load(f)
                
                # Kiểm tra từng ID
                required_keys = [
                    "telemetry.macMachineId",
                    "telemetry.sqmId",
                    "telemetry.machineId",
                    "telemetry.devDeviceId"
                ]
                
                for key in required_keys:
                    if saved_data.get(key) != self.current_ids.get(key):
                        raise ValueError(f"Lỗi xác minh: {key} không khớp")
                
                # Cập nhật UI
                self.status_indicator.config(text="✅ Lưu thành công")
                show_message(self, "Thành công", "Cập nhật ID thành công!", "success")
                
        except Exception as e:
            error_msg = f"LỖI: {str(e)}"
            print(f"[FINAL ERROR] {traceback.format_exc()}")
            show_message(self, "Lỗi nghiêm trọng", error_msg, "error")
    
    def create_backup(self):
        try:
            app_name = self.app_var.get()
            
            # Kiểm tra xem có ID để backup không
            if not self.current_ids:
                # Thử đọc ID hiện tại
                self.read_current_ids()
                if not self.current_ids:
                    raise ValueError("Không có ID nào để backup. Vui lòng tạo hoặc đọc ID trước.")
            
            # Lấy đường dẫn backup từ settings
            backup_path = self.settings_manager.get_setting("id_backup_path")
            if not backup_path:
                backup_path = os.path.join(os.path.expanduser("~"), "id_backups")
            
            # Đảm bảo thư mục tồn tại
            os.makedirs(backup_path, exist_ok=True)
            
            # Tạo tên file backup với timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(backup_path, f"{app_name}_backup_{timestamp}.json")
            
            # Lưu vào file backup
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_ids, f, indent=4, ensure_ascii=False)
            
            # Kiểm tra file backup có dữ liệu không
            if os.path.getsize(backup_file) > 0:
                show_message(self, "Thành công", f"Đã tạo backup tại:\n{backup_file}", "success")
                self.update_status("Tạo backup thành công")
            else:
                raise ValueError("File backup được tạo nhưng không có dữ liệu")
            
        except Exception as e:
            show_message(self, "Lỗi", str(e), "error")
            self.update_status("Lỗi khi tạo backup")
    
    def copy_to_clipboard(self, key):
        if self.current_ids and key in self.current_ids:
            self.clipboard_clear()
            self.clipboard_append(self.current_ids[key])
            self.update_status(f"Copied {key} to clipboard")
    
    def update_status(self, message):
        self.status_label.config(text=message)
    
    def update_timestamp(self):
        if self.last_generated:
            timestamp = self.last_generated.strftime("%Y-%m-%d %H:%M:%S")
            self.timestamp_label.config(text=f"Last Generated: {timestamp}")
    
    def read_current_ids(self):
        try:
            app_name = self.app_var.get()
            storage_path = self.file_manager.get_storage_path(app_name)
            print(f"[DEBUG] Đang đọc từ: {storage_path}")
            
            if not os.path.exists(storage_path):
                raise FileNotFoundError(f"Không tìm thấy file storage.json tại: {storage_path}")
            
            with open(storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Lấy các key cho ứng dụng tương ứng
            required_keys = {
                "telemetry.macMachineId": data.get("telemetry.macMachineId", "Not found"),
                "telemetry.sqmId": data.get("telemetry.sqmId", "Not found"),
                "telemetry.machineId": data.get("telemetry.machineId", "Not found"),
                "telemetry.devDeviceId": data.get("telemetry.devDeviceId", "Not found")
            }
            
            # Kiểm tra dữ liệu
            for key, value in required_keys.items():
                if value == "Not found":
                    raise ValueError(f"Thiếu trường dữ liệu: {key}")
            
            self.current_ids = required_keys
            
            # Cập nhật giao diện
            for key, label in self.id_labels.items():
                label.config(text=self.current_ids[key])
            
            self.status_indicator.config(text="✅ Đã đọc ID hiện tại")
            self.quick_status_label.config(text="Đã đọc ID")
            self.update_status("Current IDs loaded successfully")
            
        except Exception as e:
            print(f"[READ ERROR] Đường dẫn: {storage_path} | Lỗi: {str(e)}")
            show_message(self, "Lỗi", f"Không thể đọc ID: {str(e)}", "error")
            self.status_indicator.config(text="❌ Lỗi đọc ID")
            self.quick_status_label.config(text="Lỗi đọc ID")
    
    def open_website(self, url):
        webbrowser.open(url)
    
    def quick_fix(self):
        """Sửa lỗi nhanh bằng cách tạo và cập nhật tất cả ID"""
        try:
            # Tạo ID mới
            app_name = self.app_var.get()
            self.current_ids = self.id_generator.generate_ids(app_name)
            
            # Kiểm tra đầy đủ các trường
            required_keys = [
                "telemetry.macMachineId",
                "telemetry.sqmId",
                "telemetry.machineId",
                "telemetry.devDeviceId"
            ]
            
            for key in required_keys:
                if key not in self.current_ids:
                    raise ValueError(f"Thiếu trường {key} trong ID mới tạo")
            
            # Lưu vào file
            if self.file_manager.save_ids(self.current_ids):
                # Cập nhật giao diện
                for key, label in self.id_labels.items():
                    label.config(text=self.current_ids[key])
                
                # Cập nhật trạng thái
                self.status_indicator.config(text="✅ Đã sửa lỗi")
                self.quick_status_label.config(text="Đã sửa lỗi")
                show_message(self, "Thành công", "Đã cập nhật tất cả ID!", "success")
                
                # Kiểm tra lại sau khi lưu
                self.verify_saved_ids()
                
        except Exception as e:
            error_msg = f"Lỗi khi sửa nhanh: {str(e)}"
            print(f"[QUICK FIX ERROR] {traceback.format_exc()}")
            show_message(self, "Lỗi", error_msg, "error")
            self.status_indicator.config(text="❌ Lỗi sửa nhanh")
    
    def verify_saved_ids(self):
        """Kiểm tra xem ID đã được lưu đúng chưa"""
        try:
            storage_path = self.file_manager.get_storage_path(self.app_var.get())
            
            with open(storage_path, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)
            
            # Danh sách đầy đủ các key cần kiểm tra
            required_keys = [
                "telemetry.macMachineId",
                "telemetry.sqmId", 
                "telemetry.machineId",
                "telemetry.devDeviceId"
            ]
            
            for key in required_keys:
                if saved_data.get(key) != self.current_ids.get(key):
                    raise ValueError(f"{key} không khớp\nĐã lưu: {saved_data.get(key)}\nMong đợi: {self.current_ids[key]}")
            
            print("[VERIFY] Tất cả ID đã được cập nhật chính xác")
            
        except Exception as e:
            print(f"[VERIFY ERROR] {str(e)}")
            raise
    
    def backup_machine_guid(self):
        try:
            current_guid = get_machine_guid()
            self.machine_guid_backup = current_guid
            
            # Lưu vào file trong thư mục home
            backup_path = os.path.join(os.path.expanduser("~"), "machine_guid_backup.json")
            backup_data = {
                "guid": current_guid,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            with open(backup_path, 'w') as f:
                json.dump(backup_data, f, indent=4)
            
            # Hiển thị thông báo với đường dẫn đầy đủ và hướng dẫn
            message = f"""✅ Đã sao lưu MachineGUID thành công!

📂 File backup được lưu tại:
{backup_path}

⚠️ Lưu ý: Đây là file backup quan trọng, bạn nên:
• Lưu lại đường dẫn này
• Không xóa file backup
• Tạo bản sao để đề phòng mất file"""

            show_message(self, "Sao lưu thành công", message, "success")
            
        except Exception as e:
            show_message(self, "Lỗi", str(e), "error")

    def change_machine_guid(self):
        try:
            # Tạo GUID mới
            new_guid = str(uuid.uuid4())
            
            # Xác nhận từ người dùng
            if messagebox.askyesno("Xác nhận", 
                                 f"Bạn có chắc muốn đổi MachineGuid thành:\n{new_guid}"):
                set_machine_guid(new_guid)
                self.machine_guid_label.config(text=new_guid)
                show_message(self, "Thành công", 
                           f"Đã thay đổi MachineGuid thành:\n{new_guid}", "success")
        
        except Exception as e:
            show_message(self, "Lỗi", str(e), "error")

    def restore_machine_guid(self):
        try:
            # Kiểm tra file backup
            backup_path = os.path.join(os.path.expanduser("~"), "machine_guid_backup.json")
            
            if not os.path.exists(backup_path):
                raise Exception("Không tìm thấy file backup!")
            
            with open(backup_path, 'r') as f:
                backup_data = json.load(f)
            
            old_guid = backup_data["guid"]
            
            # Xác nhận từ người dùng
            if messagebox.askyesno("Xác nhận", 
                                 f"Phục hồi MachineGuid về:\n{old_guid}"):
                set_machine_guid(old_guid)
                self.machine_guid_label.config(text=old_guid)
                show_message(self, "Thành công", 
                           f"Đã phục hồi MachineGuid về:\n{old_guid}", "success")
        
        except Exception as e:
            show_message(self, "Lỗi", str(e), "error")
    
    def run(self):
        self.mainloop()

    def read_registry(self):
        """Đọc giá trị từ registry path được chỉ định"""
        try:
            # Mở registry key
            key_path = self.reg_path_var.get()
            value_name = self.reg_value_var.get()
            
            registry_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0,
                                        winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
            
            # Đọc giá trị
            value, regtype = winreg.QueryValueEx(registry_key, value_name)
            winreg.CloseKey(registry_key)
            
            # Hiển thị kết quả
            show_message(self, "Registry Value", 
                        f"Path: {key_path}\nName: {value_name}\nValue: {value}",
                        "info")
            
        except WindowsError as e:
            show_message(self, "Error", f"Không thể đọc registry: {str(e)}", "error")

    def edit_registry(self):
        """Sửa giá trị trong registry"""
        try:
            # Lấy thông tin từ UI
            key_path = self.reg_path_var.get()
            value_name = self.reg_value_var.get()
            
            # Đọc giá trị hiện tại
            registry_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0,
                                        winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
            current_value, regtype = winreg.QueryValueEx(registry_key, value_name)
            winreg.CloseKey(registry_key)
            
            # Hiển thị dialog để nhập giá trị mới
            new_value = tk.simpledialog.askstring(
                "Edit Registry",
                f"Current value: {current_value}\nEnter new value:",
                initialvalue=current_value
            )
            
            if new_value is not None:  # Nếu người dùng không cancel
                # Xác nhận thay đổi
                if messagebox.askyesno("Confirm",
                                     f"Are you sure you want to change the value to:\n{new_value}"):
                    # Mở registry với quyền write
                    registry_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0,
                                                winreg.KEY_SET_VALUE | winreg.KEY_WOW64_64KEY)
                    winreg.SetValueEx(registry_key, value_name, 0, winreg.REG_SZ, new_value)
                    winreg.CloseKey(registry_key)
                    show_message(self, "Success", "Registry value updated successfully!", "info")
                    
        except WindowsError as e:
            show_message(self, "Error", f"Không thể cập nhật registry: {str(e)}", "error")

    def browse_file(self):
        """Mở dialog chọn file"""
        from tkinter import filedialog
        filename = filedialog.askopenfilename(
            initialdir=self.file_path_var.get(),
            title="Select file",
            filetypes=(("JSON files", "*.json"), ("All files", "*.*"))
        )
        if filename:
            self.file_path_var.set(filename)

    def view_file(self):
        """Xem nội dung file"""
        try:
            file_path = self.file_path_var.get()
            
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File không tồn tại: {file_path}")
                
            # Đọc và hiển thị nội dung file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Tạo dialog để hiển thị nội dung
            dialog = tk.Toplevel(self)
            dialog.title(f"File Content - {os.path.basename(file_path)}")
            dialog.geometry("800x600")
            
            # Thêm text widget với scrollbar
            text_frame = ttk.Frame(dialog)
            text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            scrollbar = ttk.Scrollbar(text_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            text_widget = tk.Text(text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set)
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            scrollbar.config(command=text_widget.yview)
            
            # Insert content
            text_widget.insert(tk.END, content)
            text_widget.config(state=tk.DISABLED)  # Make read-only
            
        except Exception as e:
            show_message(self, "Error", f"Không thể đọc file: {str(e)}", "error")

    def edit_file(self):
        """Sửa nội dung file"""
        try:
            file_path = self.file_path_var.get()
            
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File không tồn tại: {file_path}")
                
            # Đọc nội dung file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Tạo dialog để sửa nội dung
            dialog = tk.Toplevel(self)
            dialog.title(f"Edit File - {os.path.basename(file_path)}")
            dialog.geometry("800x600")
            
            # Thêm text widget với scrollbar
            text_frame = ttk.Frame(dialog)
            text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            scrollbar = ttk.Scrollbar(text_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            text_widget = tk.Text(text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set)
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            scrollbar.config(command=text_widget.yview)
            
            # Insert content
            text_widget.insert(tk.END, content)
            
            # Save button
            def save_changes():
                try:
                    new_content = text_widget.get("1.0", tk.END)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    show_message(self, "Success", "File saved successfully!", "info")
                    dialog.destroy()
                except Exception as e:
                    show_message(self, "Error", f"Không thể lưu file: {str(e)}", "error")
            
            save_btn = ttk.Button(dialog, text="Save", command=save_changes)
            save_btn.pack(pady=10)
            
        except Exception as e:
            show_message(self, "Error", f"Không thể sửa file: {str(e)}", "error")

    def browse_backup_path(self, backup_type):
        """Chọn đường dẫn sao lưu cho ID hoặc GUID"""
        from tkinter import filedialog
        folder_path = filedialog.askdirectory(title=f"Select {backup_type.upper()} backup folder")
        if folder_path:
            if backup_type == "id":
                self.id_backup_path_var.set(folder_path)
                self.settings_manager.set_setting("id_backup_path", folder_path)
                # Tạo thư mục nếu chưa tồn tại
                os.makedirs(folder_path, exist_ok=True)
                print(f"[DEBUG] Đã cập nhật đường dẫn backup ID: {folder_path}")
            else:
                self.guid_backup_path_var.set(folder_path)
                self.settings_manager.set_setting("guid_backup_path", folder_path)
                # Tạo thư mục nếu chưa tồn tại
                os.makedirs(folder_path, exist_ok=True)
                print(f"[DEBUG] Đã cập nhật đường dẫn backup GUID: {folder_path}")
            
            # Lưu settings ngay lập tức
            self.settings_manager.save_settings()
            show_message(self, "Thành công", f"Đã cập nhật đường dẫn backup {backup_type.upper()}", "success")

    def apply_font_size(self, size):
        """Áp dụng font size mới cho toàn bộ ứng dụng"""
        try:
            # Chuyển đổi size thành số
            font_size = int(size)
            
            # Cập nhật style cho từng loại widget
            self.style.configure(".", font=("Tahoma", font_size))
            self.style.configure("TButton", font=("Tahoma", font_size))
            self.style.configure("TLabel", font=("Tahoma", font_size))
            self.style.configure("Title.TLabel", font=("Tahoma", font_size + 16, "bold"))
            self.style.configure("Header.TLabel", font=("Tahoma", font_size + 6, "bold"))
            self.style.configure("Info.TLabel", font=("Tahoma", font_size))
            self.style.configure("ID.TLabel", font=("Consolas", font_size + 1))
            self.style.configure("Description.TLabel", font=("Tahoma", font_size))
            
            # Lưu vào settings
            self.settings_manager.set_setting("font_size", str(font_size))
            
        except ValueError as e:
            print(f"Lỗi khi áp dụng font size: {str(e)}")

    def apply_window_size(self, size_str):
        """Áp dụng kích thước cửa sổ mới"""
        try:
            # Kiểm tra format hợp lệ (width x height)
            if "x" not in size_str:
                raise ValueError("Định dạng kích thước không hợp lệ")
                
            width, height = map(int, size_str.split("x"))
            if width < 1200 or height < 800:
                raise ValueError("Kích thước không được nhỏ hơn 1200x800")
                
            # Áp dụng kích thước mới
            self.geometry(f"{width}x{height}")
            
            # Lưu vào settings
            self.settings_manager.set_setting("window_size", size_str)
            
            # Center window
            self.center_window()
            
        except Exception as e:
            print(f"Lỗi khi áp dụng window size: {str(e)}")

def update_storage_file(new_ids):
    # Đường dẫn file storage.json
    storage_path = os.path.expanduser(r'~\AppData\Roaming\Cursor\User\globalStorage\storage.json')
    
    try:
        # Tạo thư mục nếu chưa tồn tại
        os.makedirs(os.path.dirname(storage_path), exist_ok=True)
        
        # Đọc nội dung file hiện tại nếu có
        data = {}
        if os.path.exists(storage_path):
            try:
                with open(storage_path, 'r') as f:
                    data = json.load(f)
            except json.JSONDecodeError:
                # Nếu file corrupt thì tạo mới
                data = {}
        
        # Cập nhật các ID mới
        data.update(new_ids)
        
        # Ghi lại toàn bộ nội dung
        with open(storage_path, 'w') as f:
            json.dump(data, f, indent=4)
            
    except Exception as e:
        raise Exception(f"Lỗi khi cập nhật file: {str(e)}")

if __name__ == "__main__":
    try:
        # Ẩn cửa sổ console
        if not sys.argv[-1] == 'asadmin':
            import win32gui, win32con
            hwnd = win32gui.GetForegroundWindow()
            win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
        
        # Kiểm tra quyền admin khi khởi động
        if not is_admin():
            # Hỏi người dùng có muốn chạy với quyền admin không
            if messagebox.askyesno(
                "Yêu cầu quyền Admin",
                "Ứng dụng cần quyền Admin để hoạt động đầy đủ.\nBạn có muốn chạy với quyền Admin không?"
            ):
                try:
                    if sys.argv[-1] != 'asadmin':
                        script = os.path.abspath(sys.argv[0])
                        params = ' '.join([script] + sys.argv[1:] + ['asadmin'])
                        # Chạy process mới với quyền admin
                        windll.shell32.ShellExecuteW(None, "runas", sys.executable, script, None, 1)
                        sys.exit()  # Thoát instance hiện tại ngay lập tức
                except Exception as e:
                    messagebox.showerror("Lỗi", f"Không thể chạy với quyền admin: {str(e)}")
                    sys.exit()
            else:
                sys.exit()  # Thoát nếu người dùng không đồng ý
        
        # Chỉ chạy phần này khi có quyền admin
        print("Đang khởi động Lappy Lab ...")
        
        # Khởi động ứng dụng
        app = MainApplication()
        app.run()
        
    except Exception as e:
        messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {str(e)}")
