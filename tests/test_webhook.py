import hmac
import hashlib
import json
import os
import time
from unittest.mock import patch, MagicMock
import urllib.request
import urllib.error

import pytest
from core.webhook import (
    verify_webhook_signature,
    issue_keygen_license,
    WebhookRequestHandler,
    clear_processed_events_cache
)

@pytest.fixture(autouse=True)
def reset_event_idempotency_cache():
    clear_processed_events_cache()
    yield

def test_verify_webhook_signature_success():
    secret = "test_shared_secret"
    payload = b'{"event": "checkout.paid", "data": {"email": "user@example.com"}}'
    
    # 1. Simple signature matching
    sig = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
    assert verify_webhook_signature(payload, sig, secret) is True
    
    # 2. Keygen-style header matching (t=timestamp,v1=signature)
    now_ts = str(time.time())
    msg = f"t={now_ts},".encode("utf-8") + payload
    sig_keygen = hmac.new(secret.encode("utf-8"), msg, hashlib.sha256).hexdigest()
    sig_header = f"t={now_ts},v1={sig_keygen}"
    assert verify_webhook_signature(payload, sig_header, secret) is True

def test_verify_webhook_signature_failure():
    secret = "test_shared_secret"
    payload = b'{"event": "checkout.paid"}'
    
    # Bad secret
    sig = hmac.new(b"wrong_secret", payload, hashlib.sha256).hexdigest()
    assert verify_webhook_signature(payload, sig, secret) is False
    
    # Missing / empty
    assert verify_webhook_signature(payload, "", secret) is False
    assert verify_webhook_signature(payload, sig, "") is False

def test_verify_webhook_signature_stale_timestamp():
    secret = "test_shared_secret"
    payload = b'{"event": "checkout.paid"}'
    # timestamp from 1 hour ago
    stale_ts = str(time.time() - 3600)
    msg = f"t={stale_ts},".encode("utf-8") + payload
    sig_keygen = hmac.new(secret.encode("utf-8"), msg, hashlib.sha256).hexdigest()
    sig_header = f"t={stale_ts},v1={sig_keygen}"
    
    assert verify_webhook_signature(payload, sig_header, secret) is False

def test_verify_webhook_signature_malformed_timestamp():
    secret = "test_shared_secret"
    payload = b'{"event": "checkout.paid"}'
    sig_header = "t=not-a-float,v1=somesig"
    assert verify_webhook_signature(payload, sig_header, secret) is False

@patch("urllib.request.urlopen")
def test_issue_keygen_license_success(mock_urlopen):
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({
        "data": {
            "attributes": {
                "key": "KEYGEN-NEW-LIC-123"
            }
        }
    }).encode("utf-8")
    mock_urlopen.return_value.__enter__.return_value = mock_response

    res = issue_keygen_license("user@example.com", "acc_123", "token_abc")
    assert res["data"]["attributes"]["key"] == "KEYGEN-NEW-LIC-123"

@patch("urllib.request.urlopen")
@patch("time.sleep", return_value=None)
def test_issue_keygen_license_error_redacts_secret(mock_sleep, mock_urlopen):
    # Simulate API error containing the secret token to assert redaction
    mock_err = urllib.error.HTTPError(
        "https://api.keygen.sh/v1/accounts/acc_123/licenses",
        400,
        "Bad Request",
        {},
        MagicMock(read=lambda: b'{"errors":[{"detail":"Invalid token_abc token policy"}]}')
    )
    mock_urlopen.side_effect = mock_err
    
    with pytest.raises(RuntimeError) as exc_info:
        issue_keygen_license("user@example.com", "acc_123", "token_abc")
    # Secret must be redacted and authorization token not exposed in the error message
    assert "token_abc" not in str(exc_info.value)
    assert "tok..." in str(exc_info.value)

class DummyRequestHandler(WebhookRequestHandler):
    def __init__(self, rfile_bytes, headers_dict):
        self.rfile = MagicMock(read=lambda size=None: rfile_bytes)
        self.headers = headers_dict
        self.wfile = MagicMock()
        self.response_status = None
        self.response_headers = {}

    def send_response(self, code, message=None):
        self.response_status = code

    def send_header(self, keyword, value):
        self.response_headers[keyword] = value

    def end_headers(self):
        pass

