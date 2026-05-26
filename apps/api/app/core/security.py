from cryptography.fernet import Fernet
import base64
from apps.api.app.core.config import settings
import logging

logger = logging.getLogger(__name__)

def _get_fernet() -> Fernet:
    """
    Returns a Fernet instance using SYSTEM_SECRET_KEY.
    Ensures the key is properly formatted as a 32-byte url-safe base64 string.
    """
    key_str = settings.SYSTEM_SECRET_KEY
    try:
        # If the key is already a valid fernet key, this will succeed.
        # Otherwise, we encode it properly.
        if len(key_str) == 44 and key_str.endswith("="):
            key = key_str.encode()
        else:
            # Pad or truncate to 32 bytes, then base64 encode
            padded = key_str.ljust(32, '0')[:32].encode()
            key = base64.urlsafe_b64encode(padded)
        return Fernet(key)
    except Exception as e:
        logger.error(f"Failed to initialize Fernet: {e}")
        # Fallback to a random key if misconfigured, though this breaks decryption across restarts
        return Fernet(Fernet.generate_key())

_fernet = _get_fernet()

def encrypt_token(plain_token: str) -> str:
    """Encrypts a plaintext token for safe DB storage."""
    if not plain_token:
        return ""
    return _fernet.encrypt(plain_token.encode()).decode()

def decrypt_token(encrypted_token: str) -> str:
    """Decrypts a token from the DB."""
    if not encrypted_token:
        return ""
    try:
        return _fernet.decrypt(encrypted_token.encode()).decode()
    except Exception as e:
        logger.error("Failed to decrypt token")
        return ""
