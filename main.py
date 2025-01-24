import tkinter as tk
from tkinter import ttk, messagebox
from app.utils.id_generator import IDGenerator
from app.utils.file_manager import FileManager
from app.utils.message_box import show_message
from app.utils.settings_manager import SettingsManager
from app.utils.version_info_dialog import VersionInfoDialog
import platform
from datetime import datetime
from PIL import Image, ImageTk, ImageDraw
from app.gui.cleanup_manager import CleanupManager
import os
import sys
import requests
import re
from packaging import version

def check_for_updates():
    """Kiểm tra phiên bản mới từ GitHub"""
    try:
        # Phiên bản hiện tại
        current_version = "2.1.2"
        
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

class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Lappy Hacking")
        self.geometry("1400x900")
        self.minsize(1400, 900)
        self.configure(bg='#D4D0C8')
        
        # Initialize settings manager
        self.settings_manager = SettingsManager()
        
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
        
        self.setup_ui()
        self.center_window()
        
        # Hiển thị thông báo phiên bản nếu được cấu hình
        if self.settings_manager.get_show_version_info():
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
            }
        }
        
        for style_name, config in custom_styles.items():
            self.style.configure(style_name, background=bg_color, **config)

    def _load_icons(self):
        """Load tất cả icons một lần và cache lại"""
        try:
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
        title_label = ttk.Label(left_header, text="Lappy Hacking", style="Title.TLabel")
        title_label.pack(side=tk.LEFT)
        
        # System info and version on the right
        info_frame = ttk.Frame(header_frame)
        info_frame.pack(side=tk.RIGHT)
        
        # Get system information
        system_info = self.get_system_info()
        version_info = "Version 2.1.2 (Released: Jan 23, 2025)"
        
        # Add modern styling to system info
        ttk.Label(info_frame, text=system_info, style="Subtitle.TLabel").pack(anchor="e", pady=(0, 2))
        ttk.Label(info_frame, text=version_info, style="Subtitle.TLabel").pack(anchor="e")
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_container)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Main tab with more padding
        main_tab = ttk.Frame(notebook, padding="10")
        notebook.add(main_tab, text="ID Generator")
        
        # Initialize CleanupManager
        self.cleanup_manager = CleanupManager(self, notebook)
        
        # Settings and About tab - Moved to last
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
                                command=lambda: [self.generate_ids(), self.save_ids()],
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
        right_panel = ttk.LabelFrame(main_content, text="Thông tin ID", padding="15")
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Status indicator
        status_frame = ttk.Frame(right_panel)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.status_indicator = ttk.Label(status_frame, text="⭕ Chưa tạo ID",
                                        style="Status.TLabel")
        self.status_indicator.pack(side=tk.LEFT)
        
        # ID Display Area with card-like design
        self.id_labels = {}
        id_types = {
            "Machine ID": ("🔷 telemetry.machineId", "telemetry.machineId"),
            "SQM ID": ("🔶 telemetry.sqmId", "telemetry.sqmId"),
            "Device ID": ("🔴 telemetry.devDeviceId", "telemetry.devDeviceId"),
            "MAC Machine ID": ("🔵 telemetry.macMachineId", "telemetry.macMachineId")
        }
        
        for label_text, (display_text, key) in id_types.items():
            # Create card-like frame for each ID
            card_frame = ttk.Frame(right_panel, style='Card.TFrame')
            card_frame.pack(fill=tk.X, pady=8, padx=5)
            
            # Add subtle border
            card_inner = ttk.Frame(card_frame, padding=10)
            card_inner.pack(fill=tk.X, expand=True)
            
            # Title with icon
            ttk.Label(card_inner, text=display_text,
                     style="Bold.TLabel").pack(side=tk.LEFT)
            
            # ID value with monospace font
            id_label = ttk.Label(card_inner, text="Not generated",
                               style="ID.TLabel")
            id_label.pack(side=tk.LEFT, padx=15)
            self.id_labels[key] = id_label
            
            # Copy button with icon
            copy_btn = ttk.Button(card_inner, text="📋 Copy",
                                command=lambda k=key: self.copy_to_clipboard(k),
                                style="Action.TButton", width=10)
            copy_btn.pack(side=tk.RIGHT)
        
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
        name_label.bind("<Button-1>", lambda e: self.open_website("https://lappyhacking.onrender.com/"))

        # Website with modern styling
        web_frame = ttk.Frame(header_frame)
        web_frame.pack(pady=(5, 15))
        
        ttk.Label(web_frame, 
                text="Official website:", 
                font=("Segoe UI", 11)).pack(side=tk.LEFT, padx=(0, 5))
                
        website_label = ttk.Label(web_frame, 
                                text="https://lappyhacking.onrender.com/",
                                style="Link.TLabel",
                                cursor="hand2")
        website_label.pack(side=tk.LEFT)
        website_label.bind("<Button-1>", lambda e: self.open_website("https://lappyhacking.onrender.com/"))
        
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
            "• Too many trail account on this machine"
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
        author_label.bind("<Button-1>", lambda e: self.open_website("https://lappyhacking.onrender.com/"))
        
        # Website with icon
        web_frame = ttk.Frame(author_frame)
        web_frame.pack(side=tk.RIGHT, padx=20)
        web_icon = "🌐"  # Website icon
        ttk.Label(web_frame, text=web_icon, font=("Segoe UI", 11)).pack(side=tk.LEFT, padx=5)
        ttk.Label(web_frame, text="Official website:", font=("Segoe UI", 11)).pack(side=tk.LEFT, padx=5)
        website_label = ttk.Label(web_frame, text="https://lappyhacking.onrender.com/",
                                style="Link.TLabel", cursor="hand2")
        website_label.pack(side=tk.LEFT, padx=5)
        website_label.bind("<Button-1>", lambda e: self.open_website("https://lappyhacking.onrender.com/"))
    
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
                raise ValueError("Please generate IDs first!")
            
            app_name = self.app_var.get()
            self.file_manager.set_app(app_name)
            self.file_manager.save_ids(self.current_ids)
            
            # Update status indicators
            self.status_indicator.config(text="✅ Đã lưu ID thành công")
            self.quick_status_label.config(text="Đã lưu ID")
            show_message(self, "Success", "IDs saved successfully!", "success")
            self.update_status("IDs saved to storage")
            
        except Exception as e:
            show_message(self, "Error", str(e), "error")
            self.status_indicator.config(text="❌ Lỗi khi lưu ID")
            self.quick_status_label.config(text="Lỗi khi lưu ID")
            self.update_status("Error saving IDs")
    
    def create_backup(self):
        try:
            app_name = self.app_var.get()
            self.file_manager.set_app(app_name)
            backup_path = self.file_manager.create_backup()
            show_message(self, "Success", f"Backup created at:\n{backup_path}", "success")
            self.update_status("Backup created successfully")
            
        except Exception as e:
            show_message(self, "Error", str(e), "error")
            self.update_status("Error creating backup")
    
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
            self.file_manager.set_app(app_name)
            self.current_ids = self.file_manager.read_current_ids()
            
            # Update labels
            for key, label in self.id_labels.items():
                if key in self.current_ids:
                    label.config(text=self.current_ids[key])
                else:
                    label.config(text="Not found")
            
            # Update status indicators
            self.status_indicator.config(text="✅ Đã đọc ID hiện tại")
            self.quick_status_label.config(text="Đã đọc ID")
            self.update_status("Current IDs loaded successfully")
            
        except Exception as e:
            show_message(self, "Error", str(e), "error")
            self.status_indicator.config(text="❌ Lỗi khi đọc ID")
            self.quick_status_label.config(text="Lỗi khi đọc ID")
            self.update_status("Error loading current IDs")
    
    def open_website(self, url):
        import webbrowser
        webbrowser.open(url)
    
    def run(self):
        self.mainloop()

if __name__ == "__main__":
    app = MainApplication()
    app.run()
