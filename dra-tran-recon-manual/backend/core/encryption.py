from cryptography.fernet import Fernet
import os
import base64

# Generate key from env or create new
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
if not ENCRYPTION_KEY:
    # Generate a key for development
    ENCRYPTION_KEY = base64.urlsafe_b64encode(os.urandom(32)).decode()


def encrypt_config(config_json: str) -> str:
    """Encrypt a JSON config string"""
    f = Fernet(ENCRYPTION_KEY)
    return f.encrypt(config_json.encode()).decode()


def decrypt_config(encrypted: str) -> str:
    """Decrypt an encrypted config string"""
    f = Fernet(ENCRYPTION_KEY)
    return f.decrypt(encrypted.encode()).decode()
