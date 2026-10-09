import json
import hashlib
from datetime import datetime, timezone, timedelta
from pathlib import Path

LOCAL_PEPPER = "APM_OFFLINE_SECRET_SALT_2026"
CACHE_PATH = Path.home() / ".access_paralegal_entitlement.json"

def create_entitlement(key: str) -> dict:
    now_iso = datetime.now(timezone.utc).isoformat()
    raw_payload = f"{key}::{now_iso}::{LOCAL_PEPPER}"
    signature = hashlib.sha256(raw_payload.encode()).hexdigest()
    return {
        "key": key,
        "cached_at": now_iso,
        "signature": signature
    }

def verify_entitlement() -> bool:
    if not CACHE_PATH.exists():
        return False
    data = json.loads(CACHE_PATH.read_text())
    key = data["key"]
    cached_at = data["cached_at"]
    sig = data["signature"]
    
    expected = hashlib.sha256(f"{key}::{cached_at}::{LOCAL_PEPPER}".encode()).hexdigest()
    if sig != expected:
        return False
        
    cache_time = datetime.fromisoformat(cached_at)
    if datetime.now(timezone.utc) > cache_time + timedelta(days=7):
        return False
        
    return True

# Issue test commercial founder pass token
test_key = "APM-2026-BATE-FOUNDER-PASS"
CACHE_PATH.write_text(json.dumps(create_entitlement(test_key), indent=2))
assert verify_entitlement() == True
print("[+] Entitlement Gate Validated: 7-day offline token verified.")
