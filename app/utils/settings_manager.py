import json
import os
from pathlib import Path

class SettingsManager:
    """Manager for application settings"""
    
    DEFAULT_SETTINGS = {
        'show_version_info': True
    }
    
    def __init__(self):
        self.settings_file = os.path.join(os.getenv('APPDATA'), 'Lappy_Hacking', 'settings.json')
        self._ensure_settings_file()
        
    def _ensure_settings_file(self):
        """Ensure settings file exists with default values"""
        try:
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            if not os.path.exists(self.settings_file):
                self._save_settings(self.DEFAULT_SETTINGS)
        except Exception as e:
            print(f"Warning: Could not create settings file: {e}")
    
    def _load_settings(self):
        """Load settings from file"""
        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                # Ensure all default settings exist
                return {**self.DEFAULT_SETTINGS, **settings}
        except Exception as e:
            print(f"Warning: Could not load settings: {e}")
            return self.DEFAULT_SETTINGS.copy()
    
    def _save_settings(self, settings):
        """Save settings to file"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4)
        except Exception as e:
            print(f"Warning: Could not save settings: {e}")
    
    def get_show_version_info(self):
        """Get whether to show version info dialog"""
        settings = self._load_settings()
        return settings.get('show_version_info', True)
    
    def set_show_version_info(self, show):
        """Set whether to show version info dialog"""
        settings = self._load_settings()
        settings['show_version_info'] = bool(show)
        self._save_settings(settings) 