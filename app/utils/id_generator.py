import uuid
import hashlib

class IDGenerator:
    def __init__(self):
        self.current_ids = {}
        
    def generate_machine_id(self):
        return hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()
    
    def generate_uuid(self):
        return str(uuid.uuid4())
        
    def generate_ids(self, app_name):
        machine_id = self.generate_machine_id()
        sqm_id = "{" + self.generate_uuid().upper() + "}"
        device_id = self.generate_uuid()
        mac_machine_id = self.generate_machine_id()
        
        if app_name == "Cursor":
            self.current_ids = {
                "telemetry.machineId": machine_id,
                "telemetry.sqmId": sqm_id,
                "telemetry.devDeviceId": device_id,
                "telemetry.macMachineId": mac_machine_id
            }
        elif app_name == "Windsurf":
            self.current_ids = {
                "telemetry.machineId": machine_id,
                "telemetry.sqmId": sqm_id,
                "telemetry.devDeviceId": device_id,
                "telemetry.macMachineId": mac_machine_id
            }
        else:
            raise ValueError(f"Invalid application: {app_name}")
        
        return self.current_ids
    
    def get_current_ids(self):
        return self.current_ids
