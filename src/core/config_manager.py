#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# core/config_manager.py - Quản lý cấu hình ứng dụng

import os
import json
import base64

class ConfigManager:
    """Quản lý cấu hình ứng dụng"""
    
    def __init__(self, config_file=None):
        """
        Khởi tạo với đường dẫn file cấu hình
        
        Args:
            config_file (str, optional): Đường dẫn đến file cấu hình
        """
        if config_file is None:
            # Mặc định lưu trong thư mục người dùng
            user_dir = os.path.expanduser("~")
            self.config_file = os.path.join(user_dir, ".lappy_lab_config.json")
        else:
            self.config_file = config_file
        
        self.config = self._load_config()
    
    def _load_config(self):
        """
        Tải cấu hình từ file
        
        Returns:
            dict: Cấu hình đã tải hoặc cấu hình mặc định
        """
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    
                    # Giải mã các giá trị nhạy cảm
                    if 'tempmail_api_token' in config:
                        config['tempmail_api_token'] = self._decode_sensitive_data(config['tempmail_api_token'])
                    
                    return config
            except Exception as e:
                print(f"Lỗi khi tải cấu hình: {str(e)}")
                return {}
        else:
            return {}
    
    def save_config(self):
        """Lưu cấu hình vào file"""
        try:
            # Tạo bản sao để không thay đổi cấu hình gốc
            config_to_save = self.config.copy()
            
            # Mã hóa các giá trị nhạy cảm
            if 'tempmail_api_token' in config_to_save:
                config_to_save['tempmail_api_token'] = self._encode_sensitive_data(config_to_save['tempmail_api_token'])
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_to_save, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Lỗi khi lưu cấu hình: {str(e)}")
            return False
    
    def get(self, key, default=None):
        """
        Lấy giá trị từ cấu hình
        
        Args:
            key (str): Khóa cần lấy
            default: Giá trị mặc định nếu không tìm thấy
            
        Returns:
            Giá trị của khóa hoặc giá trị mặc định
        """
        return self.config.get(key, default)
    
    def set(self, key, value):
        """
        Đặt giá trị cho cấu hình
        
        Args:
            key (str): Khóa cần đặt
            value: Giá trị cần đặt
            
        Returns:
            bool: True nếu thành công, False nếu thất bại
        """
        self.config[key] = value
        return self.save_config()
    
    def _encode_sensitive_data(self, data):
        """
        Mã hóa dữ liệu nhạy cảm
        
        Args:
            data (str): Dữ liệu cần mã hóa
            
        Returns:
            str: Dữ liệu đã mã hóa
        """
        if not data:
            return ""
        try:
            return base64.b64encode(data.encode('utf-8')).decode('utf-8')
        except:
            return ""
    
    def _decode_sensitive_data(self, encoded_data):
        """
        Giải mã dữ liệu nhạy cảm
        
        Args:
            encoded_data (str): Dữ liệu đã mã hóa
            
        Returns:
            str: Dữ liệu đã giải mã
        """
        if not encoded_data:
            return ""
        try:
            return base64.b64decode(encoded_data.encode('utf-8')).decode('utf-8')
        except:
            return "" 