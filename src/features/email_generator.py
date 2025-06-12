#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# features/email_generator.py - Công cụ tạo email mở rộng

import random
import string

def generate_extended_email(base_email, max_extension=1000, use_extension=True):
    """
    Tạo email mở rộng với định dạng ngẫu nhiên từ email cơ bản
    
    Args:
        base_email (str): Phần đầu của email (không bao gồm @gmail.com)
        max_extension (int): Số mở rộng tối đa để random
        use_extension (bool): Có sử dụng số mở rộng hay không
        
    Returns:
        str: Email đã được tạo ngẫu nhiên
    """
    # Kiểm tra và làm sạch input
    base_email = base_email.strip().lower()
    
    # Tạo số mở rộng ngẫu nhiên nếu use_extension=True
    extension = random.randint(1, max_extension) if use_extension and max_extension > 0 else 0
    
    # Tạo email với định dạng ngẫu nhiên
    format_choice = random.randint(1, 3)
    
    if format_choice == 1:
        # Định dạng 1: Chuyển đổi ngẫu nhiên chữ hoa/thường
        chars = list(base_email)
        for i in range(len(chars)):
            if random.choice([True, False]):
                chars[i] = chars[i].upper()
        formatted_email = ''.join(chars)
        
    elif format_choice == 2:
        # Định dạng 2: Tách bằng dấu chấm
        parts = []
        temp = ""
        for char in base_email:
            temp += char
            # Xác suất 30% để tách thành phần bằng dấu chấm
            if len(temp) > 1 and random.random() < 0.3:
                parts.append(temp)
                temp = ""
        if temp:  # Thêm phần còn lại
            parts.append(temp)
        formatted_email = '.'.join(parts)
        
    else:
        # Định dạng 3: Kết hợp cả hai
        parts = []
        temp = ""
        for char in base_email:
            if random.choice([True, False]):
                char = char.upper()
            temp += char
            # Xác suất 25% để tách thành phần bằng dấu chấm
            if len(temp) > 1 and random.random() < 0.25:
                parts.append(temp)
                temp = ""
        if temp:  # Thêm phần còn lại
            parts.append(temp)
        formatted_email = '.'.join(parts)
    
    # Thêm số mở rộng và domain
    if use_extension and extension > 0:
        final_email = f"{formatted_email}+{extension}@gmail.com"
    else:
        final_email = f"{formatted_email}@gmail.com"
    
    return final_email

def generate_multiple_emails(base_email, count=5, max_extension=1000, use_extension=True):
    """
    Tạo nhiều email mở rộng khác nhau
    
    Args:
        base_email (str): Phần đầu của email
        count (int): Số lượng email cần tạo
        max_extension (int): Số mở rộng tối đa
        use_extension (bool): Có sử dụng số mở rộng hay không
        
    Returns:
        list: Danh sách các email đã tạo
    """
    emails = []
    for _ in range(count):
        emails.append(generate_extended_email(base_email, max_extension, use_extension))
    return emails

# Hàm test
if __name__ == "__main__":
    test_email = "emailvidu"
    print("Với số mở rộng:")
    print(generate_extended_email(test_email, 1000, True))
    print("\nKhông có số mở rộng:")
    print(generate_extended_email(test_email, 0, False))
    print("\nNhiều email với số mở rộng:")
    print(generate_multiple_emails(test_email, 3, 1000, True))
    print("\nNhiều email không có số mở rộng:")
    print(generate_multiple_emails(test_email, 3, 0, False)) 