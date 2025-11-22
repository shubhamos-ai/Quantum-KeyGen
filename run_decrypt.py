#!/usr/bin/env python3
"""
Launcher for Image Decryption Program
Decrypts encrypted images using the encryption key
"""

if __name__ == "__main__":
    from decryption.app import DecryptApp
    
    app = DecryptApp()
    app.mainloop()
