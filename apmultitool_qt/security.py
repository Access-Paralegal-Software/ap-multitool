import os
import json
import base64
import hashlib
from datetime import datetime

from cryptography.fernet import Fernet

from core.logging_config import get_logger
from core.licensing import (
    get_machine_fingerprint,
    verify_license_online,
    Entitlement
)
from core.licensing_store import (
    load_cached_entitlement,
    save_cached_entitlement,
    clear_cached_entitlement
)

LICENSE_FILE = os.path.join(os.path.expanduser("~"), ".access_paralegal_license.json")
CASE_VAULT_FILE = os.path.join(os.path.expanduser("~"), ".access_cases_vault.enc")
logger = get_logger("qt.security")

class VaultSecurityManager:
    def __init__(self):
        self.active_license_key = None
        self.is_pro_activated = False
        self._load_license()

    def _load_license(self):
        """Loads the license key from cache, falling back to stored key for online verify or failing."""
        # 1. Try to load local cached entitlement
        ent = load_cached_entitlement()
        if ent and ent.is_valid():
            self.active_license_key = ent.license_key
            self.is_pro_activated = True
            logger.info("Local cached license entitlement loaded and validated.")
            return

        # 2. If cache invalid/absent, check if stored license key exists and try online check
        if os.path.exists(LICENSE_FILE):
            try:
                with open(LICENSE_FILE, 'r') as f:
                    data = json.load(f)
                key = data.get("key")
                if key:
                    logger.info("Attempting online verification of stored license key...")
                    ent = verify_license_online(key)
                    if ent.is_valid():
                        save_cached_entitlement(ent)
                        self.active_license_key = key
                        self.is_pro_activated = True
                        logger.info("Online verification successful. License activated.")
                        return
                    else:
                        logger.warning(f"Online verification failed: status={ent.status}. Invalidating cache.")
                        clear_cached_entitlement()
            except ConnectionError:
                logger.warning("Offline: Network is down and no valid cached entitlement exists.")
            except Exception as e:
                logger.error(f"License load exception: {e}")

        self.is_pro_activated = False
        self.active_license_key = None

    def get_machine_uuid(self) -> str:
        """Retrieves a unique hardware identifier from the OS for local cryptographic salting."""
        return get_machine_fingerprint()

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
        """Validates and saves a new license key via online verification."""
        if not key or not key.strip():
            return False
            
        cleaned_key = key.strip()
        try:
            ent = verify_license_online(cleaned_key)
            if ent.is_valid():
                save_cached_entitlement(ent)
                self.active_license_key = cleaned_key
                self.is_pro_activated = True
                try:
                    with open(LICENSE_FILE, 'w') as f:
                        json.dump({"key": self.active_license_key, "stamp": str(datetime.now())}, f)
                except Exception:
                    pass
                return True
            else:
                logger.warning(f"Activation failed: License status is {ent.status}")
                return False
        except Exception as e:
            logger.error(f"License activation online call failed: {e}")
            return False

# Singleton instance for easy import across Qt components
vault = VaultSecurityManager()

