import hmac
import hashlib
import json
import os
import sys
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler, HTTPServer
from core.logging_config import get_logger

logger = get_logger("core.webhook")

# Webhook shared secret and Keygen variables from environment
WEBHOOK_SHARED_SECRET = os.getenv("APM_WEBHOOK_SHARED_SECRET", "")
KEYGEN_ACCOUNT_ID = os.getenv("APM_KEYGEN_ACCOUNT_ID", "")
KEYGEN_PRODUCT_TOKEN = os.getenv("APM_KEYGEN_PRODUCT_TOKEN", "")
KEYGEN_PRODUCT_ID = os.getenv("APM_KEYGEN_PRODUCT_ID", "ap-multitool-pro")  # default product ID

def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verifies that the webhook payload matches the signature using the shared secret."""
    if not secret:
        logger.error("Webhook secret is not configured.")
        return False
    if not signature:
        logger.error("Signature header is missing.")
        return False
        
    # Standard signature format: e.g. t=123,v1=sha256_hash or just raw sha256 hex
    # We support both raw hex signature or v1=... signature header formats
    clean_sig = signature
    if "v1=" in signature:
        parts = signature.split(",")
        for part in parts:
            if part.strip().startswith("v1="):
                clean_sig = part.strip()[3:]
                break

    try:
        expected = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, clean_sig)
    except Exception as e:
        logger.error(f"Signature calculation error: {e}")
        return False

def issue_keygen_license(email: str, account_id: str, product_token: str, product_id: str = KEYGEN_PRODUCT_ID) -> dict:
    """
    Contacts the Keygen API to generate a new license for the customer email.
    API Endpoint: POST /v1/accounts/{account_id}/licenses
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
    req = urllib.request.Request(
        url,
        data=req_data,
        headers={
            "Content-Type": "application/vnd.api+json",
            "Accept": "application/vnd.api+json",
            "Authorization": f"Bearer {product_token}"
        },
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            license_key = res_data.get("data", {}).get("attributes", {}).get("key")
            logger.info(f"License issued successfully for email: {email} (Key starts with: {license_key[:5]}...)")
            return res_data
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8")
        logger.error(f"Keygen license creation failed with status {e.code}: {err_msg}")
        raise RuntimeError(f"Keygen API error: {err_msg}")
    except Exception as e:
        logger.error(f"Connection to Keygen API failed: {e}")
        raise ConnectionError(f"Keygen API unreachable: {e}")

class WebhookRequestHandler(BaseHTTPRequestHandler):
    """Lite HTTP Request Handler for receiving checkout webhooks."""
    
    def log_message(self, format, *args):
        # Prevent default logging to stdout to keep tests/terminal output clean
        logger.info(format % args)

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

        event_type = event.get("event") or event.get("meta", {}).get("event")
        
        # Process checkout.paid / payment.success / license.created events
        if event_type not in ("checkout.paid", "payment.success", "license.created"):
            logger.info(f"Ignoring unrelated event: {event_type}")
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ignored"}).encode('utf-8'))
            return

        # Extract email payload
        email = (
            event.get("data", {}).get("attributes", {}).get("email")
            or event.get("data", {}).get("attributes", {}).get("user", {}).get("email")
            or event.get("data", {}).get("user_email")
        )
        
        if not email:
            logger.error("Event payload is missing email address.")
            self.send_response(422)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Unprocessable Entity: Missing email"}).encode('utf-8'))
            return

        logger.info(f"Processing paid purchase event for: {email}")
        
        try:
            issue_keygen_license(email, KEYGEN_ACCOUNT_ID, KEYGEN_PRODUCT_TOKEN)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "issued"}).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": f"Internal Server Error: {e}"}).encode('utf-8'))

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
