# tests/test_support_bundle.py
"""Unit and integration tests for support bundle generation and path scrubbing."""

import os
import json
import zipfile
from pathlib import Path
import pytest

from core.support import (
    get_log_dir,
    get_user_profiles_to_scrub,
    scrub_text,
    create_support_bundle
)

def test_user_profiles_to_scrub():
    profiles = get_user_profiles_to_scrub()
    assert isinstance(profiles, list)
    # Ensure it's not empty, as USERPROFILE or HOME should exist
    assert len(profiles) > 0
    # Assert elements are strings and sorted by length descending
    for p in profiles:
        assert isinstance(p, str)
        assert len(p) > 3
    
    # Ensure they are sorted by length descending
    lengths = [len(p) for p in profiles]
    assert lengths == sorted(lengths, reverse=True)

def test_scrub_text():
    profiles = ["C:\\Users\\john_doe", "john_doe"]
    
    # Simple path scrubbing
    raw_path = "Error occurred at C:\\Users\\john_doe\\Documents\\file.txt"
    scrubbed = scrub_text(raw_path, profiles)
    assert "C:\\Users\\john_doe" not in scrubbed
    assert "<USERPROFILE>\\Documents\\file.txt" in scrubbed

    # Case insensitivity
    raw_path_lower = "error at c:\\users\\john_doe\\documents\\file.txt"
    scrubbed_lower = scrub_text(raw_path_lower, profiles)
    assert "c:\\users\\john_doe" not in scrubbed_lower
    assert "<USERPROFILE>\\documents\\file.txt" in scrubbed_lower

    # Forward slash replacement
    raw_path_forward = "Error at C:/Users/john_doe/Documents/file.txt"
    scrubbed_forward = scrub_text(raw_path_forward, profiles)
    assert "C:/Users/john_doe" not in scrubbed_forward
    assert "<USERPROFILE>/Documents/file.txt" in scrubbed_forward

def test_create_support_bundle(tmp_path, monkeypatch):
    # Set up a temporary logs directory and telemetry file
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    
    # Create fake logs
    log_file1 = log_dir / "apmultitool.log"
    log_file1.write_text("Log event from user C:\\Users\\testuser\nSome error traceback", encoding="utf-8")
    
    log_file2 = log_dir / "apmultitool.log.1"
    log_file2.write_text("Older log event", encoding="utf-8")
    
    # Create fake telemetry
    telemetry_file = tmp_path / ".access_paralegal_telemetry.json"
    telemetry_data = {
        "total_runs": 5,
        "failed_runs": 1,
        "last_error": "Failed in C:\\Users\\testuser\\Desktop\\APMultitool"
    }
    with open(telemetry_file, "w", encoding="utf-8") as f:
        json.dump(telemetry_data, f)
        
    # Monkeypatch support modules to point to our temp structures
    monkeypatch.setattr("core.support.get_log_dir", lambda: log_dir)
    monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)
    monkeypatch.setattr("core.support.check_ms_office_presence", lambda: (True, True, True))
    monkeypatch.setattr("core.support.get_libreoffice_path", lambda: "C:\\Program Files\\LibreOffice\\program\\soffice.exe")
    
    # Mock environment to scrub "C:\\Users\\testuser" and "testuser"
    monkeypatch.setattr("core.support.get_user_profiles_to_scrub", lambda: ["C:\\Users\\testuser", "testuser"])

    # Generate support bundle in temp target directory
    bundle_target = tmp_path / "output"
    bundle_target.mkdir()
    
    zip_path = create_support_bundle(target_dir=bundle_target)
    
    assert zip_path.exists()
    assert zip_path.suffix == ".zip"
    assert zip_path.name.startswith("apmultitool_support_bundle_")
    
    # Inspect ZIP structure and contents
    with zipfile.ZipFile(zip_path, "r") as z:
        namelist = z.namelist()
        assert "metadata.json" in namelist
        assert "telemetry.json" in namelist
        assert "logs/apmultitool.log" in namelist
        assert "logs/apmultitool.log.1" in namelist
        
        # Verify no sensitive DB or vault file exists in ZIP namelist
        for name in namelist:
            assert "vault" not in name.lower()
            assert ".db" not in name.lower()
            assert "license" not in name.lower()
            
        # Verify metadata is scrubbed
        metadata_str = z.read("metadata.json").decode("utf-8")
        metadata = json.loads(metadata_str)
        assert "environment" in metadata
        assert "app" in metadata
        assert "engines" in metadata
        
        # Verify telemetry content is scrubbed
        telemetry_str = z.read("telemetry.json").decode("utf-8")
        telemetry = json.loads(telemetry_str)
        assert telemetry["total_runs"] == 5
        assert "testuser" not in telemetry["last_error"]
        assert "<USERPROFILE>" in telemetry["last_error"]
        
        # Verify log file contents are scrubbed
        log_str = z.read("logs/apmultitool.log").decode("utf-8")
        assert "C:\\Users\\testuser" not in log_str
        assert "<USERPROFILE>" in log_str
