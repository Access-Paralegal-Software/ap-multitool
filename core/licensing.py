import os
import sys
import json
import time
import hashlib
import platform
import subprocess
import urllib.request
import urllib.error
from datetime import datetime, timezone

# Constants
DEFAULT_VERIFY_URL = "https://api.accessparalegal.com/v1/license/verify"
LOCAL_PEPPER = "ACCESS_PARALEGAL_SALT_2026_PEPPER"

def get_machine_fingerprint() -> str:
    """Generates a unique hardware fingerprint for the current machine."""
    try:
        if platform.system() == "Windows":
            cmd = 'wmic csproduct get uuid'
            uuid = subprocess.check_output(cmd, shell=True).decode().split('\n')[1].strip()
            if uuid and len(uuid) > 5 and uuid != "00000000-0000-0000-0000-000000000000":
                return uuid
        
        # Fallback combination of node, platform, and python version to generate a stable hash
        seed = f"{platform.node()}::{platform.platform()}::{platform.machine()}"
        return hashlib.sha256(seed.encode()).hexdigest()
    except Exception:
        return "LOCAL_FALLBACK_FINGERPRINT"

class Entitlement:
    def __init__(self, license_key: str, status: str, expires_at: str, machine_fingerprint: str):
        self.license_key = license_key
        self.status = status  # 'activated', 'expired', 'suspended', 'invalid'
        self.expires_at = expires_at  # ISO 8601 UTC string
        self.machine_fingerprint = machine_fingerprint

    def is_valid(self) -> bool:
        """Checks if the entitlement is currently active, unexpired, and matching this machine."""
        if self.status != "activated":
            return False
        
        if self.machine_fingerprint != get_machine_fingerprint():
            return False
            
        try:
            # Parse ISO timestamp and check if expired
            expiry_dt = datetime.fromisoformat(self.expires_at.replace("Z", "+00:00"))
            if datetime.now(timezone.utc) > expiry_dt:
                return False
        except Exception:
            return False
            
        return True

    def to_dict(self) -> dict:
        return {
            "license_key": self.license_key,
            "status": self.status,
            "expires_at": self.expires_at,
            "machine_fingerprint": self.machine_fingerprint
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Entitlement":
        return cls(
            license_key=data.get("license_key", ""),
            status=data.get("status", "invalid"),
            expires_at=data.get("expires_at", ""),
            machine_fingerprint=data.get("machine_fingerprint", "")
        )

def calculate_signature(entitlement: Entitlement) -> str:
    """Calculates a secure signature to detect tampering of the cached license state."""
    raw = f"{entitlement.license_key}::{entitlement.status}::{entitlement.expires_at}::{entitlement.machine_fingerprint}::{LOCAL_PEPPER}"
    return hashlib.sha256(raw.encode()).hexdigest()

def verify_license_online(license_key: str, verify_url: str = DEFAULT_VERIFY_URL, timeout_seconds: int = 5) -> Entitlement:
    """
    Contacts the online licensing server to verify a license key.
    Returns a normalized Entitlement object.
    """
    fingerprint = get_machine_fingerprint()
    payload = {
        "license_key": license_key,
        "machine_fingerprint": fingerprint
    }
    
    req_data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        verify_url,
        data=req_data,
        headers={"Content-Type": "application/json", "User-Agent": "APMultitool/1.0"},
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=timeout_seconds) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            return Entitlement(
                license_key=license_key,
                status=res_data.get("status", "invalid"),
                expires_at=res_data.get("expires_at", ""),
                machine_fingerprint=fingerprint
            )
    except urllib.error.HTTPError as e:
        # If server rejects, parse error response or default to invalid
        try:
            res_data = json.loads(e.read().decode("utf-8"))
            return Entitlement(
                license_key=license_key,
                status=res_data.get("status", "invalid"),
                expires_at=res_data.get("expires_at", ""),
                machine_fingerprint=fingerprint
            )
        except Exception:
            return Entitlement(license_key, "invalid", "", fingerprint)
    except Exception as e:
        # Network timeout or DNS failure - raise so caller knows to fall back to offline cache
        raise ConnectionError(f"Licensing server unreachable: {e}")
