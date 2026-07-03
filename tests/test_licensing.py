import os
import time
import json
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock

import pytest
from core.licensing import Entitlement, get_machine_fingerprint, calculate_signature, verify_license_online
from core.licensing_store import save_cached_entitlement, load_cached_entitlement, clear_cached_entitlement, CACHE_FILE_PATH

@pytest.fixture(autouse=True)
def clean_license_cache():
    """Ensure a clean cache file before and after each test."""
    clear_cached_entitlement()
    yield
    clear_cached_entitlement()

def test_machine_fingerprint():
    fingerprint = get_machine_fingerprint()
    assert isinstance(fingerprint, str)
    assert len(fingerprint) > 0

def test_entitlement_validation_happy_path():
    fingerprint = get_machine_fingerprint()
    future_expiry = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
    
    ent = Entitlement("TEST-KEY-123", "activated", future_expiry, fingerprint)
    assert ent.is_valid() is True

def test_entitlement_validation_expired():
    fingerprint = get_machine_fingerprint()
    past_expiry = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    
    ent = Entitlement("TEST-KEY-123", "activated", past_expiry, fingerprint)
    assert ent.is_valid() is False

def test_entitlement_validation_wrong_machine():
    future_expiry = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
    
    ent = Entitlement("TEST-KEY-123", "activated", future_expiry, "SOME-OTHER-MACHINE-UUID")
    assert ent.is_valid() is False

def test_entitlement_validation_non_activated_status():
    fingerprint = get_machine_fingerprint()
    future_expiry = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
    
    for status in ["expired", "suspended", "invalid"]:
        ent = Entitlement("TEST-KEY-123", status, future_expiry, fingerprint)
        assert ent.is_valid() is False

def test_signature_integrity():
    fingerprint = get_machine_fingerprint()
    future_expiry = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
    ent = Entitlement("TEST-KEY-123", "activated", future_expiry, fingerprint)
    
    sig1 = calculate_signature(ent)
    
    # Modify data and verify signature changes
    ent.status = "expired"
    sig2 = calculate_signature(ent)
    assert sig1 != sig2

def test_save_and_load_cache():
    fingerprint = get_machine_fingerprint()
    future_expiry = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
    ent = Entitlement("TEST-KEY-123", "activated", future_expiry, fingerprint)
    
    save_cached_entitlement(ent)
    
    loaded = load_cached_entitlement()
    assert loaded is not None
    assert loaded.license_key == "TEST-KEY-123"
    assert loaded.is_valid() is True

def test_tampered_cache_detection():
    fingerprint = get_machine_fingerprint()
    future_expiry = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
    ent = Entitlement("TEST-KEY-123", "activated", future_expiry, fingerprint)
    
    save_cached_entitlement(ent)
    
    # Manually tamper with cache file
    with open(CACHE_FILE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    data["entitlement"]["status"] = "activated_hacked"  # Tamper with payload
    
    with open(CACHE_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f)
        
    # Attempting to load should detect tampering and return None
    loaded = load_cached_entitlement()
    assert loaded is None

@patch("urllib.request.urlopen")
def test_online_verify_success(mock_urlopen):
    # Mock online server response
    mock_response = MagicMock()
    future_expiry = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
    mock_response.read.return_value = json.dumps({
        "status": "activated",
        "expires_at": future_expiry
    }).encode("utf-8")
    mock_urlopen.return_value.__enter__.return_value = mock_response
    
    ent = verify_license_online("GOOD-KEY")
    assert ent.status == "activated"
    assert ent.is_valid() is True

@patch("urllib.request.urlopen")
def test_online_verify_invalid(mock_urlopen):
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({
        "status": "invalid",
        "expires_at": ""
    }).encode("utf-8")
    mock_urlopen.return_value.__enter__.return_value = mock_response
    
    ent = verify_license_online("BAD-KEY")
    assert ent.status == "invalid"
    assert ent.is_valid() is False

def test_offline_grace_days_logic():
    # If the user has a valid cached entitlement from a recent online check,
    # and connection error is raised when verifying online, we check fallback
    fingerprint = get_machine_fingerprint()
    past_expiry = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat() # expired online check
    
    # 1. Verification of Entitlement properties directly
    # Valid online verification date (e.g. checked 2 hours ago)
    valid_verification_date = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
    ent = Entitlement("VALID-KEY", "activated", past_expiry, fingerprint, last_verified_at=valid_verification_date)
    # direct is_valid will check expires_at first, returning False if expired.
    # The grace fallback check is executed at the Manager level.
    assert ent.is_valid() is False


def test_seat_reuse_fails_different_machine():
    machine_a = "MACHINE-A-UUID"
    machine_b = "MACHINE-B-UUID"
    
    future_expiry = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
    ent_a = Entitlement("SHARED-KEY", "activated", future_expiry, machine_a)
    
    with patch("core.licensing.get_machine_fingerprint", return_value=machine_b):
        assert ent_a.is_valid() is False


@patch("urllib.request.urlopen")
def test_offline_reactivation_requires_network(mock_urlopen):
    # If network is down, calling verify_license_online must raise ConnectionError,
    # proving that offline reactivation of a raw key is not implemented/supported.
    mock_urlopen.side_effect = Exception("Network down")
    
    with pytest.raises(ConnectionError):
        verify_license_online("SOME-KEY")

