# check_database.py - Kiểm tra nội dung database VSCode
import sqlite3
import os
from pathlib import Path

def check_vscode_database():
    """Kiểm tra nội dung database VSCode"""
    
    # Tìm database VSCode
    vscode_paths = [
        Path.home() / "AppData" / "Roaming" / "Code" / "User" / "globalStorage" / "state.vscdb",
        Path.home() / "AppData" / "Roaming" / "Cursor" / "User" / "globalStorage" / "state.vscdb",
        Path.home() / "AppData" / "Roaming" / "Code" / "User" / "workspaceStorage"
    ]
    
    for base_path in vscode_paths:
        if base_path.exists():
            if base_path.is_file():
                print(f"\n📁 Checking database: {base_path}")
                analyze_database(base_path)
            elif base_path.is_dir():
                print(f"\n📁 Checking workspace storage: {base_path}")
                for workspace_dir in base_path.iterdir():
                    if workspace_dir.is_dir():
                        db_file = workspace_dir / "state.vscdb"
                        if db_file.exists():
                            print(f"  📄 {db_file}")
                            analyze_database(db_file)

def analyze_database(db_path):
    """Phân tích một database file"""
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Kiểm tra tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"    Tables: {[t[0] for t in tables]}")
        
        # Kiểm tra ItemTable nếu có
        if any('ItemTable' in str(t) for t in tables):
            # Đếm tổng số entries
            cursor.execute("SELECT COUNT(*) FROM ItemTable;")
            total_count = cursor.fetchone()[0]
            print(f"    Total entries: {total_count}")
            
            # Tìm entries có chứa 'augment'
            cursor.execute("SELECT COUNT(*) FROM ItemTable WHERE key LIKE '%augment%';")
            augment_count = cursor.fetchone()[0]
            print(f"    Entries with 'augment': {augment_count}")
            
            # Tìm entries có chứa 'telemetry'
            cursor.execute("SELECT COUNT(*) FROM ItemTable WHERE key LIKE '%telemetry%';")
            telemetry_count = cursor.fetchone()[0]
            print(f"    Entries with 'telemetry': {telemetry_count}")
            
            # Hiển thị một số keys mẫu
            cursor.execute("SELECT key FROM ItemTable LIMIT 10;")
            sample_keys = cursor.fetchall()
            print(f"    Sample keys:")
            for key in sample_keys:
                print(f"      - {key[0]}")
                
            # Tìm keys có chứa machine, device, id
            interesting_patterns = ['machine', 'device', 'id', 'uuid', 'telemetry']
            for pattern in interesting_patterns:
                cursor.execute(f"SELECT COUNT(*) FROM ItemTable WHERE key LIKE '%{pattern}%';")
                count = cursor.fetchone()[0]
                if count > 0:
                    print(f"    Entries with '{pattern}': {count}")
                    
                    # Hiển thị một số keys mẫu
                    cursor.execute(f"SELECT key FROM ItemTable WHERE key LIKE '%{pattern}%' LIMIT 3;")
                    keys = cursor.fetchall()
                    for key in keys:
                        print(f"      - {key[0]}")
        
        conn.close()
        
    except Exception as e:
        print(f"    ❌ Error: {e}")

if __name__ == "__main__":
    print("🔍 Checking VSCode databases...")
    check_vscode_database()
    print("\n✅ Done!")
