"""Encryption utilities for sensitive connector credentials.

Uses Fernet (AES-128-CBC) for symmetric encryption.
The ENCRYPTION_KEY must be a 32-byte base64-encoded string.
"""
from cryptography.fernet import Fernet
import os
import base64
import logging

logger = logging.getLogger(__name__)


def _get_encryption_key() -> str:
    """Get encryption key from environment.
    
    Fails hard if not set to prevent data loss scenarios where
    a new key is generated and old data becomes unrecoverable.
    
    Returns:
        str: The encryption key
        
    Raises:
        RuntimeError: If ENCRYPTION_KEY environment variable is not set
        ValueError: If ENCRYPTION_KEY is not a valid Fernet key
    """
    key = os.getenv("ENCRYPTION_KEY")
    
    if not key:
        raise RuntimeError(
            "CRITICAL: ENCRYPTION_KEY environment variable is not set. "
            "This would cause irreversible data loss. "
            "Generate a key with: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\" "
        )
    
    # Validate key format
    try:
        # Fernet keys are 32-byte base64-encoded strings (44 chars with padding)
        decoded = base64.urlsafe_b64decode(key.encode())
        if len(decoded) != 32:
            raise ValueError(
                f"ENCRYPTION_KEY must decode to 32 bytes, got {len(decoded)}. "
                "Generate a valid key with: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
            )
    except Exception as e:
        raise ValueError(
            f"ENCRYPTION_KEY is not a valid Fernet key: {e}. "
            "Generate a valid key with: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
        ) from e
    
    return key


# Initialize Fernet with validated key
ENCRYPTION_KEY = _get_encryption_key()
_fernet = Fernet(ENCRYPTION_KEY)


def encrypt_config(config_json: str) -> str:
    """Encrypt a JSON config string.
    
    Args:
        config_json: The JSON string to encrypt
        
    Returns:
        str: The encrypted string (base64-encoded)
        
    Raises:
        Exception: If encryption fails
    """
    try:
        encrypted = _fernet.encrypt(config_json.encode()).decode()
        logger.debug("Successfully encrypted config (%d chars)", len(config_json))
        return encrypted
    except Exception as e:
        logger.error("Failed to encrypt config: %s", e)
        raise


def decrypt_config(encrypted: str) -> str:
    """Decrypt an encrypted config string.
    
    Args:
        encrypted: The encrypted string to decrypt
        
    Returns:
        str: The decrypted JSON string
        
    Raises:
        Exception: If decryption fails (e.g., wrong key, corrupted data)
    """
    try:
        decrypted = _fernet.decrypt(encrypted.encode()).decode()
        logger.debug("Successfully decrypted config (%d chars)", len(decrypted))
        return decrypted
    except Exception as e:
        logger.error("Failed to decrypt config: %s", e)
        raise
