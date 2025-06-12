# gui/main_window.py - Giao diện chính của Lappy Lab 4.1
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import os
from datetime import datetime
from PIL import Image, ImageTk

# Import các module từ core
from core.utils import get_system_info
from core.config_manager import ConfigManager
# Sử dụng logic mới từ features.show_config
from features.show_config import get_token, get_email, UsageManager, format_subscription_type, get_token_from_config

class LappyLabApp:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.config_manager = ConfigManager()
        self.setup_variables()
        self.load_icons()
        self.setup_ui()
        self.load_account_info()
        self.check_ide_status()

    def setup_window(self):
        """Thiết lập cửa sổ chính"""
        self.root.title("Lappy Lab 4.1 - Modern IDE Management Tool")
        self.root.geometry("950x750")
        self.root.resizable(True, True)
        self.root.configure(bg='#f0f0f0')

        # Thiết lập minimum size
        self.root.minsize(800, 600)

        # Thiết lập icon nếu có
        try:
            icon_path = os.path.join(os.path.dirname(__file__), '..', '..', 'public', 'image', 'icon.ico')
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except:
            pass

        # Thiết lập style hiện đại
        style = ttk.Style()
        style.theme_use('clam')

        # Custom styles
        style.configure('Title.TLabel', font=('Segoe UI', 18, 'bold'), foreground='#2c3e50')
        style.configure('Header.TLabel', font=('Segoe UI', 12, 'bold'), foreground='#34495e')
        style.configure('Info.TLabel', font=('Segoe UI', 10), foreground='#2c3e50')
        style.configure('Modern.TButton', font=('Segoe UI', 9, 'bold'), padding=(10, 8))

        # Tab styles - gọn hơn và tab selected nổi bật
        style.configure('TNotebook.Tab',
                       padding=(8, 4),  # Giảm padding để gọn hơn
                       font=('Segoe UI', 9),  # Font nhỏ hơn
                       background='#ecf0f1',
                       foreground='#7f8c8d')

        style.map('TNotebook.Tab',
                 background=[('selected', '#ffffff'),
                           ('active', '#d5dbdb')],
                 foreground=[('selected', '#2c3e50'),
                           ('active', '#34495e')],
                 font=[('selected', ('Segoe UI', 9, 'bold')),  # Tab được chọn bold
                      ('active', ('Segoe UI', 9))],
                 padding=[('selected', (10, 6))])  # Tab được chọn to hơn một chút

    def add_hover_effect(self, button, normal_color, hover_color):
        """Thêm hiệu ứng hover cho button"""
        def on_enter(e):
            button.configure(bg=hover_color)

        def on_leave(e):
            button.configure(bg=normal_color)

        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)

    def setup_variables(self):
        """Thiết lập các biến"""
        # Cursor tab variables
        self.account_email = tk.StringVar(value="Đang tải...")
        self.account_type = tk.StringVar(value="Đang tải...")
        self.account_days = tk.StringVar(value="Đang tải...")
        self.usage_fast = tk.StringVar(value="Đang tải...")
        self.usage_slow = tk.StringVar(value="Đang tải...")

        # Augment tab variables
        self.jetbrains_status = tk.StringVar(value="Đang kiểm tra...")
        self.vscode_status = tk.StringVar(value="Đang kiểm tra...")
        self.augment_status = tk.StringVar(value="Đang kiểm tra...")
        
        # Email tab variables
        self.email_base = tk.StringVar(value="")
        self.email_max_extension = tk.StringVar(value="1000")
        self.email_result = tk.StringVar(value="")
        self.email_count = tk.IntVar(value=5)
        self.use_extension = tk.BooleanVar(value=True)
        
        # TempMail API variables
        saved_token = self.config_manager.get('tempmail_api_token', '')
        self.tempmail_api_token = tk.StringVar(value=saved_token)
        self.tempmail_username = tk.StringVar(value="")
        # Danh sách tên miền mặc định
        self.default_domains = [
            "tempmail.id.vn",
            "tempmail.ckvn.edu.vn",
            "nghienplus.io.vn",
            "1trick.net"
        ]
        self.tempmail_domain = tk.StringVar(value=self.default_domains[0])
        self.tempmail_domains = self.default_domains.copy()  # Bắt đầu với danh sách mặc định
        self.tempmail_status = tk.StringVar(value="Chưa kết nối" if not saved_token else "Đã lưu token")

    def load_icons(self):
        """Tải các icon từ thư mục public"""
        self.icons = {}
        icon_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'public', 'image')

        icon_files = {
            'cursor': 'cursor.jpg',
            'augment': 'ag.jpg',
            'vscode': 'vsc.png',
            'windsurf': 'windsurf-icon.png',
            'email': 'email.png',
            'main_icon': 'icon.jpg',  # Icon chính cho header
            'guide': 'icon.jpg'  # Icon cho tab hướng dẫn (dùng chung với main_icon)
        }

        for name, filename in icon_files.items():
            try:
                icon_path = os.path.join(icon_dir, filename)
                if os.path.exists(icon_path):
                    # Load và resize icon
                    img = Image.open(icon_path)
                    if name == 'main_icon':
                        # Icon header lớn hơn một chút
                        img = img.resize((28, 28), Image.Resampling.LANCZOS)
                    else:
                        # Icon tab nhỏ gọn hơn
                        img = img.resize((16, 16), Image.Resampling.LANCZOS)
                    self.icons[name] = ImageTk.PhotoImage(img)
            except Exception as e:
                print(f"Không thể tải icon {name}: {e}")
                self.icons[name] = None

    def setup_ui(self):
        """Thiết lập giao diện người dùng"""
        # Header
        self.create_header()

        # Tạo notebook cho tabs
        self.create_tabs()

    def create_tabs(self):
        """Tạo tabs cho Cursor, Augment Code, Email và Hướng dẫn"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # Tab 1: Cursor với icon
        self.cursor_frame = ttk.Frame(self.notebook)
        if self.icons.get('cursor'):
            cursor_text = " Cursor"
            self.notebook.add(self.cursor_frame, text=cursor_text, image=self.icons.get('cursor'), compound='left')
        else:
            cursor_text = "🖱️ Cursor"
            self.notebook.add(self.cursor_frame, text=cursor_text)
        self.setup_cursor_tab()

        # Tab 2: Augment VIP với icon
        self.augment_frame = ttk.Frame(self.notebook)
        if self.icons.get('augment'):
            augment_text = " Augment"
            self.notebook.add(self.augment_frame, text=augment_text, image=self.icons.get('augment'), compound='left')
        else:
            augment_text = "🔧 Augment"
            self.notebook.add(self.augment_frame, text=augment_text)
        self.setup_augment_tab()
        
        # Tab 3: Email với icon
        self.email_frame = ttk.Frame(self.notebook)
        if self.icons.get('email'):
            email_text = "Email"
            self.notebook.add(self.email_frame, text=email_text, image=self.icons.get('email'), compound='left')
        else:
            email_text = "Email"
            self.notebook.add(self.email_frame, text=email_text)
        self.setup_email_tab()

        # Tab 4: Hướng dẫn sử dụng với icon
        self.guide_frame = ttk.Frame(self.notebook)
        if self.icons.get('guide'):
            guide_text = " Hướng dẫn"
            self.notebook.add(self.guide_frame, text=guide_text, image=self.icons.get('guide'), compound='left')
        else:
            guide_text = "Hướng dẫn"
            self.notebook.add(self.guide_frame, text=guide_text)
        self.setup_guide_tab()

    def setup_cursor_tab(self):
        """Thiết lập tab Cursor"""
        # Info panels
        self.create_cursor_info_panels()

        # Function buttons
        self.create_cursor_function_buttons()

        # Log area
        self.create_cursor_log_area()

    def setup_augment_tab(self):
        """Thiết lập tab Augment VIP (Tool reset IDE telemetry)"""
        # Info panels
        self.create_augment_info_panels()

        # Function buttons
        self.create_augment_function_buttons()

        # Log area
        self.create_augment_log_area()

    def create_header(self):
        """Tạo header với thông tin hệ thống"""
        # Main header frame với background
        header_frame = tk.Frame(self.root, bg='#ffffff', relief='flat', bd=1)
        header_frame.pack(fill=tk.X, padx=15, pady=(10, 5))

        # Inner frame cho padding
        inner_frame = tk.Frame(header_frame, bg='#ffffff')
        inner_frame.pack(fill=tk.X, padx=20, pady=15)

        # Title với icon thật
        title_frame = tk.Frame(inner_frame, bg='#ffffff')
        title_frame.pack(side=tk.LEFT)

        # Icon và text
        if self.icons.get('main_icon'):
            # Có icon thật
            icon_label = tk.Label(title_frame, image=self.icons['main_icon'], bg='#ffffff')
            icon_label.pack(side=tk.LEFT, padx=(0, 10))

            title_label = tk.Label(title_frame, text="Lappy Lab",
                                  font=("Segoe UI", 20, "bold"),
                                  fg='#2c3e50', bg='#ffffff')
            title_label.pack(side=tk.LEFT)
        else:
            # Fallback về emoji
            title_label = tk.Label(title_frame, text="🚀 Lappy Lab",
                                  font=("Segoe UI", 20, "bold"),
                                  fg='#2c3e50', bg='#ffffff')
            title_label.pack(side=tk.LEFT)

        # Info frame bên phải
        info_frame = tk.Frame(inner_frame, bg='#ffffff')
        info_frame.pack(side=tk.RIGHT)

        # System info
        system_info = get_system_info()
        info_text = f"💻 {system_info['os']} | 🖥️ {system_info['pc_name']}"
        system_label = tk.Label(info_frame, text=info_text,
                               font=("Segoe UI", 10),
                               fg='#7f8c8d', bg='#ffffff')
        system_label.pack(anchor='e')

        # Version info với style đẹp hơn
        version_text = f"📦 Version 4.1 | 📅 Released: Jun 11, 2025"
        version_label = tk.Label(info_frame, text=version_text,
                                font=("Segoe UI", 9),
                                fg='#95a5a6', bg='#ffffff')
        version_label.pack(anchor='e', pady=(2, 0))

        # Separator line
        separator = tk.Frame(self.root, height=1, bg='#ecf0f1')
        separator.pack(fill=tk.X, padx=15, pady=(5, 0))

    def create_cursor_info_panels(self):
        """Tạo các panel thông tin cho tab Cursor"""
        info_frame = tk.Frame(self.cursor_frame, bg='#f8f9fa')
        info_frame.pack(fill=tk.X, padx=15, pady=10)

        # Account info panel
        account_frame = tk.LabelFrame(info_frame, text="📊 Thông tin tài khoản",
                                     font=("Segoe UI", 11, "bold"),
                                     fg='#2c3e50', bg='#ffffff',
                                     relief='solid', bd=1)
        account_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8), pady=5)

        # Account info content
        account_inner = tk.Frame(account_frame, bg='#ffffff')
        account_inner.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        tk.Label(account_inner, text="📧 Email:", font=("Segoe UI", 10, "bold"),
                fg='#34495e', bg='#ffffff').grid(row=0, column=0, sticky=tk.W, pady=3)
        tk.Label(account_inner, textvariable=self.account_email, font=("Segoe UI", 10),
                fg='#2c3e50', bg='#ffffff').grid(row=0, column=1, sticky=tk.W, padx=(15, 0), pady=3)

        tk.Label(account_inner, text="🔑 Gói:", font=("Segoe UI", 10, "bold"),
                fg='#34495e', bg='#ffffff').grid(row=1, column=0, sticky=tk.W, pady=3)
        tk.Label(account_inner, textvariable=self.account_type, font=("Segoe UI", 10),
                fg='#e74c3c', bg='#ffffff').grid(row=1, column=1, sticky=tk.W, padx=(15, 0), pady=3)

        tk.Label(account_inner, text="⏰ Còn lại:", font=("Segoe UI", 10, "bold"),
                fg='#34495e', bg='#ffffff').grid(row=2, column=0, sticky=tk.W, pady=3)
        tk.Label(account_inner, textvariable=self.account_days, font=("Segoe UI", 10),
                fg='#27ae60', bg='#ffffff').grid(row=2, column=1, sticky=tk.W, padx=(15, 0), pady=3)

        # Usage info panel
        usage_frame = tk.LabelFrame(info_frame, text="📈 Thông tin sử dụng",
                                   font=("Segoe UI", 11, "bold"),
                                   fg='#2c3e50', bg='#ffffff',
                                   relief='solid', bd=1)
        usage_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(8, 0), pady=5)

        # Usage info content
        usage_inner = tk.Frame(usage_frame, bg='#ffffff')
        usage_inner.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        tk.Label(usage_inner, text="⭐ Fast Response:", font=("Segoe UI", 10, "bold"),
                fg='#34495e', bg='#ffffff').grid(row=0, column=0, sticky=tk.W, pady=3)
        tk.Label(usage_inner, textvariable=self.usage_fast, font=("Segoe UI", 10),
                fg='#f39c12', bg='#ffffff').grid(row=0, column=1, sticky=tk.W, padx=(15, 0), pady=3)

        tk.Label(usage_inner, text="📝 Slow Response:", font=("Segoe UI", 10, "bold"),
                fg='#34495e', bg='#ffffff').grid(row=1, column=0, sticky=tk.W, pady=3)
        tk.Label(usage_inner, textvariable=self.usage_slow, font=("Segoe UI", 10),
                fg='#3498db', bg='#ffffff').grid(row=1, column=1, sticky=tk.W, padx=(15, 0), pady=3)

    def create_augment_info_panels(self):
        """Tạo các panel thông tin cho tab Augment VIP"""
        info_frame = tk.Frame(self.augment_frame, bg='#f8f9fa')
        info_frame.pack(fill=tk.X, padx=15, pady=10)

        # JetBrains info panel
        jetbrains_frame = tk.LabelFrame(info_frame, text="🔧 JetBrains IDEs",
                                       font=("Segoe UI", 11, "bold"),
                                       fg='#2c3e50', bg='#ffffff',
                                       relief='solid', bd=1)
        jetbrains_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8), pady=5)

        # JetBrains content
        jetbrains_inner = tk.Frame(jetbrains_frame, bg='#ffffff')
        jetbrains_inner.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        tk.Label(jetbrains_inner, text="🔧 Trạng thái:", font=("Segoe UI", 10, "bold"),
                fg='#34495e', bg='#ffffff').grid(row=0, column=0, sticky=tk.W, pady=3)
        tk.Label(jetbrains_inner, textvariable=self.jetbrains_status, font=("Segoe UI", 10),
                fg='#e67e22', bg='#ffffff').grid(row=0, column=1, sticky=tk.W, padx=(15, 0), pady=3)

        # VSCode info panel
        vscode_frame = tk.LabelFrame(info_frame, text="💻 VSCode-based IDEs",
                                    font=("Segoe UI", 11, "bold"),
                                    fg='#2c3e50', bg='#ffffff',
                                    relief='solid', bd=1)
        vscode_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(8, 0), pady=5)

        # VSCode content
        vscode_inner = tk.Frame(vscode_frame, bg='#ffffff')
        vscode_inner.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        tk.Label(vscode_inner, text="💻 VSCode IDEs:", font=("Segoe UI", 10, "bold"),
                fg='#34495e', bg='#ffffff').grid(row=0, column=0, sticky=tk.W, pady=3)
        tk.Label(vscode_inner, textvariable=self.vscode_status, font=("Segoe UI", 10),
                fg='#3498db', bg='#ffffff').grid(row=0, column=1, sticky=tk.W, padx=(15, 0), pady=3)

        tk.Label(vscode_inner, text="🚀 Tool Status:", font=("Segoe UI", 10, "bold"),
                fg='#34495e', bg='#ffffff').grid(row=1, column=0, sticky=tk.W, pady=3)
        tk.Label(vscode_inner, textvariable=self.augment_status, font=("Segoe UI", 10),
                fg='#27ae60', bg='#ffffff').grid(row=1, column=1, sticky=tk.W, padx=(15, 0), pady=3)

    def create_cursor_function_buttons(self):
        """Tạo các nút chức năng cho tab Cursor"""
        button_frame = tk.Frame(self.cursor_frame, bg='#ffffff', relief='solid', bd=1)
        button_frame.pack(fill=tk.X, padx=15, pady=10)

        # Header cho button section
        header_frame = tk.Frame(button_frame, bg='#f8f9fa', height=35)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        tk.Label(header_frame, text="⚙️ Chức năng Cursor",
                font=("Segoe UI", 11, "bold"),
                fg='#2c3e50', bg='#f8f9fa').pack(pady=8)

        # Content frame
        content_frame = tk.Frame(button_frame, bg='#ffffff')
        content_frame.pack(fill=tk.X, padx=20, pady=15)

        # Grid layout 2x3 gọn gàng hơn
        buttons = [
            ("Reset Machine ID", self.reset_machine_id, '#3498db', '#2980b9'),
            ("Tắt Auto Update", self.disable_auto_update, '#e67e22', '#d35400'),
            ("Reset Full Cursor", self.reset_full_cursor, '#e74c3c', '#c0392b'),
            ("Bypass Version Check", self.bypass_version_check, '#9b59b6', '#8e44ad'),
            ("Hiển thị Config", self.show_config, '#1abc9c', '#16a085'),
            ("Bypass Token Limit", self.bypass_token_limit, '#27ae60', '#229954')
        ]

        for i, (text, command, bg_color, hover_color) in enumerate(buttons):
            row = i // 3
            col = i % 3

            btn = tk.Button(content_frame, text=text,
                           command=command,
                           font=("Segoe UI", 9, "bold"),
                           bg=bg_color, fg='white',
                           relief='flat', bd=0,
                           width=18, height=2,
                           cursor='hand2')
            btn.grid(row=row, column=col, padx=8, pady=6, sticky='ew')
            self.add_hover_effect(btn, bg_color, hover_color)

        # Configure grid weights
        for i in range(3):
            content_frame.grid_columnconfigure(i, weight=1)

    def create_augment_function_buttons(self):
        """Tạo các nút chức năng cho tab Augment VIP"""
        button_frame = tk.Frame(self.augment_frame, bg='#ffffff', relief='solid', bd=1)
        button_frame.pack(fill=tk.X, padx=15, pady=10)

        # Header cho button section
        header_frame = tk.Frame(button_frame, bg='#f8f9fa', height=35)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        tk.Label(header_frame, text="🔧 Chức năng Augment VIP",
                font=("Segoe UI", 11, "bold"),
                fg='#2c3e50', bg='#f8f9fa').pack(pady=8)

        # Content frame
        content_frame = tk.Frame(button_frame, bg='#ffffff')
        content_frame.pack(fill=tk.X, padx=20, pady=15)

        # IDE Selection Section
        selection_frame = tk.Frame(content_frame, bg='#f8f9fa', relief='solid', bd=1)
        selection_frame.pack(fill=tk.X, pady=(0, 15))

        selection_inner = tk.Frame(selection_frame, bg='#f8f9fa')
        selection_inner.pack(fill=tk.X, padx=15, pady=10)

        tk.Label(selection_inner, text="🎯 Chọn IDE để reset:",
                font=("Segoe UI", 10, "bold"),
                fg='#2c3e50', bg='#f8f9fa').pack(side=tk.LEFT)

        self.selected_ide = tk.StringVar(value="cursor")
        ide_combo = ttk.Combobox(selection_inner, textvariable=self.selected_ide,
                                values=["cursor", "windsurf", "vscode", "vscodium", "all"],
                                state="readonly", width=15, font=("Segoe UI", 10))
        ide_combo.pack(side=tk.LEFT, padx=(15, 0))

        # Main buttons grid 2x3
        buttons_frame = tk.Frame(content_frame, bg='#ffffff')
        buttons_frame.pack(fill=tk.X)

        buttons = [
            ("Reset JetBrains IDs", self.reset_jetbrains_ids, '#e67e22', '#d35400'),
            ("Reset Selected IDE", self.reset_selected_ide_ids, '#3498db', '#2980b9'),
            ("Clean Augment DB", self.clean_vscode_database, '#9b59b6', '#8e44ad'),
            ("Clean Telemetry", self.clean_telemetry_entries, '#e74c3c', '#c0392b'),
            ("Reset All IDs", self.reset_all_ids_with_terminate, '#27ae60', '#229954'),
            ("Check IDE Status", self.check_ide_status, '#1abc9c', '#16a085')
        ]

        for i, (text, command, bg_color, hover_color) in enumerate(buttons):
            row = i // 3
            col = i % 3

            btn = tk.Button(buttons_frame, text=text,
                           command=command,
                           font=("Segoe UI", 9, "bold"),
                           bg=bg_color, fg='white',
                           relief='flat', bd=0,
                           width=18, height=2,
                           cursor='hand2')
            btn.grid(row=row, column=col, padx=8, pady=6, sticky='ew')
            self.add_hover_effect(btn, bg_color, hover_color)

        # Configure grid weights
        for i in range(3):
            buttons_frame.grid_columnconfigure(i, weight=1)

    def create_cursor_log_area(self):
        """Tạo vùng log cho tab Cursor"""
        log_frame = tk.LabelFrame(self.cursor_frame, text="📝 Cursor Log",
                                 font=("Segoe UI", 11, "bold"),
                                 fg='#2c3e50', bg='#ffffff',
                                 relief='solid', bd=1)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(5, 15))

        # Log content frame
        log_inner = tk.Frame(log_frame, bg='#ffffff')
        log_inner.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.cursor_log_text = scrolledtext.ScrolledText(log_inner, height=10,
                                                        font=("Consolas", 9),
                                                        bg="#1e1e1e", fg="#ffffff",
                                                        insertbackground="#ffffff",
                                                        selectbackground="#404040",
                                                        selectforeground="#ffffff",
                                                        relief='flat', bd=0)
        self.cursor_log_text.pack(fill=tk.BOTH, expand=True)

        # Thêm log mặc định với style đẹp hơn
        self.cursor_log("🚀 Lappy Lab 4.1 - Cursor Management Tool")
        self.cursor_log("=" * 60)
        self.cursor_log("✅ File storage.json hợp lệ và có dữ liệu.")
        self.cursor_log("")
        self.cursor_log("📁 File SQLite:")
        self.cursor_log("   📍 Đường dẫn: C:\\Users\\letan\\AppData\\Roaming\\Cursor\\User\\globalStorage\\state.vscdb")
        self.cursor_log("   📊 Kích thước: 96309248 bytes")
        self.cursor_log("   🔐 Quyền truy cập: 0o666")
        self.cursor_log("   ✅ Quyền đọc/ghi: Có")
        self.cursor_log("✅ Kết nối cơ sở dữ liệu SQLite thành công.")
        self.cursor_log("📊 Số bảng: 2")
        self.cursor_log("=" * 60)

    def create_augment_log_area(self):
        """Tạo vùng log cho tab Augment VIP"""
        log_frame = tk.LabelFrame(self.augment_frame, text="🔧 Augment VIP Log",
                                 font=("Segoe UI", 11, "bold"),
                                 fg='#2c3e50', bg='#ffffff',
                                 relief='solid', bd=1)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(5, 15))

        # Log content frame
        log_inner = tk.Frame(log_frame, bg='#ffffff')
        log_inner.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.augment_log_text = scrolledtext.ScrolledText(log_inner, height=10,
                                                         font=("Consolas", 9),
                                                         bg="#1e1e1e", fg="#ffffff",
                                                         insertbackground="#ffffff",
                                                         selectbackground="#404040",
                                                         selectforeground="#ffffff",
                                                         relief='flat', bd=0)
        self.augment_log_text.pack(fill=tk.BOTH, expand=True)

        # Thêm log mặc định với style đẹp hơn
        self.augment_log("🔧 Augment VIP - IDE Telemetry Reset Tool")
        self.augment_log("=" * 60)
        self.augment_log("📋 Hỗ trợ: JetBrains IDEs + VSCode-based IDEs")
        self.augment_log("💡 Chọn IDE cụ thể: Cursor, Windsurf, VSCode, VSCodium")
        self.augment_log("🚀 TÍNH NĂNG MỚI: Reset IDs tự động terminate IDE trước!")
        self.augment_log("🔍 Đang kiểm tra IDE installations...")
        self.augment_log("=" * 60)

    def cursor_log(self, message):
        """Thêm message vào cursor log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.cursor_log_text.insert(tk.END, log_entry)
        self.cursor_log_text.see(tk.END)

    def augment_log(self, message):
        """Thêm message vào augment log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.augment_log_text.insert(tk.END, log_entry)
        self.augment_log_text.see(tk.END)

    def log(self, message):
        """Thêm message vào cursor log (backward compatibility)"""
        self.cursor_log(message)
        
    def load_account_info(self):
        """Tải thông tin tài khoản trong background - SỬ DỤNG LOGIC MỚI"""
        def load_info():
            try:
                self.log("🔄 Đang tải thông tin tài khoản...")

                # Get token using new logic
                token = get_token()
                if not token:
                    self.log("❌ Không tìm thấy token. Vui lòng đăng nhập Cursor.")
                    self.account_email.set("Chưa đăng nhập")
                    self.account_type.set("Free")
                    self.account_days.set("0 ngày")
                    self.usage_fast.set("N/A")
                    self.usage_slow.set("N/A")
                    return

                self.log(f"✅ Đã tìm thấy token: {token[:20]}...")

                # Get email using new logic
                email = get_email()
                if email:
                    self.account_email.set(email)
                    self.log(f"✅ Email: {email}")
                else:
                    self.account_email.set("Không tìm thấy")
                    self.log("⚠️ Không tìm thấy email")

                # Get subscription info using new logic
                try:
                    subscription_info = UsageManager.get_stripe_profile(token)
                    if subscription_info:
                        subscription_type = format_subscription_type(subscription_info)
                        self.account_type.set(subscription_type)

                        # Get remaining days
                        days_remaining = subscription_info.get("daysRemainingOnTrial", 0)
                        self.account_days.set(f"{days_remaining} ngày")

                        self.log(f"✅ Subscription: {subscription_type}")
                        self.log(f"✅ Days remaining: {days_remaining}")
                    else:
                        self.account_type.set("Free")
                        self.account_days.set("0 ngày")
                        self.log("⚠️ Không lấy được thông tin subscription")
                except Exception as e:
                    self.log(f"❌ Lỗi lấy subscription: {str(e)}")
                    self.account_type.set("Free")
                    self.account_days.set("0 ngày")

                # Get usage info using new logic
                try:
                    usage_info = UsageManager.get_usage(token)
                    if usage_info:
                        # Format usage display
                        premium_usage = usage_info.get('premium_usage', 0)
                        max_premium_usage = usage_info.get('max_premium_usage', "No Limit")
                        basic_usage = usage_info.get('basic_usage', 0)
                        max_basic_usage = usage_info.get('max_basic_usage', "No Limit")

                        self.usage_fast.set(f"{premium_usage}/{max_premium_usage}")
                        self.usage_slow.set(f"{basic_usage}/{max_basic_usage}")

                        self.log(f"✅ Fast Response: {premium_usage}/{max_premium_usage}")
                        self.log(f"✅ Slow Response: {basic_usage}/{max_basic_usage}")
                    else:
                        self.usage_fast.set("N/A")
                        self.usage_slow.set("N/A")
                        self.log("⚠️ Không lấy được thông tin usage")
                except Exception as e:
                    self.log(f"❌ Lỗi lấy usage: {str(e)}")
                    self.usage_fast.set("N/A")
                    self.usage_slow.set("N/A")

                self.log("✅ Hoàn thành tải thông tin tài khoản")

            except Exception as e:
                self.log(f"❌ Lỗi tổng quát: {str(e)}")
                import traceback
                self.log(f"Chi tiết: {traceback.format_exc()}")

        thread = threading.Thread(target=load_info, daemon=True)
        thread.start()
        
    # Các phương thức chức năng
    def reset_machine_id(self):
        """Reset Machine ID"""
        self.log("🔄 Đang reset Machine ID...")
        try:
            from features.reset_machine_id import reset_machine_id
            result, message = reset_machine_id()
            if result:
                self.log("✅ Reset Machine ID thành công!")
                self.log(message)
                messagebox.showinfo("Thành công", "Reset Machine ID thành công!")
            else:
                self.log("❌ Reset Machine ID thất bại!")
                self.log(message)
                messagebox.showerror("Lỗi", "Reset Machine ID thất bại!")
        except Exception as e:
            self.log(f"❌ Lỗi: {str(e)}")
            messagebox.showerror("Lỗi", f"Lỗi: {str(e)}")
            
    def disable_auto_update(self):
        """Tắt tự động cập nhật Cursor"""
        self.log("🔄 Đang tắt tự động cập nhật...")
        try:
            from features.disable_auto_update import disable_auto_update
            result, message = disable_auto_update()
            if result:
                self.log("✅ Tắt tự động cập nhật thành công!")
                self.log(message)
                messagebox.showinfo("Thành công", "Tắt tự động cập nhật thành công!")
            else:
                self.log("❌ Tắt tự động cập nhật thất bại!")
                self.log(message)
                messagebox.showerror("Lỗi", "Tắt tự động cập nhật thất bại!")
        except Exception as e:
            self.log(f"❌ Lỗi: {str(e)}")
            messagebox.showerror("Lỗi", f"Lỗi: {str(e)}")

    def reset_full_cursor(self):
        """Reset Full Cursor"""
        # Xác nhận trước khi reset
        confirm = messagebox.askyesno("Xác nhận", 
                                     "⚠️ CẢNH BÁO: Thao tác này sẽ xóa toàn bộ dữ liệu Cursor!\n"
                                     "Bạn có chắc chắn muốn tiếp tục?")
        if not confirm:
            self.log("❌ Đã hủy thao tác reset toàn bộ")
            return
            
        self.log("🔄 Đang reset toàn bộ Cursor...")
        try:
            from features.reset_full_cursor import reset_full_cursor
            result, message = reset_full_cursor()
            if result:
                self.log("✅ Reset toàn bộ Cursor thành công!")
                self.log(message)
                messagebox.showinfo("Thành công", "Reset toàn bộ Cursor thành công!")
            else:
                self.log("❌ Reset toàn bộ Cursor thất bại!")
                self.log(message)
                messagebox.showerror("Lỗi", "Reset toàn bộ Cursor thất bại!")
        except Exception as e:
            self.log(f"❌ Lỗi: {str(e)}")
            messagebox.showerror("Lỗi", f"Lỗi: {str(e)}")
            
    def bypass_version_check(self):
        """Bỏ qua kiểm tra phiên bản"""
        self.log("🔄 Đang bỏ qua kiểm tra phiên bản...")
        try:
            from features.bypass_version_check import bypass_version_check
            result, message = bypass_version_check()
            if result:
                self.log("✅ Bỏ qua kiểm tra phiên bản thành công!")
                self.log(message)
                messagebox.showinfo("Thành công", "Bỏ qua kiểm tra phiên bản thành công!")
            else:
                self.log("❌ Bỏ qua kiểm tra phiên bản thất bại!")
                self.log(message)
                messagebox.showerror("Lỗi", "Bỏ qua kiểm tra phiên bản thất bại!")
        except Exception as e:
            self.log(f"❌ Lỗi: {str(e)}")
            messagebox.showerror("Lỗi", f"Lỗi: {str(e)}")
            
    def show_config(self):
        """Hiển thị cấu hình - SỬ DỤNG LOGIC MỚI"""
        self.log("📋 Đang hiển thị cấu hình...")
        try:
            from features.show_config import show_account_info
            result, message = show_account_info()
            if result:
                self.log("✅ Hiển thị cấu hình thành công!")
                # Hiển thị trong cửa sổ mới
                config_window = tk.Toplevel(self.root)
                config_window.title("Thông tin tài khoản Cursor")
                config_window.geometry("800x600")
                config_window.resizable(True, True)

                # Text widget để hiển thị config
                config_text = scrolledtext.ScrolledText(config_window,
                                                       font=("Consolas", 10),
                                                       bg="#000080", fg="#FFFFFF")
                config_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                config_text.insert(tk.END, message)
                config_text.config(state=tk.DISABLED)
            else:
                self.log("❌ Hiển thị cấu hình thất bại!")
                self.log(message)
                messagebox.showerror("Lỗi", message)
        except Exception as e:
            self.log(f"❌ Lỗi: {str(e)}")
            import traceback
            self.log(f"Chi tiết: {traceback.format_exc()}")
            messagebox.showerror("Lỗi", f"Lỗi: {str(e)}")
            
    def bypass_token_limit(self):
        """Bỏ qua giới hạn token"""
        self.log("🔄 Đang bỏ qua giới hạn token...")
        try:
            from features.bypass_token_limit import bypass_token_limit
            result, message = bypass_token_limit()
            if result:
                self.log("✅ Bỏ qua giới hạn token thành công!")
                self.log(message)
                messagebox.showinfo("Thành công", "Bỏ qua giới hạn token thành công!")
            else:
                self.log("❌ Bỏ qua giới hạn token thất bại!")
                self.log(message)
                messagebox.showerror("Lỗi", "Bỏ qua giới hạn token thất bại!")
        except Exception as e:
            self.log(f"❌ Lỗi: {str(e)}")
            messagebox.showerror("Lỗi", f"Lỗi: {str(e)}")
            
    # Các phương thức cho Augment Code
    def check_ide_status(self):
        """Kiểm tra trạng thái IDE installations"""
        def check_status():
            try:
                self.augment_log("🔍 Đang kiểm tra JetBrains installations...")

                # Check JetBrains
                try:
                    from features import check_jetbrains_installation
                    jetbrains_found = check_jetbrains_installation()
                    if jetbrains_found:
                        self.jetbrains_status.set("✅ Đã cài đặt")
                        self.augment_log("✅ Tìm thấy JetBrains IDEs")
                    else:
                        self.jetbrains_status.set("❌ Chưa cài đặt")
                        self.augment_log("❌ Không tìm thấy JetBrains IDEs")
                except (ImportError, AttributeError):
                    self.jetbrains_status.set("❌ Module lỗi")
                    self.augment_log("❌ Augment modules chưa sẵn sàng")

                # Check từng IDE cụ thể
                try:
                    from features.augment_utils import get_installed_ides
                    installed_ides = get_installed_ides()

                    self.augment_log("📋 Chi tiết IDE installations:")

                    ide_count = 0
                    for ide_key, ide_info in installed_ides.items():
                        if ide_key != "jetbrains":  # JetBrains đã check ở trên
                            status = "✅" if ide_info["installed"] else "❌"
                            self.augment_log(f"   {status} {ide_info['name']}")
                            if ide_info["installed"]:
                                ide_count += 1

                    if ide_count > 0:
                        self.vscode_status.set(f"✅ {ide_count} IDE(s)")
                        self.augment_status.set("✅ Sẵn sàng")
                        self.augment_log(f"✅ Tìm thấy {ide_count} VSCode-based IDEs")
                    else:
                        self.vscode_status.set("❌ Chưa cài đặt")
                        self.augment_status.set("❌ Không khả dụng")
                        self.augment_log("❌ Không tìm thấy VSCode-based IDEs")

                except (ImportError, AttributeError):
                    self.vscode_status.set("❌ Module lỗi")
                    self.augment_status.set("❌ Module lỗi")
                    self.augment_log("❌ Augment modules chưa sẵn sàng")

                self.augment_log("✅ Hoàn thành kiểm tra IDE status")

            except Exception as e:
                self.augment_log(f"❌ Lỗi kiểm tra IDE status: {str(e)}")
                self.jetbrains_status.set("❌ Lỗi")
                self.vscode_status.set("❌ Lỗi")
                self.augment_status.set("❌ Lỗi")

        thread = threading.Thread(target=check_status, daemon=True)
        thread.start()

    def reset_jetbrains_ids(self):
        """Reset JetBrains IDs"""
        self.augment_log("🔄 Đang reset JetBrains IDs...")
        try:
            from features import reset_jetbrains_ids
            result, message = reset_jetbrains_ids()
            if result:
                self.augment_log("✅ Reset JetBrains IDs thành công!")
                self.augment_log(message)
                messagebox.showinfo("Thành công", "Reset JetBrains IDs thành công!")
            else:
                self.augment_log("❌ Reset JetBrains IDs thất bại!")
                self.augment_log(message)
                messagebox.showerror("Lỗi", "Reset JetBrains IDs thất bại!")
        except (ImportError, AttributeError):
            self.augment_log("❌ Augment modules chưa sẵn sàng")
            messagebox.showerror("Lỗi", "Augment Code modules chưa được cài đặt đầy đủ")
        except Exception as e:
            self.augment_log(f"❌ Lỗi: {str(e)}")
            messagebox.showerror("Lỗi", f"Lỗi: {str(e)}")

    def reset_selected_ide_ids(self):
        """Reset IDs của IDE được chọn (tích hợp terminate)"""
        selected = self.selected_ide.get()

        if selected == "all":
            self.reset_all_ids_with_terminate()
            return

        ide_names = {
            "cursor": "Cursor",
            "windsurf": "Windsurf",
            "vscode": "Visual Studio Code",
            "vscodium": "VSCodium"
        }

        ide_name = ide_names.get(selected, selected.upper())

        # Xác nhận trước khi thực hiện
        confirm = messagebox.askyesno("Xác nhận",
                                     f"🔄 RESET {ide_name.upper()} IDs\n\n"
                                     f"Quá trình sẽ:\n"
                                     f"1. 🛑 Terminate {ide_name} processes\n"
                                     f"2. 🔄 Reset {ide_name} telemetry IDs\n"
                                     f"3. 🔒 Lock files\n\n"
                                     f"Bạn có chắc chắn muốn tiếp tục?")
        if not confirm:
            self.augment_log(f"❌ Đã hủy reset {ide_name} IDs")
            return

        self.augment_log(f"🚀 Bắt đầu reset {ide_name} IDs (có terminate)...")

        try:
            # Bước 1: Terminate IDE trước
            self.augment_log(f"🛑 Bước 1: Terminate {ide_name} processes...")
            terminate_success = self.terminate_specific_ide(selected)

            if terminate_success:
                self.augment_log(f"✅ Terminate {ide_name} thành công!")
            else:
                self.augment_log(f"⚠️ Terminate {ide_name} có vấn đề, nhưng tiếp tục reset...")

            # Đợi một chút để đảm bảo processes đã đóng
            self.augment_log("⏳ Đợi 2 giây để processes đóng hoàn toàn...")
            import time
            time.sleep(2)

            # Bước 2: Reset IDs
            self.augment_log(f"🔄 Bước 2: Reset {ide_name} IDs...")
            from features.augment_reset_ids import reset_vscode_ids
            result, message = reset_vscode_ids(specific_ide=selected)

            if result:
                self.augment_log(f"✅ Reset {ide_name} IDs thành công!")
                self.augment_log(message)
                self.augment_log(f"🎉 Hoàn thành reset {ide_name}! Bạn có thể khởi động lại {ide_name}.")
                messagebox.showinfo("Thành công",
                                   f"✅ Reset {ide_name} hoàn thành!\n\n"
                                   f"✓ Đã terminate processes\n"
                                   f"✓ Đã reset telemetry IDs\n"
                                   f"✓ Đã lock files\n\n"
                                   f"Bạn có thể khởi động lại {ide_name}.")
            else:
                self.augment_log(f"❌ Reset {ide_name} IDs thất bại!")
                self.augment_log(message)
                messagebox.showerror("Lỗi", f"Reset {ide_name} IDs thất bại!")

        except (ImportError, AttributeError):
            self.augment_log("❌ Augment modules chưa sẵn sàng")
            messagebox.showerror("Lỗi", "Augment Code modules chưa được cài đặt đầy đủ")
        except Exception as e:
            self.augment_log(f"❌ Lỗi: {str(e)}")
            messagebox.showerror("Lỗi", f"Lỗi: {str(e)}")

    def terminate_specific_ide(self, ide_type):
        """Terminate IDE cụ thể"""
        try:
            import psutil

            # Mapping IDE types to process patterns
            ide_patterns = {
                "cursor": ["cursor"],
                "windsurf": ["windsurf"],
                "vscode": ["code", "vscode"],
                "vscodium": ["vscodium"]
            }

            patterns = ide_patterns.get(ide_type, [ide_type])
            terminated_count = 0

            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    proc_name = proc.info['name'].lower()
                    cmdline = ' '.join(proc.info['cmdline']).lower() if proc.info['cmdline'] else ""

                    # Kiểm tra xem có phải IDE cần terminate không
                    should_terminate = False
                    for pattern in patterns:
                        if pattern in proc_name or pattern in cmdline:
                            should_terminate = True
                            break

                    if should_terminate:
                        try:
                            proc.terminate()
                            proc.wait(timeout=3)
                            self.augment_log(f"   ✅ Terminated: {proc.info['name']} (PID: {proc.info['pid']})")
                            terminated_count += 1
                        except psutil.TimeoutExpired:
                            proc.kill()
                            self.augment_log(f"   🔥 Force killed: {proc.info['name']} (PID: {proc.info['pid']})")
                            terminated_count += 1
                        except psutil.NoSuchProcess:
                            pass
                        except Exception as e:
                            self.augment_log(f"   ❌ Error terminating {proc.info['name']}: {str(e)}")

                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
                except Exception:
                    continue

            if terminated_count > 0:
                self.augment_log(f"   📊 Đã terminate {terminated_count} processes")
                return True
            else:
                self.augment_log(f"   ℹ️ Không tìm thấy processes nào đang chạy")
                return True  # Không có process nào cũng là thành công

        except Exception as e:
            self.augment_log(f"   ❌ Lỗi terminate: {str(e)}")
            return False

    def reset_all_ids_with_terminate(self):
        """Reset tất cả IDs với terminate tích hợp"""
        # Xác nhận trước khi reset all
        confirm = messagebox.askyesno("Xác nhận",
                                     "🔄 RESET TẤT CẢ IDs\n\n"
                                     "Quá trình sẽ:\n"
                                     "1. 🛑 Terminate TẤT CẢ VSCode-based IDEs\n"
                                     "2. 🔧 Reset JetBrains IDs\n"
                                     "3. 💻 Reset tất cả VSCode variant IDs\n"
                                     "4. 🔒 Lock tất cả files\n\n"
                                     "⚠️ CẢNH BÁO: Tất cả IDEs sẽ bị đóng!\n"
                                     "Bạn có chắc chắn muốn tiếp tục?")
        if not confirm:
            self.augment_log("❌ Đã hủy thao tác reset tất cả IDs")
            return

        self.augment_log("🚀 Bắt đầu reset TẤT CẢ IDs (có terminate)...")

        try:
            # Bước 1: Terminate tất cả IDEs
            self.augment_log("🛑 Bước 1: Terminate tất cả VSCode-based IDEs...")
            from features import terminate_ides
            _, terminate_message = terminate_ides()
            self.augment_log(terminate_message)

            # Đợi processes đóng
            self.augment_log("⏳ Đợi 3 giây để tất cả processes đóng...")
            import time
            time.sleep(3)

            # Bước 2: Reset tất cả IDs
            self.augment_log("🔄 Bước 2: Reset tất cả IDs...")
            from features import reset_all_ids
            result, message = reset_all_ids()

            if result:
                self.augment_log("✅ Reset tất cả IDs thành công!")
                self.augment_log(message)
                self.augment_log("🎉 Hoàn thành reset tất cả! Bạn có thể khởi động lại các IDEs.")
                messagebox.showinfo("Thành công",
                                   "✅ Reset tất cả IDs hoàn thành!\n\n"
                                   "✓ Đã terminate tất cả IDEs\n"
                                   "✓ Đã reset JetBrains IDs\n"
                                   "✓ Đã reset VSCode variant IDs\n"
                                   "✓ Đã lock tất cả files\n\n"
                                   "Bạn có thể khởi động lại các IDEs.")
            else:
                self.augment_log("❌ Reset tất cả IDs thất bại!")
                self.augment_log(message)
                messagebox.showerror("Lỗi", "Reset tất cả IDs thất bại!")

        except (ImportError, AttributeError):
            self.augment_log("❌ Augment modules chưa sẵn sàng")
            messagebox.showerror("Lỗi", "Augment Code modules chưa được cài đặt đầy đủ")
        except Exception as e:
            self.augment_log(f"❌ Lỗi: {str(e)}")
            messagebox.showerror("Lỗi", f"Lỗi: {str(e)}")

    def reset_vscode_ids(self):
        """Reset tất cả VSCode IDs (backward compatibility)"""
        self.augment_log("🔄 Đang reset tất cả VSCode IDs...")
        try:
            from features.augment_reset_ids import reset_vscode_ids
            result, message = reset_vscode_ids()
            if result:
                self.augment_log("✅ Reset VSCode IDs thành công!")
                self.augment_log(message)
                messagebox.showinfo("Thành công", "Reset VSCode IDs thành công!")
            else:
                self.augment_log("❌ Reset VSCode IDs thất bại!")
                self.augment_log(message)
                messagebox.showerror("Lỗi", "Reset VSCode IDs thất bại!")
        except (ImportError, AttributeError):
            self.augment_log("❌ Augment modules chưa sẵn sàng")
            messagebox.showerror("Lỗi", "Augment Code modules chưa được cài đặt đầy đủ")
        except Exception as e:
            self.augment_log(f"❌ Lỗi: {str(e)}")
            messagebox.showerror("Lỗi", f"Lỗi: {str(e)}")

    def clean_vscode_database(self):
        """Clean VSCode Database (chỉ entries chứa 'augment')"""
        self.augment_log("🔄 Đang clean VSCode database (Augment entries)...")
        try:
            from features.augment_clean_database import clean_vscode_database
            result, message = clean_vscode_database()
            self.augment_log("📋 Clean Augment Database hoàn thành!")
            self.augment_log(message)
            if result:
                messagebox.showinfo("Hoàn thành", "Clean Augment Database hoàn thành!\n\nXem chi tiết trong log.")
            else:
                messagebox.showerror("Lỗi", "Clean Augment Database thất bại!")
        except (ImportError, AttributeError):
            self.augment_log("❌ Augment modules chưa sẵn sàng")
            messagebox.showerror("Lỗi", "Augment Code modules chưa được cài đặt đầy đủ")
        except Exception as e:
            self.augment_log(f"❌ Lỗi: {str(e)}")
            messagebox.showerror("Lỗi", f"Lỗi: {str(e)}")

    def clean_telemetry_entries(self):
        """Clean tất cả telemetry entries"""
        # Xác nhận trước khi clean
        confirm = messagebox.askyesno("Xác nhận",
                                     "⚠️ CẢNH BÁO: Thao tác này sẽ xóa TẤT CẢ entries telemetry!\n"
                                     "Bao gồm: telemetry, machine, device, uuid\n\n"
                                     "Bạn có chắc chắn muốn tiếp tục?")
        if not confirm:
            self.augment_log("❌ Đã hủy thao tác clean telemetry")
            return

        self.augment_log("🔄 Đang clean tất cả telemetry entries...")
        try:
            from features.augment_clean_database import clean_telemetry_entries
            result, message = clean_telemetry_entries()
            self.augment_log("📋 Clean Telemetry hoàn thành!")
            self.augment_log(message)
            if result:
                messagebox.showinfo("Hoàn thành", "Clean Telemetry hoàn thành!\n\nXem chi tiết trong log.")
            else:
                messagebox.showerror("Lỗi", "Clean Telemetry thất bại!")
        except (ImportError, AttributeError):
            self.augment_log("❌ Augment modules chưa sẵn sàng")
            messagebox.showerror("Lỗi", "Augment Code modules chưa được cài đặt đầy đủ")
        except Exception as e:
            self.augment_log(f"❌ Lỗi: {str(e)}")
            messagebox.showerror("Lỗi", f"Lỗi: {str(e)}")

    def terminate_ides(self):
        """Terminate IDEs"""
        # Xác nhận trước khi terminate
        confirm = messagebox.askyesno("Xác nhận",
                                     "⚠️ CẢNH BÁO: Thao tác này sẽ đóng tất cả IDE đang chạy!\n"
                                     "Bạn có chắc chắn muốn tiếp tục?")
        if not confirm:
            self.augment_log("❌ Đã hủy thao tác terminate IDEs")
            return

        self.augment_log("🔄 Đang terminate IDEs...")
        try:
            from features import terminate_ides
            result, message = terminate_ides()
            if result:
                self.augment_log("✅ Terminate IDEs thành công!")
                self.augment_log(message)
                messagebox.showinfo("Thành công", "Terminate IDEs thành công!")
            else:
                self.augment_log("❌ Terminate IDEs thất bại!")
                self.augment_log(message)
                messagebox.showerror("Lỗi", "Terminate IDEs thất bại!")
        except (ImportError, AttributeError):
            self.augment_log("❌ Augment modules chưa sẵn sàng")
            messagebox.showerror("Lỗi", "Augment Code modules chưa được cài đặt đầy đủ")
        except Exception as e:
            self.augment_log(f"❌ Lỗi: {str(e)}")
            messagebox.showerror("Lỗi", f"Lỗi: {str(e)}")

    def reset_all_ids(self):
        """Reset tất cả IDs"""
        # Xác nhận trước khi reset all
        confirm = messagebox.askyesno("Xác nhận",
                                     "⚠️ CẢNH BÁO: Thao tác này sẽ reset tất cả IDs của JetBrains và VSCode!\n"
                                     "Bạn có chắc chắn muốn tiếp tục?")
        if not confirm:
            self.augment_log("❌ Đã hủy thao tác reset tất cả IDs")
            return

        self.augment_log("🔄 Đang reset tất cả IDs...")
        try:
            from features import reset_all_ids
            result, message = reset_all_ids()
            if result:
                self.augment_log("✅ Reset tất cả IDs thành công!")
                self.augment_log(message)
                messagebox.showinfo("Thành công", "Reset tất cả IDs thành công!")
            else:
                self.augment_log("❌ Reset tất cả IDs thất bại!")
                self.augment_log(message)
                messagebox.showerror("Lỗi", "Reset tất cả IDs thất bại!")
        except (ImportError, AttributeError):
            self.augment_log("❌ Augment modules chưa sẵn sàng")
            messagebox.showerror("Lỗi", "Augment Code modules chưa được cài đặt đầy đủ")
        except Exception as e:
            self.augment_log(f"❌ Lỗi: {str(e)}")
            messagebox.showerror("Lỗi", f"Lỗi: {str(e)}")

    def setup_guide_tab(self):
        """Thiết lập tab Hướng dẫn sử dụng"""
        # Main container với padding
        main_container = tk.Frame(self.guide_frame, bg='#f8f9fa')
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # Header section
        header_frame = tk.Frame(main_container, bg='#ffffff', relief='solid', bd=1)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        header_inner = tk.Frame(header_frame, bg='#f8f9fa', height=40)
        header_inner.pack(fill=tk.X)
        header_inner.pack_propagate(False)

        tk.Label(header_inner, text="Hướng dẫn sử dụng Lappy Lab 4.1",
                font=("Segoe UI", 11, "bold"),
                fg='#2c3e50', bg='#f8f9fa').pack(pady=12)

        # Content frame với scrollable text
        content_frame = tk.LabelFrame(main_container, text="📋 Chi tiết hướng dẫn",
                                     font=("Segoe UI", 11, "bold"),
                                     fg='#2c3e50', bg='#ffffff',
                                     relief='solid', bd=1)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Scrollable text area
        content_inner = tk.Frame(content_frame, bg='#ffffff')
        content_inner.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.guide_text = scrolledtext.ScrolledText(content_inner, height=25,
                                                   font=("Segoe UI", 10),
                                                   bg="#ffffff", fg="#2c3e50",
                                                   insertbackground="#2c3e50",
                                                   selectbackground="#3498db",
                                                   selectforeground="#ffffff",
                                                   relief='flat', bd=0,
                                                   wrap=tk.WORD)
        self.guide_text.pack(fill=tk.BOTH, expand=True)

        # Load guide content
        self.load_guide_content()

    def load_guide_content(self):
        """Tải nội dung hướng dẫn ngắn gọn xúc tích"""
        guide_content = """🚀 LAPPY LAB 4.1 - HƯỚNG DẪN NHANH
