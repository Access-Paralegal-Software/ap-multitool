import os
import json
import base64
import hashlib
import platform
import subprocess
from datetime import datetime

from cryptography.fernet import Fernet

from core.logging_config import get_logger

LICENSE_FILE = os.path.join(os.path.expanduser("~"), ".access_paralegal_license.json")
CASE_VAULT_FILE = os.path.join(os.path.expanduser("~"), ".access_cases_vault.enc")
logger = get_logger("qt.security")

class VaultSecurityManager:
    def __init__(self):
        self.active_license_key = None
        self.is_pro_activated = False
        self._load_license()

    def _load_license(self):
        if os.path.exists(LICENSE_FILE):
            try:
                with open(LICENSE_FILE, 'r') as f:
                    data = json.load(f)
                    if "key" in data:
                        # Add any remote validation or format checks here if necessary
                        self.active_license_key = data["key"]
                        self.is_pro_activated = True
            except Exception:
                pass

    def get_machine_uuid(self) -> str:
        """Retrieves a unique hardware identifier from the OS for local cryptographic salting."""
        try:
            cmd = 'wmic csproduct get uuid'
            # Extracts the unique motherboard/BIOS UUID on Windows
            uuid = subprocess.check_output(cmd, shell=True).decode().split('\n')[1].strip()
            return uuid
        except Exception:
            # Fallback to local hostname if WMIC is restricted
            return platform.node() or "OFFLINE_SAFE_FALLBACK"

    def get_crypto_key(self) -> bytes:
        """Generates a deterministic 32-byte Fernet key bound to device hardware and license signature."""
        license_seed = self.active_license_key or "ACCESS_FREE_TIER"
        machine_seed = self.get_machine_uuid()
        
        # Combine license and hardware identity for a unique 'Machine Key'
        final_seed = f"{license_seed}::{machine_seed}::ACCESS_PARALEGAL_SALT_2026"
        
        key_bytes = hashlib.sha256(final_seed.encode()).digest()
        return base64.urlsafe_b64encode(key_bytes)

    def save_case_vault(self, data: dict) -> bool:
        """Encrypts active state metrics using hardware keys and locks to disk."""
        try:
            raw_json = json.dumps(data)
            cipher = Fernet(self.get_crypto_key())
            encrypted = cipher.encrypt(raw_json.encode())
            
            with open(CASE_VAULT_FILE, 'wb') as f:
                f.write(encrypted)
            return True
        except Exception:
            logger.exception("case vault save failed")
            return False

    def load_case_vault(self) -> dict:
        """Silently decodes secure files on startup, injecting data into visual buffers."""
        if not os.path.exists(CASE_VAULT_FILE):
            return {}
        try:
            with open(CASE_VAULT_FILE, 'rb') as f:
                encrypted = f.read()
            
            cipher = Fernet(self.get_crypto_key())
            decrypted = cipher.decrypt(encrypted).decode()
            return json.loads(decrypted)
        except Exception:
            logger.exception("case vault load failed")
            return {}

    def activate_license(self, key: str) -> bool:
        """Validates and saves a new license key."""
        # Standard placeholder for validation logic; returning true if key length > 5
        if not key or len(key.strip()) < 5:
            return False
            
        self.is_pro_activated = True
        self.active_license_key = key.strip()
        try:
            with open(LICENSE_FILE, 'w') as f:
                json.dump({"key": self.active_license_key, "stamp": str(datetime.now())}, f)
        except Exception:
            pass
        return True

# Singleton instance for easy import across Qt components
vault = VaultSecurityManager()
