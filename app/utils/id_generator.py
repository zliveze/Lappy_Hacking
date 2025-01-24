import uuid
import hashlib

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
        """Generate all required IDs for an application"""
        if app_name not in self.SUPPORTED_APPS:
            raise ValueError(f"Unsupported application: {app_name}")
            
        self.current_ids = {
            "telemetry.machineId": self._generate_machine_id(),
            "telemetry.sqmId": "{" + self._generate_uuid().upper() + "}",
            "telemetry.devDeviceId": self._generate_uuid(),
            "telemetry.macMachineId": self._generate_machine_id()
        }
        return self.current_ids
    
    def get_current_ids(self):
        """Get the most recently generated IDs"""
        return self.current_ids.copy() if self.current_ids else None
