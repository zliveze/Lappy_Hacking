# 🚀 Hướng dẫn nhanh - Lappy Lab 4.1

## Cách chạy ứng dụng với quyền Admin

### ✅ Cách 1: Sử dụng file batch (Khuyến nghị)
```
Double-click: run_admin.bat
```
- Tự động yêu cầu quyền Administrator
- Kiểm tra dependencies
- Khởi động ứng dụng

### ✅ Cách 2: Tạo shortcut desktop
```
1. Double-click: create_shortcut.bat
2. Sử dụng shortcut "Lappy Lab 4.1 (Admin)" trên Desktop
```

### ✅ Cách 3: Chạy Python script
```bash
python run.py
```
- Tự động yêu cầu quyền admin khi cần
- Hoạt động trên cả Windows/Linux/Mac

### ✅ Cách 4: Chạy trực tiếp
```bash
python main.py
```

## Tại sao cần quyền Administrator?

### 🔒 Lý do bắt buộc:
- **Truy cập file hệ thống**: Cursor lưu dữ liệu trong thư mục được bảo vệ
- **Chỉnh sửa registry**: Một số tính năng cần thay đổi registry Windows
- **Backup an toàn**: Tạo backup trong thư mục hệ thống
- **Tránh lỗi Permission Denied**: Đảm bảo tất cả tính năng hoạt động

### ⚠️ Không có quyền admin sẽ gặp lỗi:
```
[Errno 13] Permission denied: 'C:\Users\...\Cursor\machineId'
```

## Các file quan trọng

| File | Mục đích | Quyền admin |
|------|----------|-------------|
| `run_admin.bat` | Chạy với admin | ✅ Bắt buộc |
| `create_shortcut.bat` | Tạo shortcut | ❌ Không cần |
| `run.py` | Script Python | ✅ Tự động yêu cầu |
| `main.py` | Entry point | ✅ Tự động yêu cầu |

## Xử lý lỗi thường gặp

### ❌ Lỗi: "Permission denied"
**Giải pháp**: Chạy với quyền Administrator
```bash
# Sử dụng file batch
run_admin.bat

# Hoặc click phải -> "Run as administrator"
```

### ❌ Lỗi: "Python not found"
**Giải pháp**: Cài đặt Python 3.8+
```bash
# Chạy file cài đặt
installWindows.bat
```

### ❌ Lỗi: "Module not found"
**Giải pháp**: Cài đặt dependencies
```bash
pip install -r requirements.txt
```

## Lưu ý quan trọng

### 🔥 Trước khi sử dụng:
1. **Đóng Cursor** hoàn toàn
2. **Chạy với quyền Admin**
3. **Tạo backup** (tự động)

### 🎯 Sau khi sử dụng:
1. **Khởi động lại Cursor**
2. **Kiểm tra tính năng**
3. **Báo cáo lỗi** nếu có

---

**💡 Mẹo**: Sử dụng shortcut desktop để tiện lợi nhất!
