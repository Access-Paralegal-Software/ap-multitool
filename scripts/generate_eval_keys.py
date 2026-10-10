import hmac
import hashlib
import json
import base64
from datetime import datetime, timezone, timedelta

SIGNING_SECRET = b"AP_MULTITOOL_OFFLINE_SECRET_2026_PROD"

def issue_key(seat_id: str, days_valid: int = 14) -> str:
    issued_at = datetime.now(timezone.utc)
    expires_at = issued_at + timedelta(days=days_valid)
    payload = {
        "v": 1,
        "type": "trial",
        "seat": seat_id,
        "iat": issued_at.strftime("%Y-%m-%d"),
        "exp": expires_at.strftime("%Y-%m-%d"),
    }
    raw = json.dumps(payload, separators=(',', ':'), sort_keys=True).encode("utf-8")
    sig = hmac.new(SIGNING_SECRET, raw, hashlib.sha256).digest()
    token = raw + b"." + sig[:8]
    b32 = base64.b32encode(token).decode("ascii").rstrip("=")
    return "-".join([b32[i:i+5] for i in range(0, len(b32), 5)])

if __name__ == "__main__":
    print("=== AP-Multitool v1.0.0 Evaluation Keys ===")
    for i in range(1, 6):
        seat = f"ALPHA-{i:02d}"
        key = issue_key(seat, 14)
        print(f"{seat} (Expires: {(datetime.now(timezone.utc) + timedelta(days=14)).strftime('%Y-%m-%d')}): {key}")
