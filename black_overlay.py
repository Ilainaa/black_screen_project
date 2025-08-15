# black_overlay.py
# โปรแกรมสร้างหน้าจอสีดำที่คลิกทะลุได้ (Windows เท่านั้น

import tkinter as tk
import ctypes
import sys

def make_clickthrough(hwnd):
    """ทำให้หน้าต่างไม่รับเมาส์/คีย์บอร์ด (คลิกทะลุ)"""
    try:
        styles = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
        ctypes.windll.user32.SetWindowLongW(hwnd, -20, styles | 0x80000 | 0x20)
    except Exception as e:
        print(f"Error making window click-through: {e}")

def close_black_screen(event=None):
    """ปิดโปรแกรม"""
    sys.exit()

def main():
    # สร้างหน้าต่างหลัก
    root = tk.Tk()
    root.title("Black Overlay")
    
    # เปิดเต็มจอ
    root.attributes("-fullscreen", True)
    root.attributes("-topmost", True)
    root.configure(bg='black')
    
    # ปรับให้กด Esc ปิดได้
    root.bind("<Escape>", close_black_screen)
    root.bind("<KeyPress-q>", close_black_screen)  # กด q หรือ Q เพื่อปิด
    
    # รับ Custom Key จาก command-line argument
    if len(sys.argv) > 1:
        custom_key = sys.argv[1]
        if custom_key:
            try:
                root.bind(f"<{custom_key}>", close_black_screen)
                print(f"Custom close key '<{custom_key}>' is active.")
            except tk.TclError:
                print(f"Warning: Invalid custom key '{custom_key}'.")
    
    # ให้ focus ที่หน้าต่าง
    root.focus_set()
    
    # ไม่จำเป็นต้องมี Label เพราะผู้ใช้ปิดจาก Controller หรือ Hotkey
    
    # รอให้หน้าต่างพร้อม
    root.update()
    
    try:
        # ดึง hwnd ของหน้าต่างนี้
        hwnd = ctypes.windll.user32.GetForegroundWindow()

        
        # ทำให้คลิกทะลุได้
        make_clickthrough(hwnd)
        
        print("Black overlay started. Press ESC or Q to close.")
        
    except Exception as e:
        print(f"Warning: Could not make window click-through: {e}")
        print("Overlay will work but won't be click-through")
    
    # เริ่มโปรแกรม
    root.mainloop()

if __name__ == "__main__":
    main()