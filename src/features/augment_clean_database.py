# features/augment_clean_database.py - Clean VSCode Database
import sqlite3
import base64
from pathlib import Path

try:
    from .augment_utils import get_vscode_files, decode_base64_key, get_file_info
except ImportError:
    # Fallback functions
    def get_vscode_files():
        return []
    def decode_base64_key(key):
        try:
            return base64.b64decode(key).decode('utf-8')
        except:
            return None
    def get_file_info(path):
        return None

def clean_vscode_database():
    """Clean VSCode database để xóa dữ liệu Augment"""
    try:
        vscode_files = get_vscode_files()
        if not vscode_files:
            return False, "Không tìm thấy VSCode installations"

        # Decode các query từ base64 (như trong Augment VIP)
        count_query = decode_base64_key("U0VMRUNUIENPVU5UKCopIEZST00gSXRlbVRhYmxlIFdIRVJFIGtleSBMSUtFICclYXVnbWVudCUnOw==")
        delete_query = decode_base64_key("REVMRVRFIEZST00gSXRlbVRhYmxlIFdIRVJFIGtleSBMSUtFICclYXVnbWVudCUnOw==")

        if not count_query or not delete_query:
            return False, "Không thể decode database queries"

        results = []
        success_count = 0
        total_deleted = 0

        results.append("🔍 CLEAN VSCODE DATABASE - Theo logic Augment VIP")
        results.append("📋 Query: SELECT COUNT(*) FROM ItemTable WHERE key LIKE '%augment%'")
        results.append("")

        for vscode_path in vscode_files:
            try:
                # Tìm file state.vscdb
                db_files = find_database_files(vscode_path)

                for db_file in db_files:
                    try:
                        deleted_count = clean_single_database(db_file, count_query, delete_query, results)
                        if deleted_count >= 0:
                            success_count += 1
                            total_deleted += deleted_count
                    except Exception as e:
                        results.append(f"❌ Lỗi xử lý {db_file}: {str(e)}")

            except Exception as e:
                results.append(f"❌ Lỗi xử lý {vscode_path}: {str(e)}")

        # Thêm thông tin tổng kết
        results.append("")
        results.append("📊 TỔNG KẾT:")
        results.append(f"   Databases đã kiểm tra: {success_count}")
        results.append(f"   Entries đã xóa: {total_deleted}")

        if total_deleted == 0:
            results.append("")
            results.append("ℹ️ THÔNG TIN: Không có entries nào chứa 'augment' - đây là bình thường!")
            results.append("💡 Database VSCode thường không có entries 'augment' sẵn")
            results.append("✅ Tool đã hoạt động đúng theo logic Augment VIP gốc")

        message = "\n".join(results)
        return True, message  # Luôn return True vì đây là hành vi bình thường

    except Exception as e:
        return False, f"Lỗi clean VSCode database: {str(e)}"

def find_database_files(vscode_path):
    """Tìm các file database trong thư mục VSCode"""
    db_files = []
    
    try:
        # Tìm state.vscdb trong thư mục hiện tại
        state_db = vscode_path / "state.vscdb"
        if state_db.exists():
            db_files.append(state_db)
        
        # Tìm state.vscdb.backup
        backup_db = vscode_path / "state.vscdb.backup"
        if backup_db.exists():
            db_files.append(backup_db)
        
        # Tìm trong các thư mục con nếu là thư mục globalStorage
        if vscode_path.is_dir() and "globalStorage" in str(vscode_path):
            for item in vscode_path.iterdir():
                if item.is_file() and item.name.endswith(".vscdb"):
                    db_files.append(item)
                elif item.is_dir():
                    # Tìm trong thư mục con
                    for sub_item in item.iterdir():
                        if sub_item.is_file() and sub_item.name.endswith(".vscdb"):
                            db_files.append(sub_item)
    
    except Exception:
        pass
    
    return db_files

