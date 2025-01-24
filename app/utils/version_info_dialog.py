import tkinter as tk
from tkinter import ttk
import requests

class VersionInfoDialog(tk.Toplevel):
    def __init__(self, parent, settings_manager):
        super().__init__(parent)
        
        self.settings_manager = settings_manager
        
        # Window setup
        self.title("Thông tin phiên bản")
        self.geometry("700x600")
        self.resizable(False, False)
        self.configure(bg='#D4D0C8')
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        # Windows 95/XP style colors
        bg_color = '#D4D0C8'
        
        # Main content frame
        content_frame = ttk.Frame(self, style='Retro.TFrame', padding=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Get version info from GitHub
        try:
            response = requests.get(
                "https://api.github.com/repos/Letandat071/Lappy_Hacking/releases/latest",
                timeout=5
            )
            if response.status_code == 200:
                release_info = response.json()
                version = release_info["tag_name"]
                release_date = release_info["published_at"].split("T")[0]
                release_notes = release_info["body"]
            else:
                raise Exception("Không thể kết nối đến GitHub")
        except Exception as e:
            version = "2.1.1"
            release_date = "Unknown"
            release_notes = "Không thể tải thông tin phiên bản từ GitHub"
            print(f"Error fetching version info: {str(e)}")

        # Version info
        version_text = f"""Lappy Hacking {version} (Released: {release_date})

{release_notes}"""

        # Create Text widget with scroll
        text_frame = ttk.Frame(content_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        text_widget = tk.Text(text_frame, 
                            wrap=tk.WORD,
                            font=("MS Sans Serif", 10),
                            bg=bg_color,
                            relief="sunken",
                            bd=2,
                            height=15)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text_widget.configure(yscrollcommand=scrollbar.set)
        text_widget.insert("1.0", version_text)
        text_widget.configure(state="disabled")
        
        # Don't show again checkbox
        self.show_again_var = tk.BooleanVar(value=True)
        checkbox = ttk.Checkbutton(
            content_frame,
            text="Hiển thị thông báo này khi khởi động",
            variable=self.show_again_var,
            style='Retro.TCheckbutton'
        )
        checkbox.pack(pady=(0, 10))
        
        # OK button
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(fill=tk.X)
        
        ok_button = tk.Button(
            button_frame,
            text="OK",
            font=("MS Sans Serif", 8),
            relief="raised",
            bg=bg_color,
            width=10,
            command=self.on_ok,
            bd=2,
            highlightthickness=1
        )
        ok_button.pack(side=tk.RIGHT)
        
        # Configure styles
        style = ttk.Style(self)
        style.configure('Retro.TFrame', background=bg_color)
        style.configure('Retro.TCheckbutton', background=bg_color)
        
        # Center window
        self.center_window()
        
        # Set focus on OK button
        ok_button.focus_set()
        
        # Bind Enter and Escape to close
        self.bind('<Return>', lambda e: self.on_ok())
        self.bind('<Escape>', lambda e: self.on_ok())
        
    def center_window(self):
        """Center the window on screen"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
    def on_ok(self):
        """Save settings and close"""
        self.settings_manager.set_show_version_info(self.show_again_var.get())
        self.destroy() 