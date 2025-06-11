# core/config.py - Quản lý cấu hình cho Lappy Lab 4.1
import os
import json
import configparser
from .utils import get_user_documents_path, get_cursor_paths, create_directory

class ConfigManager:
    def __init__(self):
        self.config_dir = os.path.join(get_user_documents_path(), ".lappy_lab")
        self.config_file = os.path.join(self.config_dir, "config.ini")
        self.settings_file = os.path.join(self.config_dir, "settings.json")
        self.config = configparser.ConfigParser()
        self.settings = {}
        
        # Tạo thư mục config nếu chưa tồn tại
        create_directory(self.config_dir)
        
        # Load config
        self.load_config()
        self.load_settings()
    
    def get_default_config(self):
        """Lấy cấu hình mặc định"""
        cursor_paths = get_cursor_paths()
        
        default_config = {
            'General': {
                'app_name': 'Lappy Lab',
                'version': '4.1',
                'language': 'vi',
                'theme': 'default',
                'auto_backup': 'true',
                'log_level': 'INFO'
            },
            'Paths': {
                'cursor_storage': cursor_paths.get('storage_path', ''),
                'cursor_sqlite': cursor_paths.get('sqlite_path', ''),
                'cursor_machine_id': cursor_paths.get('machine_id_path', ''),
                'cursor_app': cursor_paths.get('cursor_path', ''),
                'cursor_config': cursor_paths.get('config_path', ''),
                'backup_dir': os.path.join(self.config_dir, 'backups')
            },
            'Features': {
                'enable_reset_machine_id': 'true',
                'enable_disable_auto_update': 'true',
                'enable_reset_full_cursor': 'true',
                'enable_bypass_version_check': 'true',
                'enable_show_config': 'true',
                'enable_bypass_token_limit': 'true'
            },
            'UI': {
                'window_width': '800',
                'window_height': '600',
                'window_resizable': 'true',
                'show_system_info': 'true',
                'show_account_info': 'true',
                'show_usage_info': 'true',
                'log_max_lines': '1000'
            },
            'Security': {
                'require_confirmation': 'true',
                'create_backups': 'true',
                'verify_cursor_paths': 'true',
                'safe_mode': 'false'
            },
            'Advanced': {
                'debug_mode': 'false',
                'verbose_logging': 'false',
                'auto_refresh_info': 'true',
                'refresh_interval': '30',
                'timeout': '10'
            }
        }
        
        return default_config
    
    def load_config(self):
        """Load cấu hình từ file"""
        try:
            if os.path.exists(self.config_file):
                self.config.read(self.config_file, encoding='utf-8')
            else:
                # Tạo config mặc định
                self.create_default_config()
        except Exception as e:
            print(f"Lỗi load config: {str(e)}")
            self.create_default_config()
    
    def create_default_config(self):
        """Tạo cấu hình mặc định"""
        try:
            default_config = self.get_default_config()
            
            for section, options in default_config.items():
                self.config.add_section(section)
                for key, value in options.items():
                    self.config.set(section, key, str(value))
            
            self.save_config()
        except Exception as e:
            print(f"Lỗi tạo config mặc định: {str(e)}")
    
    def save_config(self):
        """Lưu cấu hình"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                self.config.write(f)
            return True
        except Exception as e:
            print(f"Lỗi lưu config: {str(e)}")
            return False
    
    def get_config_value(self, section, key, fallback=None):
        """Lấy giá trị config"""
        try:
            if self.config.has_section(section) and self.config.has_option(section, key):
                return self.config.get(section, key)
            return fallback
        except:
            return fallback
    
    def set_config_value(self, section, key, value):
        """Đặt giá trị config"""
        try:
            if not self.config.has_section(section):
                self.config.add_section(section)
            self.config.set(section, key, str(value))
            return self.save_config()
        except Exception as e:
            print(f"Lỗi set config: {str(e)}")
            return False
    
    def get_config_bool(self, section, key, fallback=False):
        """Lấy giá trị boolean từ config"""
        try:
            value = self.get_config_value(section, key, str(fallback))
            return value.lower() in ('true', 'yes', '1', 'on')
        except:
            return fallback
    
    def get_config_int(self, section, key, fallback=0):
        """Lấy giá trị integer từ config"""
        try:
            value = self.get_config_value(section, key, str(fallback))
            return int(value)
        except:
            return fallback
    
    def load_settings(self):
        """Load settings từ JSON"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    self.settings = json.load(f)
            else:
                self.settings = self.get_default_settings()
                self.save_settings()
        except Exception as e:
            print(f"Lỗi load settings: {str(e)}")
            self.settings = self.get_default_settings()
    
    def get_default_settings(self):
        """Lấy settings mặc định"""
        return {
            'last_run': '',
            'window_position': {'x': 100, 'y': 100},
            'recent_actions': [],
            'user_preferences': {
                'confirm_actions': True,
                'auto_backup': True,
                'show_tooltips': True
            },
            'statistics': {
                'total_runs': 0,
                'successful_operations': 0,
                'failed_operations': 0
            }
        }
    
    def save_settings(self):
        """Lưu settings"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Lỗi lưu settings: {str(e)}")
            return False
    
    def get_setting(self, key, fallback=None):
        """Lấy setting"""
        try:
            keys = key.split('.')
            value = self.settings
            for k in keys:
                value = value[k]
            return value
        except:
            return fallback
    
    def set_setting(self, key, value):
        """Đặt setting"""
        try:
            keys = key.split('.')
            current = self.settings
            for k in keys[:-1]:
                if k not in current:
                    current[k] = {}
                current = current[k]
            current[keys[-1]] = value
            return self.save_settings()
        except Exception as e:
            print(f"Lỗi set setting: {str(e)}")
            return False
    
    def get_all_config(self):
        """Lấy toàn bộ config"""
        config_dict = {}
        for section in self.config.sections():
            config_dict[section] = dict(self.config.items(section))
        return config_dict
    
    def export_config(self, export_path):
        """Export config ra file"""
        try:
            from datetime import datetime
            export_data = {
                'config': self.get_all_config(),
                'settings': self.settings,
                'export_time': str(datetime.now()),
                'version': self.get_config_value('General', 'version', '4.1')
            }
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Lỗi export config: {str(e)}")
            return False
    
    def import_config(self, import_path):
        """Import config từ file"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            # Import config
            if 'config' in import_data:
                for section, options in import_data['config'].items():
                    if not self.config.has_section(section):
                        self.config.add_section(section)
                    for key, value in options.items():
                        self.config.set(section, key, str(value))
                self.save_config()
            
            # Import settings
            if 'settings' in import_data:
                self.settings.update(import_data['settings'])
                self.save_settings()
            
            return True
        except Exception as e:
            print(f"Lỗi import config: {str(e)}")
            return False

# Global config manager instance
_config_manager = None

def get_config_manager():
    """Lấy config manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager

def setup_config():
    """Thiết lập config"""
    return get_config_manager()

def get_config():
    """Lấy config"""
    return get_config_manager().config

def get_config_value(section, key, fallback=None):
    """Lấy giá trị config"""
    return get_config_manager().get_config_value(section, key, fallback)

def set_config_value(section, key, value):
    """Đặt giá trị config"""
    return get_config_manager().set_config_value(section, key, value)

def get_config_bool(section, key, fallback=False):
    """Lấy giá trị boolean từ config"""
    return get_config_manager().get_config_bool(section, key, fallback)

def get_config_int(section, key, fallback=0):
    """Lấy giá trị integer từ config"""
    return get_config_manager().get_config_int(section, key, fallback)