def clean_single_database(db_file, count_query, delete_query, results):
    """Clean một database file"""
    try:
        if not db_file.exists():
            return -1

        # Lấy thông tin file
        file_info = get_file_info(db_file)
        results.append(f"📁 Database: {db_file.name}")
        results.append(f"   Path: {db_file}")
        if file_info:
            results.append(f"   Size: {file_info['size_formatted']}")

        # Kết nối database
        conn = sqlite3.connect(str(db_file))
        cursor = conn.cursor()

        try:
            # Kiểm tra tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            table_names = [t[0] for t in tables]
            results.append(f"   Tables: {table_names}")

            # Kiểm tra ItemTable
            if 'ItemTable' not in table_names:
                results.append(f"   ⚠️ Không có ItemTable - bỏ qua")
                return 0

            # Đếm tổng entries
            cursor.execute("SELECT COUNT(*) FROM ItemTable;")
            total_entries = cursor.fetchone()[0]
            results.append(f"   Total entries: {total_entries}")

            # Kiểm tra số lượng entries cần xóa
            cursor.execute(count_query)
            rows_to_delete = cursor.fetchone()[0]

            if rows_to_delete > 0:
                results.append(f"   🔍 Tìm thấy {rows_to_delete} entries chứa 'augment'")

                # Hiển thị một số entries mẫu
                cursor.execute("SELECT key FROM ItemTable WHERE key LIKE '%augment%' LIMIT 3;")
                sample_keys = cursor.fetchall()
                for key in sample_keys:
                    results.append(f"      - {key[0]}")

                # Thực hiện xóa
                cursor.execute(delete_query)
                conn.commit()

                results.append(f"   ✅ Đã xóa {rows_to_delete} entries")
                return rows_to_delete
            else:
                results.append(f"   ℹ️ Không có entries nào chứa 'augment'")

                # Hiển thị một số entries mẫu để debug
                cursor.execute("SELECT key FROM ItemTable LIMIT 5;")
                sample_keys = cursor.fetchall()
                if sample_keys:
                    results.append(f"   📋 Sample keys:")
                    for key in sample_keys:
                        results.append(f"      - {key[0]}")

                return 0

        finally:
            conn.close()

    except sqlite3.Error as e:
        results.append(f"   ❌ Lỗi SQLite: {str(e)}")
        return -1
    except Exception as e:
        results.append(f"   ❌ Lỗi: {str(e)}")
        return -1

def analyze_vscode_databases():
    """Phân tích các database VSCode để hiển thị thông tin"""
    try:
        vscode_files = get_vscode_files()
        if not vscode_files:
            return False, "Không tìm thấy VSCode installations"
        
        results = []
        total_databases = 0
        
        # Decode count query
        count_query = decode_base64_key("U0VMRUNUIENPVU5UKCopIEZST00gSXRlbVRhYmxlIFdIRVJFIGtleSBMSUtFICclYXVnbWVudCUnOw==")
        if not count_query:
            return False, "Không thể decode count query"
        
        for vscode_path in vscode_files:
            try:
                db_files = find_database_files(vscode_path)
                
                for db_file in db_files:
                    try:
                        info = analyze_single_database(db_file, count_query)
                        if info:
                            results.append(info)
                            total_databases += 1
                    except Exception as e:
                        results.append(f"❌ Lỗi phân tích {db_file}: {str(e)}")
                        
            except Exception as e:
                results.append(f"❌ Lỗi xử lý {vscode_path}: {str(e)}")
        
        if total_databases > 0:
            header = f"📊 PHÂN TÍCH {total_databases} VSCode DATABASES:\n" + "=" * 60 + "\n\n"
            message = header + "\n".join(results)
            return True, message
        else:
            return False, "Không tìm thấy database nào để phân tích"
            
    except Exception as e:
        return False, f"Lỗi phân tích databases: {str(e)}"

def analyze_single_database(db_file, count_query):
    """Phân tích một database file"""
    try:
        if not db_file.exists():
            return None
        
        file_info = get_file_info(db_file)
        result = f"📁 {db_file.name}\n"
        result += f"   Path: {db_file}\n"
        
        if file_info:
            result += f"   Size: {file_info['size_formatted']}\n"
            result += f"   Permissions: {file_info['permissions']}\n"
            result += f"   Read-only: {'Yes' if file_info['is_readonly'] else 'No'}\n"
        
        # Kết nối database
        conn = sqlite3.connect(str(db_file))
        cursor = conn.cursor()
        
        try:
            # Kiểm tra tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            result += f"   Tables: {len(tables)}\n"
            
            # Kiểm tra entries cần xóa
            cursor.execute(count_query)
            augment_entries = cursor.fetchone()[0]
            result += f"   Augment entries: {augment_entries}\n"
            
            # Kiểm tra tổng số entries trong ItemTable nếu có
            try:
                cursor.execute("SELECT COUNT(*) FROM ItemTable;")
                total_entries = cursor.fetchone()[0]
                result += f"   Total entries: {total_entries}\n"
            except:
                pass
                
        finally:
            conn.close()
        
        result += "\n"
        return result
        
    except Exception as e:
        return f"❌ Lỗi phân tích {db_file}: {str(e)}\n\n"

