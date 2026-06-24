import os
import sys
import json
import time
import hashlib
import platform
import subprocess
import urllib.request
import urllib.error
from datetime import datetime, timedelta, timezone

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


class TrialState:
    """Local free-trial clock, bound to this machine and started on first run."""

    def __init__(self, started_at: str, machine_fingerprint: str):
        self.started_at = started_at  # ISO 8601 UTC string
        self.machine_fingerprint = machine_fingerprint

    def _started_dt(self) -> datetime:
        return datetime.fromisoformat(self.started_at.replace("Z", "+00:00"))

    def days_remaining(self, duration_days: int, now: datetime | None = None) -> int:
        """Whole days left in the trial window, clamped to >= 0 (display value)."""
        now = now or datetime.now(timezone.utc)
        try:
            end = self._started_dt() + timedelta(days=duration_days)
        except Exception:
            return 0
        seconds_left = (end - now).total_seconds()
        if seconds_left <= 0:
            return 0
        # Round up so a partial final day still reads as "1 day left".
        return int(-(-seconds_left // 86400))

    def is_active(self, duration_days: int, now: datetime | None = None) -> bool:
        """True only if unexpired and bound to this machine."""
        if self.machine_fingerprint != get_machine_fingerprint():
            return False
        now = now or datetime.now(timezone.utc)
        try:
            end = self._started_dt() + timedelta(days=duration_days)
        except Exception:
            return False
        return now < end

    def to_dict(self) -> dict:
        return {
            "started_at": self.started_at,
            "machine_fingerprint": self.machine_fingerprint,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TrialState":
        return cls(
            started_at=data.get("started_at", ""),
            machine_fingerprint=data.get("machine_fingerprint", ""),
        )


def calculate_trial_signature(trial: TrialState) -> str:
    """Tamper-evident signature for the cached trial clock."""
    raw = f"{trial.started_at}::{trial.machine_fingerprint}::{LOCAL_PEPPER}"
    return hashlib.sha256(raw.encode()).hexdigest()


class AccessDecision:
    """Single source of truth for whether the app may be used right now."""

    def __init__(self, allowed: bool, reason: str, trial_days_remaining: int = 0):
        self.allowed = allowed
        # 'disabled' | 'licensed' | 'trial' | 'trial_expired'
        self.reason = reason
        self.trial_days_remaining = trial_days_remaining


def evaluate_access(
    *,
    licensed: bool,
    trial: TrialState | None,
    enforced: bool,
    trial_duration_days: int,
) -> AccessDecision:
    """Pure paywall decision: rollout flag, then license, then trial, else blocked."""
    if not enforced:
        # Paywall not yet rolled out — ship dark, never block a user.
        return AccessDecision(True, "disabled")
    if licensed:
        return AccessDecision(True, "licensed")
    if trial and trial.is_active(trial_duration_days):
        return AccessDecision(True, "trial", trial.days_remaining(trial_duration_days))
    return AccessDecision(False, "trial_expired")

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
