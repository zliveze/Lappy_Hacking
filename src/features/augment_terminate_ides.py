# features/augment_terminate_ides.py - Terminate IDEs
import psutil
import platform
import subprocess
import time
from pathlib import Path

def terminate_ides():
    """Terminate tất cả IDEs đang chạy - theo logic của Augment VIP"""
    try:
        # Theo Augment VIP: chỉ terminate VSCode-based và .augmentcode processes
        # Dòng 61 trong main.rs: if !cmd_str.contains("vscode") && !cmd_str.contains(".augmentcode") { continue; }

        results = []
        terminated_count = 0

        results.append("🔍 Đang tìm kiếm VSCode-based IDE processes...")
        results.append("📋 Theo logic Augment VIP: chỉ terminate VSCode variants và Augment Code")
        
        # Tìm và terminate processes theo logic Augment VIP
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                proc_name = proc.info['name'].lower()
                cmdline = ' '.join(proc.info['cmdline']).lower() if proc.info['cmdline'] else ""

                # Logic chính xác từ Augment VIP (dòng 61):
                # if !cmd_str.contains("vscode") && !cmd_str.contains(".augmentcode") { continue; }
                # Nghĩa là: chỉ xử lý processes có chứa "vscode" HOẶC ".augmentcode"

                should_terminate = False
                matched_ide = ""

                if "vscode" in cmdline:
                    should_terminate = True
                    matched_ide = "VSCode-based IDE"
                elif ".augmentcode" in cmdline:
                    should_terminate = True
                    matched_ide = "Augment Code IDE"

                if should_terminate:
                    try:
                        # Terminate process
                        proc.terminate()
                        
                        # Đợi process kết thúc
                        try:
                            proc.wait(timeout=5)
                            results.append(f"✅ Terminated: {proc.info['name']} (PID: {proc.info['pid']}) - {matched_ide}")
                            terminated_count += 1
                        except psutil.TimeoutExpired:
                            # Force kill nếu không terminate được
                            proc.kill()
                            results.append(f"🔥 Force killed: {proc.info['name']} (PID: {proc.info['pid']}) - {matched_ide}")
                            terminated_count += 1
                            
                    except psutil.NoSuchProcess:
                        results.append(f"⚠️ Process already terminated: {proc.info['name']} (PID: {proc.info['pid']})")
                    except psutil.AccessDenied:
                        results.append(f"❌ Access denied: {proc.info['name']} (PID: {proc.info['pid']}) - {matched_ide}")
                    except Exception as e:
                        results.append(f"❌ Error terminating {proc.info['name']}: {str(e)}")
                        
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
            except Exception as e:
                continue
        
        # Terminate parent processes nếu cần
        terminated_count += terminate_parent_processes(results)
        
        if terminated_count > 0:
            results.append("")
            results.append(f"🎉 Đã terminate {terminated_count} IDE processes")
            results.append("⚠️ Lưu ý: Hãy đợi vài giây trước khi khởi động lại IDEs")
            return True, "\n".join(results)
        else:
            results.append("")
            results.append("ℹ️ Không tìm thấy IDE processes nào đang chạy")
            return True, "\n".join(results)
            
    except Exception as e:
        return False, f"Lỗi terminate IDEs: {str(e)}"