def clean_telemetry_entries():
    """Clean các entries telemetry khác (không chỉ augment)"""
    try:
        vscode_files = get_vscode_files()
        if not vscode_files:
            return False, "Không tìm thấy VSCode installations"

        results = []
        success_count = 0
        total_deleted = 0

        results.append("🔍 CLEAN TELEMETRY ENTRIES - Mở rộng từ Augment VIP")
        results.append("📋 Xóa các entries: telemetry, machine, device, uuid")
        results.append("")

        # Các patterns để clean
        patterns = ['%telemetry%', '%machine%', '%device%', '%uuid%']

        for vscode_path in vscode_files:
            try:
                db_files = find_database_files(vscode_path)

                for db_file in db_files:
                    try:
                        deleted_count = clean_telemetry_single_database(db_file, patterns, results)
                        if deleted_count >= 0:
                            success_count += 1
                            total_deleted += deleted_count
                    except Exception as e:
                        results.append(f"❌ Lỗi xử lý {db_file}: {str(e)}")

            except Exception as e:
                results.append(f"❌ Lỗi xử lý {vscode_path}: {str(e)}")

        results.append("")
        results.append("📊 TỔNG KẾT:")
        results.append(f"   Databases đã xử lý: {success_count}")
        results.append(f"   Entries đã xóa: {total_deleted}")

        message = "\n".join(results)
        return True, message

    except Exception as e:
        return False, f"Lỗi clean telemetry entries: {str(e)}"

def clean_telemetry_single_database(db_file, patterns, results):
    """Clean telemetry entries từ một database"""
    try:
        if not db_file.exists():
            return -1

        results.append(f"📁 Database: {db_file.name}")

        conn = sqlite3.connect(str(db_file))
        cursor = conn.cursor()
        total_deleted = 0

        try:
            # Kiểm tra ItemTable
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [t[0] for t in cursor.fetchall()]

            if 'ItemTable' not in tables:
                results.append(f"   ⚠️ Không có ItemTable")
                return 0

            for pattern in patterns:
                # Đếm entries
                count_query = f"SELECT COUNT(*) FROM ItemTable WHERE key LIKE '{pattern}';"
                cursor.execute(count_query)
                count = cursor.fetchone()[0]

                if count > 0:
                    # Hiển thị một số keys mẫu
                    cursor.execute(f"SELECT key FROM ItemTable WHERE key LIKE '{pattern}' LIMIT 3;")
                    sample_keys = cursor.fetchall()

                    results.append(f"   🔍 Pattern '{pattern}': {count} entries")
                    for key in sample_keys:
                        results.append(f"      - {key[0]}")

                    # Xóa
                    delete_query = f"DELETE FROM ItemTable WHERE key LIKE '{pattern}';"
                    cursor.execute(delete_query)
                    total_deleted += count

            if total_deleted > 0:
                conn.commit()
                results.append(f"   ✅ Đã xóa tổng cộng {total_deleted} entries")
            else:
                results.append(f"   ℹ️ Không có telemetry entries nào")

            return total_deleted

        finally:
            conn.close()

    except Exception as e:
        results.append(f"   ❌ Lỗi: {str(e)}")
        return -1

def backup_database(db_file):
    """Tạo backup của database trước khi clean"""
    try:
        backup_file = db_file.with_suffix(db_file.suffix + ".backup")

        # Copy file
        import shutil
        shutil.copy2(db_file, backup_file)

        return True, f"Đã tạo backup: {backup_file}"
    except Exception as e:
        return False, f"Lỗi tạo backup: {str(e)}"
