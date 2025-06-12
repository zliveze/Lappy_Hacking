# Lappy Lab 4.1

Công cụ quản lý Cursor với giao diện tiếng Việt

## Tính năng

### 🔧 Chức năng chính
- **Reset Machine ID**: Tạo Machine ID mới cho Cursor
- **Tắt tự động cập nhật**: Vô hiệu hóa auto update của Cursor
- **Reset toàn bộ Cursor**: Xóa toàn bộ dữ liệu và cache
- **Bỏ qua kiểm tra phiên bản**: Tắt version check
- **Hiển thị cấu hình**: Xem chi tiết cấu hình hệ thống
- **Bỏ qua giới hạn token**: Tắt token limit (thử nghiệm)

### 📊 Thông tin hiển thị
- Thông tin tài khoản Cursor (email, gói, ngày còn lại)
- Thông tin sử dụng (Fast/Slow Response)
- Thông tin hệ thống
- Log chi tiết các thao tác

## Yêu cầu hệ thống

- **Python**: 3.8 trở lên
- **Hệ điều hành**: Windows, macOS, Linux
- **Cursor**: Đã cài đặt và chạy ít nhất 1 lần

## Cài đặt

### 1. Clone repository
```bash
git clone https://github.com/lappyteam/lappy-lab.git
cd lappy-lab/Lappy_Hacking
```

### 2. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 3. Chạy ứng dụng

#### 🎯 Chạy KHÔNG hiển thị cửa sổ CMD (Khuyến nghị)
```bash
# Cách tốt nhất - Hoàn toàn ẩn
start_lappy.vbs

# PowerShell ẩn
run_hidden.ps1

# Batch file ẩn
run_silent.bat

# Python file trực tiếp
main.pyw
```

#### 🖥️ Chạy VỚI hiển thị cửa sổ CMD (Debug)
```bash
# Console version với thông tin chi tiết
python main.py

# Alternative runner
python run.py

# Batch file với admin
run_admin.bat
```

#### 📋 Thứ tự ưu tiên
1. **start_lappy.vbs** ← Tốt nhất (hoàn toàn ẩn)
2. **run_hidden.ps1** ← PowerShell ẩn
3. **run_silent.bat** ← Batch ẩn
4. **main.pyw** ← Python ẩn
5. **main.py** ← Console debug

## Sử dụng

### Giao diện chính
1. **Header**: Hiển thị tên ứng dụng và thông tin hệ thống
2. **Panel thông tin**: 
   - Trái: Thông tin tài khoản
   - Phải: Thông tin sử dụng
3. **Nút chức năng**: 6 nút chính được sắp xếp 2 hàng
4. **Log area**: Hiển thị chi tiết các thao tác

### Các chức năng

#### Reset Machine ID
- Tạo Machine ID mới cho Cursor
- Backup tự động trước khi thay đổi
- Cập nhật trong storage.json, SQLite và file machineId

#### Tắt tự động cập nhật
- Vô hiệu hóa thư mục updater
- Chỉnh sửa app-update.yml và product.json
- Tắt auto update trong settings

#### Reset toàn bộ Cursor
- ⚠️ **CẢNH BÁO**: Xóa toàn bộ dữ liệu Cursor
- Tạo backup trước khi xóa
- Xóa user data, cache, extensions

#### Bỏ qua kiểm tra phiên bản
- Tắt version check trong product.json
- Cập nhật settings.json
- Chỉnh sửa storage.json

#### Hiển thị cấu hình
- Xem thông tin hệ thống
- Kiểm tra đường dẫn Cursor
- Xem nội dung settings.json và storage.json

#### Bỏ qua giới hạn token
- Thử nghiệm tắt token limit
- Chỉnh sửa các file cấu hình
- ⚠️ Hiệu quả có thể khác nhau

## Cấu trúc thư mục

