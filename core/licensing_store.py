import os
import json
from datetime import datetime, timezone
from pathlib import Path
from core.licensing import (
    Entitlement,
    TrialState,
    calculate_signature,
    calculate_trial_signature,
    get_machine_fingerprint,
)
from core.logging_config import get_logger

logger = get_logger("core.licensing_store")

CACHE_FILE_PATH = Path(os.path.expanduser("~")) / ".access_paralegal_entitlement.json"
TRIAL_FILE_PATH = Path(os.path.expanduser("~")) / ".access_paralegal_trial.json"

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


def _save_trial(trial: TrialState):
    payload = {
        "trial": trial.to_dict(),
        "signature": calculate_trial_signature(trial),
    }
    with open(TRIAL_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def load_or_start_trial() -> TrialState:
    """
    Returns the local trial clock, starting it on first run.

    A missing, tampered, or foreign-machine trial file is treated as a fresh
    install: a new clock is issued and persisted. This fails open (the user keeps
    a usable trial) rather than locking out a legitimate user on a corrupt file.
    """
    trial = _load_valid_trial()
    if trial is not None:
        return trial

    trial = TrialState(
        started_at=datetime.now(timezone.utc).isoformat(),
        machine_fingerprint=get_machine_fingerprint(),
    )
    try:
        _save_trial(trial)
    except Exception as e:
        logger.error(f"Failed to persist new trial clock: {e}")
    return trial


def _load_valid_trial() -> TrialState | None:
    if not TRIAL_FILE_PATH.exists():
        return None
    try:
        with open(TRIAL_FILE_PATH, "r", encoding="utf-8") as f:
            payload = json.load(f)

        trial_data = payload.get("trial")
        signature = payload.get("signature")
        if not trial_data or not signature:
            return None

        trial = TrialState.from_dict(trial_data)
        if signature != calculate_trial_signature(trial):
            logger.error("Trial clock signature mismatch! Tampering detected.")
            return None
        if trial.machine_fingerprint != get_machine_fingerprint():
            logger.error("Trial clock machine fingerprint mismatch! Attempted copy.")
            return None
        return trial
    except Exception as e:
        logger.error(f"Failed to load trial clock: {e}")
        return None


def clear_trial():
    """Removes the local trial clock file."""
    try:
        if TRIAL_FILE_PATH.exists():
            TRIAL_FILE_PATH.unlink()
    except Exception as e:
        logger.error(f"Failed to delete trial clock: {e}")