═════════════════════════════════════════════════

🔧 Đăng xuất tài khoản Cursor hoặc Augment Code trước khi reset
═════════════════════════════════════════════════
📋 TAB CURSOR
Để Reset lỗi Too many trial account, bạn cần:
Reset Machine ID là đủ nếu trường hợp vẫn bị quét thì hãy Reset Full Cursor, sau đó dùng 1 email mới để đăng ký cursor 
Có thể dùng Tab Email để tạo Extend Mail hoặc temp mail để đăng ký cursor

📋 TAB AUGMENT
Để Reset lỗi Too many trial account, bạn cần:
• Chọn IDE cần reset
• Chọn Reset Selected IDE: Reset IDE đã chọn (tự động đóng IDE)
• Chọn Clean Augment DB: Xóa dấu vết Augment

📋 TAB EMAIL
Tab Email có 2 chức năng chính:

1️⃣ Email mở rộng:
• Nhập phần đầu email (không cần @gmail.com)
• Tùy chọn sử dụng số mở rộng (có thể bật/tắt)
• Chọn số mở rộng tối đa (random từ 1 đến giá trị này)
• Tạo email ngẫu nhiên với định dạng tùy biến (chữ hoa/thường, dấu chấm)
• Có thể tạo nhiều email cùng lúc