def terminate_parent_processes(results):
    """Terminate parent processes của IDEs"""
    terminated_count = 0
    
    try:
        # Tìm các parent process có thể liên quan
        parent_patterns = [
            "jetbrains",
            "intellij", 
            "pycharm",
            "webstorm",
            "phpstorm",
            "rubymine",
            "clion",
            "datagrip",
            "rider",
            "goland",
            "android-studio"
        ]
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                proc_name = proc.info['name'].lower()
                cmdline = ' '.join(proc.info['cmdline']).lower() if proc.info['cmdline'] else ""
                
                # Kiểm tra parent process
                is_parent = False
                matched_pattern = ""
                
                for pattern in parent_patterns:
                    if pattern in proc_name or pattern in cmdline:
                        is_parent = True
                        matched_pattern = pattern
                        break
                
                if is_parent:
                    try:
                        # Terminate parent process
                        proc.terminate()
                        
                        try:
                            proc.wait(timeout=3)
                            results.append(f"✅ Terminated parent: {proc.info['name']} (PID: {proc.info['pid']}) - {matched_pattern}")
                            terminated_count += 1
                        except psutil.TimeoutExpired:
                            proc.kill()
                            results.append(f"🔥 Force killed parent: {proc.info['name']} (PID: {proc.info['pid']}) - {matched_pattern}")
                            terminated_count += 1
                            
                    except psutil.NoSuchProcess:
                        pass
                    except psutil.AccessDenied:
                        results.append(f"❌ Access denied (parent): {proc.info['name']} (PID: {proc.info['pid']})")
                    except Exception as e:
                        results.append(f"❌ Error terminating parent {proc.info['name']}: {str(e)}")
                        
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
            except Exception:
                continue
                
    except Exception:
        pass
    
    return terminated_count

def get_running_ides():
    """Lấy danh sách IDEs đang chạy"""
    try:
        ide_processes = []
        
        # Danh sách IDE names để tìm kiếm
        ide_names = [
            "idea", "pycharm", "webstorm", "phpstorm", "rubymine", 
            "clion", "datagrip", "rider", "goland", "studio",
            "code", "cursor", "augment"
        ]
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'memory_info']):
            try:
                proc_name = proc.info['name'].lower()
                cmdline = ' '.join(proc.info['cmdline']).lower() if proc.info['cmdline'] else ""
                
                # Kiểm tra xem có phải IDE không
                is_ide = False
                ide_type = ""
                
                for ide_name in ide_names:
                    if ide_name in proc_name or ide_name in cmdline:
                        is_ide = True
                        ide_type = ide_name.upper()
                        break
                
                # Kiểm tra thêm cho VSCode variants
                if not is_ide:
                    if ("vscode" in cmdline or ".augmentcode" in cmdline):
                        is_ide = True
                        ide_type = "VSCODE/AUGMENT"
                
                if is_ide:
                    memory_mb = proc.info['memory_info'].rss / 1024 / 1024
                    ide_processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'type': ide_type,
                        'memory_mb': round(memory_mb, 1)
                    })
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
            except Exception:
                continue
        
        return ide_processes
        
    except Exception as e:
        return []

def analyze_running_ides():
    """Phân tích các IDEs đang chạy"""
    try:
        running_ides = get_running_ides()
        
        if not running_ides:
            return True, "ℹ️ Không có IDE nào đang chạy"
        
        results = []
        results.append(f"🔍 PHÂN TÍCH {len(running_ides)} IDE PROCESSES ĐANG CHẠY:")
        results.append("=" * 60)
        results.append("")
        
        # Nhóm theo loại IDE
        ide_groups = {}
        total_memory = 0
        
        for ide in running_ides:
            ide_type = ide['type']
            if ide_type not in ide_groups:
                ide_groups[ide_type] = []
            ide_groups[ide_type].append(ide)
            total_memory += ide['memory_mb']
        
        # Hiển thị theo nhóm
        for ide_type, processes in ide_groups.items():
            results.append(f"📁 {ide_type}:")
            group_memory = sum(p['memory_mb'] for p in processes)
            
            for proc in processes:
                results.append(f"   • {proc['name']} (PID: {proc['pid']}) - {proc['memory_mb']} MB")
            
            results.append(f"   Subtotal: {len(processes)} processes, {round(group_memory, 1)} MB")
            results.append("")
        
        results.append(f"📊 TỔNG KẾT:")
        results.append(f"   Total processes: {len(running_ides)}")
        results.append(f"   Total memory: {round(total_memory, 1)} MB")
        results.append(f"   IDE types: {len(ide_groups)}")
        
        return True, "\n".join(results)
        
    except Exception as e:
        return False, f"Lỗi phân tích running IDEs: {str(e)}"
