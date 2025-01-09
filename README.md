# 🚀 Lappy Hacking

![Version](https://img.shields.io/badge/version-2.1-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20|%20macOS%20|%20Linux-lightgrey.svg)
![Python Version](https://img.shields.io/badge/python-3.6+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

<p align="center">
  <img src="public/image/icon.jpg" alt="Lappy Hacking Logo" width="200"/>
</p>

## 📝 Mô tả

Lappy Hacking là một công cụ đa nền tảng được thiết kế để quản lý và sửa chữa các vấn đề liên quan đến ID trong các ứng dụng phát triển như Cursor IDE và Windsurf. Phiên bản 2.1 giới thiệu tính năng quản lý tài khoản mới cùng giao diện người dùng hiện đại để tối ưu hóa trải nghiệm người dùng.

### 🌟 Tính năng chính

- **Quản lý ID**: Tạo, đọc và lưu trữ ID cho nhiều ứng dụng
- **Quản lý tài khoản**: Tạo và quản lý tài khoản email tạm thời cho Cursor
- **Dọn dẹp thông minh**: Xóa cache và dữ liệu tạm thời một cách an toàn
- **Sao lưu tự động**: Tạo bản sao lưu trước khi thực hiện thay đổi
- **Giao diện thân thiện**: UI/UX được thiết kế trực quan và dễ sử dụng
- **Hỗ trợ đa nền tảng**: Tương thích với Windows, macOS và Linux

## 🚀 Tính năng mới trong 2.0

- Thêm chức năng dọn dẹp dữ liệu với giao diện trực quan
- Cải thiện khả năng nhận dạng hệ thống và tên máy tính
- Tối ưu hóa hiệu suất và sử dụng bộ nhớ
- Thêm tính năng tự động khởi động lại ứng dụng sau khi dọn dẹp
- Cải thiện UX với thanh tiến trình và thông báo chi tiết

## 🌟 Tính năng mới trong 2.1

### 📧 Quản lý Tài khoản Cursor
- Tạo tài khoản email tạm thời (có hiệu lực 14 ngày)
- Gia hạn thời gian sử dụng thêm 14 ngày
- Theo dõi thời gian còn lại của từng tài khoản
- Quản lý nhiều tài khoản cùng lúc
- Tự động làm mới hộp thư mỗi 15 giây
- Phân loại thư thường và thư rác
- Hiển thị mã xác thực đăng nhập

### 📊 Thống kê và Theo dõi
- Hiển thị tổng số tài khoản
- Theo dõi số tài khoản đang hoạt động
- Đếm số tài khoản hết hạn
- Hiển thị thời gian còn lại dạng đếm ngược

### 🎨 Cải tiến Giao diện
- Thiết kế hiện đại và thân thiện
- Hướng dẫn sử dụng chi tiết
- Biểu tượng trực quan cho các chức năng
- Hoạt ảnh loading khi chuyển đổi tài khoản
- Thông báo trạng thái rõ ràng

### 🎯 Tính năng Windsurf (Đang phát triển)
- Tạo và quản lý tài khoản Windsurf
- Tích hợp với hệ thống quản lý ID

## 🛠 Cài đặt
Clone repository
```bash
git clone https://github.com/Letandat071/Lappy_Hacking.git
cd Lappy_Hacking
pip install -r requirements.txt
python main.py
```

## 📦 Yêu cầu hệ thống

- Python 3.6 trở lên
- Tkinter (thường được cài đặt sẵn với Python)
- Pillow (PIL) cho xử lý hình ảnh
- Requests cho API calls
- Windows 10/11, macOS 10.14+, hoặc Linux với GUI

## 🎯 Giải quyết vấn đề phổ biến

- "You've reached your trial request limit"
- "Too many trial accounts on this machine"
- Các vấn đề về xác thực và định danh

## 🤝 Hướng dẫn sử dụng

### Tạo và sử dụng tài khoản Cursor:
1. Nhấn "Tạo tài khoản mới" để tạo email tạm thời
2. Copy email và sử dụng để đăng nhập Cursor
3. Khi đăng nhập:
   - Nhập email vào form đăng nhập
   - Chọn "Email sign-in code" thay vì nhập mật khẩu
   - Quay lại app và đợi nhận mã xác thực
4. Mã xác thực sẽ hiển thị trong hộp thư đến
5. Email tự động làm mới sau mỗi 15 giây

### Quản lý ID:
1. Chọn ứng dụng (Cursor/Windsurf)
2. Sử dụng các chức năng:
   - Tạo ID mới
   - Đọc ID hiện tại
   - Lưu ID
   - Tạo Backup

## 📝 Lưu ý
- Đây là tài khoản dạng email, không sử dụng mật khẩu
- Mỗi tài khoản có thời hạn 14 ngày và có thể gia hạn
- Nên sao lưu ID trước khi thực hiện thay đổi

## 🤝 Đóng góp

Mọi đóng góp đều được chào đón! Vui lòng:

1. Fork dự án
2. Tạo nhánh tính năng (`git checkout -b feature/AmazingFeature`)
3. Commit thay đổi (`git commit -m 'Add some AmazingFeature'`)
4. Push lên nhánh (`git push origin feature/AmazingFeature`)
5. Mở Pull Request

## 📄 License

Phân phối dưới giấy phép MIT. Xem `LICENSE` để biết thêm thông tin.

## 👨‍💻 Tác giả

**Nguyenky** - [Website](https://lappyhacking.onrender.com/)

## 🙏 Ghi nhận

- Cảm ơn cộng đồng đã đóng góp ý kiến và báo cáo lỗi
- Đặc biệt cảm ơn những người dùng đã kiểm thử phiên bản beta

## 📞 Liên hệ

- Website: [https://lappyhacking.onrender.com/](https://lappyhacking.onrender.com/)
- GitHub: [@Letandat071](https://github.com/Letandat071)