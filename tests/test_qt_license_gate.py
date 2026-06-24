import os
import json
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta, timezone

import pytest
from apmultitool_qt.security import VaultSecurityManager, LICENSE_FILE
from core.licensing import Entitlement, get_machine_fingerprint
from core.licensing_store import save_cached_entitlement, clear_cached_entitlement

@pytest.fixture(autouse=True)
def clean_license_files():
    clear_cached_entitlement()
    if os.path.exists(LICENSE_FILE):
        try:
            os.remove(LICENSE_FILE)
        except Exception:
            pass
    yield
    clear_cached_entitlement()
    if os.path.exists(LICENSE_FILE):
        try:
            os.remove(LICENSE_FILE)
        except Exception:
            pass

def test_manager_init_inactive():
    # Initial state with no files should not be activated
    manager = VaultSecurityManager()
    assert manager.is_pro_activated is False
    assert manager.active_license_key is None

def test_manager_init_valid_cache():
    # Write a valid cached entitlement
    fingerprint = get_machine_fingerprint()
    future_expiry = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
    ent = Entitlement("VALID-KEY", "activated", future_expiry, fingerprint)
    save_cached_entitlement(ent)
    
    manager = VaultSecurityManager()
    assert manager.is_pro_activated is True
    assert manager.active_license_key == "VALID-KEY"

@patch("apmultitool_qt.security.verify_license_online")
def test_manager_init_stale_cache_restores_online(mock_verify):
    # Setup stored key file but no valid cache (e.g. cache expired/missing)
    with open(LICENSE_FILE, "w") as f:
        json.dump({"key": "STORED-KEY", "stamp": str(datetime.now())}, f)
        
    # Mock online server validating the key successfully
    future_expiry = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
    mock_verify.return_value = Entitlement("STORED-KEY", "activated", future_expiry, get_machine_fingerprint())
    
    manager = VaultSecurityManager()
    assert manager.is_pro_activated is True
    assert manager.active_license_key == "STORED-KEY"
    mock_verify.assert_called_once_with("STORED-KEY")

@patch("apmultitool_qt.security.verify_license_online")
def test_manager_activation_success(mock_verify):
    future_expiry = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
    mock_verify.return_value = Entitlement("NEW-KEY", "activated", future_expiry, get_machine_fingerprint())
    
    manager = VaultSecurityManager()
    assert manager.is_pro_activated is False
    
    success = manager.activate_license("NEW-KEY")
    assert success is True
    assert manager.is_pro_activated is True
    assert manager.active_license_key == "NEW-KEY"
    
    # Stored key file should exist
    assert os.path.exists(LICENSE_FILE)
    with open(LICENSE_FILE, "r") as f:
        data = json.load(f)
    assert data["key"] == "NEW-KEY"

@patch("apmultitool_qt.security.verify_license_online")
def test_manager_activation_failure(mock_verify):
    # Mock online validation returning invalid status
    mock_verify.return_value = Entitlement("BAD-KEY", "invalid", "", get_machine_fingerprint())
    
    manager = VaultSecurityManager()
    success = manager.activate_license("BAD-KEY")
    assert success is False
    assert manager.is_pro_activated is False
    assert manager.active_license_key is None
