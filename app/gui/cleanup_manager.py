import tkinter as tk
from tkinter import ttk
import os
import shutil
import sys
from pathlib import Path
import time
import threading

class CleanupManager:
    def __init__(self, parent, notebook):
        self.parent = parent
        self.notebook = notebook
        
        # Cache các widget thường xuyên sử dụng
        self._widgets = {}
        
        # Initialize cleanup tab
        self.cleanup_tab = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(self.cleanup_tab, text="Cleanup")
        
        # App selection variable
        self.selected_app = tk.StringVar(value="Cursor")
        
        # Directories to clear - define once
        self.dirs_to_clear = {
            'Local Storage': 'Dữ liệu cục bộ',
            'Session Storage': 'Dữ liệu phiên',
            'WebStorage': 'Bộ nhớ web',
            'User/globalStorage': 'Dữ liệu người dùng',
            'Cache': 'Bộ nhớ đệm',
            'Code Cache': 'Bộ nhớ đệm mã',
            'GPUCache': 'Bộ nhớ đệm GPU'
        }
        
        # Description items - define once
        self.desc_items = [
            ("💾", "Local Storage", "Dữ liệu lưu trữ cục bộ"),
            ("🔄", "Session Storage", "Dữ liệu phiên làm việc"),
            ("🌐", "WebStorage", "Bộ nhớ đệm web"),
            ("👤", "User/globalStorage", "Dữ liệu người dùng"),
            ("📝", "Local State", "Trạng thái ứng dụng")
        ]
        
        # Setup UI components
        self.setup_ui()
        
    def clear_widgets(self):
        """Clear cached widgets"""
        for widget in self._widgets.values():
            if widget and widget.winfo_exists():
                widget.destroy()
        self._widgets.clear()
        
    def get_widget(self, key):
        """Get cached widget"""
        return self._widgets.get(key)
        
    def set_widget(self, key, widget):
        """Cache widget"""
        self._widgets[key] = widget
        
    def setup_ui(self):
        # Main container with gradient background
        self.main_frame = ttk.Frame(self.cleanup_tab)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header with icon
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Cleanup icon (🧹)
        ttk.Label(header_frame, 
                 text="🧹",
                 font=("Segoe UI", 32)).pack(side=tk.LEFT, padx=(0, 15))
        
        # Title and subtitle
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=tk.LEFT)
        
        ttk.Label(title_frame, 
                 text="Dọn dẹp dữ liệu ứng dụng", 
                 style="Header.TLabel").pack(anchor="w")
        
        ttk.Label(title_frame,
                 text="Lưu ý khi sử dụng tính năng này: Ứng dụng sẽ được reset lại toàn bộ dữ liệu, hãy chắc chắn rằng bạn đã sao lưu dữ liệu cần thiết trước khi sử dụng tính năng này",
                 style="Subtitle.TLabel").pack(anchor="w")
        
        # App Selection Frame
        app_frame = ttk.LabelFrame(self.main_frame, text="Chọn ứng dụng", padding="15")
        app_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Radio buttons for app selection
        ttk.Radiobutton(app_frame, text="Cursor", value="Cursor",
                       variable=self.selected_app, 
                       command=self.on_app_change).pack(side=tk.LEFT, padx=20)
        ttk.Radiobutton(app_frame, text="Windsurf", value="Windsurf",
                       variable=self.selected_app,
                       command=self.on_app_change).pack(side=tk.LEFT, padx=20)
        ttk.Radiobutton(app_frame, text="AIDE", value="AIDE",
                       variable=self.selected_app,
                       command=self.on_app_change).pack(side=tk.LEFT, padx=20)
        
        # Content area
        content_frame = ttk.Frame(self.main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Left panel - Information
        info_frame = ttk.LabelFrame(content_frame, text="Thông tin", padding="15")
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Description with icons
        for icon, title, desc in self.desc_items:
            item_frame = ttk.Frame(info_frame)
            item_frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(item_frame, text=icon, font=("Segoe UI", 16)).pack(side=tk.LEFT, padx=(0, 10))
            
            text_frame = ttk.Frame(item_frame)
            text_frame.pack(side=tk.LEFT, fill=tk.X)
            
            ttk.Label(text_frame, text=title, style="Bold.TLabel").pack(anchor="w")
            ttk.Label(text_frame, text=desc, style="Info.TLabel").pack(anchor="w")
        
        # Right panel - Actions and Results
        action_frame = ttk.Frame(content_frame)
        action_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Warning message
        warning_frame = ttk.Frame(action_frame)
        warning_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(warning_frame,
                 text="⚠️",
                 font=("Segoe UI", 24)).pack(side=tk.LEFT, padx=(0, 10))
                 
        ttk.Label(warning_frame,
                 text="Ứng dụng sẽ được đóng tự động trong quá trình dọn dẹp",
                 style="Warning.TLabel").pack(side=tk.LEFT)
        
        # Action button - Pack BEFORE results frame
        self.cleanup_btn = ttk.Button(action_frame,
                                    text="Bắt đầu dọn dẹp",
                                    style="Action.TButton",
                                    command=self.start_cleanup)
        self.cleanup_btn.pack(fill=tk.X, pady=(0, 20))
        
        # Results area with scrollbar
        self.results_frame = ttk.LabelFrame(action_frame, text="Kết quả", padding="15")
        self.results_frame.pack(fill=tk.BOTH, expand=True)

        # Create canvas and scrollbar for results
        self.canvas = tk.Canvas(self.results_frame, height=300)
        scrollbar = ttk.Scrollbar(self.results_frame, orient="vertical", command=self.canvas.yview)
        
        # Progress frame that will contain all results
        self.progress_frame = ttk.Frame(self.canvas)
        
        # Configure canvas
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack scrollbar and canvas
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create window in canvas for progress_frame
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.progress_frame, anchor="nw")
        
        # Update canvas scroll region when progress_frame changes
        self.progress_frame.bind("<Configure>", self.update_scroll_region)
        self.canvas.bind("<Configure>", self.update_canvas_width)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(self.progress_frame, 
                                      variable=self.progress_var,
                                      mode='determinate')
        self.progress.pack(fill=tk.X, pady=(0, 10))
        
        # Status label
        self.status_label = ttk.Label(self.progress_frame,
                                    text="Sẵn sàng dọn dẹp",
                                    style="Status.TLabel")
        self.status_label.pack(fill=tk.X, pady=(0, 10))

    def update_scroll_region(self, event=None):
        """Update the scroll region to encompass the inner frame"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def update_canvas_width(self, event):
        """Update the inner frame's width to fill the canvas"""
        self.canvas.itemconfig(self.canvas_frame, width=event.width)

    def start_cleanup(self):
        # Clear previous results
        self.clear_widgets()
        
        # Reset progress bar
        self.progress_var.set(0)
        self.progress.pack(fill=tk.X, pady=(0, 10))
        
        # Disable button during cleanup
        self.cleanup_btn.configure(state="disabled")
        
        # Start cleanup in separate thread
        thread = threading.Thread(target=self.perform_cleanup)
        thread.daemon = True
        thread.start()

    def perform_cleanup(self):
        try:
            results = []
            app_name = self.selected_app.get()
            app_path = self.get_app_data_path()
            
            # Close app first
            self.close_app()
            results.append((f"Đóng {app_name}", "Thành công", "✓"))
            
            # Clear directories in batches to reduce memory usage
            batch_size = 3
            for i in range(0, len(self.dirs_to_clear.items()), batch_size):
                batch = list(self.dirs_to_clear.items())[i:i+batch_size]
                
                for dir_name, description in batch:
                    dir_path = os.path.join(app_path, dir_name)
                    if os.path.exists(dir_path):
                        try:
                            shutil.rmtree(dir_path)
                            results.append((f"Xóa {description}\n→ {dir_path}", "Thành công", "✓"))
                        except Exception as e:
                            results.append((f"Xóa {description}\n→ {dir_path}", f"Lỗi: {str(e)}", "✗"))
            
            # Process results
            total_steps = len(results)
            for i, (action, status, symbol) in enumerate(results):
                # Update progress
                progress = (i + 1) / total_steps * 100
                self.progress_var.set(progress)
                
                # Update status
                status_label = self.get_widget('status_label')
                if status_label:
                    status_label.configure(text=f"Đang xử lý: {action}")
                
                # Create result item
                self.create_result_item(action, status, symbol)
                
                # Small delay to prevent UI freeze
                self.parent.update_idletasks()
                time.sleep(0.1)
            
            # Cleanup completed
            if status_label:
                status_label.configure(text=f"Hoàn tất dọn dẹp! Đang khởi động lại {app_name}...")
            
            # Start app after cleanup
            self.start_app()
            if status_label:
                status_label.configure(text=f"Hoàn tất! {app_name} đã được khởi động lại.")
            
        finally:
            # Re-enable button
            cleanup_btn = self.get_widget('cleanup_btn')
            if cleanup_btn:
                cleanup_btn.configure(state="normal")

    def create_result_item(self, action, status, symbol):
        """Create a result item with file path and status"""
        result_frame = ttk.Frame(self.progress_frame)
        result_frame.pack(fill=tk.X, pady=2)
        
        # Left container for symbol and action
        left_container = ttk.Frame(result_frame)
        left_container.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 20))
        
        # Status symbol (✓ or ✗)
        color = "green" if symbol == "✓" else "red"
        symbol_label = ttk.Label(left_container,
                               text=symbol,
                               foreground=color,
                               font=("Segoe UI", 11))
        symbol_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Action text with file path
        action_label = ttk.Label(left_container,
                               text=action,
                               style="Info.TLabel",
                               wraplength=400,
                               justify="left")
        action_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Status text (right-aligned with fixed width)
        status_frame = ttk.Frame(result_frame)
        status_frame.pack(side=tk.RIGHT, padx=(0, 10))
        
        status_label = ttk.Label(status_frame,
                               text=status,
                               foreground=color,
                               style="Info.TLabel",
                               width=12)
        status_label.pack()
        
        # Ensure new item is visible
        self.canvas.yview_moveto(1.0)

    def get_app_data_path(self):
        """Get the path to app data directory based on OS and selected app"""
        app_name = self.selected_app.get()
        if sys.platform == "win32":
            return os.path.join(os.getenv('APPDATA'), app_name)
        elif sys.platform == "darwin":
            return os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', app_name)
        else:  # Linux
            return os.path.join(os.path.expanduser('~'), '.config', app_name)

    def close_app(self):
        """Kill app process if running"""
        app_name = self.selected_app.get()
        if sys.platform == "win32":
            os.system(f'taskkill /F /IM "{app_name}.exe" 2>nul')
        else:
            os.system(f'pkill -f {app_name}')

    def start_app(self):
        """Start selected application"""
        try:
            app_name = self.selected_app.get()
            if sys.platform == "win32":
                # Danh sách các đường dẫn có thể có của ứng dụng
                possible_paths = [
                    # Đường dẫn Programs
                    os.path.join(os.getenv('LOCALAPPDATA'), 'Programs', app_name, f'{app_name}.exe'),
                    # Đường dẫn Programs x86
                    os.path.join(os.getenv('PROGRAMFILES(X86)'), app_name, f'{app_name}.exe'),
                    # Đường dẫn Programs x64
                    os.path.join(os.getenv('PROGRAMFILES'), app_name, f'{app_name}.exe'),
                    # Đường dẫn AppData Local
                    os.path.join(os.getenv('LOCALAPPDATA'), app_name, f'{app_name}.exe')
                ]
                
                # Kiểm tra từng đường dẫn
                app_found = False
                for app_path in possible_paths:
                    if os.path.exists(app_path):
                        os.startfile(app_path)
                        app_found = True
                        self.create_result_item(f"Khởi động {app_name}", "Thành công", "✓")
                        break
                
                if not app_found:
                    self.create_result_item(
                        f"Khởi động {app_name}", 
                        "Không tìm thấy ứng dụng. Vui lòng khởi động thủ công.", 
                        "✗"
                    )
            else:
                os.system(f'open -a {app_name}')
                self.create_result_item(f"Khởi động {app_name}", "Thành công", "✓")
            
        except Exception as e:
            self.create_result_item(f"Khởi động {app_name}", f"Lỗi: {str(e)}", "✗")

    def on_app_change(self):
        """Handle app selection change"""
        # Clear previous results
        self.clear_widgets()
        
        # Reset progress bar
        self.progress_var.set(0)
        self.progress.pack_forget()
        
        # Reset status
        app_name = self.selected_app.get()
        self.status_label.configure(text=f"Sẵn sàng dọn dẹp {app_name}")
        
        # Make sure cleanup button is visible and enabled
        self.cleanup_btn.pack(fill=tk.X, pady=(20, 0))
        self.cleanup_btn.configure(state="normal") 