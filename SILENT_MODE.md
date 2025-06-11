# Chế độ ẩn cửa sổ CMD - Lappy Lab 4.1

## Tổng quan
Để giải quyết vấn đề cửa sổ CMD xuất hiện khi chạy ứng dụng, chúng tôi đã thêm các tùy chọn chạy ẩn.

## Các cách chạy ứng dụng

### 1. Chạy với cửa sổ CMD (mặc định)
```bash
python main.py
# hoặc
python run.py
# hoặc
run_admin.bat (chọn option 1)
```

### 2. Chạy ẩn cửa sổ CMD
```bash
pythonw main.pyw
# hoặc
run_silent.bat
# hoặc
run_admin.bat (chọn option 2)
```

## Files mới được tạo

### `main.pyw`
- Phiên bản không console của main.py
- Sử dụng pythonw.exe để chạy mà không hiển thị cửa sổ CMD
- Xử lý lỗi bằng messagebox thay vì console

### `run_silent.bat`
- Script batch để chạy ứng dụng ở chế độ ẩn
- Tự động yêu cầu quyền Administrator
- Sử dụng pythonw.exe để ẩn console

### Shortcuts Desktop
Chạy `create_shortcut.bat` để tạo 2 shortcuts:
1. **Lappy Lab 4.1 (Admin)** - Chạy với cửa sổ CMD
2. **Lappy Lab 4.1 (Silent)** - Chạy ẩn cửa sổ CMD

## Thay đổi trong files hiện có

### `main.py`
- Thay đổi tham số `ShellExecuteW` từ `1` thành `0` để ẩn cửa sổ

### `run.py`
- Thay đổi tham số `ShellExecuteW` từ `1` thành `0` để ẩn cửa sổ

### `run_admin.bat`
- Thêm tùy chọn chọn chế độ chạy (với hoặc không cửa sổ CMD)

### `create_shortcut.bat`
- Tạo thêm shortcut cho chế độ Silent

## Khuyến nghị sử dụng

- **Chế độ Admin (có CMD)**: Dùng khi cần debug hoặc xem log
- **Chế độ Silent**: Dùng khi muốn chạy ứng dụng ngầm, không bị làm phiền bởi cửa sổ CMD

## Xử lý lỗi

Trong chế độ Silent:
- Lỗi sẽ được hiển thị qua messagebox
- Nếu không thể hiển thị messagebox, lỗi sẽ được ghi vào file `error.log`
