import tkinter as tk
from tkinter import ttk, messagebox

class CursorPremium:
    def __init__(self, window, notebook):
        self.window = window
        
        # Tạo tab mới
        self.tab = ttk.Frame(notebook)
        notebook.add(self.tab, text="Cursor Premium")
        
        # Header với icon và tiêu đề
        header_frame = ttk.Frame(self.tab)
        header_frame.pack(fill=tk.X, pady=(10, 15))
        
        lock_label = ttk.Label(header_frame, text="🔒", font=("Segoe UI", 32))
        lock_label.pack(side=tk.LEFT, padx=10)
        
        title_label = ttk.Label(header_frame, 
                              text="Cursor Premium", 
                              font=("Segoe UI", 20, "bold"))
        title_label.pack(side=tk.LEFT)

        # Container chính chia 2 cột
        main_container = ttk.Frame(self.tab)
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 10))
        
        # Cột trái
        left_column = ttk.Frame(main_container)
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Tính năng Premium
        features_frame = ttk.LabelFrame(left_column, text="✨ Tính năng Cursor Pro", padding="10")
        features_frame.pack(fill=tk.BOTH, expand=True)
        
        features_text = """• Code Completion nâng cao với AI
• Tự động hoàn thiện code thông minh
• Gợi ý code chất lượng cao
• Tối ưu hóa hiệu suất làm việc
• Hỗ trợ đa ngôn ngữ lập trình
• Chat AI thông minh tích hợp
• Không giới hạn số lượng request
• Và nhiều tính năng khác..."""

        features_label = ttk.Label(features_frame,
                                text=features_text,
                                justify="left",
                                font=("Segoe UI", 12))
        features_label.pack(padx=10, pady=10, anchor="w")
        
        # Nút đăng nhập và hỗ trợ
        button_frame = ttk.Frame(left_column)
        button_frame.pack(fill=tk.X, pady=10)
        
        login_button = ttk.Button(button_frame, 
                                text="Đăng nhập Cursor Pro", 
                                command=self.show_locked_message,
                                width=25)
        login_button.pack(side=tk.LEFT, padx=5)
        
        support_button = ttk.Button(button_frame,
                                  text="Liên hệ hỗ trợ",
                                  command=self.show_support_info,
                                  width=20)
        support_button.pack(side=tk.LEFT)
        
        # Cột phải
        right_column = ttk.Frame(main_container)
        right_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Thông tin tài khoản
        account_frame = ttk.LabelFrame(right_column, text="⚠️ Thông báo", padding="10")
        account_frame.pack(fill=tk.BOTH, expand=True)
        
        account_text = """• KHÔNG thay đổi mật khẩu
• KHÔNG đăng nhập nhiều thiết bị
• KHÔNG chia sẻ tài khoản
• KHÔNG lạm dụng tài nguyên

🔒 Trạng thái: Tạm khóa
• Vấn đề bản quyền & kinh phí
• Đang phát triển & tối ưu
• Sẽ thông báo khi mở lại"""

        account_label = ttk.Label(account_frame,
                               text=account_text,
                               justify="left",
                               font=("Segoe UI", 12))
        account_label.pack(padx=10, pady=10, anchor="w")

    def show_locked_message(self):
        messagebox.showwarning(
            "Tính năng bị khóa",
            "Tính năng này hiện đang bị tạm khóa vì lý do bản quyền và kinh phí.\n\n"
            "Vui lòng thử lại sau hoặc liên hệ hỗ trợ để biết thêm chi tiết."
        )
    
    def show_support_info(self):
        messagebox.showinfo(
            "Thông tin hỗ trợ",
            "Để được hỗ trợ, vui lòng truy cập:\n"
            "🌐 Website: https://lappyhacking.onrender.com\n\n"
            "Hoặc liên hệ qua email hỗ trợ của chúng tôi."
        ) 