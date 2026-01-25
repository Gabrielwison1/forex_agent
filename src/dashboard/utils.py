import secrets
import os
import hashlib
from dotenv import set_key, load_dotenv

def verify_master_key(input_key):
    """Verifies the input key against the stored MASTER_KEY_HASH."""
    load_dotenv(override=True)
    stored_hash = os.getenv("MASTER_KEY_HASH")
    
    if not stored_hash:
        return False
        
    # Hash the input to compare
    input_hash = hashlib.sha256(input_key.strip().encode()).hexdigest()
    
    # Secure comparison
    return secrets.compare_digest(input_hash, stored_hash)

def update_master_key(new_key):
    """Updates the master key by storing its hash."""
    new_hash = hashlib.sha256(new_key.strip().encode()).hexdigest()
    set_key('.env', 'MASTER_KEY_HASH', new_hash)
    load_dotenv(override=True)
    return True

def update_admin_password(new_password):
    """Updates the admin password securely by storing its hash."""
    new_hash = hashlib.sha256(new_password.strip().encode()).hexdigest()
    set_key('.env', 'ADMIN_PASSWORD_HASH', new_hash)
    load_dotenv(override=True)
    return True
