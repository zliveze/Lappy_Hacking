# Lappy Lab 4.0

![Lappy Lab Logo](public/images/icon.ico)

## Giới thiệu

Lappy Lab 4.0 là một công cụ tiện ích dành cho người dùng Cursor, giúp tối ưu hóa và tùy chỉnh trải nghiệm sử dụng Cursor. Ứng dụng được thiết kế với giao diện hoài cổ theo phong cách Windows 95/XP, mang lại cảm giác thân thuộc và dễ sử dụng.

## Tính năng chính

- **Reset Machine ID**: Khôi phục ID máy để giải quyết các vấn đề xác thực
- **Tắt tự động cập nhật Cursor**: Ngăn Cursor tự động cập nhật lên phiên bản mới
- **Reset Full Cursor**: Khôi phục hoàn toàn Cursor về trạng thái ban đầu
- **Bỏ qua kiểm tra phiên bản**: Cho phép sử dụng các phiên bản Cursor cũ hơn
- **Hiển thị cấu hình**: Xem thông tin cấu hình hiện tại của Cursor
- **Bỏ qua giới hạn token**: Tối ưu hóa việc sử dụng token trong Cursor

## Yêu cầu hệ thống

- Windows 10/11
- Python 3.6 trở lên
- Cursor đã được cài đặt

## Cài đặt

### Phương pháp 1: Sử dụng file .exe

1. Tải xuống file LappyLab.exe từ [trang Releases](https://github.com/zliveze/Lappy_Hacking/releases)
2. Chạy file với quyền Administrator

### Phương pháp 2: Từ mã nguồn

1. Clone repository:
   ```
   git clone https://github.com/zliveze/Lappy_Hacking.git
   ```

2. Cài đặt các thư viện cần thiết:
   ```
   pip install -r requirements.txt
   ```

3. Chạy ứng dụng:
   ```
   python main.py
   ```

## Build ứng dụng

Để build ứng dụng thành file .exe:

1. Đảm bảo đã cài đặt PyInstaller:
   ```
   pip install pyinstaller
   ```

2. Chạy file build.bat:
   ```
   .\build.bat
   ```

3. File .exe sẽ được tạo trong thư mục `dist`

## Cách sử dụng

1. Chạy ứng dụng với quyền Administrator
2. Chọn chức năng bạn muốn sử dụng từ các nút trong giao diện
3. Theo dõi quá trình thực hiện trong vùng log
4. Khởi động lại Cursor sau khi thực hiện các thay đổi

## Lưu ý quan trọng

- Luôn sao lưu dữ liệu quan trọng trước khi sử dụng các chức năng reset
- Một số chức năng yêu cầu quyền Administrator để hoạt động đúng
- Ứng dụng sẽ tự động kiểm tra quyền và yêu cầu nâng cấp nếu cần

## Đóng góp

Mọi đóng góp đều được hoan nghênh! Nếu bạn muốn đóng góp vào dự án:

1. Fork repository
2. Tạo branch mới (`git checkout -b feature/amazing-feature`)
3. Commit thay đổi của bạn (`git commit -m 'Add some amazing feature'`)
4. Push lên branch (`git push origin feature/amazing-feature`)
5. Mở Pull Request

## Giấy phép

Dự án này được phân phối dưới giấy phép MIT. Xem file `LICENSE` để biết thêm thông tin.

## Liên hệ

Nguyên Kỷ - [@zliveze](https://github.com/zliveze) - Zliveze@gmail.com

Website: [https://lappy-lab.vercel.app/](https://lappy-lab.vercel.app/)

Link dự án: [https://github.com/zliveze/Lappy_Hacking](https://github.com/zliveze/Lappy_Hacking)
