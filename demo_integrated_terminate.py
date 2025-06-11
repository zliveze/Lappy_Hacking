# demo_integrated_terminate.py - Demo chức năng terminate tích hợp
import sys
import os

# Thêm thư mục src vào Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def demo_terminate_specific():
    """Demo terminate IDE cụ thể"""
    print("🛑 DEMO: Terminate IDE cụ thể")
    print("=" * 50)
    
    try:
        import psutil
        
        # Hiển thị processes hiện tại
        print("📋 Processes hiện tại:")
        ide_processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                proc_name = proc.info['name'].lower()
                cmdline = ' '.join(proc.info['cmdline']).lower() if proc.info['cmdline'] else ""
                
                # Tìm IDE processes
                ide_patterns = ['cursor', 'windsurf', 'code', 'vscode', 'vscodium']
                for pattern in ide_patterns:
                    if pattern in proc_name or pattern in cmdline:
                        ide_processes.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'pattern': pattern
                        })
                        break
                        
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if ide_processes:
            print(f"   Tìm thấy {len(ide_processes)} IDE processes:")
            for proc in ide_processes:
                print(f"   - {proc['name']} (PID: {proc['pid']}) - {proc['pattern']}")
        else:
            print("   Không có IDE processes nào đang chạy")
            
        print("\n💡 Trong ứng dụng thực tế:")
        print("   1. Chọn IDE trong dropdown (cursor, windsurf, etc.)")
        print("   2. Click 'Reset IDE IDs'")
        print("   3. Tool sẽ tự động:")
        print("      - Terminate IDE đó")
        print("      - Đợi 2 giây")
        print("      - Reset IDs")
        print("      - Lock files")
        print("      - Thông báo hoàn thành")
        
    except Exception as e:
        print(f"❌ Lỗi: {str(e)}")

def demo_workflow():
    """Demo workflow tích hợp"""
    print("\n🚀 DEMO: Workflow tích hợp")
    print("=" * 50)
    
    print("📋 QUY TRÌNH RESET IDE (Tích hợp Terminate):")
    print()
    print("1. 🔍 User chọn IDE: 'cursor'")
    print("2. 🖱️ User click 'Reset IDE IDs'")
    print("3. ❓ Hiển thị dialog xác nhận:")
    print("   '🔄 RESET CURSOR IDs'")
    print("   'Quá trình sẽ:'")
    print("   '1. 🛑 Terminate Cursor processes'")
    print("   '2. 🔄 Reset Cursor telemetry IDs'")
    print("   '3. 🔒 Lock files'")
    print("   'Bạn có chắc chắn muốn tiếp tục?'")
    print()
    print("4. ✅ User click 'Yes'")
    print("5. 🛑 Tool terminate Cursor processes")
    print("6. ⏳ Đợi 2 giây")
    print("7. 🔄 Reset Cursor IDs")
    print("8. 🔒 Lock files")
    print("9. 🎉 Thông báo hoàn thành")
    print("10. 🚀 User có thể khởi động lại Cursor")
    
    print("\n🎯 LỢI ÍCH:")
    print("   ✅ Không cần terminate thủ công")
    print("   ✅ Đảm bảo IDE đóng hoàn toàn trước khi reset")
    print("   ✅ Quy trình tự động, an toàn")
    print("   ✅ Thông báo rõ ràng từng bước")
    print("   ✅ Xác nhận trước khi thực hiện")

def demo_ui_changes():
    """Demo thay đổi giao diện"""
    print("\n🖥️ DEMO: Thay đổi giao diện")
    print("=" * 50)
    
    print("📋 GIAO DIỆN CŨ:")
    print("Row 1: [Reset JetBrains] [Chọn IDE ▼] [Reset IDE IDs] [Clean Augment DB]")
    print("Row 2: [Clean Telemetry] [Terminate IDEs] [Reset All IDs] [Check Status]")
    print()
    print("📋 GIAO DIỆN MỚI:")
    print("Row 1: [Reset JetBrains] [Chọn IDE ▼] [Reset IDE IDs] [Clean Augment DB]")
    print("                                        ↑ Đã tích hợp terminate")
    print("Row 2: [Clean Telemetry] [Reset All IDs] [Check IDE Status]")
    print("                         ↑ Đã tích hợp terminate")
    print()
    print("🔄 THAY ĐỔI:")
    print("   ❌ Loại bỏ nút 'Terminate IDEs' riêng biệt")
    print("   ✅ Tích hợp terminate vào 'Reset IDE IDs'")
    print("   ✅ Tích hợp terminate vào 'Reset All IDs'")
    print("   ✅ Giao diện gọn gàng hơn")
    print("   ✅ Workflow tự nhiên hơn")

def demo_safety_features():
    """Demo tính năng an toàn"""
    print("\n🛡️ DEMO: Tính năng an toàn")
    print("=" * 50)
    
    print("🔒 CÁC BIỆN PHÁP AN TOÀN:")
    print()
    print("1. 📋 XÁC NHẬN TRƯỚC KHI THỰC HIỆN:")
    print("   - Hiển thị dialog chi tiết")
    print("   - Liệt kê từng bước sẽ thực hiện")
    print("   - Cảnh báo IDE sẽ bị đóng")
    print("   - User phải click 'Yes' để tiếp tục")
    print()
    print("2. ⏳ THỜI GIAN CHỜ:")
    print("   - Đợi 2 giây sau terminate")
    print("   - Đảm bảo processes đóng hoàn toàn")
    print("   - Tránh lỗi file đang được sử dụng")
    print()
    print("3. 📊 THÔNG BÁO CHI TIẾT:")
    print("   - Log từng bước thực hiện")
    print("   - Hiển thị số processes đã terminate")
    print("   - Thông báo kết quả từng bước")
    print("   - Hướng dẫn khởi động lại IDE")
    print()
    print("4. 🔄 XỬ LÝ LỖI:")
    print("   - Try-catch cho từng bước")
    print("   - Tiếp tục reset nếu terminate thất bại")
    print("   - Thông báo lỗi rõ ràng")
    print("   - Không crash ứng dụng")

if __name__ == "__main__":
    print("🚀 DEMO: Lappy Lab 4.1 - Integrated Terminate Feature")
    print("=" * 60)
    
    demo_terminate_specific()
    demo_workflow()
    demo_ui_changes()
    demo_safety_features()
    
    print("\n" + "=" * 60)
    print("✅ Demo hoàn thành!")
    print("\n🎯 TÓM TẮT:")
    print("   ✅ Đã tích hợp terminate vào Reset IDE IDs")
    print("   ✅ Quy trình tự động, an toàn")
    print("   ✅ Giao diện gọn gàng hơn")
    print("   ✅ Trải nghiệm người dùng tốt hơn")
