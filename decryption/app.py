import customtkinter as CTk
from tkinter import filedialog, messagebox
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import cv2 as cv
import numpy as np
from PIL import Image, ImageTk
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from shared.config import ENCRYPTED_IMAGES_DIR, KEYS_DIR

class DecryptApp(CTk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("700x700")
        self.title("Image Decryption")
        self.resizable(False, False)
        
        self.main_frame = CTk.CTkFrame(self, fg_color="#FCFCFC", bg_color="#FCFCFC")
        self.main_frame.pack(fill="both", expand=True)
        
        self.encrypted_file = None
        self.decrypted_image = None
        
        self.create_ui()
    
    def create_ui(self):
        header = CTk.CTkLabel(
            self.main_frame,
            text="Image Decryption System",
            font=CTk.CTkFont(size=36, weight="bold"),
            text_color="#000000"
        )
        header.pack(pady=20)
        
        CTk.CTkLabel(
            self.main_frame,
            text="Step 1: Select Encrypted Image",
            font=CTk.CTkFont(size=16, weight="bold"),
            text_color="#333333"
        ).pack(pady=(20, 5))
        
        self.select_file_btn = CTk.CTkButton(
            self.main_frame,
            text="Browse Encrypted File",
            width=200,
            height=40,
            fg_color="#2196F3",
            text_color="white",
            hover_color="#1976D2",
            corner_radius=10,
            font=CTk.CTkFont(size=14),
            command=self.select_file
        )
        self.select_file_btn.pack(pady=5)
        
        self.file_label = CTk.CTkLabel(
            self.main_frame,
            text="No file selected",
            font=CTk.CTkFont(size=12),
            text_color="#666666"
        )
        self.file_label.pack(pady=5)
        
        CTk.CTkLabel(
            self.main_frame,
            text="Step 2: Enter Encryption Key",
            font=CTk.CTkFont(size=16, weight="bold"),
            text_color="#333333"
        ).pack(pady=(20, 5))
        
        self.key_entry = CTk.CTkEntry(
            self.main_frame,
            width=500,
            height=40,
            placeholder_text="Paste your encryption key here (64 hex characters)",
            font=CTk.CTkFont(size=12)
        )
        self.key_entry.pack(pady=5)
        
        CTk.CTkLabel(
            self.main_frame,
            text="Or load key from file:",
            font=CTk.CTkFont(size=12),
            text_color="#666666"
        ).pack(pady=(5, 2))
        
        self.load_key_btn = CTk.CTkButton(
            self.main_frame,
            text="Load Key File",
            width=150,
            height=30,
            fg_color="#9C27B0",
            text_color="white",
            hover_color="#7B1FA2",
            corner_radius=8,
            font=CTk.CTkFont(size=12),
            command=self.load_key_file
        )
        self.load_key_btn.pack(pady=5)
        
        CTk.CTkLabel(
            self.main_frame,
            text="Step 3: Decrypt",
            font=CTk.CTkFont(size=16, weight="bold"),
            text_color="#333333"
        ).pack(pady=(20, 5))
        
        self.decrypt_btn = CTk.CTkButton(
            self.main_frame,
            text="Decrypt Image",
            width=200,
            height=50,
            fg_color="#4CAF50",
            text_color="white",
            hover_color="#45a049",
            corner_radius=10,
            font=CTk.CTkFont(size=18, weight="bold"),
            command=self.decrypt_image
        )
        self.decrypt_btn.pack(pady=10)
        
        self.status_label = CTk.CTkLabel(
            self.main_frame,
            text="Waiting for input...",
            font=CTk.CTkFont(size=14),
            text_color="#555555"
        )
        self.status_label.pack(pady=10)
        
        self.image_frame = CTk.CTkFrame(self.main_frame, width=400, height=300, fg_color="#e0e0e0")
        self.image_frame.pack(pady=10)
        self.image_frame.pack_propagate(False)
        
        self.image_label = CTk.CTkLabel(self.image_frame, text="Decrypted image will appear here", text_color="#888888")
        self.image_label.pack(expand=True)
    
    def select_file(self):
        filename = filedialog.askopenfilename(
            title="Select Encrypted Image",
            initialdir=str(ENCRYPTED_IMAGES_DIR),
            filetypes=[("Binary files", "*.bin"), ("All files", "*.*")]
        )
        
        if filename:
            self.encrypted_file = filename
            self.file_label.configure(text=f"Selected: {os.path.basename(filename)}")
            self.status_label.configure(text="File selected! Now enter the encryption key.")
    
    def load_key_file(self):
        filename = filedialog.askopenfilename(
            title="Select Key File",
            initialdir=str(KEYS_DIR),
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r') as f:
                    content = f.read()
                    for line in content.split('\n'):
                        if line.startswith("Encryption Key:"):
                            key = line.split(":")[1].strip()
                            self.key_entry.delete(0, 'end')
                            self.key_entry.insert(0, key)
                            self.status_label.configure(text="Key loaded successfully!")
                            return
                
                messagebox.showerror("Error", "Could not find encryption key in file")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load key file: {e}")
    
    def decrypt_image(self):
        if not self.encrypted_file:
            messagebox.showwarning("Missing Input", "Please select an encrypted file first!")
            return
        
        key_hex = self.key_entry.get().strip()
        
        if not key_hex:
            messagebox.showwarning("Missing Input", "Please enter the encryption key!")
            return
        
        if len(key_hex) != 64:
            messagebox.showerror("Invalid Key", "Encryption key must be exactly 64 hexadecimal characters!")
            return
        
        try:
            encryption_key = bytes.fromhex(key_hex)
        except ValueError:
            messagebox.showerror("Invalid Key", "Encryption key must contain only hexadecimal characters (0-9, a-f)!")
            return
        
        try:
            with open(self.encrypted_file, 'rb') as f:
                encrypted_content = f.read()
            
            if len(encrypted_content) < 16:
                raise ValueError("Encrypted file is too small or corrupted (minimum 16 bytes required for IV)")
            
            iv = encrypted_content[:16]
            encrypted_data = encrypted_content[16:]
            
            cipher = Cipher(
                algorithms.AES(encryption_key),
                modes.CFB(iv),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
            
            nparr = np.frombuffer(decrypted_data, np.uint8)
            image = cv.imdecode(nparr, cv.IMREAD_COLOR)
            
            if image is None:
                raise ValueError("Failed to decode image - incorrect key or corrupted file")
            
            self.decrypted_image = image
            
            self.display_image(image)
            
            self.status_label.configure(text="Decryption successful! Image displayed below.", text_color="#4CAF50")
            
            save = messagebox.askyesno("Save Image?", "Decryption successful! Do you want to save the decrypted image?")
            if save:
                self.save_decrypted_image()
            
        except Exception as e:
            messagebox.showerror("Decryption Failed", f"Error: {str(e)}\n\nPossible causes:\n- Incorrect encryption key\n- Corrupted encrypted file\n- File format mismatch")
            self.status_label.configure(text="Decryption failed! Check the key and file.", text_color="#f44336")
    
    def display_image(self, cv_image):
        rgb_image = cv.cvtColor(cv_image, cv.COLOR_BGR2RGB)
        
        pil_image = Image.fromarray(rgb_image)
        
        max_width, max_height = 380, 280
        pil_image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        
        photo = ImageTk.PhotoImage(pil_image)
        
        self.image_label.configure(image=photo, text="")
        self.image_label.image = photo
    
    def save_decrypted_image(self):
        if self.decrypted_image is None:
            return
        
        filename = filedialog.asksaveasfilename(
            title="Save Decrypted Image",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
        )
        
        if filename:
            cv.imwrite(filename, self.decrypted_image)
            messagebox.showinfo("Success", f"Image saved to {filename}")

if __name__ == "__main__":
    app = DecryptApp()
    app.mainloop()
