import os
import json
from pathlib import Path
from core.licensing import Entitlement, calculate_signature, get_machine_fingerprint
from core.logging_config import get_logger

logger = get_logger("core.licensing_store")

CACHE_FILE_PATH = Path(os.path.expanduser("~")) / ".access_paralegal_entitlement.json"

def save_cached_entitlement(entitlement: Entitlement):
    """Saves the entitlement to the local cache file, along with a secure signature."""
    try:
        signature = calculate_signature(entitlement)
        payload = {
            "entitlement": entitlement.to_dict(),
            "signature": signature
        }
        with open(CACHE_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save cached entitlement: {e}")

def load_cached_entitlement() -> Entitlement | None:
    """
    Loads and validates the cached entitlement state.
    Returns None if the cache is missing, tampered, or bound to a different machine.
    """
    if not CACHE_FILE_PATH.exists():
        return None
        
    try:
        with open(CACHE_FILE_PATH, "r", encoding="utf-8") as f:
            payload = json.load(f)
            
        entitlement_data = payload.get("entitlement")
        signature = payload.get("signature")
        
        if not entitlement_data or not signature:
            logger.warning("Cached entitlement is incomplete.")
            return None
            
        entitlement = Entitlement.from_dict(entitlement_data)
        
        # Verify signature to detect tampering
        expected_signature = calculate_signature(entitlement)
        if signature != expected_signature:
            logger.error("Cached entitlement signature mismatch! Tampering detected.")
            return None
            
        # Verify machine fingerprint
        if entitlement.machine_fingerprint != get_machine_fingerprint():
            logger.error("Cached entitlement machine fingerprint mismatch! Attempted registry copy.")
            return None
            
        return entitlement
    except Exception as e:
        logger.error(f"Failed to load cached entitlement: {e}")
        return None

def clear_cached_entitlement():
    """Removes the local cached entitlement file."""
    try:
        if CACHE_FILE_PATH.exists():
            CACHE_FILE_PATH.unlink()
    except Exception as e:
        logger.error(f"Failed to delete cached entitlement: {e}")
