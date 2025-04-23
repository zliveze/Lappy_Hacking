"""
Script để chuyển đổi file icon.ico thành icon.jpg
"""

import os
from PIL import Image

def convert_ico_to_jpg(ico_path, jpg_path):
    """Chuyển đổi file .ico thành .jpg"""
    try:
        if os.path.exists(ico_path):
            print(f"Đang chuyển đổi {ico_path} thành {jpg_path}...")
            # Mở file .ico
            img = Image.open(ico_path)
            # Lưu thành file .jpg
            img.save(jpg_path)
            print(f"Đã chuyển đổi thành công!")
            return True
        else:
            print(f"Không tìm thấy file {ico_path}")
            return False
    except Exception as e:
        print(f"Lỗi khi chuyển đổi: {str(e)}")
        return False

if __name__ == "__main__":
    # Đường dẫn đến file icon.ico
    ico_path = os.path.join("public", "images", "icon.ico")
    # Đường dẫn đến file icon.jpg
    jpg_path = os.path.join("public", "images", "icon.jpg")
    
    # Tạo thư mục nếu chưa tồn tại
    os.makedirs(os.path.dirname(jpg_path), exist_ok=True)
    
    # Chuyển đổi
    convert_ico_to_jpg(ico_path, jpg_path)
