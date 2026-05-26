import os
from cryptography.fernet import Fernet
import base64

# Key should be a base64 encoded 32-byte string.
# In development, we use a fallback if not provided.
_fallback_key = base64.urlsafe_b64encode(b"01234567890123456789012345678912")
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", _fallback_key.decode("utf-8"))

try:
    _fernet = Fernet(ENCRYPTION_KEY.encode("utf-8"))
except Exception as e:
    # If the provided key is invalid, fallback to avoid app crash during import,
    # but encryption will fail or be insecure.
    _fernet = Fernet(_fallback_key)

def encrypt_value(value: str) -> str:
    if not value:
        return value
    return _fernet.encrypt(value.encode("utf-8")).decode("utf-8")

def decrypt_value(encrypted: str) -> str:
    if not encrypted:
        return encrypted
    try:
        return _fernet.decrypt(encrypted.encode("utf-8")).decode("utf-8")
    except Exception:
        # Return none or original if decryption fails
        return ""