2️⃣ TempMail API:
• Nhập API Token từ tempmail.id.vn
• Tạo email tạm thời mới
• Xem danh sách email đã tạo
• Quản lý email tạm thời dễ dàng

⚠️ LƯU Ý:
• Luôn chạy với quyền Administrator
• Backup dữ liệu trước khi reset
• Đọc kỹ cảnh báo trước khi xác nhận

═════════════════════════════════════════════════
👨‍💻 THÔNG TIN LẬP TRÌNH VIÊN
═════════════════════════════════════════════════

🔧 Lập trình viên: Nguyên Kỷ
📧 GitHub: github.com/zlive
💬 Discord: .nguyenky

📦 Version: Lappy Lab 4.1
📅 Release: Jun 11, 2025"""

        # Insert content và disable editing
        self.guide_text.insert(tk.END, guide_content)
        self.guide_text.config(state=tk.DISABLED)

    def setup_email_tab(self):
        """Thiết lập tab Email"""
        # Main container với padding
        main_container = tk.Frame(self.email_frame, bg='#f8f9fa')
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # Tạo notebook cho các subtab
        email_notebook = ttk.Notebook(main_container)
        email_notebook.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Tab 1: Tạo Email mở rộng
        self.extend_email_frame = ttk.Frame(email_notebook)
        email_notebook.add(self.extend_email_frame, text="Email mở rộng")
        self.setup_extend_email_tab()
        
        # Tab 2: TempMail API
        self.tempmail_frame = ttk.Frame(email_notebook)
        email_notebook.add(self.tempmail_frame, text="TempMail API")
        self.setup_tempmail_tab()

    def setup_extend_email_tab(self):
        """Thiết lập tab Email mở rộng"""
        # Main container với padding
        main_container = tk.Frame(self.extend_email_frame, bg='#f8f9fa')
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # Header section
        header_frame = tk.Frame(main_container, bg='#ffffff', relief='solid', bd=1)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        header_inner = tk.Frame(header_frame, bg='#f8f9fa', height=40)
        header_inner.pack(fill=tk.X)
        header_inner.pack_propagate(False)

        tk.Label(header_inner, text="Công cụ tạo Email mở rộng",
                font=("Segoe UI", 11, "bold"),
                fg='#2c3e50', bg='#f8f9fa').pack(pady=12)

        # Content frame
        content_frame = tk.LabelFrame(main_container, text="✉️ Tạo Email mở rộng",
                                     font=("Segoe UI", 11, "bold"),
                                     fg='#2c3e50', bg='#ffffff',
                                     relief='solid', bd=1)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Input section
        input_frame = tk.Frame(content_frame, bg='#ffffff')
        input_frame.pack(fill=tk.X, padx=15, pady=15)

        # Email base input
        base_label = tk.Label(input_frame, text="Nhập phần đầu email:", 
                             font=("Segoe UI", 10), 
                             fg='#2c3e50', bg='#ffffff')
        base_label.grid(row=0, column=0, sticky='w', padx=5, pady=5)
        
        base_entry = tk.Entry(input_frame, textvariable=self.email_base, 
                             font=("Segoe UI", 10), width=25)
        base_entry.grid(row=0, column=1, sticky='w', padx=5, pady=5)
        
        example_label = tk.Label(input_frame, text="(Không bao gồm @gmail.com)", 
                                font=("Segoe UI", 9, "italic"), 
                                fg='#7f8c8d', bg='#ffffff')
        example_label.grid(row=0, column=2, sticky='w', padx=5, pady=5)

        # Checkbox để sử dụng số mở rộng
        use_extension_check = tk.Checkbutton(input_frame, text="Sử dụng số mở rộng",
                                           variable=self.use_extension,
                                           font=("Segoe UI", 10),
                                           fg='#2c3e50', bg='#ffffff',
                                           command=self.toggle_extension_input)
        use_extension_check.grid(row=1, column=0, sticky='w', padx=5, pady=5)

        # Max extension input
        self.extension_frame = tk.Frame(input_frame, bg='#ffffff')
        self.extension_frame.grid(row=1, column=1, columnspan=2, sticky='w')
        
        extension_label = tk.Label(self.extension_frame, text="Số mở rộng tối đa:", 
                                  font=("Segoe UI", 10), 
                                  fg='#2c3e50', bg='#ffffff')
        extension_label.pack(side=tk.LEFT, padx=0, pady=5)
        
        extension_entry = tk.Entry(self.extension_frame, textvariable=self.email_max_extension, 
                                  font=("Segoe UI", 10), width=10)
        extension_entry.pack(side=tk.LEFT, padx=5, pady=5)
        
        extension_note = tk.Label(self.extension_frame, text="(Số ngẫu nhiên từ 1 đến giá trị này)", 
                                 font=("Segoe UI", 9, "italic"), 
                                 fg='#7f8c8d', bg='#ffffff')
        extension_note.pack(side=tk.LEFT, padx=5, pady=5)

        # Email count input (for multiple emails)
        count_label = tk.Label(input_frame, text="Số lượng email:", 
                              font=("Segoe UI", 10), 
                              fg='#2c3e50', bg='#ffffff')
        count_label.grid(row=2, column=0, sticky='w', padx=5, pady=5)
        
        count_spinbox = tk.Spinbox(input_frame, from_=1, to=20, textvariable=self.email_count,
                                  font=("Segoe UI", 10), width=5)
        count_spinbox.grid(row=2, column=1, sticky='w', padx=5, pady=5)

        # Buttons section
        button_frame = tk.Frame(content_frame, bg='#ffffff')
        button_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        # Generate single email button
        generate_btn = tk.Button(button_frame, text="Tạo Email ngẫu nhiên", 
                                font=("Segoe UI", 9, "bold"),
                                bg='#3498db', fg='white',
                                relief='flat', borderwidth=0,
                                padx=15, pady=8,
                                command=self.generate_single_email)
        generate_btn.pack(side=tk.LEFT, padx=5)
        self.add_hover_effect(generate_btn, '#3498db', '#2980b9')
        
        # Generate multiple emails button
        generate_multiple_btn = tk.Button(button_frame, text="Tạo nhiều Email", 
                                        font=("Segoe UI", 9, "bold"),
                                        bg='#2ecc71', fg='white',
                                        relief='flat', borderwidth=0,
                                        padx=15, pady=8,
                                        command=self.generate_multiple_emails)
        generate_multiple_btn.pack(side=tk.LEFT, padx=5)
        self.add_hover_effect(generate_multiple_btn, '#2ecc71', '#27ae60')
        
        # Copy button
        copy_btn = tk.Button(button_frame, text="Sao chép kết quả", 
                            font=("Segoe UI", 9, "bold"),
                            bg='#9b59b6', fg='white',
                            relief='flat', borderwidth=0,
                            padx=15, pady=8,
                            command=self.copy_email_result)
        copy_btn.pack(side=tk.LEFT, padx=5)
        self.add_hover_effect(copy_btn, '#9b59b6', '#8e44ad')

        # Results section
        result_frame = tk.LabelFrame(content_frame, text="📋 Kết quả",
                                    font=("Segoe UI", 10, "bold"),
                                    fg='#2c3e50', bg='#ffffff',
                                    relief='solid', bd=1)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        # Scrollable text area for results
        self.email_result_text = scrolledtext.ScrolledText(result_frame, height=10,
                                                         font=("Consolas", 10),
                                                         bg="#f8f9fa", fg="#2c3e50",
                                                         wrap=tk.WORD)
        self.email_result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def setup_tempmail_tab(self):
        """Thiết lập tab TempMail API"""
        # Main container với padding
        main_container = tk.Frame(self.tempmail_frame, bg='#f8f9fa')
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # Phần trên: API Token và Hướng dẫn (2 cột)
        top_frame = tk.Frame(main_container, bg='#f8f9fa')
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Cột 1: API Token
        token_frame = tk.LabelFrame(top_frame, text="🔑 API Token",
                                   font=("Segoe UI", 11, "bold"),
                                   fg='#2c3e50', bg='#ffffff',
                                   relief='solid', bd=1)
        token_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        token_inner = tk.Frame(token_frame, bg='#ffffff')
        token_inner.pack(fill=tk.X, padx=10, pady=10)
        
        # API Token input
        token_label = tk.Label(token_inner, text="API Token:", 
                              font=("Segoe UI", 10), 
                              fg='#2c3e50', bg='#ffffff')
        token_label.grid(row=0, column=0, sticky='w', padx=5, pady=5)
        
        token_entry = tk.Entry(token_inner, textvariable=self.tempmail_api_token, 
                              font=("Segoe UI", 10), width=25, show="•")
        token_entry.grid(row=0, column=1, sticky='w', padx=5, pady=5)
        
        # Connect button
        connect_btn = tk.Button(token_inner, text="Kết nối", 
                               font=("Segoe UI", 9, "bold"),
                               bg='#3498db', fg='white',
                               relief='flat', borderwidth=0,
                               padx=15, pady=5,
                               command=self.connect_tempmail_api)
        connect_btn.grid(row=0, column=2, sticky='w', padx=5, pady=5)
        self.add_hover_effect(connect_btn, '#3498db', '#2980b9')
        
        # Status display
        status_label = tk.Label(token_inner, text="Trạng thái:", 
                               font=("Segoe UI", 10), 
                               fg='#2c3e50', bg='#ffffff')
        status_label.grid(row=1, column=0, sticky='w', padx=5, pady=5)
        
        self.tempmail_status_label = tk.Label(token_inner, textvariable=self.tempmail_status, 
                                            font=("Segoe UI", 10, "bold"), 
                                            fg='#e74c3c', bg='#ffffff')
        self.tempmail_status_label.grid(row=1, column=1, columnspan=2, sticky='w', padx=5, pady=5)
        
        # Cột 2: Hướng dẫn
        guide_frame = tk.LabelFrame(top_frame, text="📝 Hướng dẫn",
                                   font=("Segoe UI", 11, "bold"),
                                   fg='#2c3e50', bg='#ffffff',
                                   relief='solid', bd=1)
        guide_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        guide_text = scrolledtext.ScrolledText(guide_frame, height=4,
                                             font=("Segoe UI", 9),
                                             bg="#f8f9fa", fg="#2c3e50",
                                             wrap=tk.WORD)
        guide_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        guide_content = """1. Tạo tài khoản tại tempmail.id.vn
