# 🚀 Cách chạy Lappy Lab 4.1

## 🎯 Chạy KHÔNG hiển thị cửa sổ CMD (Khuyến nghị)

### Cách 1: VBScript (Tốt nhất - Hoàn toàn ẩn)
```
Double-click: start_lappy.vbs
```
- ✅ Hoàn toàn không hiển thị cửa sổ nào
- ✅ Tự động yêu cầu quyền admin
- ✅ Tự động tìm Python

### Cách 2: PowerShell Script
```
Right-click: run_hidden.ps1 → Run with PowerShell
```
- ✅ Ẩn cửa sổ PowerShell
- ✅ Tự động yêu cầu quyền admin

### Cách 3: Batch File Silent
```
Double-click: run_silent.bat
```
- ✅ Ẩn cửa sổ CMD
- ✅ Fallback nếu không có pythonw

### Cách 4: Python File (Direct)
```
Double-click: main.pyw
```
- ✅ Chạy trực tiếp với pythonw
- ⚠️ Cần quyền admin thủ công

## 🖥️ Chạy VỚI hiển thị cửa sổ CMD (Debug)

### Console Version
```
python main.py
```
- ✅ Hiển thị console để debug
- ✅ Thông tin chi tiết

### Alternative Runner
```
python run.py
```
- ✅ Kiểm tra dependencies
- ✅ Thông tin khởi động

## 📋 Thứ tự ưu tiên khuyến nghị

1. **start_lappy.vbs** ← Tốt nhất cho người dùng cuối
2. **run_hidden.ps1** ← Tốt cho power users
3. **run_silent.bat** ← Tương thích cao
4. **main.pyw** ← Đơn giản nhất
5. **main.py** ← Chỉ để debug

## 🔧 Yêu cầu hệ thống

- ✅ Windows 10/11
- ✅ Python 3.8+
- ✅ Quyền Administrator
- ✅ Các dependencies trong requirements.txt

## 💡 Lưu ý

- **start_lappy.vbs** là cách tốt nhất để chạy ứng dụng mà không thấy cửa sổ CMD
- Tất cả các phương thức đều tự động yêu cầu quyền admin
- Nếu gặp lỗi, sử dụng **main.py** để xem chi tiết lỗi
