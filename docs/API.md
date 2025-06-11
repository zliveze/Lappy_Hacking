# Lappy Lab 4.1 - API Documentation

## Tổng quan

Lappy Lab 4.1 được tổ chức theo kiến trúc modular với các package riêng biệt:

- `src/core/` - Chức năng cốt lõi
- `src/gui/` - Giao diện người dùng  
- `src/features/` - Các tính năng chính

## Core Package

### utils.py

#### `get_system_info()`
Lấy thông tin hệ thống.

**Returns:** `dict` - Thông tin hệ thống
```python
{
    'os': 'Windows 10',
    'pc_name': 'DESKTOP-ABC123',
    'architecture': '64bit',
    'processor': 'Intel64 Family 6 Model 142 Stepping 10, GenuineIntel',
    'python_version': '3.9.7',
    'memory_total': '16 GB',
    'memory_available': '8 GB',
    'disk_usage': '45.2%'
}
```

#### `get_cursor_paths()`
Lấy các đường dẫn quan trọng của Cursor.

**Returns:** `dict` - Đường dẫn Cursor
```python
{
    'storage_path': 'C:\\Users\\...\\storage.json',
    'sqlite_path': 'C:\\Users\\...\\state.vscdb',
    'machine_id_path': 'C:\\Users\\...\\machineId',
    'cursor_path': 'C:\\Users\\...\\Cursor',
    'config_path': 'C:\\Users\\...\\settings.json'
}
```

#### `backup_file(file_path, backup_suffix=None)`
Tạo backup file.

**Parameters:**
- `file_path` (str): Đường dẫn file cần backup
- `backup_suffix` (str, optional): Hậu tố backup

**Returns:** `str|False` - Đường dẫn backup hoặc False nếu lỗi

#### `is_cursor_running()`
Kiểm tra Cursor có đang chạy không.

**Returns:** `bool` - True nếu Cursor đang chạy

#### `kill_cursor_processes()`
Tắt tất cả process Cursor.

**Returns:** `int` - Số process đã tắt

### config.py

#### `ConfigManager`
Class quản lý cấu hình ứng dụng.

##### `get_config_value(section, key, fallback=None)`
Lấy giá trị config.

**Parameters:**
- `section` (str): Tên section
- `key` (str): Tên key
- `fallback` (any): Giá trị mặc định

**Returns:** `str` - Giá trị config

##### `set_config_value(section, key, value)`
Đặt giá trị config.

**Parameters:**
- `section` (str): Tên section
- `key` (str): Tên key  
- `value` (any): Giá trị mới

**Returns:** `bool` - True nếu thành công

### cursor_info.py

#### `get_account_info()`
Lấy thông tin tài khoản Cursor.

**Returns:** `dict|None` - Thông tin tài khoản
```python
{
    'email': 'user@example.com',
    'type': 'Pro',
    'days': 30,
    'subscription_status': 'active'
}
```

#### `get_usage_info()`
Lấy thông tin sử dụng Cursor.

**Returns:** `dict|None` - Thông tin sử dụng
```python
{
    'fast_used': 50,
    'fast_limit': 500,
    'slow_used': 100,
    'slow_limit': 'Không giới hạn'
}
```

## Features Package

### reset_machine_id.py

#### `reset_machine_id()`
Reset Machine ID của Cursor.

**Returns:** `tuple(bool, str)` - (Thành công, Thông báo)

#### `verify_machine_id_reset()`
Kiểm tra Machine ID đã được reset chưa.

**Returns:** `tuple(bool, str)` - (Thành công, Thông tin Machine ID)

### disable_auto_update.py

#### `disable_auto_update()`
Tắt tự động cập nhật Cursor.

**Returns:** `tuple(bool, str)` - (Thành công, Thông báo)

### reset_full_cursor.py

#### `reset_full_cursor()`
Reset toàn bộ Cursor (xóa tất cả dữ liệu).

**Returns:** `tuple(bool, str)` - (Thành công, Thông báo)

#### `backup_cursor_data()`
Tạo backup toàn bộ dữ liệu Cursor.

**Returns:** `tuple(bool, str)` - (Thành công, Đường dẫn backup)

### bypass_version_check.py

#### `bypass_version_check()`
Bỏ qua kiểm tra phiên bản Cursor.

**Returns:** `tuple(bool, str)` - (Thành công, Thông báo)

### bypass_token_limit.py

#### `bypass_token_limit()`
Bỏ qua giới hạn token Cursor.

**Returns:** `tuple(bool, str)` - (Thành công, Thông báo)

## GUI Package

### main_window.py

#### `LappyLabApp`
Class chính của ứng dụng GUI.

##### `__init__()`
Khởi tạo ứng dụng.

##### `run()`
Chạy ứng dụng.

##### `log(message)`
Thêm message vào log.

**Parameters:**
- `message` (str): Nội dung log

### config_window.py

#### `ConfigWindow`
Cửa sổ hiển thị cấu hình.

#### `show_config_window(parent=None)`
Hiển thị cửa sổ cấu hình.

**Parameters:**
- `parent` (tk.Widget, optional): Widget cha

## Cách sử dụng

### Import modules
```python
# Core
from src.core.utils import get_system_info, get_cursor_paths
from src.core.config import get_config_manager
from src.core.cursor_info import get_account_info

# Features  
from src.features.reset_machine_id import reset_machine_id
from src.features.disable_auto_update import disable_auto_update

# GUI
from src.gui.main_window import LappyLabApp
```

### Sử dụng features
```python
# Reset Machine ID
success, message = reset_machine_id()
if success:
    print("Reset thành công!")
else:
    print(f"Lỗi: {message}")

# Lấy thông tin tài khoản
account_info = get_account_info()
if account_info:
    print(f"Email: {account_info['email']}")
```

### Chạy GUI
```python
from src.gui.main_window import LappyLabApp
from src.core.config import setup_config

# Khởi tạo config
setup_config()

# Tạo và chạy app
app = LappyLabApp()
app.run()
```

## Error Handling

Tất cả functions trả về tuple `(success, message)` để xử lý lỗi:

```python
success, message = some_function()
if success:
    print(f"Thành công: {message}")
else:
    print(f"Lỗi: {message}")
```

## Logging

Sử dụng method `log()` của `LappyLabApp` để ghi log:

```python
app.log("✅ Thao tác thành công")
app.log("❌ Có lỗi xảy ra")
app.log("ℹ️ Thông tin bổ sung")
```

## Configuration

Config được lưu trong `~/.lappy_lab/`:
- `config.ini` - Cấu hình chính
- `settings.json` - Settings JSON
- `backups/` - Thư mục backup

## Backup

Tất cả thao tác đều tạo backup tự động:
- Format: `filename.bak.YYYYMMDD_HHMMSS`
- Vị trí: Cùng thư mục với file gốc
- Backup toàn bộ: `~/Documents/LappyLab_Backups/`
