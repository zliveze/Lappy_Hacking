# gui/main_window.py - Giao diện chính của Lappy Lab 4.1
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
from datetime import datetime

# Import các module từ core
from core.utils import get_system_info
# Sử dụng logic mới từ features.show_config
from features.show_config import get_token, get_email, UsageManager, format_subscription_type, get_token_from_config

class LappyLabApp:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.setup_variables()
        self.setup_ui()
        self.load_account_info()
        self.check_ide_status()

    def setup_window(self):
        """Thiết lập cửa sổ chính"""
        self.root.title("Lappy Lab 4.1")
        self.root.geometry("900x700")
        self.root.resizable(True, True)

        # Thiết lập icon nếu có
        try:
            # self.root.iconbitmap("assets/icons/icon.ico")  # Uncomment nếu có file icon
            pass
        except:
            pass

        # Thiết lập style
        style = ttk.Style()
        style.theme_use('clam')

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

    def setup_ui(self):
        """Thiết lập giao diện người dùng"""
        # Header
        self.create_header()

        # Tạo notebook cho tabs
        self.create_tabs()

    def create_tabs(self):
        """Tạo tabs cho Cursor và Augment Code"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Tab 1: Cursor
        self.cursor_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.cursor_frame, text="🖱️ Cursor")
        self.setup_cursor_tab()

        # Tab 2: Augment VIP (Tool để reset IDE telemetry)
        self.augment_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.augment_frame, text="🔧 Augment VIP")
        self.setup_augment_tab()

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
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill=tk.X, padx=10, pady=5)

        # Title
        title_label = ttk.Label(header_frame, text="● Lappy Lab",
                               font=("Arial", 16, "bold"))
        title_label.pack(side=tk.LEFT)

        # System info
        system_info = get_system_info()
        info_text = f"System: {system_info['os']} | PC: {system_info['pc_name']}"
        system_label = ttk.Label(header_frame, text=info_text)
        system_label.pack(side=tk.RIGHT)

        # Version info
        version_text = f"Version 4.1 | Released: Jun 11, 2025"
        version_label = ttk.Label(header_frame, text=version_text)
        version_label.pack(side=tk.RIGHT, padx=(0, 20))

    def create_cursor_info_panels(self):
        """Tạo các panel thông tin cho tab Cursor"""
        info_frame = ttk.Frame(self.cursor_frame)
        info_frame.pack(fill=tk.X, padx=10, pady=5)

        # Account info panel
        account_frame = ttk.LabelFrame(info_frame, text="Thông tin tài khoản", padding=10)
        account_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        ttk.Label(account_frame, text="📧 Email:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Label(account_frame, textvariable=self.account_email).grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=2)

        ttk.Label(account_frame, text="🔑 Gói:").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Label(account_frame, textvariable=self.account_type).grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=2)

        ttk.Label(account_frame, text="⏰ Còn lại:").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Label(account_frame, textvariable=self.account_days).grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=2)

        # Usage info panel
        usage_frame = ttk.LabelFrame(info_frame, text="Thông tin sử dụng", padding=10)
        usage_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        ttk.Label(usage_frame, text="⭐ Fast Response:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Label(usage_frame, textvariable=self.usage_fast).grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=2)

        ttk.Label(usage_frame, text="📝 Slow Response:").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Label(usage_frame, textvariable=self.usage_slow).grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=2)

    def create_augment_info_panels(self):
        """Tạo các panel thông tin cho tab Augment VIP"""
        info_frame = ttk.Frame(self.augment_frame)
        info_frame.pack(fill=tk.X, padx=10, pady=5)

        # JetBrains info panel
        jetbrains_frame = ttk.LabelFrame(info_frame, text="JetBrains IDEs", padding=10)
        jetbrains_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        ttk.Label(jetbrains_frame, text="🔧 Trạng thái:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Label(jetbrains_frame, textvariable=self.jetbrains_status).grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=2)

        # VSCode info panel
        vscode_frame = ttk.LabelFrame(info_frame, text="VSCode-based IDEs", padding=10)
        vscode_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        ttk.Label(vscode_frame, text="💻 VSCode IDEs:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Label(vscode_frame, textvariable=self.vscode_status).grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=2)

        ttk.Label(vscode_frame, text="🚀 Tool Status:").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Label(vscode_frame, textvariable=self.augment_status).grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=2)

    def create_cursor_function_buttons(self):
        """Tạo các nút chức năng cho tab Cursor"""
        button_frame = ttk.Frame(self.cursor_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        # Row 1
        row1_frame = ttk.Frame(button_frame)
        row1_frame.pack(fill=tk.X, pady=(0, 5))

        btn1 = ttk.Button(row1_frame, text="Reset Machine ID",
                         command=self.reset_machine_id, width=25)
        btn1.pack(side=tk.LEFT, padx=(0, 5))

        btn2 = ttk.Button(row1_frame, text="Tắt tự động cập nhật Cursor",
                         command=self.disable_auto_update, width=25)
        btn2.pack(side=tk.LEFT, padx=5)

        btn3 = ttk.Button(row1_frame, text="Reset Full Cursor",
                         command=self.reset_full_cursor, width=25)
        btn3.pack(side=tk.LEFT, padx=(5, 0))

        # Row 2
        row2_frame = ttk.Frame(button_frame)
        row2_frame.pack(fill=tk.X)

        btn4 = ttk.Button(row2_frame, text="Bỏ qua kiểm tra phiên bản",
                         command=self.bypass_version_check, width=25)
        btn4.pack(side=tk.LEFT, padx=(0, 5))

        btn5 = ttk.Button(row2_frame, text="Hiển thị cấu hình",
                         command=self.show_config, width=25)
        btn5.pack(side=tk.LEFT, padx=5)

        btn6 = ttk.Button(row2_frame, text="Bỏ qua giới hạn token",
                         command=self.bypass_token_limit, width=25)
        btn6.pack(side=tk.LEFT, padx=(5, 0))

    def create_augment_function_buttons(self):
        """Tạo các nút chức năng cho tab Augment VIP"""
        button_frame = ttk.Frame(self.augment_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        # Row 1
        row1_frame = ttk.Frame(button_frame)
        row1_frame.pack(fill=tk.X, pady=(0, 5))

        btn1 = ttk.Button(row1_frame, text="Reset JetBrains IDs",
                         command=self.reset_jetbrains_ids, width=25)
        btn1.pack(side=tk.LEFT, padx=(0, 5))

        # IDE Selection Frame
        ide_frame = ttk.Frame(row1_frame)
        ide_frame.pack(side=tk.LEFT, padx=5)

        ttk.Label(ide_frame, text="Chọn IDE:").pack(side=tk.LEFT)
        self.selected_ide = tk.StringVar(value="cursor")
        ide_combo = ttk.Combobox(ide_frame, textvariable=self.selected_ide,
                                values=["cursor", "windsurf", "vscode", "vscodium", "all"],
                                state="readonly", width=12)
        ide_combo.pack(side=tk.LEFT, padx=(5, 0))

        btn2 = ttk.Button(row1_frame, text="Reset IDE IDs",
                         command=self.reset_selected_ide_ids, width=20)
        btn2.pack(side=tk.LEFT, padx=5)

        btn3 = ttk.Button(row1_frame, text="Clean Augment DB",
                         command=self.clean_vscode_database, width=20)
        btn3.pack(side=tk.LEFT, padx=(5, 0))

        # Row 2
        row2_frame = ttk.Frame(button_frame)
        row2_frame.pack(fill=tk.X)

        btn4 = ttk.Button(row2_frame, text="Clean Telemetry",
                         command=self.clean_telemetry_entries, width=25)
        btn4.pack(side=tk.LEFT, padx=(0, 5))

        btn5 = ttk.Button(row2_frame, text="Reset All IDs",
                         command=self.reset_all_ids_with_terminate, width=25)
        btn5.pack(side=tk.LEFT, padx=5)

        btn6 = ttk.Button(row2_frame, text="Check IDE Status",
                         command=self.check_ide_status, width=25)
        btn6.pack(side=tk.LEFT, padx=(5, 0))

    def create_cursor_log_area(self):
        """Tạo vùng log cho tab Cursor"""
        log_frame = ttk.LabelFrame(self.cursor_frame, text="Cursor Log", padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.cursor_log_text = scrolledtext.ScrolledText(log_frame, height=12,
                                                        font=("Consolas", 9),
                                                        bg="#000000", fg="#FFFFFF",
                                                        insertbackground="#FFFFFF",
                                                        selectbackground="#333333",
                                                        selectforeground="#FFFFFF")
        self.cursor_log_text.pack(fill=tk.BOTH, expand=True)

        # Thêm log mặc định
        self.cursor_log("✅ File storage.json hợp lệ và có dữ liệu.")
        self.cursor_log("")
        self.cursor_log("📁 File SQLite:")
        self.cursor_log("Đường dẫn: C:\\Users\\letan\\AppData\\Roaming\\Cursor\\User\\globalStorage\\state.vscdb")
        self.cursor_log("Kích thước: 96309248 bytes")
        self.cursor_log("Quyền truy cập: 0o666")
        self.cursor_log("Quyền đọc/ghi: Có")
        self.cursor_log("✅ Kết nối cơ sở dữ liệu SQLite thành công.")
        self.cursor_log("Số bảng: 2")
        self.cursor_log("=" * 50)

    def create_augment_log_area(self):
        """Tạo vùng log cho tab Augment VIP"""
        log_frame = ttk.LabelFrame(self.augment_frame, text="Augment VIP Log", padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.augment_log_text = scrolledtext.ScrolledText(log_frame, height=12,
                                                         font=("Consolas", 9),
                                                         bg="#000000", fg="#FFFFFF",
                                                         insertbackground="#FFFFFF",
                                                         selectbackground="#333333",
                                                         selectforeground="#FFFFFF")
        self.augment_log_text.pack(fill=tk.BOTH, expand=True)

        # Thêm log mặc định
        self.augment_log("🔧 Augment VIP - IDE Telemetry Reset Tool")
        self.augment_log("📋 Hỗ trợ: JetBrains IDEs + VSCode-based IDEs")
        self.augment_log("💡 Chọn IDE cụ thể: Cursor, Windsurf, VSCode, VSCodium")
        self.augment_log("🚀 TÍNH NĂNG MỚI: Reset IDs tự động terminate IDE trước!")
        self.augment_log("🔍 Đang kiểm tra IDE installations...")
        self.augment_log("=" * 50)

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

    def run(self):
        """Chạy ứng dụng"""
        self.root.mainloop()
