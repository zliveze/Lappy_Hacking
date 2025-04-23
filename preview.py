import os
import sys
import platform
import tkinter as tk
from gui import LappyLabGUI

def main():
    """Hàm chính để xem trước giao diện"""
    print("Đang khởi động Lappy Lab Preview...")
    
    # Chạy giao diện người dùng
    root = tk.Tk()
    app = LappyLabGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 