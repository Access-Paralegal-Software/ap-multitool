import hmac
import hashlib
import json
import os
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from core.logging_config import get_logger

logger = get_logger("core.webhook")

# Webhook shared secret and Keygen variables from environment
WEBHOOK_SHARED_SECRET = os.getenv("APM_WEBHOOK_SHARED_SECRET", "")
KEYGEN_ACCOUNT_ID = os.getenv("APM_KEYGEN_ACCOUNT_ID", "")
KEYGEN_PRODUCT_TOKEN = os.getenv("APM_KEYGEN_PRODUCT_TOKEN", "")
KEYGEN_PRODUCT_ID = os.getenv("APM_KEYGEN_PRODUCT_ID", "ap-multitool-pro")  # default product ID

# Hardening parameters
MAX_AGE_SECONDS = int(os.getenv("APM_WEBHOOK_MAX_AGE_SECONDS", "300"))

# Simple in-memory sliding cache for event idempotency (replays)
PROCESSED_EVENTS = {}
CLEANUP_INTERVAL = 3600  # prune old events hourly
last_cleanup_time = time.time()

def clear_processed_events_cache():
    """Testing helper to reset processed events list."""
    global PROCESSED_EVENTS
    PROCESSED_EVENTS.clear()

def _cleanup_expired_events():
    global last_cleanup_time, PROCESSED_EVENTS
    now = time.time()
    if now - last_cleanup_time > CLEANUP_INTERVAL:
        expired_cutoff = now - MAX_AGE_SECONDS
        PROCESSED_EVENTS = {ev: ts for ev, ts in PROCESSED_EVENTS.items() if ts > expired_cutoff}
        last_cleanup_time = now

def verify_webhook_signature(payload: bytes, signature_header: str, secret: str) -> bool:
    """
    Verifies that the webhook payload matches the signature using the shared secret.
    Requires constant-time comparison, header canonicalization, and strict parsing.
    Supports either:
      - Raw hex signature
      - Keygen format: t=timestamp,v1=signature
    """
    if not secret:
        logger.error("[SEC] Webhook secret is not configured.")
        return False
    if not signature_header:
        logger.error("[SEC] Signature header is missing.")
        return False

    clean_sig = ""
    timestamp_str = ""

    # Parse Keygen format: t=123,v1=sha256_hash
    if "v1=" in signature_header or "t=" in signature_header:
        parts = signature_header.split(",")
        for part in parts:
            part = part.strip()
            if part.startswith("t="):
                timestamp_str = part[2:]
            elif part.startswith("v1="):
                clean_sig = part[3:]
    else:
        # Fallback to raw hex
        clean_sig = signature_header.strip()

    if not clean_sig:
        logger.error("[SEC] Malformed signature: v1 token not found.")
        return False

    # If timestamp was provided, enforce replay timestamp validation bounds
    if timestamp_str:
        try:
            ts = float(timestamp_str)
            now = time.time()
            if abs(now - ts) > MAX_AGE_SECONDS:
                logger.error(f"[SEC] Rejecting stale timestamp: t={ts} (current={now}, max_age={MAX_AGE_SECONDS}s)")
                return False
        except ValueError:
            logger.error(f"[SEC] Rejecting malformed signature timestamp: {timestamp_str}")
            return False

    try:
        # Keygen signature format hashes the payload combined with the timestamp: "t:payload"
        if timestamp_str:
            msg = f"t={timestamp_str},".encode("utf-8") + payload
        else:
            msg = payload

        expected = hmac.new(secret.encode("utf-8"), msg, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected.encode("utf-8"), clean_sig.encode("utf-8"))
    except Exception as e:
        logger.error(f"[SEC] Signature validation error: {e}")
        return False

