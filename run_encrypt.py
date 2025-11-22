#!/usr/bin/env python3
"""
Launcher for Image Encryption Program
Captures photos from webcam and encrypts them with AES-256
"""

if __name__ == "__main__":
    from encryption.app import CaptureApp
    
    app = CaptureApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
