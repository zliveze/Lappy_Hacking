# gui/config_window.py - Hiển thị cấu hình Cursor
import os
import json
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from ..core.utils import get_cursor_paths, get_system_info, check_file_exists, format_file_size, get_file_size
from ..core.config import get_config_manager

class ConfigWindow:
    def __init__(self, parent=None):
        self.parent = parent
        self.window = tk.Toplevel(parent) if parent else tk.Tk()
        self.setup_window()
        self.setup_ui()
        self.load_config_info()
    
    def setup_window(self):
        """Thiết lập cửa sổ"""
        self.window.title("Cấu hình Cursor - Lappy Lab 4.1")
        self.window.geometry("900x700")
        self.window.resizable(True, True)
        
        # Center window
        self.window.transient(self.parent)
        self.window.grab_set()
    
    def setup_ui(self):
        """Thiết lập giao diện"""
        # Main frame
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_frame, text="Cấu hình Cursor", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.create_system_tab()
        self.create_paths_tab()
        self.create_files_tab()
        self.create_settings_tab()
        self.create_storage_tab()
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Làm mới", 
                  command=self.refresh_config).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Xuất cấu hình", 
                  command=self.export_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Đóng", 
                  command=self.window.destroy).pack(side=tk.RIGHT)
    
    def create_system_tab(self):
        """Tạo tab thông tin hệ thống"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Hệ thống")
        
        # System info
        info_frame = ttk.LabelFrame(frame, text="Thông tin hệ thống", padding=10)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.system_text = scrolledtext.ScrolledText(info_frame, height=20, 
                                                    font=("Consolas", 9))
        self.system_text.pack(fill=tk.BOTH, expand=True)
    
    def create_paths_tab(self):
        """Tạo tab đường dẫn"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Đường dẫn")
        
        # Paths info
        paths_frame = ttk.LabelFrame(frame, text="Đường dẫn Cursor", padding=10)
        paths_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.paths_text = scrolledtext.ScrolledText(paths_frame, height=20, 
                                                   font=("Consolas", 9))
        self.paths_text.pack(fill=tk.BOTH, expand=True)
    
    def create_files_tab(self):
        """Tạo tab thông tin file"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Files")
        
        # Files info
        files_frame = ttk.LabelFrame(frame, text="Thông tin Files", padding=10)
        files_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.files_text = scrolledtext.ScrolledText(files_frame, height=20, 
                                                   font=("Consolas", 9))
        self.files_text.pack(fill=tk.BOTH, expand=True)
    
    def create_settings_tab(self):
        """Tạo tab settings.json"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Settings")
        
        # Settings info
        settings_frame = ttk.LabelFrame(frame, text="settings.json", padding=10)
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.settings_text = scrolledtext.ScrolledText(settings_frame, height=20, 
                                                      font=("Consolas", 9))
        self.settings_text.pack(fill=tk.BOTH, expand=True)
    
    def create_storage_tab(self):
        """Tạo tab storage.json"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Storage")
        
        # Storage info
        storage_frame = ttk.LabelFrame(frame, text="storage.json", padding=10)
        storage_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.storage_text = scrolledtext.ScrolledText(storage_frame, height=20, 
                                                     font=("Consolas", 9))
        self.storage_text.pack(fill=tk.BOTH, expand=True)
    
    def load_config_info(self):
        """Load thông tin cấu hình"""
        self.load_system_info()
        self.load_paths_info()
        self.load_files_info()
        self.load_settings_info()
        self.load_storage_info()
    
    def load_system_info(self):
        """Load thông tin hệ thống"""
        try:
            self.system_text.delete(1.0, tk.END)
            
            system_info = get_system_info()
            
            content = "=== THÔNG TIN HỆ THỐNG ===\n\n"
            content += f"Hệ điều hành: {system_info['os']}\n"
            content += f"Tên máy: {system_info['pc_name']}\n"
            content += f"Kiến trúc: {system_info['architecture']}\n"
            content += f"Processor: {system_info['processor']}\n"
            content += f"Python version: {system_info['python_version']}\n"
            content += f"RAM tổng: {system_info['memory_total']}\n"
            content += f"RAM khả dụng: {system_info['memory_available']}\n"
            content += f"Disk usage: {system_info['disk_usage']}\n"
            
            # Thêm thông tin Lappy Lab
            content += "\n=== THÔNG TIN LAPPY LAB ===\n\n"
            config_mgr = get_config_manager()
            content += f"Version: {config_mgr.get_config_value('General', 'version', '4.1')}\n"
            content += f"Language: {config_mgr.get_config_value('General', 'language', 'vi')}\n"
            content += f"Theme: {config_mgr.get_config_value('General', 'theme', 'default')}\n"
            content += f"Config dir: {config_mgr.config_dir}\n"
            
            self.system_text.insert(tk.END, content)
            
        except Exception as e:
            self.system_text.insert(tk.END, f"Lỗi load thông tin hệ thống: {str(e)}")
    
    def load_paths_info(self):
        """Load thông tin đường dẫn"""
        try:
            self.paths_text.delete(1.0, tk.END)
            
            cursor_paths = get_cursor_paths()
            
            content = "=== ĐƯỜNG DẪN CURSOR ===\n\n"
            
            for name, path in cursor_paths.items():
                exists = "✓" if (check_file_exists(path) if 'path' in name else os.path.exists(path)) else "✗"
                content += f"{name}:\n"
                content += f"  Path: {path}\n"
                content += f"  Exists: {exists}\n\n"
            
            self.paths_text.insert(tk.END, content)
            
        except Exception as e:
            self.paths_text.insert(tk.END, f"Lỗi load thông tin đường dẫn: {str(e)}")
    
    def load_files_info(self):
        """Load thông tin files"""
        try:
            self.files_text.delete(1.0, tk.END)
            
            cursor_paths = get_cursor_paths()
            
            content = "=== THÔNG TIN FILES ===\n\n"
            
            important_files = [
                ('storage.json', cursor_paths.get('storage_path')),
                ('state.vscdb (SQLite)', cursor_paths.get('sqlite_path')),
                ('machineId', cursor_paths.get('machine_id_path')),
                ('settings.json', cursor_paths.get('config_path'))
            ]
            
            for name, path in important_files:
                content += f"{name}:\n"
                if path and check_file_exists(path):
                    size = get_file_size(path)
                    content += f"  Path: {path}\n"
                    content += f"  Size: {format_file_size(size)}\n"
                    content += f"  Status: ✓ Tồn tại\n"
                    
                    # Thêm thông tin chi tiết
                    try:
                        stat = os.stat(path)
                        import time
                        modified_time = time.ctime(stat.st_mtime)
                        content += f"  Modified: {modified_time}\n"
                        content += f"  Permissions: {oct(stat.st_mode & 0o777)}\n"
                    except:
                        pass
                else:
                    content += f"  Path: {path or 'Không xác định'}\n"
                    content += f"  Status: ✗ Không tồn tại\n"
                
                content += "\n"
            
            self.files_text.insert(tk.END, content)
            
        except Exception as e:
            self.files_text.insert(tk.END, f"Lỗi load thông tin files: {str(e)}")
    
    def load_settings_info(self):
        """Load thông tin settings.json"""
        try:
            self.settings_text.delete(1.0, tk.END)
            
            cursor_paths = get_cursor_paths()
            config_path = cursor_paths.get('config_path')
            
            if not config_path or not check_file_exists(config_path):
                self.settings_text.insert(tk.END, "File settings.json không tồn tại")
                return
            
            with open(config_path, 'r', encoding='utf-8') as f:
                settings_data = json.load(f)
            
            content = json.dumps(settings_data, indent=2, ensure_ascii=False)
            self.settings_text.insert(tk.END, content)
            
        except Exception as e:
            self.settings_text.insert(tk.END, f"Lỗi load settings.json: {str(e)}")
    
    def load_storage_info(self):
        """Load thông tin storage.json"""
        try:
            self.storage_text.delete(1.0, tk.END)
            
            cursor_paths = get_cursor_paths()
            storage_path = cursor_paths.get('storage_path')
            
            if not storage_path or not check_file_exists(storage_path):
                self.storage_text.insert(tk.END, "File storage.json không tồn tại")
                return
            
            with open(storage_path, 'r', encoding='utf-8') as f:
                storage_data = json.load(f)
            
            # Ẩn thông tin nhạy cảm
            safe_data = {}
            for key, value in storage_data.items():
                if any(sensitive in key.lower() for sensitive in ['token', 'password', 'secret', 'key']):
                    if isinstance(value, str) and len(value) > 10:
                        safe_data[key] = value[:10] + "..." + value[-5:]
                    else:
                        safe_data[key] = "***HIDDEN***"
                else:
                    safe_data[key] = value
            
            content = json.dumps(safe_data, indent=2, ensure_ascii=False)
            self.storage_text.insert(tk.END, content)
            
        except Exception as e:
            self.storage_text.insert(tk.END, f"Lỗi load storage.json: {str(e)}")
    
    def refresh_config(self):
        """Làm mới cấu hình"""
        try:
            self.load_config_info()
            messagebox.showinfo("Thành công", "Đã làm mới cấu hình!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi làm mới cấu hình: {str(e)}")
    
    def export_config(self):
        """Xuất cấu hình ra file"""
        try:
            from tkinter import filedialog
            from datetime import datetime
            
            # Chọn file để lưu
            filename = filedialog.asksaveasfilename(
                title="Xuất cấu hình",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                initialname=f"cursor_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            
            if not filename:
                return
            
            # Thu thập tất cả thông tin
            export_data = {
                "export_time": datetime.now().isoformat(),
                "system_info": get_system_info(),
                "cursor_paths": get_cursor_paths(),
                "lappy_lab_config": get_config_manager().get_all_config(),
                "lappy_lab_settings": get_config_manager().settings
            }
            
            # Thêm thông tin files nếu có
            cursor_paths = get_cursor_paths()
            
            # Settings.json
            config_path = cursor_paths.get('config_path')
            if config_path and check_file_exists(config_path):
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        export_data["cursor_settings"] = json.load(f)
                except:
                    export_data["cursor_settings"] = "Error reading file"
            
            # Storage.json (ẩn thông tin nhạy cảm)
            storage_path = cursor_paths.get('storage_path')
            if storage_path and check_file_exists(storage_path):
                try:
                    with open(storage_path, 'r', encoding='utf-8') as f:
                        storage_data = json.load(f)
                    
                    # Ẩn thông tin nhạy cảm
                    safe_storage = {}
                    for key, value in storage_data.items():
                        if any(sensitive in key.lower() for sensitive in ['token', 'password', 'secret', 'key']):
                            safe_storage[key] = "***HIDDEN***"
                        else:
                            safe_storage[key] = value
                    
                    export_data["cursor_storage"] = safe_storage
                except:
                    export_data["cursor_storage"] = "Error reading file"
            
            # Lưu file
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("Thành công", f"Đã xuất cấu hình ra file:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi xuất cấu hình: {str(e)}")

def show_config_window(parent=None):
    """Hiển thị cửa sổ cấu hình"""
    try:
        config_window = ConfigWindow(parent)
        if not parent:
            config_window.window.mainloop()
    except Exception as e:
        if parent:
            messagebox.showerror("Lỗi", f"Lỗi hiển thị cấu hình: {str(e)}")
        else:
            print(f"Lỗi hiển thị cấu hình: {str(e)}")
