import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class RetroMessageBox(tk.Toplevel):
    """A retro-styled message box with Windows 95/XP look"""
    
    ICONS = {
        "info": ("ℹ️", "#0066CC"),
        "success": ("✓", "#008000"),
        "error": ("❌", "#CC0000"),
        "warning": ("⚠️", "#FF6600")
    }
    
    def __init__(self, parent, title, message, message_type="info"):
        super().__init__(parent)
        
        # Window setup
        self.title(title)
        self.geometry("300x150")
        self.resizable(False, False)
        
        # Windows 95/XP style colors
        self.bg_color = '#D4D0C8'
        self.configure(bg=self.bg_color)
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        # Setup UI
        self._create_widgets(message, message_type)
        self._setup_styles()
        self._center_window()
        
        # Set focus and bindings
        self.ok_button.focus_set()
        self.bind('<Return>', lambda e: self.destroy())
        self.bind('<Escape>', lambda e: self.destroy())
        
    def _create_widgets(self, message, message_type):
        """Create and layout all widgets"""
        # Main content frame
        content_frame = ttk.Frame(self, style='Retro.TFrame', padding=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Icon frame
        icon_frame = ttk.Frame(content_frame, style='Retro.TFrame')
        icon_frame.pack(side=tk.TOP, fill=tk.X, padx=20, pady=(0,10))
        
        # Get icon and color
        icon_text, icon_color = self.ICONS.get(message_type, self.ICONS["info"])
        
        # Icon
        icon_label = ttk.Label(
            icon_frame, 
            text=icon_text,
            font=("Segoe UI", 32),
            foreground=icon_color,
            background=self.bg_color
        )
        icon_label.pack(side=tk.LEFT, padx=(0,10))
        
        # Message
        message_label = ttk.Label(
            icon_frame,
            text=message,
            wraplength=200,
            justify=tk.LEFT,
            style='Retro.TLabel'
        )
        message_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Button frame
        button_frame = ttk.Frame(content_frame, style='Retro.TFrame')
        button_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        # OK button
        self.ok_button = tk.Button(
            button_frame,
            text="OK",
            font=("MS Sans Serif", 8),
            relief="raised",
            bg=self.bg_color,
            width=10,
            command=self.destroy,
            bd=2,
            highlightthickness=1,
            activebackground=self.bg_color
        )
        self.ok_button.pack(side=tk.RIGHT)
        
    def _setup_styles(self):
        """Configure ttk styles"""
        style = ttk.Style(self)
        style.configure('Retro.TFrame', background=self.bg_color)
        style.configure('Retro.TLabel', 
                       background=self.bg_color,
                       font=("MS Sans Serif", 10))
        
    def _center_window(self):
        """Center the window on screen"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

def show_message(parent, title, message, message_type="info"):
    """
    Hiển thị hộp thoại thông báo
    
    Args:
        parent: Widget cha
        title: Tiêu đề thông báo
        message: Nội dung thông báo
        message_type: Loại thông báo (info, warning, error, success)
    """
    if message_type == "error":
        messagebox.showerror(title, message, parent=parent)
    elif message_type == "warning":
        messagebox.showwarning(title, message, parent=parent)
    elif message_type == "success":
        messagebox.showinfo(title, message, parent=parent)
    else:
        messagebox.showinfo(title, message, parent=parent) 