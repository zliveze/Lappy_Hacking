import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import threading
import time
from datetime import datetime, timedelta
from app.utils.email_manager import EmailManager

class AccountManager:
    def __init__(self, window, notebook):
        self.window = window
        
        # Create main tab
        self.tab = ttk.Frame(notebook, padding="10")
        notebook.add(self.tab, text="Quản lý tài khoản")
        
        # Create sub-notebook for Cursor and Windsurf tabs
        self.sub_notebook = ttk.Notebook(self.tab)
        self.sub_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create Cursor and Windsurf tabs
        self.cursor_tab = ttk.Frame(self.sub_notebook, padding="10")
        self.windsurf_tab = ttk.Frame(self.sub_notebook, padding="10")
        
        self.sub_notebook.add(self.cursor_tab, text="Tạo tài khoản Cursor")
        self.sub_notebook.add(self.windsurf_tab, text="Tạo tài khoản Windsurf")
        
        # Initialize variables
        self.api_url = "https://www.1secmail.com/api/v1/"
        self.current_email = None
        self.email_check_thread = None
        self.should_check_email = False
        self.is_checking_emails = False
        self.last_check_time = 0
        self.check_interval = 15  # Seconds between checks
        
        # Loading animation variables
        self.loading_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.loading_index = 0
        self.loading_timer = None
        
        # Initialize components
        self.setup_cursor_tab()
        self.setup_windsurf_tab()
    
    def setup_cursor_tab(self):
        # Main container
        main_container = ttk.Frame(self.cursor_tab)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Instructions (1/3)
        left_panel = ttk.LabelFrame(main_container, text="Hướng dẫn sử dụng", padding="10")
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5), pady=0)
        
        # Add icon and title
        title_frame = ttk.Frame(left_panel)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Add icon (you can replace with your own icon)
        ttk.Label(title_frame, text="📧", font=("Segoe UI", 24)).pack(side=tk.LEFT, padx=5)
        ttk.Label(title_frame, text="Cursor Account Manager", font=("Segoe UI", 14, "bold")).pack(side=tk.LEFT, padx=5)
        
        # Separator after title
        ttk.Separator(left_panel, orient="horizontal").pack(fill=tk.X, pady=10)
        
        instructions = [
            "1. Nhấn 'Tạo tài khoản mới' để tạo tài khoản (có hiệu lực 14 ngày)",
            "2. Copy email và sử dụng để đăng nhập tài khoản Cursor",
            "3. Khi đăng nhập Cursor:",
            "   - Nhập email vào form đăng nhập",
            "   - Chọn 'Email sign-in code' thay vì nhập mật khẩu",
            "   - Quay lại app và đợi nhận mã xác thực",
            "4. Mã xác thực sẽ được hiển thị trong hộp thư đến",
            "5. Email sẽ tự động làm mới sau mỗi 15 giây",
        ]
        
        for instruction in instructions:
            ttk.Label(left_panel, text=instruction, wraplength=300).pack(anchor=tk.W, pady=2)
        
        # Add warning box
        warning_frame = ttk.Frame(left_panel, style="Warning.TFrame")
        warning_frame.pack(fill=tk.X, pady=10)
        ttk.Label(warning_frame, text="⚠️ Lưu ý:", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W, padx=5, pady=(5,0))
        ttk.Label(warning_frame, text="Đây là tài khoản dạng Email, không sử dụng mật khẩu", 
                 wraplength=300, foreground="orange").pack(anchor=tk.W, padx=5, pady=(0,5))
        
        # Add statistics frame
        stats_frame = ttk.LabelFrame(left_panel, text="Thống kê", padding="10")
        stats_frame.pack(fill=tk.X, pady=10)
        
        self.stats_vars = {
            "total_emails": tk.StringVar(value="0"),
            "active_emails": tk.StringVar(value="0"),
            "expired_emails": tk.StringVar(value="0")
        }
        
        ttk.Label(stats_frame, text="📊 Tổng số email:").pack(anchor=tk.W)
        ttk.Label(stats_frame, textvariable=self.stats_vars["total_emails"], 
                 font=("Segoe UI", 10, "bold")).pack(anchor=tk.W)
        
        ttk.Label(stats_frame, text="✅ Email đang hoạt động:").pack(anchor=tk.W)
        ttk.Label(stats_frame, textvariable=self.stats_vars["active_emails"],
                 font=("Segoe UI", 10, "bold"), foreground="green").pack(anchor=tk.W)
        
        ttk.Label(stats_frame, text="❌ Email hết hạn:").pack(anchor=tk.W)
        ttk.Label(stats_frame, textvariable=self.stats_vars["expired_emails"],
                 font=("Segoe UI", 10, "bold"), foreground="red").pack(anchor=tk.W)
        
        # Right panel - Email Management (2/3)
        right_panel = ttk.Frame(main_container)
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Email Management Section
        email_frame = ttk.LabelFrame(right_panel, text="Quản lý Email", padding="10")
        email_frame.pack(fill=tk.BOTH, expand=False, pady=(0, 5))
        
        # Top control frame with better styling
        control_frame = ttk.Frame(email_frame)
        control_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Left side - Buttons with icons
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(side=tk.LEFT)
        
        ttk.Button(btn_frame, text="🆕 Tạo tài khoản mới", command=self.generate_temp_email).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="⏰ Gia hạn +14 ngày", command=self.extend_selected_email).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="🗑️ Xóa tài khoản", command=self.remove_selected_email).pack(side=tk.LEFT, padx=2)
        
        # Right side - Selected email with icon
        selected_frame = ttk.Frame(control_frame)
        selected_frame.pack(side=tk.RIGHT)
        
        ttk.Label(selected_frame, text="📧", font=("Segoe UI", 12)).pack(side=tk.LEFT, padx=2)
        ttk.Label(selected_frame, text="Tài khoản:", font=("Segoe UI", 8)).pack(side=tk.LEFT, padx=2)
        self.selected_email_var = tk.StringVar(value="Chưa chọn tài khoản!")
        ttk.Entry(selected_frame, textvariable=self.selected_email_var, state="readonly", width=35).pack(side=tk.LEFT, padx=2)
        ttk.Button(selected_frame, text="📋 Copy", command=lambda: self.copy_to_clipboard(self.selected_email_var.get())).pack(side=tk.LEFT, padx=2)
        
        # Email list frame with better styling
        list_frame = ttk.Frame(email_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # Create email list
        columns = ("Tài khoản", "Thời gian còn lại", "Trạng thái")
        self.email_list = ttk.Treeview(list_frame, columns=columns, show="headings", height=4)
        
        # Configure columns
        self.email_list.heading("Tài khoản", text="Tài khoản")
        self.email_list.heading("Thời gian còn lại", text="Thời gian còn lại")
        self.email_list.heading("Trạng thái", text="Trạng thái")
        
        self.email_list.column("Tài khoản", width=250)
        self.email_list.column("Thời gian còn lại", width=150)
        self.email_list.column("Trạng thái", width=80)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.email_list.yview)
        self.email_list.configure(yscrollcommand=scrollbar.set)
        
        # Pack list components
        self.email_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Email content frame with better styling
        content_frame = ttk.LabelFrame(right_panel, text="Hộp thư", padding="10")
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 0))
        
        # Add refresh button with icon
        refresh_frame = ttk.Frame(content_frame)
        refresh_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Button(refresh_frame, text="🔄 Làm mới hộp thư", command=self.refresh_mailbox).pack(side=tk.RIGHT)
        
        # Add status label
        self.status_var = tk.StringVar(value="Trạng thái: Đang chờ...")
        ttk.Label(refresh_frame, textvariable=self.status_var).pack(side=tk.LEFT)
        
        self.content_notebook = ttk.Notebook(content_frame)
        self.content_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.setup_content_tab("inbox", "📥 Hộp thư đến")
        self.setup_content_tab("spam", "⚠️ Thư rác")
        
        # Initialize email manager
        self.email_manager = EmailManager()
        self.refresh_email_list()
        
        # Start countdown timer
        self.update_countdown_timer()
        
        # Bind selection event
        self.email_list.bind("<<TreeviewSelect>>", self.on_email_select)
        
        # Update statistics
        self.update_statistics()
    
    def setup_email_content_frame(self):
        # Create notebook for inbox/spam
        content_frame = ttk.LabelFrame(self.cursor_tab, text="Hộp thư", padding="10")
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add refresh button
        refresh_frame = ttk.Frame(content_frame)
        refresh_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Button(refresh_frame, text="Làm mới hộp thư", command=self.refresh_mailbox).pack(side=tk.RIGHT)
        
        self.content_notebook = ttk.Notebook(content_frame)
        self.content_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.setup_content_tab("inbox", "Hộp thư đến")
        self.setup_content_tab("spam", "Thư rác")
    
    def refresh_mailbox(self):
        """Refresh mailbox manually"""
        if not self.current_email:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn email trước!")
            return
        
        try:
            self.fetch_messages()
            messagebox.showinfo("Thành công", "Đã làm mới hộp thư!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể làm mới hộp thư: {str(e)}")
    
    def setup_content_tab(self, tab_type, tab_name):
        tab = ttk.Frame(self.content_notebook)
        self.content_notebook.add(tab, text=tab_name)
        
        # Create frames for list and content
        list_frame = ttk.Frame(tab)
        content_frame = ttk.Frame(tab)
        
        # Store references
        if tab_type == "inbox":
            self.inbox_list_frame = list_frame
            self.inbox_content_frame = content_frame
        else:
            self.spam_list_frame = list_frame
            self.spam_content_frame = content_frame
        
        # Initially show list frame
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Setup email list and content
        self.setup_email_list(list_frame, tab_type)
        self.setup_content_frame(content_frame, tab_type)
    
    def refresh_email_list(self):
        """Update the email list display"""
        # Clear existing items
        for item in self.email_list.get_children():
            self.email_list.delete(item)
        
        # Add emails from manager
        current_time = datetime.now()
        for email_info in self.email_manager.get_all_emails():
            remaining = (email_info["expires_at"] - current_time).total_seconds()
            countdown = self.format_countdown(remaining)
            status = "Hoạt động" if email_info["is_active"] else "Hết hạn"
            
            self.email_list.insert("", "end", values=(
                email_info["email"],
                countdown,
                status
            ))
        
        # Update statistics
        self.update_statistics()
    
    def on_email_select(self, event):
        """Handle email selection"""
        selection = self.email_list.selection()
        if not selection:
            return
        
        # Get selected email
        email = self.email_list.item(selection[0])["values"][0]
        self.selected_email_var.set(email)
        
        # Start loading animation
        self.is_checking_emails = True
        self.start_loading_animation()
        
        # Clear previous email content and show list view
        self.inbox_content.configure(state="normal")
        self.inbox_content.delete(1.0, tk.END)
        self.inbox_content.configure(state="disabled")
        self.spam_content.configure(state="normal")
        self.spam_content.delete(1.0, tk.END)
        self.spam_content.configure(state="disabled")
        
        # Show list view for both tabs
        self.show_email_list("inbox")
        self.show_email_list("spam")
        
        # Update current email for fetching messages
        info = self.email_manager.get_email_info(email)
        if info and info["is_active"]:
            # Stop existing auto-refresh if any
            self.should_check_email = False
            if self.email_check_thread and self.email_check_thread.is_alive():
                self.email_check_thread.join(timeout=1.0)
            
            # Update current email
            self.current_email = {
                "address": email,
                "username": info["username"],
                "domain": info["domain"]
            }
            
            # Clear existing messages
            for item in self.inbox_list.get_children():
                self.inbox_list.delete(item)
            for item in self.spam_list.get_children():
                self.spam_list.delete(item)
            
            # Add loading placeholders
            self.inbox_list.insert("", "end", values=("", "", "Đang tải...", ""))
            self.spam_list.insert("", "end", values=("", "", "Đang tải...", ""))
            
            # Start new auto-refresh thread
            self.should_check_email = True
            self.email_check_thread = threading.Thread(target=self.check_emails)
            self.email_check_thread.daemon = True
            self.email_check_thread.start()
            
            # Fetch messages immediately
            self.fetch_messages()
    
    def check_emails(self):
        """Check emails periodically with rate limiting"""
        while self.should_check_email:
            try:
                current_time = time.time()
                # Only check if enough time has passed since last check
                if current_time - self.last_check_time >= self.check_interval:
                    if not self.is_checking_emails:  # Prevent concurrent checks
                        self.is_checking_emails = True
                        self.fetch_messages()
                        self.last_check_time = current_time
                        self.is_checking_emails = False
            except Exception as e:
                print(f"Error checking emails: {e}")
                self.is_checking_emails = False
            
            # Sleep for a short time to prevent high CPU usage
            time.sleep(1)
    
    def extend_selected_email(self):
        """Extend selected email by 14 days"""
        selection = self.email_list.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn email để gia hạn!")
            return
        
        email = self.email_list.item(selection[0])["values"][0]
        if self.email_manager.extend_email(email):
            self.refresh_email_list()
            messagebox.showinfo("Thành công", f"Đã gia hạn email {email} thêm 14 ngày!")
        else:
            messagebox.showerror("Lỗi", "Không thể gia hạn email!")
    
    def remove_selected_email(self):
        """Remove selected email"""
        selection = self.email_list.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn email để xóa!")
            return
        
        email = self.email_list.item(selection[0])["values"][0]
        if messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa email {email}?"):
            if self.email_manager.remove_email(email):
                # Stop auto-refresh if removing current email
                if self.current_email and self.current_email["address"] == email:
                    self.should_check_email = False
                    self.current_email = None
                
                self.refresh_email_list()
                self.selected_email_var.set("Chưa chọn email")
                messagebox.showinfo("Thành công", f"Đã xóa email {email}!")
            else:
                messagebox.showerror("Lỗi", "Không thể xóa email!")
    
    def generate_temp_email(self):
        try:
            # Generate new email
            print("\n=== Generating New Email ===")
            print("Requesting new email address...")
            response = requests.get(f"{self.api_url}?action=genRandomMailbox&count=1")
            
            if response.status_code != 200:
                print(f"Error response: {response.status_code}")
                print(f"Response content: {response.text}")
                raise Exception("Không thể tạo email mới")
            
            email = response.json()[0]
            print(f"Generated email: {email}")
            
            # Add to manager
            username, domain = email.split('@')
            self.email_manager.add_email(email, username, domain)
            
            # Update UI
            self.refresh_email_list()
            self.selected_email_var.set(email)
            
            # Set as current email
            self.current_email = {
                "address": email,
                "username": username,
                "domain": domain
            }
            
            print("=== Email Generation Complete ===\n")
            messagebox.showinfo("Thành công", f"Đã tạo email: {email}")
            
        except Exception as e:
            print(f"Error in generate_temp_email: {str(e)}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Lỗi", str(e))
    
    def setup_windsurf_tab(self):
        # Placeholder for Windsurf tab
        ttk.Label(self.windsurf_tab, text="Chức năng đang được phát triển...").pack() 
    
    def setup_email_list(self, parent, list_type):
        """Setup email list with columns and scrollbar"""
        # Email list frame
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create Treeview with hidden ID column
        columns = ("ID", "From", "Subject", "Time")
        email_list = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
        
        # Configure columns
        email_list.heading("ID", text="ID")
        email_list.heading("From", text="Từ")
        email_list.heading("Subject", text="Tiêu đề")
        email_list.heading("Time", text="Thời gian")
        
        # Configure column widths
        email_list.column("ID", width=0, stretch=tk.NO)  # Hide ID column
        email_list.column("From", width=150)
        email_list.column("Subject", width=300)
        email_list.column("Time", width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=email_list.yview)
        email_list.configure(yscrollcommand=scrollbar.set)
        
        # Pack components
        email_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Store reference
        if list_type == "inbox":
            self.inbox_list = email_list
        else:
            self.spam_list = email_list
        
        # Bind selection event
        email_list.bind("<<TreeviewSelect>>", self.show_email_content)
    
    def setup_content_frame(self, parent, list_type):
        """Setup frame for displaying email content"""
        # Header frame
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Back button
        back_btn = ttk.Button(
            header_frame,
            text="← Quay lại",
            command=lambda: self.show_email_list(list_type)
        )
        back_btn.pack(side=tk.LEFT)
        
        # Email info
        self.email_info_var = tk.StringVar(value="")
        info_label = ttk.Label(header_frame, textvariable=self.email_info_var)
        info_label.pack(side=tk.LEFT, padx=10)
        
        # Content frame
        content_frame = ttk.Frame(parent)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create text widget for content
        content = tk.Text(content_frame, wrap=tk.WORD)
        content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure text tags for formatting
        content.tag_configure("h1", font=("Segoe UI", 24, "bold"))
        content.tag_configure("h2", font=("Segoe UI", 20, "bold"))
        content.tag_configure("h3", font=("Segoe UI", 16, "bold"))
        content.tag_configure("normal", font=("Segoe UI", 12))
        content.tag_configure("small", font=("Segoe UI", 10))
        content.tag_configure("code", font=("Courier New", 16, "bold"), foreground="blue")
        content.tag_configure("center", justify="center")
        content.tag_configure("gray", foreground="#646464")
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(content_frame, orient=tk.VERTICAL, command=content.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        content.configure(yscrollcommand=scrollbar.set)
        
        # Store reference
        if list_type == "inbox":
            self.inbox_content = content
        else:
            self.spam_content = content
    
    def show_email_list(self, list_type):
        """Show email list and hide content"""
        if list_type == "inbox":
            self.inbox_content_frame.pack_forget()
            self.inbox_list_frame.pack(fill=tk.BOTH, expand=True)
        else:
            self.spam_content_frame.pack_forget()
            self.spam_list_frame.pack(fill=tk.BOTH, expand=True)
    
    def show_email_content(self, event):
        """Show selected email content"""
        # Get selected item from either inbox or spam
        selection = None
        msg_list = None
        list_type = "inbox"
        content_widget = self.inbox_content
        list_frame = self.inbox_list_frame
        content_frame = self.inbox_content_frame
        
        if self.content_notebook.select() == str(self.content_notebook.children["!frame"]):
            selection = self.inbox_list.selection()
            msg_list = self.inbox_list
        else:
            selection = self.spam_list.selection()
            msg_list = self.spam_list
            list_type = "spam"
            content_widget = self.spam_content
            list_frame = self.spam_list_frame
            content_frame = self.spam_content_frame
        
        if not selection:
            return
            
        try:
            # Get message ID from values
            item = msg_list.item(selection[0])
            msg_id = item["values"][0]
            from_address = item["values"][1]
            subject = item["values"][2]
            time = item["values"][3]
            
            if not msg_id or msg_id == "":  # Empty message placeholder
                return
            
            # Switch to content view
            list_frame.pack_forget()
            content_frame.pack(fill=tk.BOTH, expand=True)
            
            # Update email info
            self.email_info_var.set(f"Từ: {from_address} | Tiêu đề: {subject} | Thời gian: {time}")
            
            # Get message content
            username = self.current_email["username"]
            domain = self.current_email["domain"]
            
            response = requests.get(
                f"{self.api_url}?action=readMessage&login={username}&domain={domain}&id={msg_id}"
            )
            
            if response.status_code == 200:
                message = response.json()
                content_widget.configure(state="normal")
                self.format_email_content(content_widget, message)
                content_widget.configure(state="disabled")
            else:
                raise Exception("Không thể tải nội dung thư")
        
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải nội dung email: {str(e)}")
            self.show_email_list(list_type)
    
    def format_email_content(self, content_widget, message):
        """Format email content with better styling"""
        content_widget.delete(1.0, tk.END)
        
        # Try to extract verification code
        import re
        code_match = re.search(r'(\d{6})', message.get("textBody", ""))
        verification_code = code_match.group(1) if code_match else None
        
        # Add title
        content_widget.insert(tk.END, "Sign up for Cursor\n\n", "h1")
        
        # Add main content
        if verification_code:
            content_widget.insert(tk.END, "You requested to sign up for Cursor. Your one-time code is:\n\n", "normal")
            content_widget.insert(tk.END, f"{verification_code}\n\n", "code")
            content_widget.insert(tk.END, "This code expires in 10 minutes.\n\n", "gray")
            content_widget.insert(tk.END, "If you didn't request to sign up for Cursor, you can safely ignore this email. "
                                     "Someone else might have typed your email address by mistake.\n", "gray")
        else:
            # If not a verification email, show original content
            content = message.get("textBody", "") or message.get("htmlBody", "")
            # Remove HTML tags
            content = re.sub(r'<[^>]+>', '', content)
            content_widget.insert(tk.END, content, "normal")
    
    def fetch_messages(self):
        """Fetch messages from API and update UI"""
        if not self.current_email:
            return
            
        try:
            print("\n=== Fetching Messages ===")
            username = self.current_email["username"]
            domain = self.current_email["domain"]
            
            response = requests.get(
                f"{self.api_url}?action=getMessages&login={username}&domain={domain}"
            )
            
            if response.status_code == 200:
                messages = response.json()
                print(f"Found {len(messages)} messages")
                # Update UI in main thread
                self.window.after(0, lambda: self.update_email_lists(messages))
                self.status_var.set(f"Trạng thái: Đã tìm thấy {len(messages)} thư")
                # Stop loading animation
                self.is_checking_emails = False
                self.stop_loading_animation()
            else:
                print(f"Error fetching messages: {response.status_code}")
                print(f"Response content: {response.text}")
                self.status_var.set("Trạng thái: Lỗi khi kiểm tra thư")
                self.is_checking_emails = False
                self.stop_loading_animation()
            
            print("=== Fetch Complete ===\n")
                
        except Exception as e:
            print(f"Error in fetch_messages: {str(e)}")
            import traceback
            traceback.print_exc()
            self.status_var.set("Trạng thái: Lỗi khi kiểm tra thư")
            self.is_checking_emails = False
            self.stop_loading_animation()
    
    def update_email_lists(self, messages):
        """Update inbox and spam lists with fetched messages"""
        try:
            print(f"\n=== Email Update ===")
            print(f"Total messages: {len(messages)}")
            
            # Clear existing items
            for item in self.inbox_list.get_children():
                self.inbox_list.delete(item)
            for item in self.spam_list.get_children():
                self.spam_list.delete(item)
            
            # Sort messages by time
            messages.sort(key=lambda x: x.get("date", ""), reverse=True)
            
            # Separate messages into inbox and spam
            inbox_messages = [msg for msg in messages if not self.is_spam(msg)]
            spam_messages = [msg for msg in messages if self.is_spam(msg)]
            
            print(f"Inbox messages: {len(inbox_messages)}")
            print(f"Spam messages: {len(spam_messages)}")
            
            # Add inbox messages
            if not inbox_messages:
                self.inbox_list.insert("", "end", values=("", "", "Không có thư mới", ""))
            else:
                for msg in inbox_messages:
                    try:
                        date_str = msg.get("date", "")
                        date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                        time_str = date_obj.strftime("%H:%M:%S")
                    except:
                        time_str = "Unknown"
                        
                    from_address = msg.get("from", "Không có người gửi")
                    subject = msg.get("subject", "Không có tiêu đề")
                    msg_id = str(msg.get("id", "no-id"))
                    
                    self.inbox_list.insert("", "end", values=(msg_id, from_address, subject, time_str))
            
            # Add spam messages
            if not spam_messages:
                self.spam_list.insert("", "end", values=("", "", "Không có thư rác", ""))
            else:
                for msg in spam_messages:
                    try:
                        date_str = msg.get("date", "")
                        date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                        time_str = date_obj.strftime("%H:%M:%S")
                    except:
                        time_str = "Unknown"
                        
                    from_address = msg.get("from", "Không có người gửi")
                    subject = msg.get("subject", "Không có tiêu đề")
                    msg_id = str(msg.get("id", "no-id"))
                    
                    self.spam_list.insert("", "end", values=(msg_id, from_address, subject, time_str))
            
            print("=== Update Complete ===\n")
                
        except Exception as e:
            print(f"Error updating email lists: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def is_spam(self, message):
        """Simple spam detection based on keywords"""
        spam_keywords = ["spam", "advertisement", "promotion", "winner", "lottery"]
        subject = message.get("subject", "").lower()
        return any(keyword in subject for keyword in spam_keywords)
    
    def copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        if text == "Chưa chọn email":
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn email trước!")
            return
            
        self.window.clipboard_clear()
        self.window.clipboard_append(text)
        messagebox.showinfo("Thành công", "Đã copy vào clipboard!") 
    
    def format_countdown(self, remaining_seconds):
        """Format remaining time as days, hours, minutes, seconds"""
        if remaining_seconds <= 0:
            return "Hết hạn"
            
        days = remaining_seconds // (24 * 3600)
        remaining_seconds %= (24 * 3600)
        hours = remaining_seconds // 3600
        remaining_seconds %= 3600
        minutes = remaining_seconds // 60
        seconds = remaining_seconds % 60
        
        return f"{int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s"
    
    def update_countdown_timer(self):
        """Update countdown timer for all emails"""
        try:
            current_time = datetime.now()
            
            # Update each email's remaining time
            for item in self.email_list.get_children():
                email = self.email_list.item(item)["values"][0]
                info = self.email_manager.get_email_info(email)
                
                if info and info["is_active"]:
                    remaining = (info["expires_at"] - current_time).total_seconds()
                    countdown = self.format_countdown(remaining)
                    status = "Hoạt động" if remaining > 0 else "Hết hạn"
                    
                    # Update item
                    self.email_list.item(item, values=(email, countdown, status))
        except Exception as e:
            print(f"Error updating countdown: {e}")
        
        # Schedule next update
        self.window.after(1000, self.update_countdown_timer) 
    
    def update_statistics(self):
        """Update email statistics"""
        try:
            emails = self.email_manager.get_all_emails()
            total = len(emails)
            active = sum(1 for e in emails if e["is_active"])
            expired = total - active
            
            self.stats_vars["total_emails"].set(str(total))
            self.stats_vars["active_emails"].set(str(active))
            self.stats_vars["expired_emails"].set(str(expired))
        except Exception as e:
            print(f"Error updating statistics: {e}") 
    
    def start_loading_animation(self):
        """Start loading animation"""
        self.loading_index = 0
        self.update_loading_animation()
    
    def update_loading_animation(self):
        """Update loading animation frame"""
        if self.is_checking_emails:
            loading_char = self.loading_chars[self.loading_index]
            self.status_var.set(f"Trạng thái: Đang chuyển đổi tài khoản... {loading_char}")
            self.loading_index = (self.loading_index + 1) % len(self.loading_chars)
            self.loading_timer = self.window.after(100, self.update_loading_animation)
    
    def stop_loading_animation(self):
        """Stop loading animation"""
        if self.loading_timer:
            self.window.after_cancel(self.loading_timer)
            self.loading_timer = None 