def issue_keygen_license(email: str, account_id: str, product_token: str, product_id: str = KEYGEN_PRODUCT_ID) -> dict:
    """
    Contacts the Keygen API to generate a new license for the customer email.
    Includes explicit timeouts, retry backoffs, and strict secret redaction.
    """
    if not account_id or not product_token:
        raise ValueError("Keygen account ID or product token is missing.")

    url = f"https://api.keygen.sh/v1/accounts/{account_id}/licenses"
    payload = {
        "data": {
            "type": "licenses",
            "attributes": {
                "metadata": {
                    "customer_email": email
                }
            },
            "relationships": {
                "policy": {
                    "data": {
                        "type": "policies",
                        "id": product_id
                    }
                }
            }
        }
    }
    
    req_data = json.dumps(payload).encode("utf-8")
    
    # Redact sensitive bearer token in header definitions for any logs or outputs
    safe_product_token = product_token[:3] + "..." if len(product_token) >= 3 else "..."
    headers = {
        "Content-Type": "application/vnd.api+json",
        "Accept": "application/vnd.api+json",
        "Authorization": f"Bearer {product_token}"
    }

    # Retry parameters
    max_retries = 3
    retry_delay = 1.0

    for attempt in range(max_retries):
        req = urllib.request.Request(url, data=req_data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                license_key = res_data.get("data", {}).get("attributes", {}).get("key")
                # Structure logs safely without leaking the full key or recipient email details directly in cleartext
                safe_email = email.split("@")[0][:3] + "...@" + email.split("@")[1] if "@" in email else "..."
                safe_lic = license_key[:5] + "..." if license_key else "..."
                logger.info(f"License issued successfully for: {safe_email} (Key: {safe_lic})")
                return res_data
        except urllib.error.HTTPError as e:
            err_msg = e.read().decode("utf-8")
            # Scrub authorization header/secret leaks from logs and error strings
            safe_err = err_msg.replace(product_token, safe_product_token)
            logger.error(f"Keygen API HTTP error status={e.code} during attempt {attempt+1}: {safe_err}")
            if attempt == max_retries - 1:
                raise RuntimeError(f"Keygen API error: {safe_err}")
        except Exception as e:
            safe_e = str(e).replace(product_token, safe_product_token)
            logger.warning(f"Connection attempt {attempt+1} failed: {safe_e}")
            if attempt == max_retries - 1:
                raise ConnectionError(f"Keygen API unreachable after {max_retries} attempts: {safe_e}")
            time.sleep(retry_delay)
            retry_delay *= 2

def log_activation_failure(email: str, error: str):
    """Logs license activation failures to a file that maintainers can monitor."""
    try:
        log_path = Path("data/activation_failures.log")
        log_path.parent.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Scrub secrets
        safe_err = error
        if KEYGEN_PRODUCT_TOKEN:
            safe_err = safe_err.replace(KEYGEN_PRODUCT_TOKEN, "[REDACTED]")
        if WEBHOOK_SHARED_SECRET:
            safe_err = safe_err.replace(WEBHOOK_SHARED_SECRET, "[REDACTED]")
            
        log_entry = {
            "timestamp": timestamp,
            "email": email,
            "error": safe_err
        }
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception as exc:
        logger.error(f"Failed to write to activation failure alert log: {exc}")

class WebhookRequestHandler(BaseHTTPRequestHandler):
    """Lite HTTP Request Handler for receiving checkout webhooks."""
    
    def log_message(self, format, *args):
        # Redact raw inputs before writing to log sinks
        clean_args = []
        for a in args:
            arg_str = str(a)
            if WEBHOOK_SHARED_SECRET and WEBHOOK_SHARED_SECRET in arg_str:
                arg_str = arg_str.replace(WEBHOOK_SHARED_SECRET, "[REDACTED]")
            if KEYGEN_PRODUCT_TOKEN and KEYGEN_PRODUCT_TOKEN in arg_str:
                arg_str = arg_str.replace(KEYGEN_PRODUCT_TOKEN, "[REDACTED]")
            clean_args.append(arg_str)
        logger.info(format % tuple(clean_args))

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)

        signature = self.headers.get('X-Signature', '') or self.headers.get('Keygen-Signature', '')
        
        # Verify signature
        if not verify_webhook_signature(post_data, signature, WEBHOOK_SHARED_SECRET):
            self.send_response(401)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Unauthorized: Signature mismatch"}).encode('utf-8'))
            return

        try:
            event = json.loads(post_data.decode('utf-8'))
        except Exception:
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Bad Request: Invalid JSON"}).encode('utf-8'))
            return

        # Schema & Identity Verification
        if not isinstance(event, dict):
            self.send_response(422)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Unprocessable Entity: Expected JSON object"}).encode('utf-8'))
            return

        # Check for event identifier to guard against replay attacks
        event_id = event.get("id") or event.get("meta", {}).get("id")
        if event_id:
            _cleanup_expired_events()
            if event_id in PROCESSED_EVENTS:
                logger.error(f"[SEC] Duplicate webhook event detected: id={event_id}")
                self.send_response(409)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Conflict: Duplicate event detected"}).encode('utf-8'))
                return
            PROCESSED_EVENTS[event_id] = time.time()

        event_type = event.get("event") or event.get("meta", {}).get("event")
        
        # Process checkout.paid / payment.success / license.created events strictly
        if event_type not in ("checkout.paid", "payment.success", "license.created"):
            logger.info(f"Ignoring unrelated event: {event_type}")
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ignored"}).encode('utf-8'))
            return

        # Extract email payload securely
        data_block = event.get("data")
        if not isinstance(data_block, dict):
            self.send_response(422)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Unprocessable Entity: Missing data attribute"}).encode('utf-8'))
            return

        attrs = data_block.get("attributes")
        email = None
        if isinstance(attrs, dict):
            email = attrs.get("email") or (attrs.get("user", {}) if isinstance(attrs.get("user"), dict) else {}).get("email")
        if not email:
            email = data_block.get("user_email")

        if not email or not isinstance(email, str) or "@" not in email:
            logger.error("Event payload is missing valid email address.")
            self.send_response(422)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Unprocessable Entity: Missing email"}).encode('utf-8'))
            return

        logger.info("Processing paid purchase event.")
        
        try:
            issue_keygen_license(email, KEYGEN_ACCOUNT_ID, KEYGEN_PRODUCT_TOKEN)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "issued"}).encode('utf-8'))
        except Exception as e:
            # Log activation failure for alerting
            log_activation_failure(email, str(e))
            
            # Scrub authorization header/secret leaks from response payloads
            safe_e = str(e).replace(KEYGEN_PRODUCT_TOKEN, "[REDACTED]")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": f"Internal Server Error: {safe_e}"}).encode('utf-8'))

def run_webhook_server(port: int = 8080):
    server = HTTPServer(('0.0.0.0', port), WebhookRequestHandler)
    logger.info(f"Starting Webhook Server on port {port}...")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        logger.info("Server stopped.")
