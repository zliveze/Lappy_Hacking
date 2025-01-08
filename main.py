import tkinter as tk
from tkinter import ttk, messagebox
from app.utils.id_generator import IDGenerator
from app.utils.file_manager import FileManager
import platform
from datetime import datetime
from PIL import Image, ImageTk, ImageDraw
from app.gui.cleanup_manager import CleanupManager
import os
import sys

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class ModernIDManager:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Lappy Hacking")
        self.window.geometry("1100x700")  # Increased window size
        self.window.minsize(1100, 700)
        self.window.configure(bg='#f0f0f0')
        
        try:
            # Sử dụng đường dẫn tuyệt đối
            current_dir = os.path.dirname(os.path.abspath(__file__))
            icon_path = os.path.join(current_dir, "public", "image", "icon.jpg")
            cursor_icon_path = os.path.join(current_dir, "public", "image", "cursor-icon.jpg")
            windsurf_icon_path = os.path.join(current_dir, "public", "image", "windsurf-icon.png")
            
            # Load icons
            app_icon = Image.open(icon_path)
            app_icon = ImageTk.PhotoImage(app_icon)
            self.window.iconphoto(True, app_icon)
            
            # Load other icons
            icon_size = (24, 24)
            self.cursor_icon = ImageTk.PhotoImage(
                Image.open(cursor_icon_path).resize(icon_size, Image.Resampling.LANCZOS)
            )
            self.windsurf_icon = ImageTk.PhotoImage(
                Image.open(windsurf_icon_path).resize(icon_size, Image.Resampling.LANCZOS)
            )
        except Exception as e:
            print(f"Error loading icons: {e}")
        
        # Configure style
        self.style = ttk.Style()
        self.style.configure("Title.TLabel", font=("Segoe UI", 24, "bold"))
        self.style.configure("Subtitle.TLabel", font=("Segoe UI", 10))
        self.style.configure("Header.TLabel", font=("Segoe UI", 14, "bold"))
        self.style.configure("Info.TLabel", font=("Segoe UI", 10))
        self.style.configure("ID.TLabel", font=("Consolas", 10), foreground="blue")
        self.style.configure("Action.TButton", font=("Segoe UI", 10))
        self.style.configure("Error.TLabel", font=("Segoe UI", 11), foreground="red")
        self.style.configure("Link.TLabel", font=("Segoe UI", 10, "underline"), foreground="blue")
        self.style.configure("Description.TLabel", font=("Segoe UI", 11), wraplength=700, justify="left")
        self.style.configure("Version.TLabel", font=("Segoe UI", 12))
        self.style.configure("Bold.TLabel", font=("Segoe UI", 11, "bold"))
        self.style.configure("Status.TLabel", font=("Segoe UI", 11))
        self.style.configure("Warning.TLabel", font=("Segoe UI", 11), foreground="orange")
        self.style.configure("Subtitle.TLabel", font=("Segoe UI", 10), foreground="gray")
        
        # Initialize backend
        self.id_generator = IDGenerator()
        self.file_manager = FileManager()
        self.current_ids = None
        self.last_generated = None
        
        self.setup_ui()
        self.center_window()
        
    def center_window(self):
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")
        
    def setup_ui(self):
        # Main container with padding
        main_container = ttk.Frame(self.window, padding="20")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Header Section with title
        header_frame = ttk.Frame(main_container)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Title
        ttk.Label(header_frame, text="Lappy Hacking", style="Title.TLabel").pack(side=tk.LEFT)
        
        # System info and version on the right
        info_frame = ttk.Frame(header_frame)
        info_frame.pack(side=tk.RIGHT)
        
        # Get system information
        system_info = self.get_system_info()
        version_info = "Version 2.0 (Released: Jan 07, 2025)"
        
        ttk.Label(info_frame, text=system_info, style="Subtitle.TLabel").pack(anchor="e", pady=(0, 2))
        ttk.Label(info_frame, text=version_info, style="Subtitle.TLabel").pack(anchor="e")
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_container)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Main tab with more padding
        main_tab = ttk.Frame(notebook, padding="10")
        notebook.add(main_tab, text="Chức năng chính")
        
        # Initialize CleanupManager
        self.cleanup_manager = CleanupManager(self.window, notebook)
        
        # Settings and About tab - Moved to last
        settings_tab = ttk.Frame(notebook, padding="10")
        notebook.add(settings_tab, text="Cài đặt")
        
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
        
        # Left Panel - Controls (narrower)
        left_panel = ttk.LabelFrame(main_content, text="Bảng điều khiển", padding="15")
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        
        # Application Selection
        select_frame = ttk.LabelFrame(left_panel, text="Chọn ứng dụng", padding="10")
        select_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.app_var = tk.StringVar(value="Cursor")
        
        # Radio buttons with icons
        for app, icon in [("Cursor", self.cursor_icon), ("Windsurf", self.windsurf_icon)]:
            frame = ttk.Frame(select_frame)
            frame.pack(fill=tk.X, pady=5)
            rb = ttk.Radiobutton(frame, text=app, value=app, 
                               variable=self.app_var, command=self.on_app_change,
                               width=15)
            rb.pack(side=tk.LEFT)
            tk.Label(frame, image=icon, bg='#f0f0f0').pack(side=tk.LEFT)
        
        # Action Buttons with more spacing
        for text, command in [
            ("Tạo ID mới", self.generate_ids),
            ("Đọc ID hiện tại", self.read_current_ids),
            ("Lưu ID", self.save_ids),
            ("Tạo Backup", self.create_backup)
        ]:
            btn = ttk.Button(left_panel, text=text, command=command, style="Action.TButton")
            btn.pack(fill=tk.X, pady=5)
        
        # Right Panel - ID Information (wider)
        right_panel = ttk.LabelFrame(main_content, text="Thông tin ID", padding="15")
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # ID Display Area with better spacing
        self.id_labels = {}
        id_types = {
            "Machine ID": "telemetry.machineId",
            "SQM ID": "telemetry.sqmId",
            "Device ID": "telemetry.devDeviceId",
            "MAC Machine ID": "telemetry.macMachineId"
        }
        
        for label_text, key in id_types.items():
            frame = ttk.Frame(right_panel)
            frame.pack(fill=tk.X, pady=8)
            
            # Label with fixed width
            ttk.Label(frame, text=f"{label_text}:", width=15, anchor="e").pack(side=tk.LEFT, padx=(0, 15))
            
            # ID value
            id_label = ttk.Label(frame, text="Not generated", style="ID.TLabel")
            id_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.id_labels[key] = id_label
            
            # Copy button
            copy_btn = ttk.Button(frame, text="Copy", width=8,
                              command=lambda k=key: self.copy_to_clipboard(k))
            copy_btn.pack(side=tk.RIGHT, padx=(15, 0))
            
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
            else:
                self.windsurf_path_var.set(self.file_manager.get_storage_path(app_name))
            self.update_path_status()
    
    def update_path_status(self):
        # Update Cursor status
        cursor_exists = self.file_manager.path_exists("Cursor")
        self.cursor_status_var.set("✓ Found" if cursor_exists else "✗ Not found")
        
        # Update Windsurf status
        windsurf_exists = self.file_manager.path_exists("Windsurf")
        self.windsurf_status_var.set("✓ Found" if windsurf_exists else "✗ Not found")
    
    def on_app_change(self):
        self.current_ids = None
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
            
            self.update_status("IDs generated successfully")
            self.update_timestamp()
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.update_status("Error generating IDs")
    
    def save_ids(self):
        try:
            if not self.current_ids:
                raise ValueError("Please generate IDs first!")
            
            app_name = self.app_var.get()
            self.file_manager.set_app(app_name)
            self.file_manager.save_ids(self.current_ids)
            messagebox.showinfo("Success", "IDs saved successfully!")
            self.update_status("IDs saved to storage")
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.update_status("Error saving IDs")
    
    def create_backup(self):
        try:
            app_name = self.app_var.get()
            self.file_manager.set_app(app_name)
            backup_path = self.file_manager.create_backup()
            messagebox.showinfo("Success", f"Backup created at:\n{backup_path}")
            self.update_status("Backup created successfully")
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.update_status("Error creating backup")
    
    def copy_to_clipboard(self, key):
        if self.current_ids and key in self.current_ids:
            self.window.clipboard_clear()
            self.window.clipboard_append(self.current_ids[key])
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
            
            self.update_status("Current IDs loaded successfully")
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.update_status("Error loading current IDs")
    
    def open_website(self, url):
        import webbrowser
        webbrowser.open(url)
    
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = ModernIDManager()
    app.run()