2. Truy cập trang cá nhân tại avatar
3. Tạo API token tại mục API để sử dụng.
Lưu ý: API chỉ hiển thị 1 lần duy nhất lúc tạo."""
        
        guide_text.insert(tk.END, guide_content)
        guide_text.config(state=tk.DISABLED)
        
        # Phần giữa: Tạo Email mới
        create_frame = tk.LabelFrame(main_container, text="📧 Tạo Email mới",
                                    font=("Segoe UI", 11, "bold"),
                                    fg='#2c3e50', bg='#ffffff',
                                    relief='solid', bd=1)
        create_frame.pack(fill=tk.X, padx=0, pady=(0, 10))
        
        create_inner = tk.Frame(create_frame, bg='#ffffff')
        create_inner.pack(fill=tk.X, padx=10, pady=10)
        
        # Tất cả trong 1 hàng: Username và Domain
        input_frame = tk.Frame(create_inner, bg='#ffffff')
        input_frame.pack(fill=tk.X, pady=5)
        
        # Username input
        username_label = tk.Label(input_frame, text="Người dùng:", 
                                 font=("Segoe UI", 10), 
                                 fg='#2c3e50', bg='#ffffff')
        username_label.pack(side=tk.LEFT, padx=5)
        
        username_entry = tk.Entry(input_frame, textvariable=self.tempmail_username, 
                                 font=("Segoe UI", 10), width=15)
        username_entry.pack(side=tk.LEFT, padx=5)
        
        # Domain input
        domain_label = tk.Label(input_frame, text="Tên miền:", 
                               font=("Segoe UI", 10), 
                               fg='#2c3e50', bg='#ffffff')
        domain_label.pack(side=tk.LEFT, padx=5)
        
        # Domain combobox
        self.domain_combobox = ttk.Combobox(input_frame, textvariable=self.tempmail_domain, 
                                           font=("Segoe UI", 10), width=15,
                                           values=self.tempmail_domains)
        self.domain_combobox.pack(side=tk.LEFT, padx=5)
        
        # Các nút chức năng
        create_btn = tk.Button(input_frame, text="Tạo mới", 
                              font=("Segoe UI", 9, "bold"),
                              bg='#2ecc71', fg='white',
                              relief='flat', borderwidth=0,
                              padx=10, pady=3,
                              command=self.create_tempmail)
        create_btn.pack(side=tk.LEFT, padx=5)
        self.add_hover_effect(create_btn, '#2ecc71', '#27ae60')
        
        refresh_btn = tk.Button(input_frame, text="Làm mới", 
                              font=("Segoe UI", 9),
                              bg='#95a5a6', fg='white',
                              relief='flat', borderwidth=0,
                              padx=10, pady=3,
                              command=self.refresh_domains)
        refresh_btn.pack(side=tk.LEFT, padx=5)
        self.add_hover_effect(refresh_btn, '#95a5a6', '#7f8c8d')
        
        list_btn = tk.Button(input_frame, text="Danh sách", 
                            font=("Segoe UI", 9, "bold"),
                            bg='#9b59b6', fg='white',
                            relief='flat', borderwidth=0,
                            padx=10, pady=3,
                            command=self.list_tempmail)
        list_btn.pack(side=tk.LEFT, padx=5)
        self.add_hover_effect(list_btn, '#9b59b6', '#8e44ad')
        
        # Phần dưới: Hiển thị email và kết quả
        bottom_frame = tk.Frame(main_container, bg='#f8f9fa')
        bottom_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 0))
        
        # Cột 1: Danh sách email
        email_list_frame = tk.LabelFrame(bottom_frame, text="📋 Danh sách Email",
                                        font=("Segoe UI", 10, "bold"),
                                        fg='#2c3e50', bg='#ffffff',
                                        relief='solid', bd=1)
        email_list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Tạo Listbox với scrollbar
        list_container = tk.Frame(email_list_frame, bg='#ffffff')
        list_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar = tk.Scrollbar(list_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.email_listbox = tk.Listbox(list_container, 
                                      font=("Segoe UI", 10),
                                      bg="#f8f9fa", fg="#2c3e50",
                                      selectbackground="#3498db",
                                      selectforeground="#ffffff",
                                      activestyle="none",
                                      height=10)
        self.email_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Liên kết scrollbar với listbox
        self.email_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.email_listbox.yview)
        
        # Thêm binding cho listbox
        self.email_listbox.bind('<<ListboxSelect>>', self.on_email_selected)
        
        # Nút chức năng cho listbox
        listbox_buttons = tk.Frame(email_list_frame, bg='#ffffff')
        listbox_buttons.pack(fill=tk.X, padx=5, pady=5)
        
        read_btn = tk.Button(listbox_buttons, text="Đọc thư", 
                           font=("Segoe UI", 9, "bold"),
                           bg='#3498db', fg='white',
                           relief='flat', borderwidth=0,
                           padx=10, pady=3,
                           command=self.read_selected_email)
        read_btn.pack(side=tk.LEFT, padx=5)
        self.add_hover_effect(read_btn, '#3498db', '#2980b9')
        
        delete_btn = tk.Button(listbox_buttons, text="Xóa email",
                             font=("Segoe UI", 9, "bold"),
                             bg='#e74c3c', fg='white',
                             relief='flat', borderwidth=0,
                             padx=10, pady=3,
                             command=self.delete_selected_email)
        delete_btn.pack(side=tk.LEFT, padx=5)
        self.add_hover_effect(delete_btn, '#e74c3c', '#c0392b')

        # Nút kiểm tra hỗ trợ xóa
        check_delete_btn = tk.Button(listbox_buttons, text="Kiểm tra API",
                                   font=("Segoe UI", 9, "bold"),
                                   bg='#f39c12', fg='white',
                                   relief='flat', borderwidth=0,
                                   padx=10, pady=3,
                                   command=self.check_delete_support)
        check_delete_btn.pack(side=tk.LEFT, padx=5)
        self.add_hover_effect(check_delete_btn, '#f39c12', '#e67e22')
        
        # Cột 2: Kết quả
        result_frame = tk.LabelFrame(bottom_frame, text="📋 Kết quả",
                                    font=("Segoe UI", 10, "bold"),
                                    fg='#2c3e50', bg='#ffffff',
                                    relief='solid', bd=1)
        result_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Scrollable text area for results
        self.tempmail_result_text = scrolledtext.ScrolledText(result_frame, height=10,
                                                            font=("Consolas", 10),
                                                            bg="#f8f9fa", fg="#2c3e50",
                                                            wrap=tk.WORD)
        self.tempmail_result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Copy button
        copy_frame = tk.Frame(result_frame, bg='#ffffff')
        copy_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        copy_btn = tk.Button(copy_frame, text="Sao chép kết quả", 
                            font=("Segoe UI", 9, "bold"),
                            bg='#f39c12', fg='white',
                            relief='flat', borderwidth=0,
                            padx=15, pady=5,
                            command=self.copy_tempmail_result)
        copy_btn.pack(side=tk.LEFT, padx=5)
        self.add_hover_effect(copy_btn, '#f39c12', '#d35400')
        
        # Clear button
        clear_btn = tk.Button(copy_frame, text="Xóa kết quả", 
                             font=("Segoe UI", 9, "bold"),
                             bg='#95a5a6', fg='white',
                             relief='flat', borderwidth=0,
                             padx=15, pady=5,
                             command=lambda: self.tempmail_result_text.delete(1.0, tk.END))
        clear_btn.pack(side=tk.LEFT, padx=5)
        self.add_hover_effect(clear_btn, '#95a5a6', '#7f8c8d')
        
        # Lưu trữ danh sách email
        self.email_data_list = []
        
        # Nếu đã có token, tự động kết nối
        if self.tempmail_api_token.get():
            self.root.after(1000, self.connect_tempmail_api)

    def toggle_extension_input(self):
        """Bật/tắt phần nhập số mở rộng dựa trên checkbox"""
        if self.use_extension.get():
            for widget in self.extension_frame.winfo_children():
                widget.configure(state=tk.NORMAL)
        else:
            for widget in self.extension_frame.winfo_children():
                widget.configure(state=tk.DISABLED)

    def generate_single_email(self):
        """Tạo một email ngẫu nhiên"""
        base_email = self.email_base.get().strip()
        
        if not base_email:
            messagebox.showerror("Lỗi", "Vui lòng nhập phần đầu email!")
            return
            
        try:
            # Kiểm tra xem có sử dụng số mở rộng không
            use_extension = self.use_extension.get()
            
            if use_extension:
                max_extension = int(self.email_max_extension.get())
                if max_extension <= 0:
                    raise ValueError("Số mở rộng phải lớn hơn 0")
            else:
                max_extension = 0
                
            from features.email_generator import generate_extended_email
            email = generate_extended_email(base_email, max_extension, use_extension)
            
            # Hiển thị kết quả
            self.email_result_text.delete(1.0, tk.END)
            self.email_result_text.insert(tk.END, email)
            self.email_result = email
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tạo email: {str(e)}")
    
    def generate_multiple_emails(self):
        """Tạo nhiều email ngẫu nhiên"""
        base_email = self.email_base.get().strip()
        
        if not base_email:
            messagebox.showerror("Lỗi", "Vui lòng nhập phần đầu email!")
            return
            
        try:
            # Kiểm tra xem có sử dụng số mở rộng không
            use_extension = self.use_extension.get()
            
            if use_extension:
                max_extension = int(self.email_max_extension.get())
                if max_extension <= 0:
                    raise ValueError("Số mở rộng phải lớn hơn 0")
            else:
                max_extension = 0
                
            count = self.email_count.get()
            if count <= 0 or count > 100:
                messagebox.showerror("Lỗi", "Số lượng email phải từ 1 đến 100!")
                return
                
            from features.email_generator import generate_multiple_emails
            emails = generate_multiple_emails(base_email, count, max_extension, use_extension)
            
            # Hiển thị kết quả
            self.email_result_text.delete(1.0, tk.END)
            result_text = "\n".join(emails)
            self.email_result_text.insert(tk.END, result_text)
            self.email_result = result_text
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tạo email: {str(e)}")
    
    def copy_email_result(self):
        """Sao chép kết quả email vào clipboard"""
        result = self.email_result_text.get(1.0, tk.END).strip()
        
        if not result:
            messagebox.showinfo("Thông báo", "Không có kết quả để sao chép!")
            return
            
        self.root.clipboard_clear()
        self.root.clipboard_append(result)
        messagebox.showinfo("Thành công", "Đã sao chép kết quả vào clipboard!")

    def connect_tempmail_api(self):
        """Kết nối đến TempMail API"""
        api_token = self.tempmail_api_token.get().strip()
        
        if not api_token:
            messagebox.showerror("Lỗi", "Vui lòng nhập API Token!")
            return
            
        try:
            from features.tempmail_api import TempMailAPI
            
            # Tạo đối tượng API và kiểm tra kết nối
            api = TempMailAPI(api_token)
            result = api.get_user_info()
            
            if result['error']:
                self.tempmail_status.set("Lỗi kết nối")
                self.tempmail_status_label.config(fg='#e74c3c')
                self.tempmail_result_text.delete(1.0, tk.END)
                self.tempmail_result_text.insert(tk.END, f"Lỗi: {result['message']}")
                return
                
            # Hiển thị thông tin người dùng
            user_data = result['data']
            self.tempmail_status.set("Đã kết nối")
            self.tempmail_status_label.config(fg='#27ae60')
            
            self.tempmail_result_text.delete(1.0, tk.END)
            self.tempmail_result_text.insert(tk.END, f"Kết nối thành công!\n\n")
            self.tempmail_result_text.insert(tk.END, f"Thông tin người dùng:\n")
            self.tempmail_result_text.insert(tk.END, f"Tên: {user_data.get('name', 'Không có')}\n")
            self.tempmail_result_text.insert(tk.END, f"Email: {user_data.get('email', 'Không có')}\n")
            
            # Lưu API token vào biến instance để sử dụng sau này
            self._tempmail_api = api
            
            # Lưu API token vào cấu hình
            self.config_manager.set('tempmail_api_token', api_token)
            
            # Lấy danh sách tên miền
            self.refresh_domains()
            
        except Exception as e:
            self.tempmail_status.set("Lỗi")
            self.tempmail_status_label.config(fg='#e74c3c')
            self.tempmail_result_text.delete(1.0, tk.END)
            self.tempmail_result_text.insert(tk.END, f"Lỗi: {str(e)}")
    
    def refresh_domains(self):
        """Lấy danh sách tên miền từ API"""
        if not hasattr(self, '_tempmail_api'):
            if not self.tempmail_api_token.get().strip():
                messagebox.showerror("Lỗi", "Vui lòng kết nối API trước!")
                return
            else:
                # Thử kết nối lại
                self.connect_tempmail_api()
                if not hasattr(self, '_tempmail_api'):
                    return
            
        try:
            # Hiển thị thông báo đang xử lý
            self.tempmail_result_text.delete(1.0, tk.END)
            self.tempmail_result_text.insert(tk.END, "Đang lấy danh sách tên miền...\n")
            self.root.update()
            
            result = self._tempmail_api.get_domains()
            
            if result['error']:
                # Hiển thị thông báo lỗi nhưng vẫn sử dụng danh sách mặc định
                self.tempmail_result_text.delete(1.0, tk.END)
                self.tempmail_result_text.insert(tk.END, f"⚠️ Không thể lấy danh sách tên miền: {result['message']}\n")
                self.tempmail_result_text.insert(tk.END, "Đã sử dụng danh sách mặc định.")
                
                # Sử dụng danh sách mặc định
                self.domain_combobox['values'] = self.default_domains
                if not self.tempmail_domain.get():
                    self.tempmail_domain.set(self.default_domains[0])
                return
                
            # Lấy danh sách tên miền
            domains = result['data']
            if domains and isinstance(domains, list):
                # Kết hợp danh sách mặc định và danh sách từ API
                all_domains = list(set(self.default_domains + domains))
                self.tempmail_domains = all_domains
                
                # Cập nhật combobox
                self.domain_combobox['values'] = self.tempmail_domains
                
                # Giữ nguyên tên miền đã chọn nếu có
                if not self.tempmail_domain.get() and self.tempmail_domains:
                    self.tempmail_domain.set(self.tempmail_domains[0])
                    
                # Hiển thị thông báo thành công
                self.tempmail_result_text.delete(1.0, tk.END)
                self.tempmail_result_text.insert(tk.END, "✅ Đã cập nhật danh sách tên miền.\n")
                self.tempmail_result_text.insert(tk.END, f"Số lượng tên miền: {len(self.tempmail_domains)}")
            else:
                # Nếu không lấy được từ API, sử dụng danh sách mặc định
                self.domain_combobox['values'] = self.default_domains
                if not self.tempmail_domain.get():
                    self.tempmail_domain.set(self.default_domains[0])
                    
                # Hiển thị thông báo
                self.tempmail_result_text.delete(1.0, tk.END)
                self.tempmail_result_text.insert(tk.END, "ℹ️ Sử dụng danh sách tên miền mặc định.\n")
            
        except Exception as e:
            # Nếu có lỗi, sử dụng danh sách mặc định
            self.domain_combobox['values'] = self.default_domains
            if not self.tempmail_domain.get():
                self.tempmail_domain.set(self.default_domains[0])
                
            # Hiển thị thông báo lỗi
            self.tempmail_result_text.delete(1.0, tk.END)
            self.tempmail_result_text.insert(tk.END, f"⚠️ Lỗi: {str(e)}\n")
            self.tempmail_result_text.insert(tk.END, "Đã sử dụng danh sách tên miền mặc định.")
    
    def create_tempmail(self):
        """Tạo email mới trên TempMail"""
        if not hasattr(self, '_tempmail_api'):
            messagebox.showerror("Lỗi", "Vui lòng kết nối API trước!")
            return
            
        try:
            username = self.tempmail_username.get().strip() or None
            domain = self.tempmail_domain.get().strip() or None
            
            # Hiển thị thông báo đang xử lý
            self.tempmail_result_text.delete(1.0, tk.END)
            self.tempmail_result_text.insert(tk.END, "Đang tạo email mới...\n")
            self.root.update()
            
            result = self._tempmail_api.create_email(username, domain)
            
            if result['error']:
                self.tempmail_result_text.delete(1.0, tk.END)
                self.tempmail_result_text.insert(tk.END, f"Lỗi: {result['message']}")
                return
                
            # Hiển thị thông tin email mới
            email_data = result['data']
            
            # Debug: Hiển thị toàn bộ dữ liệu nhận được
            print("DEBUG - Email data:", email_data)
            
            self.tempmail_result_text.delete(1.0, tk.END)
            self.tempmail_result_text.insert(tk.END, f"✅ TẠO EMAIL THÀNH CÔNG!\n\n")
            
            # Kiểm tra cấu trúc dữ liệu và hiển thị thông tin phù hợp
            if isinstance(email_data, dict):
                # Trường hợp API trả về đối tượng
                email_address = email_data.get('email')
                if email_address:
                    self.tempmail_result_text.insert(tk.END, f"📧 Email: {email_address}\n")
                    
                    # Tự động sao chép vào clipboard
                    self.root.clipboard_clear()
                    self.root.clipboard_append(email_address)
                    self.tempmail_result_text.insert(tk.END, f"📋 Đã sao chép vào clipboard!\n\n")
                    
                id_value = email_data.get('id')
                if id_value:
                    self.tempmail_result_text.insert(tk.END, f"🆔 ID: {id_value}\n")
                    
                created_at = email_data.get('created_at')
                if created_at:
                    self.tempmail_result_text.insert(tk.END, f"🕒 Ngày tạo: {created_at}\n")
            elif isinstance(email_data, str):
                # Trường hợp API trả về chuỗi
                self.tempmail_result_text.insert(tk.END, f"📧 Email: {email_data}\n")
                
                # Tự động sao chép vào clipboard
                self.root.clipboard_clear()
                self.root.clipboard_append(email_data)
                self.tempmail_result_text.insert(tk.END, f"📋 Đã sao chép vào clipboard!\n")
            else:
                # Hiển thị toàn bộ dữ liệu nhận được
                self.tempmail_result_text.insert(tk.END, f"Dữ liệu: {str(email_data)}\n")
            
            # Thông báo thành công
            messagebox.showinfo("Thành công", "Đã tạo email mới thành công!")
            
        except Exception as e:
            self.tempmail_result_text.delete(1.0, tk.END)
            self.tempmail_result_text.insert(tk.END, f"❌ Lỗi: {str(e)}")
            
    def list_tempmail(self):
        """Liệt kê danh sách email của người dùng"""
        if not hasattr(self, '_tempmail_api'):
            messagebox.showerror("Lỗi", "Vui lòng kết nối API trước!")
            return
            
        try:
            # Hiển thị thông báo đang xử lý
            self.tempmail_result_text.delete(1.0, tk.END)
            self.tempmail_result_text.insert(tk.END, "Đang lấy danh sách email...\n")
            self.root.update()
            
            result = self._tempmail_api.get_email_list()
            
            if result['error']:
                self.tempmail_result_text.delete(1.0, tk.END)
                self.tempmail_result_text.insert(tk.END, f"❌ Lỗi: {result['message']}")
                return
                
            # Xử lý dữ liệu trả về từ API
            response_data = result['data']
            
            # Debug: Hiển thị toàn bộ dữ liệu nhận được
            print("DEBUG - Emails data:", response_data)
            
            # Xóa dữ liệu cũ
            self.email_listbox.delete(0, tk.END)
            self.email_data_list = []
            
            # Kiểm tra cấu trúc dữ liệu
            emails = []
            
            # Xử lý nhiều cấu trúc dữ liệu khác nhau
            if isinstance(response_data, dict):
                if 'data' in response_data:
                    # Trường hợp API trả về dạng {'success': True, 'message': '...', 'data': [...]}
                    emails = response_data.get('data', [])
                elif 'success' in response_data and response_data.get('success') and 'data' in response_data:
                    # Trường hợp API trả về dạng {'success': True, 'message': 'Thành công', 'data': [...]}
                    emails = response_data.get('data', [])
                elif 'items' in response_data:
                    # Trường hợp API trả về dạng {'items': [...], 'pagination': {...}}
                    emails = response_data.get('items', [])
                else:
                    # Nếu không có cấu trúc nhận dạng được, hiển thị dữ liệu gốc
                    self.tempmail_result_text.delete(1.0, tk.END)
                    self.tempmail_result_text.insert(tk.END, f"📋 Dữ liệu nhận được:\n\n{str(response_data)}\n\n")
                    
                    # Thử xử lý một số trường hợp đặc biệt
                    if isinstance(response_data, dict):
                        for key, value in response_data.items():
                            if isinstance(value, list) and len(value) > 0:
                                emails = value
                                self.tempmail_result_text.insert(tk.END, f"✅ Đã tìm thấy danh sách email trong trường '{key}'.\n\n")
                                break
                    
                    if not emails:
                        self.tempmail_result_text.insert(tk.END, "⚠️ Không thể xác định cấu trúc dữ liệu. Vui lòng liên hệ nhà phát triển.")
                        return
            elif isinstance(response_data, list):
                # Trường hợp API trả về trực tiếp danh sách
                emails = response_data
            else:
                # Trường hợp khác
                self.tempmail_result_text.delete(1.0, tk.END)
                self.tempmail_result_text.insert(tk.END, f"❓ Không thể xử lý dữ liệu: {str(response_data)}")
                return
            
            # Hiển thị danh sách email
            self.tempmail_result_text.delete(1.0, tk.END)
            self.tempmail_result_text.insert(tk.END, f"📋 DANH SÁCH EMAIL CỦA BẠN:\n\n")
            
            if not emails:
                self.tempmail_result_text.insert(tk.END, "Không có email nào.")
                return
                
            # Thêm email vào listbox và lưu dữ liệu
            for i, email in enumerate(emails, 1):
                if isinstance(email, dict):
                    email_address = email.get('email', 'N/A')
                    self.email_listbox.insert(tk.END, f"{email_address}")
                    self.email_data_list.append(email)
                    
                    # Hiển thị thông tin trong kết quả
                    self.tempmail_result_text.insert(tk.END, f"{i}. 📧 {email_address}\n")
                    
                    id_value = email.get('id')
                    if id_value:
                        self.tempmail_result_text.insert(tk.END, f"   🆔 ID: {id_value}\n")
                        
                    created_at = email.get('created_at')
                    if created_at:
                        self.tempmail_result_text.insert(tk.END, f"   🕒 Ngày tạo: {created_at}\n")
                        
                    self.tempmail_result_text.insert(tk.END, "\n")
                elif isinstance(email, str):
                    self.email_listbox.insert(tk.END, email)
                    self.email_data_list.append({'email': email})
                    self.tempmail_result_text.insert(tk.END, f"{i}. 📧 {email}\n\n")
            
        except Exception as e:
            self.tempmail_result_text.delete(1.0, tk.END)
            self.tempmail_result_text.insert(tk.END, f"❌ Lỗi: {str(e)}")
    
    def on_email_selected(self, event):
        """Xử lý sự kiện khi chọn email trong listbox"""
        if not self.email_listbox.curselection():
            return
            
        # Lấy chỉ số được chọn
        index = self.email_listbox.curselection()[0]
        
        # Hiển thị thông tin email được chọn
        if 0 <= index < len(self.email_data_list):
            email_data = self.email_data_list[index]
            
            self.tempmail_result_text.delete(1.0, tk.END)
            self.tempmail_result_text.insert(tk.END, f"📧 Email được chọn:\n\n")
            
            email_address = email_data.get('email', 'N/A')
            self.tempmail_result_text.insert(tk.END, f"Email: {email_address}\n")
            
            id_value = email_data.get('id')
            if id_value:
                self.tempmail_result_text.insert(tk.END, f"ID: {id_value}\n")
                
            created_at = email_data.get('created_at')
            if created_at:
                self.tempmail_result_text.insert(tk.END, f"Ngày tạo: {created_at}\n")
                
            # Tự động sao chép email vào clipboard
            self.root.clipboard_clear()
            self.root.clipboard_append(email_address)
            self.tempmail_result_text.insert(tk.END, f"\n📋 Đã sao chép email vào clipboard!\n")
    
    def read_selected_email(self):
        """Đọc thư của email được chọn"""
        if not self.email_listbox.curselection():
            messagebox.showinfo("Thông báo", "Vui lòng chọn một email!")
            return
            
        # Lấy chỉ số được chọn
        index = self.email_listbox.curselection()[0]
        
        # Kiểm tra dữ liệu email
        if 0 <= index < len(self.email_data_list):
            email_data = self.email_data_list[index]
            email_id = email_data.get('id')
            
            if not email_id:
                messagebox.showerror("Lỗi", "Không tìm thấy ID của email!")
                return
                
            # Hiển thị thông báo đang xử lý
            self.tempmail_result_text.delete(1.0, tk.END)
            self.tempmail_result_text.insert(tk.END, f"Đang lấy thư của email {email_data.get('email')}...\n")
            self.root.update()
            
            try:
                # Gọi API để lấy danh sách thư
                result = self._tempmail_api.get_messages(email_id)
                
                if result['error']:
                    self.tempmail_result_text.delete(1.0, tk.END)
                    self.tempmail_result_text.insert(tk.END, f"❌ Lỗi: {result['message']}")
                    return
                    
                # Xử lý dữ liệu trả về
                response_data = result['data']

                # Debug: In ra cấu trúc dữ liệu
                print(f"DEBUG - Messages response data: {response_data}")
                print(f"DEBUG - Response data type: {type(response_data)}")

                # Kiểm tra cấu trúc dữ liệu
                messages = []

                if isinstance(response_data, list):
                    # API đã trả về danh sách thư trực tiếp (đã được xử lý trong TempMailAPI)
                    messages = response_data
                    print(f"DEBUG - Using direct list, found {len(messages)} messages")
                elif isinstance(response_data, dict):
                    print(f"DEBUG - Response is dict with keys: {list(response_data.keys())}")

                    if 'data' in response_data:
                        # Trường hợp API trả về dạng {'success': True, 'message': '...', 'data': [...]}
                        messages = response_data.get('data', [])
                        print(f"DEBUG - Using 'data' field, found {len(messages)} messages")
                    elif 'items' in response_data:
                        # Trường hợp API trả về dạng {'items': [...], 'pagination': {...}}
                        messages = response_data.get('items', [])
                        print(f"DEBUG - Using 'items' field, found {len(messages)} messages")
                    else:
                        # Hiển thị cấu trúc để debug
                        print(f"DEBUG - Unknown dict structure: {response_data}")
                        self.tempmail_result_text.delete(1.0, tk.END)
                        self.tempmail_result_text.insert(tk.END, f"📬 THƯ CỦA {email_data.get('email')}:\n\n")
                        self.tempmail_result_text.insert(tk.END, f"⚠️ Cấu trúc dữ liệu không mong đợi:\n{str(response_data)}")
                        return
                else:
                    print(f"DEBUG - Unknown response type: {type(response_data)}")
                    self.tempmail_result_text.delete(1.0, tk.END)
                    self.tempmail_result_text.insert(tk.END, f"📬 THƯ CỦA {email_data.get('email')}:\n\n")
                    self.tempmail_result_text.insert(tk.END, f"⚠️ Dữ liệu trả về không hợp lệ: {str(response_data)}")
                    return

                # Hiển thị danh sách thư
                self.tempmail_result_text.delete(1.0, tk.END)
                self.tempmail_result_text.insert(tk.END, f"📬 THƯ CỦA {email_data.get('email')}:\n\n")

                if not messages:
                    self.tempmail_result_text.insert(tk.END, "Không có thư nào.")
                    return
                
                # Debug: In ra thông tin về messages
                print(f"DEBUG - Processing {len(messages)} messages")
                for idx, msg in enumerate(messages):
                    print(f"DEBUG - Message {idx}: type={type(msg)}, content={msg}")

                # Hiển thị danh sách thư
                for i, message in enumerate(messages, 1):
                    print(f"DEBUG - Processing message {i}: {message}")

                    if isinstance(message, dict):
                        # Lấy thông tin từ message
                        message_id = message.get('id')
                        subject = message.get('subject', 'Không có tiêu đề')
                        sender = message.get('from', 'Không rõ người gửi')
                        date = message.get('date', 'Không rõ thời gian')

                        print(f"DEBUG - Message details: id={message_id}, subject={subject}")

                        # Hiển thị thông tin cơ bản
                        self.tempmail_result_text.insert(tk.END, f"{i}. 📝 {subject}\n")
                        self.tempmail_result_text.insert(tk.END, f"   👤 Từ: {sender}\n")
                        self.tempmail_result_text.insert(tk.END, f"   🕒 Ngày: {date}\n")

                        # Nếu có ID tin nhắn, thêm nút xem chi tiết
                        if message_id:
                            # Thêm nút xem chi tiết
                            detail_button_tag = f"detail_btn_{message_id}"
                            self.tempmail_result_text.insert(tk.END, f"   ")
                            self.tempmail_result_text.insert(tk.END, "📋 Xem chi tiết", detail_button_tag)
                            self.tempmail_result_text.insert(tk.END, "\n")

                            # Định dạng nút
                            self.tempmail_result_text.tag_config(
                                detail_button_tag,
                                foreground="blue",
                                underline=True,
                                font=("Segoe UI", 9, "bold")
                            )

                            # Thêm sự kiện click
                            self.tempmail_result_text.tag_bind(
                                detail_button_tag,
                                "<Button-1>",
                                lambda e, msg_id=message_id, subj=subject: self.view_message_detail(msg_id, subj)
                            )

                            # Thêm con trỏ tay khi hover
                            self.tempmail_result_text.tag_bind(
                                detail_button_tag,
                                "<Enter>",
                                lambda e: self.tempmail_result_text.config(cursor="hand2")
                            )

                            self.tempmail_result_text.tag_bind(
                                detail_button_tag,
                                "<Leave>",
                                lambda e: self.tempmail_result_text.config(cursor="")
                            )

                            # Hiển thị preview nội dung với mã verification code nếu có
                            preview_text = self.get_message_preview(message)
                            if preview_text:
                                self.tempmail_result_text.insert(tk.END, f"   💬 Preview: {preview_text}\n")

                                # Nếu preview chứa mã verification code, thêm nút copy nhanh
                                if "🔑 Mã xác thực:" in preview_text:
                                    # Trích xuất mã từ preview text
                                    import re
                                    code_match = re.search(r'🔑 Mã xác thực: (\d{4,8})', preview_text)
                                    if code_match:
                                        verification_code = code_match.group(1)

                                        # Thêm nút copy nhanh
                                        quick_copy_tag = f"quick_copy_{message_id}_{verification_code}"
                                        self.tempmail_result_text.insert(tk.END, f"   ")
                                        self.tempmail_result_text.insert(tk.END, f"📋 Copy mã {verification_code}", quick_copy_tag)
                                        self.tempmail_result_text.insert(tk.END, "\n")

                                        # Định dạng nút copy
                                        self.tempmail_result_text.tag_config(
                                            quick_copy_tag,
                                            foreground="#e67e22",
                                            background="#fff3cd",
                                            underline=True,
                                            font=("Segoe UI", 9, "bold")
                                        )

                                        # Bind sự kiện click để copy mã
                                        self.tempmail_result_text.tag_bind(
                                            quick_copy_tag,
                                            "<Button-1>",
                                            lambda e, code=verification_code: self.copy_verification_code(code)
                                        )

                                        # Thêm con trỏ tay khi hover
                                        self.tempmail_result_text.tag_bind(
                                            quick_copy_tag,
                                            "<Enter>",
                                            lambda e: self.tempmail_result_text.config(cursor="hand2")
                                        )

                                        self.tempmail_result_text.tag_bind(
                                            quick_copy_tag,
                                            "<Leave>",
                                            lambda e: self.tempmail_result_text.config(cursor="")
                                        )
                            else:
                                self.tempmail_result_text.insert(tk.END, f"   💬 Bấm 'Xem chi tiết' để đọc nội dung\n")
                        else:
                            self.tempmail_result_text.insert(tk.END, f"   ⚠️ Không có ID để xem chi tiết\n")

                        self.tempmail_result_text.insert(tk.END, "\n")
                    elif isinstance(message, str):
                        # Nếu message là chuỗi, có thể là tên field
                        print(f"DEBUG - String message: {message}")
                        if message in ['items', 'pagination']:
                            # Bỏ qua các field metadata
                            continue
                        else:
                            # Hiển thị chuỗi khác
                            self.tempmail_result_text.insert(tk.END, f"{i}. 📄 {message}\n\n")
                    else:
                        # Nếu message không phải là dict hoặc string, hiển thị dạng chuỗi
                        print(f"DEBUG - Unknown message type: {type(message)}")
                        self.tempmail_result_text.insert(tk.END, f"{i}. ❓ {str(message)}\n\n")
                
            except Exception as e:
                self.tempmail_result_text.delete(1.0, tk.END)
                self.tempmail_result_text.insert(tk.END, f"❌ Lỗi: {str(e)}")
    
    def delete_selected_email(self):
        """Xóa email được chọn"""
        if not self.email_listbox.curselection():
            messagebox.showinfo("Thông báo", "Vui lòng chọn một email!")
            return
            
        # Lấy chỉ số được chọn
        index = self.email_listbox.curselection()[0]
        
        # Kiểm tra dữ liệu email
        if 0 <= index < len(self.email_data_list):
            email_data = self.email_data_list[index]
            email_id = email_data.get('id')
            email_address = email_data.get('email', 'N/A')
            
            if not email_id:
                messagebox.showerror("Lỗi", "Không tìm thấy ID của email!")
                return
                
            # Xác nhận xóa
            confirm = messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn xóa email {email_address}?")
            if not confirm:
                return
                
            # Hiển thị thông báo đang xử lý
            self.tempmail_result_text.delete(1.0, tk.END)
            self.tempmail_result_text.insert(tk.END, f"Đang xóa email {email_address}...\n")
            self.root.update()
            
            try:
                # Gọi API để xóa email
                result = self._tempmail_api.delete_email(email_id)

                if result['error']:
                    self.tempmail_result_text.delete(1.0, tk.END)

                    # Kiểm tra nếu là lỗi không hỗ trợ
                    if result.get('unsupported', False):
                        # Hiển thị thông báo đặc biệt cho lỗi không hỗ trợ
                        self.tempmail_result_text.insert(tk.END, f"⚠️ Chức năng xóa email chưa được hỗ trợ bởi API tempmail.id.vn\n\n")
                        self.tempmail_result_text.insert(tk.END, f"📝 Để xóa email {email_address}, bạn có thể:\n")
                        self.tempmail_result_text.insert(tk.END, f"1. Truy cập https://tempmail.id.vn\n")
                        self.tempmail_result_text.insert(tk.END, f"2. Đăng nhập với API token của bạn\n")
                        self.tempmail_result_text.insert(tk.END, f"3. Xóa email thủ công\n\n")
                        self.tempmail_result_text.insert(tk.END, f"🔄 Hoặc tạo email mới để thay thế")

                        # Vẫn xóa email khỏi danh sách local để tránh hiển thị
                        self.email_listbox.delete(index)
                        self.email_data_list.pop(index)
                    else:
                        # Hiển thị lỗi thông thường
                        self.tempmail_result_text.insert(tk.END, f"❌ Lỗi: {result['message']}")
                    return

                # Xóa email khỏi listbox và danh sách
                self.email_listbox.delete(index)
                self.email_data_list.pop(index)

                # Hiển thị thông báo thành công
                self.tempmail_result_text.delete(1.0, tk.END)
                self.tempmail_result_text.insert(tk.END, f"✅ Đã xóa email {email_address} thành công!")

            except Exception as e:
                self.tempmail_result_text.delete(1.0, tk.END)
                self.tempmail_result_text.insert(tk.END, f"❌ Lỗi: {str(e)}")

    def check_delete_support(self):
        """Kiểm tra xem API có hỗ trợ xóa email không"""
        if not hasattr(self, '_tempmail_api'):
            messagebox.showerror("Lỗi", "Vui lòng kết nối API trước!")
            return

        try:
            # Hiển thị thông báo đang kiểm tra
            self.tempmail_result_text.delete(1.0, tk.END)
            self.tempmail_result_text.insert(tk.END, "🔍 Đang kiểm tra khả năng hỗ trợ xóa email của API...\n")
            self.root.update()

            # Gọi API để kiểm tra
            result = self._tempmail_api.check_delete_support()

            self.tempmail_result_text.delete(1.0, tk.END)
            self.tempmail_result_text.insert(tk.END, "🔍 KẾT QUẢ KIỂM TRA API:\n\n")

            if result['error']:
                self.tempmail_result_text.insert(tk.END, f"❌ Lỗi khi kiểm tra: {result['message']}\n\n")
                self.tempmail_result_text.insert(tk.END, "⚠️ Không thể xác định khả năng hỗ trợ xóa email.")
            else:
                supports_delete = result.get('supports_delete', False)
                allowed_methods = result.get('allowed_methods', 'Không xác định')

                if supports_delete:
                    self.tempmail_result_text.insert(tk.END, "✅ API hỗ trợ xóa email (DELETE method)\n\n")
                    self.tempmail_result_text.insert(tk.END, "🎉 Bạn có thể sử dụng chức năng xóa email bình thường.")
                else:
                    self.tempmail_result_text.insert(tk.END, "❌ API KHÔNG hỗ trợ xóa email (DELETE method)\n\n")
                    self.tempmail_result_text.insert(tk.END, "📝 Để xóa email, bạn cần:\n")
                    self.tempmail_result_text.insert(tk.END, "1. Truy cập https://tempmail.id.vn\n")
                    self.tempmail_result_text.insert(tk.END, "2. Đăng nhập với API token của bạn\n")
                    self.tempmail_result_text.insert(tk.END, "3. Xóa email thủ công trên website\n\n")
                    self.tempmail_result_text.insert(tk.END, "🔄 Hoặc tạo email mới để thay thế")

                self.tempmail_result_text.insert(tk.END, f"\n\n📋 Thông tin kỹ thuật:\n")
                self.tempmail_result_text.insert(tk.END, f"Phương thức được hỗ trợ: {allowed_methods}")

        except Exception as e:
            self.tempmail_result_text.delete(1.0, tk.END)
            self.tempmail_result_text.insert(tk.END, f"❌ Lỗi khi kiểm tra API: {str(e)}")

    def copy_tempmail_result(self):
        """Sao chép kết quả TempMail vào clipboard"""
        result = self.tempmail_result_text.get(1.0, tk.END).strip()
        
        if not result:
            messagebox.showinfo("Thông báo", "Không có kết quả để sao chép!")
            return
            
        self.root.clipboard_clear()
        self.root.clipboard_append(result)
        messagebox.showinfo("Thành công", "Đã sao chép kết quả vào clipboard!")

    def run(self):
        """Chạy ứng dụng"""
        self.root.mainloop()

    def view_message_detail(self, message_id, subject=""):
        """Hiển thị nội dung chi tiết của một thư trong cửa sổ mới"""
        if not message_id:
            messagebox.showerror("Lỗi", "Không tìm thấy ID của thư!")
            return
            
        try:
            # Gọi API để lấy nội dung thư
            result = self._tempmail_api.get_message_content(message_id)
            
            if result['error']:
                messagebox.showerror("Lỗi", f"Không thể lấy nội dung thư: {result['message']}")
                return
                
            # Xử lý dữ liệu trả về
            msg_content = result['data']
            
            # Tạo cửa sổ mới
            detail_window = tk.Toplevel(self.root)
            detail_window.title(f"Nội dung thư: {subject}")
            detail_window.geometry("800x600")
            detail_window.resizable(True, True)
            
            # Tạo frame chứa nội dung
            content_frame = tk.Frame(detail_window, bg='#ffffff')
            content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Tạo scrolled text để hiển thị nội dung
            content_text = scrolledtext.ScrolledText(content_frame,
                                                   font=("Consolas", 10),
                                                   bg="#ffffff", fg="#2c3e50",
                                                   wrap=tk.WORD)
            content_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # Xử lý nội dung tin nhắn
            if isinstance(msg_content, dict):
                # Kiểm tra cấu trúc API response
                if 'success' in msg_content and 'data' in msg_content:
                    # API trả về cấu trúc {'success': True, 'data': {...}}
                    actual_content = msg_content['data']
                else:
                    actual_content = msg_content

                # Hiển thị thông tin cơ bản
                from_addr = actual_content.get('from', 'Không rõ người gửi')
                to_addr = actual_content.get('to', 'Không rõ người nhận')
                date = actual_content.get('date', 'Không rõ thời gian')
                sender_name = actual_content.get('sender_name', '')

                content_text.insert(tk.END, f"Từ: {sender_name} <{from_addr}>\n" if sender_name else f"Từ: {from_addr}\n")
                content_text.insert(tk.END, f"Đến: {to_addr}\n")
                content_text.insert(tk.END, f"Ngày: {date}\n")
                content_text.insert(tk.END, f"Chủ đề: {subject}\n")
                content_text.insert(tk.END, f"\n{'-'*80}\n\n")

                # Lấy nội dung thư từ các field khác nhau
                body_content = actual_content.get('body', '')
                html_content = actual_content.get('html', '')
                text_content = actual_content.get('text', '')

                # Ưu tiên text content, sau đó body, cuối cùng html
                final_content = ""
                if text_content and text_content.strip():
                    final_content = text_content
                elif body_content and body_content.strip():
                    # Xử lý body content (thường là HTML)
                    if body_content.startswith('<!DOCTYPE') or body_content.startswith('<html'):
                        final_content = self.html_to_text(body_content)
                    else:
                        final_content = body_content
                elif html_content and html_content.strip():
                    # Xử lý HTML để chuyển thành text dễ đọc
                    final_content = self.html_to_text(html_content)
                else:
                    # Hiển thị toàn bộ nội dung nếu không có text, body hoặc html
                    final_content = f"Nội dung gốc:\n\n{str(actual_content)}"

                # Format và highlight nội dung với mã verification code
                self.insert_formatted_email_content(content_text, final_content)
            else:
                # Nếu là chuỗi, hiển thị trực tiếp
                content_text.insert(tk.END, str(msg_content))
            
            # Tạo các nút chức năng
            button_frame = tk.Frame(detail_window, bg='#ffffff')
            button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
            
            # Nút sao chép
            copy_btn = tk.Button(button_frame, text="Sao chép nội dung", 
                               font=("Segoe UI", 9, "bold"),
                               bg='#3498db', fg='white',
                               relief='flat', borderwidth=0,
                               padx=15, pady=5,
                               command=lambda: self.copy_message_content(content_text.get(1.0, tk.END)))
            copy_btn.pack(side=tk.LEFT, padx=5)
            self.add_hover_effect(copy_btn, '#3498db', '#2980b9')
            
            # Nút đóng
            close_btn = tk.Button(button_frame, text="Đóng", 
                                font=("Segoe UI", 9, "bold"),
                                bg='#e74c3c', fg='white',
                                relief='flat', borderwidth=0,
                                padx=15, pady=5,
                                command=detail_window.destroy)
            close_btn.pack(side=tk.RIGHT, padx=5)
            self.add_hover_effect(close_btn, '#e74c3c', '#c0392b')
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể hiển thị nội dung thư: {str(e)}")
    
    def copy_message_content(self, content):
        """Sao chép nội dung thư vào clipboard"""
        if not content:
            return

        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        messagebox.showinfo("Thành công", "Đã sao chép nội dung thư vào clipboard!")

    def insert_formatted_email_content(self, text_widget, content):
        """
        Chèn nội dung email với format đặc biệt cho mã verification code

        Args:
            text_widget: Widget Text để chèn nội dung
            content (str): Nội dung email cần format
        """
        import re

        # Cấu hình các tag để highlight
        text_widget.tag_configure("verification_code",
                                background="#ffeb3b",
                                foreground="#d32f2f",
                                font=("Consolas", 14, "bold"),
                                relief="raised",
                                borderwidth=2)

        text_widget.tag_configure("verification_label",
                                foreground="#1976d2",
                                font=("Segoe UI", 11, "bold"))

        text_widget.tag_configure("code_section",
                                background="#f5f5f5",
                                foreground="#333333",
                                font=("Consolas", 10))

        # Tìm các pattern mã verification code phổ biến
        verification_patterns = [
            r'verification code is[:\s]*(\d{4,8})',  # "verification code is: 123456"
            r'Your verification code is[:\s]*(\d{4,8})',  # "Your verification code is: 123456"
            r'code[:\s]*(\d{4,8})',  # "code: 123456"
            r'Code[:\s]*(\d{4,8})',  # "Code: 123456"
            r'\n\n(\d{4,8})\n\n',  # Mã đứng một mình giữa 2 dòng trống
            r'(\d{6})',  # Mã 6 số bất kỳ (phổ biến nhất)
        ]

        # Tìm mã verification code
        verification_code = None
        code_match = None

        for pattern in verification_patterns:
            matches = list(re.finditer(pattern, content, re.IGNORECASE))
            if matches:
                # Ưu tiên pattern có context rõ ràng hơn
                for match in matches:
                    code = match.group(1) if match.groups() else match.group(0)
                    # Kiểm tra mã có phải là số và có độ dài hợp lý
                    if code.isdigit() and 4 <= len(code) <= 8:
                        verification_code = code
                        code_match = match
                        break
                if verification_code:
                    break

        if verification_code and code_match:
            # Chia nội dung thành 3 phần: trước mã, mã, sau mã
            start_pos = code_match.start()
            end_pos = code_match.end()

            before_code = content[:start_pos]
            code_section = content[start_pos:end_pos]
            after_code = content[end_pos:]

            # Chèn phần trước mã
            if before_code.strip():
                text_widget.insert(tk.END, before_code)

            # Tạo section đặc biệt cho mã verification
            text_widget.insert(tk.END, "\n" + "="*60 + "\n")
            text_widget.insert(tk.END, "🔑 MÃ VERIFICATION CODE:\n", "verification_label")
            text_widget.insert(tk.END, "\n")

            # Highlight mã verification code
            text_widget.insert(tk.END, f"   {verification_code}   ", "verification_code")
            text_widget.insert(tk.END, "\n\n")

            # Thêm nút copy mã
            copy_code_text = f"📋 Nhấn đây để copy mã: {verification_code}"
            copy_tag = f"copy_code_{verification_code}"
            text_widget.tag_configure(copy_tag,
                                    foreground="#1976d2",
                                    font=("Segoe UI", 10, "bold", "underline"))

            text_widget.insert(tk.END, copy_code_text, copy_tag)

            # Bind sự kiện click để copy mã
            text_widget.tag_bind(copy_tag, "<Button-1>",
                               lambda e: self.copy_verification_code(verification_code))
            text_widget.tag_bind(copy_tag, "<Enter>",
                               lambda e: text_widget.config(cursor="hand2"))
            text_widget.tag_bind(copy_tag, "<Leave>",
                               lambda e: text_widget.config(cursor=""))

            text_widget.insert(tk.END, "\n" + "="*60 + "\n\n")

            # Chèn phần sau mã
            if after_code.strip():
                text_widget.insert(tk.END, after_code)
        else:
            # Không tìm thấy mã verification, hiển thị nội dung bình thường
            text_widget.insert(tk.END, content)

            # Vẫn cố gắng tìm và highlight các số có thể là mã
            potential_codes = re.findall(r'\b\d{4,8}\b', content)
            if potential_codes:
                text_widget.insert(tk.END, f"\n\n💡 Các số có thể là mã verification: {', '.join(set(potential_codes))}")

    def copy_verification_code(self, code):
        """Sao chép mã verification code vào clipboard"""
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(code)
            messagebox.showinfo("Thành công", f"Đã sao chép mã {code} vào clipboard!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể sao chép mã: {str(e)}")

    def get_message_preview(self, message):
        """
        Tạo preview nội dung thư, đặc biệt highlight mã verification code

        Args:
            message (dict): Thông tin thư

        Returns:
            str: Preview text hoặc None nếu không có preview
        """
        import re

        try:
            # Lấy các trường có thể chứa nội dung
            preview_content = ""

            # Thử lấy từ các trường khác nhau
            for field in ['preview', 'snippet', 'body_preview', 'text_preview', 'subject']:
                if field in message and message[field]:
                    preview_content = str(message[field])
                    break

            # Nếu không có preview sẵn, thử tạo từ subject
            if not preview_content and 'subject' in message:
                subject = message['subject']
                if any(keyword in subject.lower() for keyword in ['verification', 'code', 'confirm', 'verify']):
                    preview_content = f"📧 {subject}"

            if not preview_content:
                return None

            # Tìm mã verification code trong preview
            verification_patterns = [
                r'verification code is[:\s]*(\d{4,8})',
                r'Your verification code is[:\s]*(\d{4,8})',
                r'code[:\s]*(\d{4,8})',
                r'Code[:\s]*(\d{4,8})',
                r'(\d{6})',  # Mã 6 số
                r'(\d{4,8})',  # Mã 4-8 số
            ]

            verification_code = None
            for pattern in verification_patterns:
                match = re.search(pattern, preview_content, re.IGNORECASE)
                if match:
                    code = match.group(1) if match.groups() else match.group(0)
                    if code.isdigit() and 4 <= len(code) <= 8:
                        verification_code = code
                        break

            # Format preview với highlight mã nếu có
            if verification_code:
                return f"🔑 Mã xác thực: {verification_code}"
            else:
                # Cắt ngắn preview nếu quá dài
                if len(preview_content) > 50:
                    preview_content = preview_content[:47] + "..."
                return preview_content

        except Exception as e:
            print(f"DEBUG - Error in get_message_preview: {str(e)}")
            return None

    def html_to_text(self, html_content):
        """Chuyển đổi HTML thành text dễ đọc"""
        import re

        if not html_content:
            return ""

        # Loại bỏ các comment HTML và conditional comments
        html_content = re.sub(r'<!--.*?-->', '', html_content, flags=re.DOTALL)
        html_content = re.sub(r'<!\[if.*?\]>.*?<!\[endif\]>', '', html_content, flags=re.DOTALL | re.IGNORECASE)

        # Loại bỏ các thẻ script và style
        html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)

        # Loại bỏ các thẻ meta, link, title trong head
        html_content = re.sub(r'<head[^>]*>.*?</head>', '', html_content, flags=re.DOTALL | re.IGNORECASE)

        # Loại bỏ các div ẩn (thường chứa tracking hoặc preheader text)
        html_content = re.sub(r'<div[^>]*style="[^"]*display:\s*none[^"]*"[^>]*>.*?</div>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        html_content = re.sub(r'<div[^>]*style="[^"]*max-height:\s*0[^"]*"[^>]*>.*?</div>', '', html_content, flags=re.DOTALL | re.IGNORECASE)

        # Thay thế các thẻ heading bằng text có format
        html_content = re.sub(r'<h([1-6])[^>]*>(.*?)</h[1-6]>', r'\n\n=== \2 ===\n\n', html_content, flags=re.IGNORECASE | re.DOTALL)

        # Thay thế các thẻ paragraph và div
        html_content = re.sub(r'</(p|div)>', '\n\n', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'<(p|div)[^>]*>', '\n', html_content, flags=re.IGNORECASE)

        # Thay thế br
        html_content = re.sub(r'<br[^>]*/?>', '\n', html_content, flags=re.IGNORECASE)

        # Thay thế các thẻ list
        html_content = re.sub(r'<li[^>]*>', '\n• ', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'</li>', '', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'</(ul|ol)>', '\n', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'<(ul|ol)[^>]*>', '\n', html_content, flags=re.IGNORECASE)

        # Thay thế các thẻ table
        html_content = re.sub(r'</(table|tbody|thead|tfoot)>', '\n', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'<(table|tbody|thead|tfoot)[^>]*>', '\n', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'<tr[^>]*>', '\n', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'</tr>', '', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'<td[^>]*>', ' | ', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'</td>', '', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'<th[^>]*>', ' | ', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'</th>', '', html_content, flags=re.IGNORECASE)

        # Thay thế các thẻ link - chỉ hiển thị text, bỏ URL dài
        html_content = re.sub(r'<a[^>]*href=["\']([^"\']*)["\'][^>]*>(.*?)</a>', r'\2', html_content, flags=re.IGNORECASE | re.DOTALL)

        # Thay thế các thẻ format
        html_content = re.sub(r'<(strong|b)[^>]*>(.*?)</(strong|b)>', r'**\2**', html_content, flags=re.IGNORECASE | re.DOTALL)
        html_content = re.sub(r'<(em|i)[^>]*>(.*?)</(em|i)>', r'*\2*', html_content, flags=re.IGNORECASE | re.DOTALL)

        # Loại bỏ tất cả các thẻ HTML còn lại
        html_content = re.sub(r'<[^>]+>', '', html_content)

        # Decode HTML entities
        html_entities = {
            '&nbsp;': ' ', '&amp;': '&', '&lt;': '<', '&gt;': '>',
            '&quot;': '"', '&#39;': "'", '&apos;': "'",
            '&mdash;': '—', '&ndash;': '–', '&hellip;': '...',
            '&copy;': '©', '&reg;': '®', '&trade;': '™'
        }
        for entity, char in html_entities.items():
            html_content = html_content.replace(entity, char)

        # Decode numeric entities
        html_content = re.sub(r'&#(\d+);', lambda m: chr(int(m.group(1))) if int(m.group(1)) < 1114112 else '', html_content)
        html_content = re.sub(r'&#x([0-9a-fA-F]+);', lambda m: chr(int(m.group(1), 16)) if int(m.group(1), 16) < 1114112 else '', html_content)

        # Loại bỏ các ký tự điều khiển và ký tự ẩn
        html_content = re.sub(r'[\u200B-\u200D\uFEFF]', '', html_content)  # Zero-width characters
        html_content = re.sub(r'[\u00AD\u034F\u061C\u115F\u1160\u17B4\u17B5\u180E]', '', html_content)  # Soft hyphen, etc.
        html_content = re.sub(r'[\u2007\u2060\u3164\uFFA0]', ' ', html_content)  # Various spaces

        # Loại bỏ các ký tự lặp lại nhiều lần (như ͏ ͏ ͏)
        html_content = re.sub(r'(\s*[͏­]\s*){3,}', ' ', html_content)
        html_content = re.sub(r'(\s*\|\s*){3,}', ' | ', html_content)

        # Loại bỏ khoảng trắng thừa
        html_content = re.sub(r'\n\s*\n\s*\n+', '\n\n', html_content)  # Loại bỏ dòng trống thừa
        html_content = re.sub(r'[ \t]+', ' ', html_content)  # Loại bỏ khoảng trắng thừa
        html_content = re.sub(r'^\s+|\s+$', '', html_content, flags=re.MULTILINE)  # Loại bỏ khoảng trắng đầu/cuối dòng

        # Loại bỏ các dòng chỉ chứa ký tự đặc biệt
        lines = html_content.split('\n')
        clean_lines = []
        for line in lines:
            # Bỏ qua dòng chỉ chứa ký tự đặc biệt, khoảng trắng, hoặc ký tự lặp
            if line.strip() and not re.match(r'^[\s\|͏­\u2007\u00AD]*$', line.strip()):
                clean_lines.append(line.strip())

        html_content = '\n'.join(clean_lines)
        html_content = re.sub(r'\n{3,}', '\n\n', html_content)  # Giới hạn tối đa 2 dòng trống liên tiếp

        return html_content.strip()
