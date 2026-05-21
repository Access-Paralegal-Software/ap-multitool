import os
import re
import pytest

pytestmark = [pytest.mark.packaging]

# Paths to verify
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACKAGING_DIR = os.path.join(ROOT_DIR, "packaging", "windows")
ISS_SCRIPT = os.path.join(PACKAGING_DIR, "apmultitool_installer.iss")
BUILD_SCRIPT = os.path.join(PACKAGING_DIR, "build_installer.ps1")
PREPARE_SCRIPT = os.path.join(PACKAGING_DIR, "prepare_bundle.ps1")

def test_packaging_scripts_exist():
    """Verify that all critical packaging scripts and configuration files exist."""
    assert os.path.exists(PACKAGING_DIR), f"Packaging directory {PACKAGING_DIR} does not exist"
    assert os.path.exists(ISS_SCRIPT), f"Inno Setup script {ISS_SCRIPT} does not exist"
    assert os.path.exists(BUILD_SCRIPT), f"Build orchestrator script {BUILD_SCRIPT} does not exist"
    assert os.path.exists(PREPARE_SCRIPT), f"Prepare bundle script {PREPARE_SCRIPT} does not exist"

def test_installer_script_contains_expected_executables():
    """Verify that the Inno Setup script references both GUI and CLI executables."""
    with open(ISS_SCRIPT, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Ensure standard executable definitions exist
    assert '#define AppExeName "Access_Paralegal_Multitool.exe"' in content
    assert '#define AppCliName "apmultitool.exe"' in content
    
    # Verify both executables are part of the Start Menu or Icons definitions
    assert '{app}\\{#AppExeName}' in content
    assert '{app}\\{#AppCliName}' in content

def test_installer_script_version_matches():
    """Verify the Inno Setup script version syntax is valid semantic versioning."""
    with open(ISS_SCRIPT, "r", encoding="utf-8") as f:
        content = f.read()
    
    match = re.search(r'#define AppVersion "([^"]+)"', content)
    assert match is not None, "AppVersion definition not found in installer script"
    version_str = match.group(1)
    
    # Semantic version regex (e.g. 0.5.0)
    semver_pattern = r'^\d+\.\d+\.\d+(-[a-zA-Z0-9.]+)?$'
    assert re.match(semver_pattern, version_str), f"AppVersion '{version_str}' is not a valid semantic version"

def test_installer_script_contains_path_registration():
    """Verify that Inno Setup script contains optional registry PATH hooks."""
    with open(ISS_SCRIPT, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Check registry block and environment path additions
    assert '[Registry]' in content
    assert 'Root: HKCU; Subkey: "Environment"' in content
    assert 'ValueName: "Path"' in content
    assert 'ValueData: "{olddata};{app}"' in content
    assert 'Tasks: addtopath' in content
    
    # Check Pascal broadcast method to notify active Windows shells
    assert 'procedure BroadcastEnvironmentChange' in content
    assert 'SendMessageTimeout(HWND_BROADCAST, WM_SETTINGCHANGE' in content
    
    # Check cleanup routine during uninstall
    assert 'procedure CurUninstallStepChanged' in content
    assert 'RegWriteStringValue(HKEY_CURRENT_USER, \'Environment\', \'Path\'' in content
