import secrets
import os
from dotenv import set_key, load_dotenv

def verify_master_key(input_key):
    """Verifies the input key against the stored MASTER_RECOVERY_KEY."""
    # Force reload environment to ensure we have the latest file state
    load_dotenv(override=True)
    stored_key = os.getenv("MASTER_RECOVERY_KEY")
    
    if not stored_key:
        return False
        
    # Constant time comparison
    return secrets.compare_digest(input_key.strip(), stored_key.strip())

def update_admin_password(new_password):
    """Updates the admin password securely."""
    set_key('.env', 'ADMIN_PASSWORD', new_password)
    # Reload env for the running process
    load_dotenv(override=True)
    return True
