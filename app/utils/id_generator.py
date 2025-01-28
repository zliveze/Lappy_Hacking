import uuid
import hashlib
import random

class IDGenerator:
    """Generator for application IDs"""
    
    SUPPORTED_APPS = {"Cursor", "Windsurf", "AIDE"}
    ID_KEYS = [
        "telemetry.machineId",
        "telemetry.sqmId",
        "telemetry.devDeviceId",
        "telemetry.macMachineId"
    ]
    
    def __init__(self):
        self.current_ids = {}
        
    def _generate_machine_id(self):
        """Generate a machine ID using SHA-256"""
        return hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()
    
    def _generate_uuid(self):
        """Generate a UUID string"""
        return str(uuid.uuid4())
        
    def generate_ids(self, app_name):
        """Tạo ID duy nhất cho từng loại ứng dụng"""
        base_seed = {
            "Cursor": str(uuid.getnode()),  # Dùng hardware address
            "Windsurf": str(random.getrandbits(256)),  # Random số lớn
            "AIDE": str(uuid.uuid4())  # UUID ngẫu nhiên
        }.get(app_name, "")
        
        machine_hash = hashlib.sha256(f"{app_name}_{base_seed}".encode()).hexdigest()
        
        return {
            "telemetry.macMachineId": hashlib.sha256(f"{machine_hash}_MAC".encode()).hexdigest(),
            "telemetry.sqmId": "{" + str(uuid.uuid4()).upper() + "}",
            "telemetry.machineId": hashlib.sha256(f"{machine_hash}_MACHINE".encode()).hexdigest(),
            "telemetry.devDeviceId": str(uuid.uuid4())
        }
    
    def get_current_ids(self):
        """Get the most recently generated IDs"""
        return self.current_ids.copy() if self.current_ids else None
