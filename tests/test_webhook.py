import hmac
import hashlib
import json
import os
from unittest.mock import patch, MagicMock
import urllib.request
import urllib.error

import pytest
from core.webhook import verify_webhook_signature, issue_keygen_license, WebhookRequestHandler

def test_verify_webhook_signature_success():
    secret = "test_shared_secret"
    payload = b'{"event": "checkout.paid", "data": {"email": "user@example.com"}}'
    
    # 1. Simple signature matching
    sig = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
    assert verify_webhook_signature(payload, sig, secret) is True
    
    # 2. Keygen-style header matching (v1=signature)
    sig_header = f"t=123,v1={sig}"
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
def test_issue_keygen_license_error(mock_urlopen):
    # Simulate API error
    mock_err = urllib.error.HTTPError(
        "https://api.keygen.sh/v1/accounts/acc_123/licenses",
        400,
        "Bad Request",
        {},
        MagicMock(read=lambda: b'{"errors":[{"detail":"Invalid policy"}]}')
    )
    mock_urlopen.side_effect = mock_err
    
    with pytest.raises(RuntimeError) as exc_info:
        issue_keygen_license("user@example.com", "acc_123", "token_abc")
    assert "Keygen API error" in str(exc_info.value)

class MockServer:
    def __init__(self):
        pass

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
    payload = b'{"event": "checkout.paid", "data": {"attributes": {"email": "paid@example.com"}}}'
    secret = "my_secret"
    sig = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
    
    headers = {"Content-Length": str(len(payload)), "X-Signature": sig}
    
    with patch("core.webhook.WEBHOOK_SHARED_SECRET", secret):
        handler = DummyRequestHandler(payload, headers)
        handler.do_POST()
        
        assert handler.response_status == 200
        mock_issue.assert_called_once_with("paid@example.com", "", "")

@patch("core.webhook.issue_keygen_license")
def test_handler_invalid_signature(mock_issue):
    payload = b'{"event": "checkout.paid", "data": {"attributes": {"email": "paid@example.com"}}}'
    headers = {"Content-Length": str(len(payload)), "X-Signature": "bad_sig"}
    
    with patch("core.webhook.WEBHOOK_SHARED_SECRET", "my_secret"):
        handler = DummyRequestHandler(payload, headers)
        handler.do_POST()
        
        assert handler.response_status == 401
        mock_issue.assert_not_called()

@patch("core.webhook.issue_keygen_license")
def test_handler_unrelated_event(mock_issue):
    payload = b'{"event": "user.created", "data": {"attributes": {"email": "user@example.com"}}}'
    secret = "my_secret"
    sig = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
    headers = {"Content-Length": str(len(payload)), "X-Signature": sig}
    
    with patch("core.webhook.WEBHOOK_SHARED_SECRET", secret):
        handler = DummyRequestHandler(payload, headers)
        handler.do_POST()
        
        assert handler.response_status == 200
        # Check that we did not invoke keygen
        mock_issue.assert_not_called()
