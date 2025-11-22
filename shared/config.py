import os
from pathlib import Path

# Get the root directory of the project
ROOT_DIR = Path(__file__).parent.parent.absolute()

# Shared storage directories
ENCRYPTED_IMAGES_DIR = ROOT_DIR / "encrypted_images"
KEYS_DIR = ROOT_DIR / "keys"

def ensure_directories():
    """Create necessary directories if they don't exist."""
    ENCRYPTED_IMAGES_DIR.mkdir(exist_ok=True)
    KEYS_DIR.mkdir(exist_ok=True)

# Initialize directories when module is imported
ensure_directories()