```
Lappy_Hacking/
├── main.py                    # Entry point chính
├── run.py                     # Script chạy ứng dụng
├── run_admin.bat              # Chạy với quyền Admin (Windows)
├── create_shortcut.bat        # Tạo shortcut desktop
├── requirements.txt           # Dependencies
├── README.md                  # Tài liệu
├── LICENSE                    # Giấy phép
├── installWindows.bat         # Cài đặt Windows
├── install_Linux_MacOS.sh     # Cài đặt Linux/macOS
├── build.py                   # Build executable
├── src/                       # Source code chính
│   ├── __init__.py
│   ├── gui/                   # Giao diện người dùng
│   │   ├── __init__.py
│   │   ├── main_window.py     # Cửa sổ chính
│   │   └── config_window.py   # Cửa sổ cấu hình
│   ├── core/                  # Core functionality
│   │   ├── __init__.py
│   │   ├── config.py          # Quản lý cấu hình
│   │   ├── utils.py           # Hàm tiện ích
│   │   └── cursor_info.py     # Thông tin Cursor
│   └── features/              # Các chức năng chính
│       ├── __init__.py
│       ├── reset_machine_id.py
│       ├── disable_auto_update.py
│       ├── reset_full_cursor.py
│       ├── bypass_version_check.py
│       └── bypass_token_limit.py
├── assets/                    # Tài nguyên
│   ├── icons/                 # Icon ứng dụng
│   │   └── README.md
│   └── images/                # Hình ảnh
├── locales/                   # Đa ngôn ngữ
│   └── vi.json               # Tiếng Việt
└── docs/                      # Tài liệu chi tiết
    └── API.md                # API Documentation
```

## Lưu ý quan trọng

### ⚠️ Cảnh báo
- **Backup**: Luôn tạo backup trước khi thực hiện thay đổi
- **Tắt Cursor**: Đóng Cursor trước khi sử dụng các chức năng
- **Quyền admin**: **BẮT BUỘC** chạy với quyền Administrator để tránh lỗi
- **Rủi ro**: Sử dụng với trách nhiệm của bản thân

### 🔑 Quyền Administrator
- **Windows**: Ứng dụng sẽ tự động yêu cầu quyền admin khi cần
- **Khuyến nghị**: Sử dụng `run_admin.bat` hoặc shortcut desktop
- **Lý do**: Cần quyền để truy cập và chỉnh sửa file hệ thống của Cursor

### 🔒 Bảo mật
- Thông tin nhạy cảm (token) được ẩn khi hiển thị
- Backup tự động được tạo trước mọi thay đổi
- Không gửi dữ liệu ra ngoài

### 🐛 Xử lý lỗi
- Kiểm tra log để biết chi tiết lỗi
- Khôi phục từ backup nếu cần
- Báo cáo lỗi qua GitHub Issues

## Phát triển

### Thêm chức năng mới
1. Tạo file module mới trong `src/features/`
2. Import và gọi từ `src/gui/main_window.py`
3. Thêm nút trong `create_function_buttons()`
4. Cập nhật README.md và API.md

### Cấu trúc code
- **Core**: Chức năng cốt lõi, không phụ thuộc GUI
- **GUI**: Giao diện người dùng, sử dụng tkinter
- **Features**: Các tính năng chính, sử dụng core
- **Assets**: Tài nguyên tĩnh (icon, hình ảnh)
- **Locales**: Đa ngôn ngữ
- **Docs**: Tài liệu API và hướng dẫn

### 🔨 Build executable

#### Cách 1: Quick Build (Khuyến nghị)
```bash
# Windows - Batch file tự động
build_quick.bat

# PowerShell - Quick mode
.\build_advanced.ps1 -Quick
```

#### Cách 2: Advanced Build
```bash
# Python script với menu
python build.py

# PowerShell với tùy chọn
.\build_advanced.ps1 -Clean          # Build + Clean
.\build_advanced.ps1 -Installer      # Build + Installer
.\build_advanced.ps1 -Help           # Xem help
```

#### Cách 3: Manual PyInstaller
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon=public/image/icon.ico main.pyw
```

#### 📦 Kết quả build:
- **File executable**: `dist/LappyLab.exe`
- **Icon**: Tự động sử dụng `public/image/icon.ico`
- **Kích thước**: ~15-25 MB (tùy dependencies)
- **Console**: Ẩn hoàn toàn (không hiển thị CMD)

## Changelog

### v4.1 (2025-06-11)
- Giao diện GUI với tkinter
- 6 chức năng chính
- Hiển thị thông tin tài khoản và sử dụng
- Log chi tiết
- Backup tự động
- Hỗ trợ đa nền tảng

## Đóng góp

1. Fork repository
2. Tạo feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Tạo Pull Request

## Giấy phép

Distributed under the MIT License. See `LICENSE` for more information.

## Liên hệ

- **Email**: support@lappylab.com
- **Website**: https://lappylab.com
- **Discord**: https://discord.gg/lappylab
- **Issues**: https://github.com/lappylab/lappy-lab/issues

## Cảm ơn

- Cộng đồng Cursor
- Các beta tester
- Tất cả contributors

---

**Lappy Lab 4.1** - Công cụ quản lý Cursor tốt nhất với giao diện tiếng Việt
