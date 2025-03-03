import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import uuid
import winreg
from datetime import datetime
from ..utils.message_box import show_message

class AdvancedTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding="20")
        self.parent = parent
        self.machine_guid_backup = None
        self.setup_ui()

    def setup_ui(self):
        # Create scrollable frame
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        
        # Main container with scrolling
        main_container = ttk.Frame(canvas)
        
        # Configure canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack scrollbar and canvas
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create window inside canvas
        canvas_frame = canvas.create_window((0, 0), window=main_container, anchor="nw")
        
        # Update canvas when frame size changes
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        main_container.bind('<Configure>', configure_scroll_region)
        
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

        # Content container with padding
        content_container = ttk.Frame(main_container, padding="20")
        content_container.pack(fill=tk.BOTH, expand=True)

        # Header section
        header_frame = ttk.Frame(content_container)
        header_frame.pack(fill=tk.X, pady=(0, 30))

        ttk.Label(header_frame, 
                 text="Advanced Tools", 
                 style="Header.TLabel").pack(side=tk.LEFT)

        # Log Section
        log_frame = ttk.LabelFrame(content_container, text="Operation Log", padding="5")
        log_frame.pack(fill=tk.X, pady=(0, 10))

        self.log_text = tk.Text(log_frame, height=6, wrap=tk.WORD)
        self.log_text.pack(fill=tk.X, padx=5, pady=5)

        # Machine GUID Management Section
        guid_frame = ttk.LabelFrame(content_container, text="Machine GUID Management", padding="5")
        guid_frame.pack(fill=tk.X, pady=(0, 25))

        # Current GUID display
        guid_display_frame = ttk.Frame(guid_frame)
        guid_display_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(guid_display_frame, text="Current MachineGuid:", 
                 style="Bold.TLabel").pack(side=tk.LEFT, padx=10)
        
        self.machine_guid_label = ttk.Label(guid_display_frame, text="", 
                                          style="ID.TLabel")
        self.machine_guid_label.pack(side=tk.LEFT, padx=10)

        # GUID Buttons frame
        guid_buttons_frame = ttk.Frame(guid_frame)
        guid_buttons_frame.pack(fill=tk.X, pady=10)

        # Backup button
        backup_btn = ttk.Button(guid_buttons_frame, 
                              text="💾 Sao lưu GUID",
                              command=self.backup_machine_guid,
                              style="Green.TButton",
                              width=20)
        backup_btn.pack(side=tk.LEFT, padx=10)

        # Change button
        change_btn = ttk.Button(guid_buttons_frame,
                              text="🔄 Thay đổi GUID",
                              command=self.change_machine_guid,
                              style="Red.TButton",
                              width=20)
        change_btn.pack(side=tk.LEFT, padx=10)

        # Restore button
        restore_btn = ttk.Button(guid_buttons_frame,
                               text="⏮ Phục hồi GUID",
                               command=self.restore_machine_guid,
                               style="Blue.TButton",
                               width=20)
        restore_btn.pack(side=tk.LEFT, padx=10)

        # Update current GUID display
        self.update_current_guid()
        
        # Block Cursor Update Section
        block_update_frame = ttk.LabelFrame(content_container, text="Block Cursor Update", padding="15")
        block_update_frame.pack(fill=tk.X, pady=(0, 25))

        # Status display
        status_frame = ttk.Frame(block_update_frame)
        status_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(status_frame, text="Trạng thái:", 
                 style="Bold.TLabel").pack(side=tk.LEFT, padx=10)
        
        self.block_status_label = ttk.Label(status_frame, text="Đang kiểm tra...", 
                                          style="Status.TLabel")
        self.block_status_label.pack(side=tk.LEFT, padx=10)

        # Block/Unblock buttons frame
        block_buttons_frame = ttk.Frame(block_update_frame)
        block_buttons_frame.pack(fill=tk.X, pady=10)

        # Block button
        block_btn = ttk.Button(block_buttons_frame, 
                             text="🚫 Chặn Update",
                             command=self.block_cursor_update,
                             style="Green.TButton",
                             width=20)
        block_btn.pack(side=tk.LEFT, padx=10)

        # Unblock button
        unblock_btn = ttk.Button(block_buttons_frame,
                               text="✅ Gỡ chặn Update",
                               command=self.unblock_cursor_update,
                               style="Red.TButton",
                               width=20)
        unblock_btn.pack(side=tk.LEFT, padx=10)

        # Check initial block status
        self.check_block_status()
        
        # Guide Section
        guide_frame = ttk.LabelFrame(content_container, text="Hướng dẫn sử dụng MachineGUID", padding="20")
        guide_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 25))
        
        # Tiêu đề hướng dẫn
        guide_title = ttk.Label(
            guide_frame,
            text="Hướng dẫn sửa lỗi",
            style="Header.TLabel"
        )
        guide_title.pack(anchor=tk.W, pady=(5, 15))
        
        # Các lưu ý quan trọng
        notes = [
            "⚠️ Lưu ý đảm bảo đã sao Lưu MachineGUID",
            "📝 Fix Cursor 0.45 trở lên",
            "❗ Đảm bảo đã tắt Cursor"
        ]
        
        notes_frame = ttk.Frame(guide_frame)
        notes_frame.pack(fill=tk.X, padx=10)
        
        for note in notes:
            note_label = ttk.Label(
                notes_frame,
                text=note,
                style="Warning.TLabel"
            )
            note_label.pack(anchor=tk.W, pady=3)
        
        # Các bước thực hiện
        steps = [
            "1. Thay đổi thông tin ID bằng cách nhấp vào nút sửa lỗi nhanh",
            "2. Tại Thay đổi MachineGUID (Sao lưu trước khi đổi)",
            "3. Mở lại Cursor và Login bằng tài khoản mới", 
            "4. Mở chat lên và thực hiện chat (Để IDE xác nhận GUID)",
            "5. Quay lại Lappy Lab và khôi phục lại MachineGUID"
        ]
        
        steps_frame = ttk.Frame(guide_frame)
        steps_frame.pack(fill=tk.X, padx=10, pady=(15, 0))
        
        for step in steps:
            step_label = ttk.Label(
                steps_frame,
                text=step,
                style="Description.TLabel",
                wraplength=580
            )
            step_label.pack(anchor=tk.W, pady=5)
            
        # Thêm Note màu cam
        note_frame = ttk.Frame(guide_frame)
        note_frame.pack(fill=tk.X, padx=10, pady=(15, 5))
        note_label = ttk.Label(
            note_frame,
            text="Lưu ý: MachineGuid chỉ được sử dụng cho Cursor 0.45 trở lên vì đây là đoạn mã rất nguy hiểm\nvì nó có thể gây ảnh hưởng nghiêm trọng đến xác minh các ứng dụng \nvà bản quyền trên máy tính của bạn, hãy đảm bảo đã backup đoạn mã trước khi thực hiện",
            style="Warning.TLabel",
            wraplength=580
        )
        note_label.pack(anchor=tk.W)
        
        # Warning Section
        warning_frame = ttk.Frame(content_container)
        warning_frame.pack(fill=tk.X, pady=(0, 10))
        warning_text = ("⚠️ WARNING: These tools are for advanced users only.\n"
                       "Incorrect modifications can cause system instability.")
        ttk.Label(warning_frame, 
                 text=warning_text,
                 style="Warning.TLabel",
                 wraplength=600).pack(padx=10)

    def update_current_guid(self):
        """Cập nhật hiển thị GUID hiện tại"""
        try:
            current_guid = self.get_machine_guid()
            self.machine_guid_label.config(text=current_guid)
        except Exception as e:
            self.machine_guid_label.config(text="Unable to read")
            self.log(f"Error reading current GUID: {str(e)}")

    def get_machine_guid(self):
        """Đọc Machine GUID từ registry"""
        try:
            key_path = r"SOFTWARE\Microsoft\Cryptography"
            registry_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, 
                                        winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
            value, regtype = winreg.QueryValueEx(registry_key, "MachineGuid")
            winreg.CloseKey(registry_key)
            return value
        except WindowsError as e:
            raise Exception(f"Không thể đọc MachineGuid: {str(e)}")

    def set_machine_guid(self, new_guid):
        """Cập nhật Machine GUID trong registry"""
        try:
            key_path = r"SOFTWARE\Microsoft\Cryptography"
            registry_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0,
                                        winreg.KEY_SET_VALUE | winreg.KEY_WOW64_64KEY)
            winreg.SetValueEx(registry_key, "MachineGuid", 0, winreg.REG_SZ, new_guid)
            winreg.CloseKey(registry_key)
        except WindowsError as e:
            raise Exception(f"Không thể cập nhật MachineGuid: {str(e)}")

    def backup_machine_guid(self):
        try:
            current_guid = self.get_machine_guid()
            self.machine_guid_backup = current_guid
            
            # Lấy đường dẫn từ settings
            settings_manager = self.winfo_toplevel().settings_manager
            backup_path = settings_manager.get_setting("guid_backup_path")
            
            if not backup_path:
                backup_path = os.path.join(os.path.expanduser("~"), "machine_guid_backup.json")
            else:
                # Đảm bảo thư mục tồn tại
                os.makedirs(os.path.dirname(os.path.join(backup_path, "machine_guid_backup.json")), exist_ok=True)
                backup_path = os.path.join(backup_path, "machine_guid_backup.json")
            
            backup_data = {
                "guid": current_guid,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            with open(backup_path, 'w') as f:
                json.dump(backup_data, f, indent=4)
            
            message = f"""✅ Đã sao lưu MachineGUID thành công!

📂 File backup được lưu tại:
{backup_path}

⚠️ Lưu ý: Đây là file backup quan trọng, bạn nên:
• Lưu lại đường dẫn này
• Không xóa file backup
• Tạo bản sao để đề phòng mất file"""

            show_message(self, "Sao lưu thành công", message, "success")
            self.log(f"Backed up GUID: {current_guid}")
            
        except Exception as e:
            self.log(f"Error backing up GUID: {str(e)}")
            show_message(self, "Lỗi", str(e), "error")

    def change_machine_guid(self):
        try:
            # Tạo GUID mới
            new_guid = str(uuid.uuid4())
            
            # Xác nhận từ người dùng
            if messagebox.askyesno("Xác nhận", 
                                 f"Bạn có chắc muốn đổi MachineGuid thành:\n{new_guid}"):
                self.set_machine_guid(new_guid)
                self.update_current_guid()
                self.log(f"Changed GUID to: {new_guid}")
                show_message(self, "Thành công", 
                           f"Đã thay đổi MachineGuid thành:\n{new_guid}", "success")
        
        except Exception as e:
            self.log(f"Error changing GUID: {str(e)}")
            show_message(self, "Lỗi", str(e), "error")

    def restore_machine_guid(self):
        try:
            # Lấy đường dẫn từ settings
            settings_manager = self.winfo_toplevel().settings_manager
            backup_path = settings_manager.get_setting("guid_backup_path")
            
            if not backup_path:
                backup_path = os.path.join(os.path.expanduser("~"), "machine_guid_backup.json")
            else:
                backup_path = os.path.join(backup_path, "machine_guid_backup.json")
            
            if not os.path.exists(backup_path):
                raise Exception("Không tìm thấy file backup!")
            
            with open(backup_path, 'r') as f:
                backup_data = json.load(f)
            
            old_guid = backup_data["guid"]
            
            # Xác nhận từ người dùng
            if messagebox.askyesno("Xác nhận", 
                                 f"Phục hồi MachineGuid về:\n{old_guid}"):
                self.set_machine_guid(old_guid)
                self.update_current_guid()
                self.log(f"Restored GUID to: {old_guid}")
                show_message(self, "Thành công", 
                           f"Đã phục hồi MachineGuid về:\n{old_guid}", "success")
        
        except Exception as e:
            self.log(f"Error restoring GUID: {str(e)}")
            show_message(self, "Lỗi", str(e), "error")

    def check_block_status(self):
        """Kiểm tra trạng thái chặn update"""
        try:
            hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
            if not os.path.exists(hosts_path):
                self.block_status_label.config(text="❌ Không tìm thấy file hosts", foreground="#CC0000")  # Màu đỏ
                return False

            with open(hosts_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if "# block cursor auto update\n127.0.0.1 download.todesktop.com" in content:
                self.block_status_label.config(text="✅ Đã chặn Update", foreground="#00CC00")  # Màu xanh lá
                self.log("Trạng thái: Đã chặn Cursor Update")
                return True
            else:
                self.block_status_label.config(text="❌ Chưa chặn Update", foreground="#CC0000")  # Màu đỏ
                self.log("Trạng thái: Chưa chặn Cursor Update")
                return False
                
        except Exception as e:
            self.block_status_label.config(text="❌ Lỗi kiểm tra", foreground="#CC0000")  # Màu đỏ
            self.log(f"Lỗi kiểm tra trạng thái block: {str(e)}")
            return False

    def block_cursor_update(self):
        """Thêm rules chặn update vào file hosts"""
        try:
            if self.check_block_status():
                show_message(self, "Thông báo", "Đã chặn Update từ trước!", "info")
                return

            hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
            
            # Đọc nội dung hiện tại
            with open(hosts_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Thêm rules chặn
            block_rules = "\n\n# block cursor auto update\n127.0.0.1 download.todesktop.com"
            
            # Ghi nội dung mới
            with open(hosts_path, 'w', encoding='utf-8') as f:
                f.write(content + block_rules)
            
            self.check_block_status()
            show_message(self, "Thành công", "Đã chặn Cursor Update!", "success")
            self.log("Đã thêm rules chặn Cursor Update")
            
        except Exception as e:
            error_msg = f"Lỗi khi chặn Update: {str(e)}"
            show_message(self, "Lỗi", error_msg, "error")
            self.log(error_msg)

    def unblock_cursor_update(self):
        """Xóa rules chặn update khỏi file hosts"""
        try:
            if not self.check_block_status():
                show_message(self, "Thông báo", "Chưa bật chặn Update!", "info")
                return

            hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
            
            # Đọc nội dung hiện tại
            with open(hosts_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Xóa rules chặn
            content = content.replace("\n# block cursor auto update\n127.0.0.1 download.todesktop.com", "")
            
            # Ghi nội dung mới
            with open(hosts_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.check_block_status()
            show_message(self, "Thành công", "Đã gỡ chặn Cursor Update!", "success")
            self.log("Đã xóa rules chặn Cursor Update")
            
        except Exception as e:
            error_msg = f"Lỗi khi gỡ chặn Update: {str(e)}"
            show_message(self, "Lỗi", error_msg, "error")
            self.log(error_msg)

    def log(self, message):
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END) 