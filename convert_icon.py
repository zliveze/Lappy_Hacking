"""
Script để chuyển đổi file icon.ico thành chuỗi base64
"""

import os
import base64

def convert_icon_to_base64(icon_path):
    """Chuyển đổi file icon thành chuỗi base64"""
    try:
        with open(icon_path, "rb") as icon_file:
            icon_data = icon_file.read()
            base64_data = base64.b64encode(icon_data).decode("utf-8")
            return base64_data
    except Exception as e:
        print(f"Lỗi khi chuyển đổi icon: {str(e)}")
        return None

def update_icon_base64_file(base64_data):
    """Cập nhật file icon_base64.py với dữ liệu mới"""
    try:
        with open("icon_base64.py", "w", encoding="utf-8") as py_file:
            py_file.write('"""\n')
            py_file.write('Module chứa dữ liệu icon dưới dạng base64\n')
            py_file.write('"""\n\n')
            py_file.write('# Icon dưới dạng base64\n')
            py_file.write('ICON_BASE64 = """\n')
            py_file.write(base64_data)
            py_file.write('\n"""\n\n')
            py_file.write('def get_icon_data():\n')
            py_file.write('    """Trả về dữ liệu icon dưới dạng base64"""\n')
            py_file.write('    return ICON_BASE64')
        print(f"Đã cập nhật file icon_base64.py thành công!")
        return True
    except Exception as e:
        print(f"Lỗi khi cập nhật file icon_base64.py: {str(e)}")
        return False

if __name__ == "__main__":
    # Đường dẫn đến file icon
    icon_path = os.path.join("public", "images", "icon.ico")
    
    if os.path.exists(icon_path):
        print(f"Đang chuyển đổi file {icon_path} thành base64...")
        base64_data = convert_icon_to_base64(icon_path)
        if base64_data:
            update_icon_base64_file(base64_data)
    else:
        print(f"Không tìm thấy file {icon_path}")
