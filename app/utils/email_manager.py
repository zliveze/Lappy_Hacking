import json
import os
from datetime import datetime, timedelta

class EmailManager:
    def __init__(self):
        self.emails = {}  # Dictionary to store email information
        self.config_file = "email_config.json"
        self.load_emails()
    
    def add_email(self, email, username, domain):
        """Add a new email with 14 days expiration"""
        now = datetime.now()
        expiry = now + timedelta(days=14)
        
        self.emails[email] = {
            "username": username,
            "domain": domain,
            "created_at": now.isoformat(),
            "expires_at": expiry.isoformat(),
            "is_active": True
        }
        self.save_emails()
        return self.emails[email]
    
    def extend_email(self, email, days=14):
        """Extend email expiration by specified days"""
        if email in self.emails:
            expires_at = datetime.fromisoformat(self.emails[email]["expires_at"])
            new_expiry = expires_at + timedelta(days=days)
            self.emails[email]["expires_at"] = new_expiry.isoformat()
            self.emails[email]["is_active"] = True
            self.save_emails()
            return True
        return False
    
    def remove_email(self, email):
        """Remove an email from management"""
        if email in self.emails:
            del self.emails[email]
            self.save_emails()
            return True
        return False
    
    def get_email_info(self, email):
        """Get information about an email"""
        if email in self.emails:
            info = self.emails[email].copy()
            info["expires_at"] = datetime.fromisoformat(info["expires_at"])
            info["created_at"] = datetime.fromisoformat(info["created_at"])
            return info
        return None
    
    def get_all_emails(self):
        """Get all managed emails with their status"""
        now = datetime.now()
        result = []
        
        for email, info in self.emails.items():
            expires_at = datetime.fromisoformat(info["expires_at"])
            is_expired = expires_at < now
            
            if is_expired and info["is_active"]:
                info["is_active"] = False
                self.save_emails()
            
            result.append({
                "email": email,
                "username": info["username"],
                "domain": info["domain"],
                "created_at": datetime.fromisoformat(info["created_at"]),
                "expires_at": expires_at,
                "is_active": info["is_active"],
                "is_expired": is_expired,
                "days_remaining": (expires_at - now).days if not is_expired else 0
            })
        
        return sorted(result, key=lambda x: (not x["is_active"], x["expires_at"]), reverse=True)
    
    def save_emails(self):
        """Save emails to config file"""
        with open(self.config_file, "w") as f:
            json.dump(self.emails, f, indent=2)
    
    def load_emails(self):
        """Load emails from config file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r") as f:
                    self.emails = json.load(f)
        except Exception:
            self.emails = {} 