# overlay_controller.py
import tkinter as tk
from tkinter import ttk, messagebox
import ctypes
import sys
import subprocess
import os
import threading
from PIL import Image, ImageTk


class BlackOverlayController:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("DarkScn")
        self.root.geometry("220x140")
        self.root.resizable(False, False)
        
        # ตัวแปรเก็บสถานะ
        self.overlay_process = None
        self.is_overlay_active = False
        self.custom_key = 'None'  # เก็บค่า custom key
        self.custom_key_raw = None  # เก็บค่า raw key สำหรับการเปรียบเทียบ
        
        # ตั้งค่า icon สำหรับหน้าต่าง
        self.set_window_icon()
        
        # สร้าง UI
        self.create_ui()
        
        # ทำให้หน้าต่าง UI อยู่ด้านบนเสมอ
        self.root.attributes("-topmost", True)
        
        # ป้องกันการขยับหน้าต่าง (ทำให้ไม่สามารถ drag ได้)
        self.make_window_unmovable()
        
    def set_window_icon(self):
        """ตั้งค่า icon สำหรับหน้าต่าง"""
        try:
            # โหลดรูป icon
            icon_img = Image.open("book_icon.png")
            
            # ปรับขนาด icon ให้เหมาะสม (32x32 หรือ 16x16)
            icon_img = icon_img.resize((32, 32), Image.Resampling.LANCZOS)
            self.window_icon = ImageTk.PhotoImage(icon_img)
            
            # ตั้งค่า icon ให้หน้าต่าง
            self.root.iconphoto(True, self.window_icon)
            
        except FileNotFoundError:
            print("Warning: ไม่พบไฟล์ book_icon.png - ใช้ icon เริ่มต้น")
        except Exception as e:
            print(f"Warning: เกิดข้อผิดพลาดในการโหลด icon: {e}")
    
    def make_window_unmovable(self):
        """ทำให้หน้าต่างไม่สามารถขยับได้"""
        def disable_event():
            pass
        
        # ปิดการทำงานของ title bar drag
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # ใช้ Windows API เพื่อป้องกันการขยับ
        def prevent_move():
            try:
                hwnd = self.root.winfo_id()
                # ลบ WS_CAPTION และ WS_THICKFRAME ออก
                style = ctypes.windll.user32.GetWindowLongW(hwnd, -16)
                style &= ~0x00C00000  # ลบ WS_CAPTION
                style &= ~0x00040000  # ลบ WS_THICKFRAME
                ctypes.windll.user32.SetWindowLongW(hwnd, -16, style)
                
                # อัพเดทหน้าต่าง
                ctypes.windll.user32.SetWindowPos(hwnd, 0, 0, 0, 0, 0, 0x0027)
            except:
                pass
                
        self.root.after(100, prevent_move)
        
    def create_ui(self):
        # สร้าง Frame หลัก
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame สำหรับปุ่ม
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        # โหลดรูปภาพ
        self.load_images()
        
        # สร้างปุ่ม Open (Lock)
        open_frame = ttk.Frame(button_frame)
        open_frame.pack(side=tk.LEFT, padx=10)
        
        self.open_btn = tk.Button(open_frame, 
                                 image=self.lock_img if hasattr(self, 'lock_img') else None,
                                 command=self.open_overlay,
                                 bd=0, highlightthickness=0, relief='flat',
                                 bg=self.root.cget('bg'), activebackground=self.root.cget('bg'))
        self.open_btn.pack()
        ttk.Label(open_frame, text="Open", font=("Arial", 9, "bold")).pack(pady=(5,0))
        
        # สร้างปุ่ม Close (Unlock)  
        close_frame = ttk.Frame(button_frame)
        close_frame.pack(side=tk.LEFT, padx=10)
        
        self.close_btn = tk.Button(close_frame,
                                  image=self.unlock_img if hasattr(self, 'unlock_img') else None,
                                  command=self.close_overlay,
                                  bd=0, highlightthickness=0, relief='flat',
                                  bg=self.root.cget('bg'), activebackground=self.root.cget('bg'))
        self.close_btn.pack()
        ttk.Label(close_frame, text="Close", font=("Arial", 9, "bold")).pack(pady=(5,0))
        
        # สร้างปุ่ม Edit (Settings)
        edit_frame = ttk.Frame(button_frame)
        edit_frame.pack(side=tk.LEFT, padx=10)
        
        self.edit_btn = tk.Button(edit_frame,
                                 image=self.edit_img if hasattr(self, 'edit_img') else None,
                                 command=self.edit_settings,
                                 bd=0, highlightthickness=0, relief='flat',
                                 bg=self.root.cget('bg'), activebackground=self.root.cget('bg'))
        self.edit_btn.pack()
        ttk.Label(edit_frame, text="Edit", font=("Arial", 9, "bold")).pack(pady=(5,0))
        
        # แสดงสถานะ
        self.status_label = ttk.Label(main_frame, text="Status: Ready", font=("Arial", 8))
        self.status_label.pack(pady=(10,0))
        
    def load_images(self):
        """โหลดรูปภาพสำหรับปุ่ม"""
        try:
            # ปรับขนาดรูปภาพ
            lock_img = Image.open("lock.png").resize((32, 32), Image.Resampling.LANCZOS)
            self.lock_img = ImageTk.PhotoImage(lock_img)
            
            unlock_img = Image.open("unlock.png").resize((32, 32), Image.Resampling.LANCZOS)
            self.unlock_img = ImageTk.PhotoImage(unlock_img)
            
            edit_img = Image.open("edit.png").resize((32, 32), Image.Resampling.LANCZOS)
            self.edit_img = ImageTk.PhotoImage(edit_img)
            
        except FileNotFoundError as e:
            messagebox.showwarning("Warning", f"ไม่พบไฟล์รูปภาพ: {e.filename}")
        except Exception as e:
            messagebox.showerror("Error", f"เกิดข้อผิดพลาดในการโหลดรูปภาพ: {str(e)}")
    
    def open_overlay(self):
        """เปิดหน้าจอสีดำ"""
        if not self.is_overlay_active:
            try:
                # รันไฟล์ black_overlay.py ในกระบวนการแยก
                self.overlay_process = subprocess.Popen([sys.executable, "black_overlay.py"])
                self.is_overlay_active = True
                self.status_label.config(text="Status: Overlay Active")
                
                # ตรวจสอบสถานะของ process
                self.check_overlay_process()
                
            except FileNotFoundError:
                messagebox.showerror("Error", "ไม่พบไฟล์ black_overlay.py")
            except Exception as e:
                messagebox.showerror("Error", f"เกิดข้อผิดพลาด: {str(e)}")
        else:
            messagebox.showinfo("Info", "Overlay กำลังทำงานอยู่แล้ว")
    
    def close_overlay(self):
        """ปิดหน้าจอสีดำ"""
        if self.is_overlay_active and self.overlay_process:
            try:
                self.overlay_process.terminate()
                self.overlay_process = None
                self.is_overlay_active = False
                self.status_label.config(text="Status: Overlay Closed")
            except Exception as e:
                messagebox.showerror("Error", f"เกิดข้อผิดพลาดในการปิด: {str(e)}")
        else:
            messagebox.showinfo("Info", "ไม่มี Overlay ที่กำลังทำงานอยู่")
    
    def edit_settings(self):
        """เปิดหน้าต่าง Select Box สำหรับตั้งค่า"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("300x200")
        settings_window.resizable(False, False)
        settings_window.attributes("-topmost", True)
        
        # จัดกลางหน้าจอ
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # เนื้อหาการตั้งค่า
        main_frame = ttk.Frame(settings_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Hotkey Settings", font=("Arial", 12, "bold")).pack(pady=(0,15))
        
        # 1. Default close
        default_frame = ttk.Frame(main_frame)
        default_frame.pack(fill=tk.X, pady=5)
        ttk.Label(default_frame, text="Default close:", width=15).pack(side=tk.LEFT)
        ttk.Label(default_frame, text="Esc", font=("Arial", 9), foreground="blue").pack(side=tk.LEFT)
        
        # 2. Play Custom Key
        custom_frame = ttk.Frame(main_frame)
        custom_frame.pack(fill=tk.X, pady=5)
        ttk.Label(custom_frame, text="Play Custom Key:", width=15).pack(side=tk.LEFT)
        
        # แสดงค่า custom key ที่บันทึกไว้
        custom_key_text = getattr(self, 'custom_key', 'None')
        self.custom_key_label = ttk.Label(custom_frame, text=custom_key_text, 
                                         font=("Arial", 9), foreground="green" if custom_key_text != 'None' else "gray")
        self.custom_key_label.pack(side=tk.LEFT)
        
        # 3. Set Custom Key button
        set_key_frame = ttk.Frame(main_frame)
        set_key_frame.pack(fill=tk.X, pady=15)
        
        ttk.Button(set_key_frame, text="Set Custom Key...", 
                  command=self.open_key_setter).pack()
        
        # ปุ่มปิด
        ttk.Button(main_frame, text="Close", 
                  command=settings_window.destroy).pack(pady=(20,0))
    
    def open_key_setter(self):
        """เปิดหน้าต่างสำหรับตั้งค่า Custom Key"""
        key_window = tk.Toplevel(self.root)
        key_window.title("Set Custom Key")
        key_window.geometry("350x170")
        key_window.resizable(False, False)
        key_window.attributes("-topmost", True)
        
        # จัดกลางหน้าจอ
        key_window.transient(self.root)
        key_window.grab_set()
        
        main_frame = ttk.Frame(key_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Press a key to set as custom hotkey", 
                 font=("Arial", 10)).pack(pady=(0,10))
        
        # แสดงคีย์ที่กด
        self.key_display = ttk.Label(main_frame, text="Waiting for key...", 
                                    font=("Arial", 12, "bold"), foreground="red")
        self.key_display.pack(pady=10)
        
        # ตัวแปรเก็บคีย์
        self.captured_key = None
        
        def on_key_press(event):
            # แปลงคีย์ให้เป็นชื่อที่อ่านง่าย
            key_name = self.format_key_name(event.keysym)
            self.captured_key = event.keysym
            self.key_display.config(text=f"Key: {key_name}", foreground="green")
            
            # เปิดใช้งานปุ่ม Save
            save_btn.config(state="normal")
        
        # ผูกการกดคีย์
        key_window.bind("<KeyPress>", on_key_press)
        key_window.focus_set()
        
        # Frame สำหรับปุ่ม
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=15)
        
        # ปุ่ม Save
        save_btn = ttk.Button(button_frame, text="Save", state="disabled",
                             command=lambda: self.save_custom_key(key_window))
        save_btn.pack(side=tk.LEFT, padx=5)
        
        # ปุ่ม Cancel
        ttk.Button(button_frame, text="Cancel", 
                  command=key_window.destroy).pack(side=tk.LEFT, padx=5)
    
    def format_key_name(self, keysym):
        """แปลงชื่อคีย์ให้อ่านง่าย"""
        key_mapping = {
            'Return': 'Enter',
            'BackSpace': 'Backspace',
            'Tab': 'Tab',
            'Escape': 'Esc',
            'space': 'Space',
            'Up': 'Arrow Up',
            'Down': 'Arrow Down',
            'Left': 'Arrow Left',
            'Right': 'Arrow Right',
            'Control_L': 'Ctrl',
            'Control_R': 'Ctrl',
            'Alt_L': 'Alt',
            'Alt_R': 'Alt',
            'Shift_L': 'Shift',
            'Shift_R': 'Shift'
        }
        
        return key_mapping.get(keysym, keysym.upper() if len(keysym) == 1 else keysym)
    
    def save_custom_key(self, window):
        """บันทึก Custom Key"""
        if self.captured_key:
            self.custom_key = self.format_key_name(self.captured_key)
            self.custom_key_raw = self.captured_key
            
            # อัพเดทข้อความใน settings window ถ้ายังเปิดอยู่
            if hasattr(self, 'custom_key_label'):
                self.custom_key_label.config(text=self.custom_key, foreground="green")
            
            messagebox.showinfo("Success", f"Custom key set to: {self.custom_key}")
            window.destroy()
        else:
            messagebox.showwarning("Warning", "Please press a key first!")
    
    def check_overlay_process(self):
        """ตรวจสอบสถานะของ overlay process"""
        if self.overlay_process and self.is_overlay_active:
            if self.overlay_process.poll() is not None:
                # Process หยุดทำงานแล้ว
                self.is_overlay_active = False
                self.overlay_process = None
                self.status_label.config(text="Status: Overlay Closed")
            else:
                # ตรวจสอบอีกครั้งหลัง 1 วินาที
                self.root.after(1000, self.check_overlay_process)
    
    def on_closing(self):
        """เมื่อปิดโปรแกรม"""
        if self.is_overlay_active and self.overlay_process:
            self.overlay_process.terminate()
        self.root.destroy()
    
    def run(self):
        """รันโปรแกรม"""
        self.root.mainloop()

if __name__ == "__main__":
    app = BlackOverlayController()
    app.run()