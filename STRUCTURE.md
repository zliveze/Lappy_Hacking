# Lappy Lab 4.1 - Cấu trúc dự án

## Tổng quan

Dự án đã được tổ chức lại theo kiến trúc modular chuyên nghiệp để dễ dàng quản lý, phát triển và bảo trì.

## Cấu trúc thư mục

### Root Level
```
Lappy_Hacking/
├── main.py              # Entry point chính - khởi tạo và chạy ứng dụng
├── run.py               # Script tiện ích để chạy ứng dụng
├── requirements.txt     # Danh sách dependencies
├── README.md           # Tài liệu chính
├── LICENSE             # Giấy phép MIT
├── STRUCTURE.md        # File này - mô tả cấu trúc
├── install.bat         # Script cài đặt cho Windows
├── install.sh          # Script cài đặt cho Linux/macOS
└── build.py            # Script build executable
```

### Source Code (src/)
```
src/
├── __init__.py         # Package initialization
├── gui/                # Giao diện người dùng
├── core/               # Chức năng cốt lõi
└── features/           # Các tính năng chính
```

#### GUI Package (src/gui/)
```
gui/
├── __init__.py
├── main_window.py      # Cửa sổ chính của ứng dụng
└── config_window.py    # Cửa sổ hiển thị cấu hình
```

#### Core Package (src/core/)
```
core/
├── __init__.py
├── config.py           # Quản lý cấu hình ứng dụng
├── utils.py            # Các hàm tiện ích chung
└── cursor_info.py      # Lấy thông tin tài khoản Cursor
```

#### Features Package (src/features/)
```
features/
├── __init__.py
├── reset_machine_id.py      # Reset Machine ID
├── disable_auto_update.py   # Tắt tự động cập nhật
├── reset_full_cursor.py     # Reset toàn bộ Cursor
├── bypass_version_check.py  # Bỏ qua kiểm tra phiên bản
└── bypass_token_limit.py    # Bỏ qua giới hạn token
```

### Assets (assets/)
```
assets/
├── icons/              # Icon ứng dụng
│   └── README.md      # Hướng dẫn về icon
└── images/            # Hình ảnh khác
```

### Localization (locales/)
```
locales/
└── vi.json            # Ngôn ngữ tiếng Việt
```

### Documentation (docs/)
```
docs/
└── API.md             # Tài liệu API chi tiết
```

## Luồng hoạt động

### 1. Khởi tạo ứng dụng
```
main.py → src/gui/main_window.py → src/core/config.py
```

### 2. Sử dụng tính năng
```
GUI Button → src/features/[feature].py → src/core/utils.py
```

### 3. Hiển thị cấu hình
```
GUI Button → src/gui/config_window.py → src/core/[modules]
```

## Import Structure

### Từ main.py
```python
from src.gui.main_window import LappyLabApp
from src.core.config import setup_config
```

### Từ GUI modules
```python
from ..core.utils import get_system_info
from ..core.cursor_info import get_account_info
from ..features.reset_machine_id import reset_machine_id
```

### Từ Features modules
```python
from ..core.utils import get_cursor_paths, backup_file
```

## Ưu điểm của cấu trúc mới

### 1. **Separation of Concerns**
- GUI logic tách biệt khỏi business logic
- Core functions có thể tái sử dụng
- Features độc lập với nhau

### 2. **Maintainability**
- Dễ dàng tìm và sửa lỗi
- Thêm tính năng mới không ảnh hưởng code cũ
- Code được tổ chức logic

### 3. **Scalability**
- Dễ dàng thêm GUI mới (CLI, web, etc.)
- Thêm features mới đơn giản
- Hỗ trợ đa ngôn ngữ

### 4. **Testing**
- Có thể test từng module riêng biệt
- Mock dependencies dễ dàng
- Unit test và integration test

### 5. **Documentation**
- API documentation rõ ràng
- Code self-documenting
- Dễ onboard developer mới

## Migration từ cấu trúc cũ

### Files đã di chuyển:
- `main.py` → Chỉ còn entry point
- `config.py` → `src/core/config.py`
- `utils.py` → `src/core/utils.py`
- `cursor_acc_info.py` → `src/core/cursor_info.py`
- `show_config.py` → `src/gui/config_window.py`
- `reset_machine_id.py` → `src/features/reset_machine_id.py`
- `disable_auto_update.py` → `src/features/disable_auto_update.py`
- `reset_full_cursor.py` → `src/features/reset_full_cursor.py`
- `bypass_version_check.py` → `src/features/bypass_version_check.py`
- `bypass_token_limit.py` → `src/features/bypass_token_limit.py`

### Files mới:
- `src/gui/main_window.py` - Extracted từ main.py
- `src/__init__.py`, `src/*//__init__.py` - Package initialization
- `assets/`, `locales/`, `docs/` - Thư mục tổ chức
- `STRUCTURE.md` - File này

### Files đã cập nhật:
- `README.md` - Cập nhật cấu trúc mới
- `build.py` - Cập nhật đường dẫn
- `run.py` - Entry point alternative

## Best Practices

### 1. **Import Guidelines**
- Sử dụng relative imports trong package
- Absolute imports từ root
- Tránh circular imports

### 2. **Code Organization**
- Một class/function chính per file
- Related functions cùng module
- Constants ở đầu file

### 3. **Error Handling**
- Consistent error format: `(success, message)`
- Logging thông qua GUI
- Graceful degradation

### 4. **Configuration**
- Centralized config management
- Environment-specific settings
- User preferences

### 5. **Documentation**
- Docstrings cho tất cả public functions
- Type hints khi có thể
- Examples trong docstring

## Development Workflow

### 1. **Thêm tính năng mới**
```bash
# 1. Tạo file trong src/features/
touch src/features/new_feature.py

# 2. Implement function
def new_feature():
    return True, "Success"

# 3. Add to GUI
# Edit src/gui/main_window.py

# 4. Test
python main.py
```

### 2. **Thêm utility function**
```bash
# Edit src/core/utils.py
def new_utility():
    pass
```

### 3. **Thêm GUI component**
```bash
# Edit src/gui/ files
```

## Future Enhancements

### 1. **Plugin System**
- Dynamic feature loading
- Third-party plugins
- Plugin marketplace

### 2. **Multiple Interfaces**
- CLI interface
- Web interface
- REST API

### 3. **Advanced Features**
- Scheduled tasks
- Batch operations
- Remote management

### 4. **Internationalization**
- More languages
- RTL support
- Cultural adaptations

## Conclusion

Cấu trúc mới giúp Lappy Lab 4.1 trở thành một dự án chuyên nghiệp, dễ bảo trì và mở rộng. Việc tổ chức code theo modules giúp team development hiệu quả hơn và giảm thiểu bugs.
