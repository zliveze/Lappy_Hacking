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
        # Tạo seed ngẫu nhiên mới mỗi lần gọi
        random_seed = str(uuid.uuid4()) + str(random.getrandbits(256))
        
        # Tạo base hash từ seed
        base_hash = hashlib.sha256(random_seed.encode()).hexdigest()
        
        return {
            "telemetry.macMachineId": hashlib.sha256(f"{base_hash}_MAC_{random_seed}".encode()).hexdigest(),
            "telemetry.sqmId": "{" + str(uuid.uuid4()).upper() + "}",
            "telemetry.machineId": hashlib.sha256(f"{base_hash}_MACHINE_{random_seed}".encode()).hexdigest(),
            "telemetry.devDeviceId": str(uuid.uuid4())
        }
    
    def get_current_ids(self):
        """Get the most recently generated IDs"""
        return self.current_ids.copy() if self.current_ids else None
