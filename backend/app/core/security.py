import os
import base64
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import logging

logger = logging.getLogger(__name__)

# --- Configuration --- 
# Fetch the secret key from environment variable
# Ensure this key is strong and kept secret!
# Generate one using: Fernet.generate_key()
SECRET_KEY_ENV_VAR = "ENCRYPTION_KEY"
ENCRYPTION_KEY = os.getenv(SECRET_KEY_ENV_VAR)

if not ENCRYPTION_KEY:
    logger.error(f"CRITICAL: Environment variable '{SECRET_KEY_ENV_VAR}' not set. Password encryption/decryption will fail.")
    # In a real app, you might raise an exception here to prevent startup
    # For now, we'll let it proceed but log the error.
    # raise ValueError(f"Environment variable '{SECRET_KEY_ENV_VAR}' is required.")
    derived_key = None # Set key to None if env var is missing
else:
    try:
        # Ensure the key is URL-safe base64 encoded
        key_bytes = base64.urlsafe_b64decode(ENCRYPTION_KEY)
        if len(key_bytes) != 32:
             raise ValueError("ENCRYPTION_KEY must be a 32-byte URL-safe base64 encoded string.")
        # Use the key directly for AESGCM
        derived_key = key_bytes
        logger.info("Successfully loaded encryption key.")
    except (ValueError, TypeError) as e:
        logger.error(f"CRITICAL: Invalid ENCRYPTION_KEY format: {e}. Must be 32-byte URL-safe base64 encoded.")
        derived_key = None

# --- Encryption/Decryption Functions --- 

def encrypt(plaintext: str) -> str | None:
    """Encrypts plaintext using AES-GCM and returns base64 encoded ciphertext + nonce."""
    logger.debug(f"Attempting encryption. Key available: {derived_key is not None}")
    if derived_key is None:
        logger.error("Encryption cannot proceed: Encryption key is not available.")
        return None
    if not plaintext:
         return None # Handle empty plaintext if necessary
         
    try:
        aesgcm = AESGCM(derived_key)
        nonce = os.urandom(12)  # GCM standard nonce size
        plaintext_bytes = plaintext.encode('utf-8')
        ciphertext_bytes = aesgcm.encrypt(nonce, plaintext_bytes, None) # No associated data
        
        # Combine nonce and ciphertext, then base64 encode for storage
        encrypted_data = base64.urlsafe_b64encode(nonce + ciphertext_bytes).decode('utf-8')
        return encrypted_data
    except Exception as e:
        logger.error(f"Encryption failed: {e}", exc_info=True)
        return None

def decrypt(encrypted_data: str) -> str | None:
    """Decrypts base64 encoded ciphertext + nonce using AES-GCM."""
    if derived_key is None:
        logger.error("Decryption cannot proceed: Encryption key is not available.")
        return None
    if not encrypted_data:
        return None
        
    try:
        aesgcm = AESGCM(derived_key)
        decoded_data = base64.urlsafe_b64decode(encrypted_data.encode('utf-8'))
        
        # Split nonce and ciphertext
        nonce = decoded_data[:12]
        ciphertext_bytes = decoded_data[12:]
        
        plaintext_bytes = aesgcm.decrypt(nonce, ciphertext_bytes, None) # No associated data
        return plaintext_bytes.decode('utf-8')
    except InvalidToken:
        logger.error("Decryption failed: Invalid token or incorrect key.")
        return None
    except Exception as e:
        logger.error(f"Decryption failed: {e}", exc_info=True)
        return None

# --- Hashing Functions (Optional - Keep if needed elsewhere, e.g., for app users) --- 
# from passlib.context import CryptContext
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# 
# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     """Verifies a plain password against a hashed password."""
#     return pwd_context.verify(plain_password, hashed_password)
# 
# def get_password_hash(password: str) -> str:
#     """Hashes a plain password."""
#     return pwd_context.hash(password) 