@patch("core.webhook.issue_keygen_license")
def test_handler_valid_signature_paid_event(mock_issue):
    payload = b'{"id": "evt_1", "event": "checkout.paid", "data": {"attributes": {"email": "paid@example.com"}}}'
    secret = "my_secret"
    sig = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
    
    headers = {"Content-Length": str(len(payload)), "X-Signature": sig}
    
    with patch("core.webhook.WEBHOOK_SHARED_SECRET", secret):
        handler = DummyRequestHandler(payload, headers)
        handler.do_POST()
        
        assert handler.response_status == 200
        mock_issue.assert_called_once_with("paid@example.com", "", "")

@patch("core.webhook.issue_keygen_license")
def test_handler_replay_protection_duplicate_event(mock_issue):
    payload = b'{"id": "evt_1", "event": "checkout.paid", "data": {"attributes": {"email": "paid@example.com"}}}'
    secret = "my_secret"
    sig = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
    headers = {"Content-Length": str(len(payload)), "X-Signature": sig}
    
    with patch("core.webhook.WEBHOOK_SHARED_SECRET", secret):
        # First request succeeds
        handler1 = DummyRequestHandler(payload, headers)
        handler1.do_POST()
        assert handler1.response_status == 200
        
        # Second duplicate request fails with HTTP 409 Conflict
        handler2 = DummyRequestHandler(payload, headers)
        handler2.do_POST()
        assert handler2.response_status == 409
        
        # DOWNSTREAM LICENSE WAS ONLY ISSUED ONCE
        mock_issue.assert_called_once()

@patch("core.webhook.issue_keygen_license")
def test_handler_malformed_json_fails(mock_issue):
    payload = b'{"event": "checkout.paid", "data": {'  # malformed JSON
    secret = "my_secret"
    sig = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
    headers = {"Content-Length": str(len(payload)), "X-Signature": sig}
    
    with patch("core.webhook.WEBHOOK_SHARED_SECRET", secret):
        handler = DummyRequestHandler(payload, headers)
        handler.do_POST()
        assert handler.response_status == 400
        mock_issue.assert_not_called()

@patch("core.webhook.issue_keygen_license")
def test_handler_malformed_schema_fails(mock_issue):
    # JSON array instead of object
    payload = b'[{"event": "checkout.paid"}]'
    secret = "my_secret"
    sig = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
    headers = {"Content-Length": str(len(payload)), "X-Signature": sig}
    
    with patch("core.webhook.WEBHOOK_SHARED_SECRET", secret):
        handler = DummyRequestHandler(payload, headers)
        handler.do_POST()
        assert handler.response_status == 422
        mock_issue.assert_not_called()

@patch("core.webhook.issue_keygen_license")
def test_handler_unsupported_event_ignored(mock_issue):
    payload = b'{"event": "user.deleted", "data": {"attributes": {"email": "user@example.com"}}}'
    secret = "my_secret"
    sig = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
    headers = {"Content-Length": str(len(payload)), "X-Signature": sig}
    
    with patch("core.webhook.WEBHOOK_SHARED_SECRET", secret):
        handler = DummyRequestHandler(payload, headers)
        handler.do_POST()
        assert handler.response_status == 200
        mock_issue.assert_not_called()

@patch("core.webhook.issue_keygen_license")
def test_handler_activation_failure_logs_alert(mock_issue):
    from pathlib import Path
    mock_issue.side_effect = RuntimeError("Keygen API connection timed out")
    
    payload = b'{"id": "evt_fail_1", "event": "checkout.paid", "data": {"attributes": {"email": "fail@example.com"}}}'
    secret = "my_secret"
    sig = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
    headers = {"Content-Length": str(len(payload)), "X-Signature": sig}
    
    log_file = Path("data/activation_failures.log")
    if log_file.exists():
        log_file.unlink()
        
    with patch("core.webhook.WEBHOOK_SHARED_SECRET", secret):
        handler = DummyRequestHandler(payload, headers)
        handler.do_POST()
        
        assert handler.response_status == 500
        assert log_file.exists()
        
        content = log_file.read_text(encoding="utf-8")
        assert "fail@example.com" in content
        assert "Keygen API connection timed out" in content
        
    if log_file.exists():
        log_file.unlink()
