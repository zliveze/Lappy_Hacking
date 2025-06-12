# 🔨 Hướng dẫn Build Lappy Lab 4.1

## 🎯 Tổng quan

Lappy Lab có thể được đóng gói thành file `.exe` độc lập với icon đẹp mắt từ thư mục `public/image/icon.ico`.

## 📋 Yêu cầu

- ✅ **Python 3.8+**
- ✅ **PyInstaller** (tự động cài đặt)
- ✅ **Windows** (khuyến nghị cho .exe)
- ✅ **Icon file**: `public/image/icon.ico`

## 🚀 Cách build nhanh

### 1. Quick Build (Dễ nhất)
```bash
# Chỉ cần double-click
build_quick.bat
```
- ✅ Tự động kiểm tra Python
- ✅ Tự động cài PyInstaller
- ✅ Tự động build với icon
- ✅ Hiển thị kết quả

### 2. PowerShell Quick
```powershell
.\build_advanced.ps1 -Quick
```
- ✅ Build + Clean tự động
- ✅ Thông tin chi tiết
- ✅ Mở thư mục kết quả

## 🔧 Cách build nâng cao

### 1. Python Script (Menu)
```bash
python build.py
```

**Menu options:**
- `1` - Build executable
- `2` - Build + Clean (Khuyến nghị)
- `3` - Build + Installer
- `4` - Clean build files
- `5` - Thông tin build

### 2. PowerShell Advanced
```powershell
# Build thông thường
.\build_advanced.ps1

# Build + Clean
.\build_advanced.ps1 -Clean

# Build + Installer
.\build_advanced.ps1 -Installer

# Xem help
.\build_advanced.ps1 -Help
```

## 📁 Cấu trúc build

### Input files:
```
Lappy_Hacking/
├── main.pyw              # Entry point (không console)
├── src/                  # Source code
├── public/image/icon.ico # Icon của app
├── locales/              # Ngôn ngữ
└── assets/               # Tài nguyên
```

### Output files:
```
dist/
└── LappyLab.exe         # File executable (15-25 MB)

build/                   # Files tạm (sẽ được xóa)
LappyLab.spec           # PyInstaller spec (sẽ được xóa)
version_info.txt        # Version info (sẽ được xóa)
```

## 🎨 Icon và Branding

### Icon được sử dụng:
- **File**: `public/image/icon.ico`
- **Format**: ICO (Windows icon)
- **Kích thước**: Multi-size (16x16, 32x32, 48x48, 256x256)

### Version Info:
- **Product Name**: Lappy Lab
- **Version**: 4.1.0.0
- **Company**: Lappy Team
- **Description**: Cursor Management Tool

## ⚙️ Cấu hình build

### PyInstaller settings:
```python
# Entry point
main.pyw                 # Không hiển thị console

# Icon
icon='public/image/icon.ico'

# Console
console=False           # Ẩn hoàn toàn CMD

# Compression
upx=True               # Nén file

# Bundle
onefile=True           # 1 file .exe duy nhất
```

### Included files:
- ✅ `src/` - Source code
- ✅ `public/` - Icons, images
- ✅ `locales/` - Translations
- ✅ `assets/` - Resources

### Hidden imports:
- ✅ tkinter modules
- ✅ PIL/Pillow
- ✅ requests, psutil
- ✅ Project modules

## 🐛 Troubleshooting

### Lỗi thường gặp:

#### 1. "PyInstaller not found"
```bash
pip install pyinstaller
```

#### 2. "Icon not found"
- Kiểm tra file `public/image/icon.ico` có tồn tại
- Hoặc build sẽ tiếp tục không có icon

#### 3. "Import errors"
```bash
pip install -r requirements.txt
```

#### 4. "Permission denied"
- Chạy với quyền Administrator
- Tắt antivirus tạm thời

#### 5. File .exe quá lớn
- Sử dụng `--exclude-module` để loại bỏ modules không cần
- Kiểm tra dependencies thừa

### Debug build:
```bash
# Build với debug info
pyinstaller --debug=all LappyLab.spec

# Kiểm tra dependencies
pyi-archive_viewer dist/LappyLab.exe
```

## 📊 Kết quả mong đợi

### Thành công:
```
✅ Build thành công!
📁 File executable: dist/LappyLab.exe
📏 Kích thước: 18.5 MB
🎨 Icon: public/image/icon.ico
🚀 Có thể chạy: dist/LappyLab.exe
```

### File properties:
- **Tên**: LappyLab.exe
- **Kích thước**: 15-25 MB
- **Icon**: Icon từ public/image/icon.ico
- **Console**: Không hiển thị
- **Dependencies**: Tự chứa (portable)

## 🚀 Chạy file .exe

### Cách 1: Double-click
```
dist/LappyLab.exe
```

### Cách 2: Command line
```bash
cd dist
LappyLab.exe
```

### Cách 3: Copy và chạy
- Copy `LappyLab.exe` đến bất kỳ đâu
- Double-click để chạy
- Không cần cài đặt Python

## 📦 Distribution

### Chia sẻ file:
1. **Single file**: Chỉ cần `dist/LappyLab.exe`
2. **Portable**: Không cần cài đặt
3. **Self-contained**: Tất cả dependencies đã bao gồm
4. **Icon**: Hiển thị đẹp trong Windows Explorer

### Upload/Share:
- File size: ~15-25 MB
- Format: Windows Executable (.exe)
- Requirements: Windows 10/11
- Antivirus: Có thể cần whitelist

## 🎉 Kết luận

Build script đã được tối ưu để:
- ✅ **Dễ sử dụng**: Chỉ cần 1 click
- ✅ **Tự động**: Kiểm tra và cài đặt dependencies
- ✅ **Icon đẹp**: Sử dụng icon từ public/
- ✅ **Không console**: Chạy ẩn hoàn toàn
- ✅ **Portable**: 1 file .exe độc lập

**Khuyến nghị**: Sử dụng `build_quick.bat` cho lần đầu build!
