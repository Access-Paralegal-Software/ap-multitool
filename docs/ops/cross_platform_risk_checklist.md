---
id: cross_platform_risk_checklist
title: Cross-Platform Risk Checklist
type: ops-checklist
status: active
project: APMultitool
created_at: 2026-05-21
---

# Cross-Platform Risk Checklist

This checklist tracks architectural assumptions, dependencies, and OS-specific risks that affect porting APMultitool from Windows to macOS and Linux.

---

## 📄 1. Document Conversion & Office COM Dependencies

On Windows, conversions from DOCX and XLSX to PDF rely heavily on local Microsoft Office COM engines (`win32com.client`) or fallback scripts.

- [ ] **Microsoft Office COM Portability (High Risk)**:
  - **Issue**: `win32com` does not exist on macOS or Linux.
  - **Impact**: Any attempt to convert `.docx` or `.xlsx` files using the Word/Excel COM API will raise `ImportError` or fail at runtime.
  - **Mitigation**: Introduce a headless compiler abstraction. Detect the host OS and fallback to LibreOffice CLI (e.g., `soffice --headless --convert-to pdf`) or PDF-native Python conversion alternatives.
- [ ] **Direct PDF Operations**:
  - **Status**: Safe. `pypdf`, `reportlab`, and `extract-msg` are pure Python libraries and behave identically across OS platforms.

---

## 📦 2. Packaging & Security Gatekeepers

Operating systems enforce distinct executable authorization structures.

- [ ] **macOS Gatekeeper Warning (High Risk)**:
  - **Issue**: macOS blockages of unsigned/unnotarized bundles.
  - **Impact**: Double-clicking the compiled DMG installer will trigger a security quarantine block.
  - **Mitigation**: Follow the signing and notarization steps in [macos_signing_requirements.md](file:///C:/Users/aewoo/Desktop/Repos/ap-multitool/docs/ops/macos_signing_requirements.md). Inform alpha testers of the right-click "Open" bypass protocol.
- [ ] **Linux Debian Packaging (Medium Risk)**:
  - **Issue**: `dpkg-deb` builds are architecture-bound (e.g., `amd64`).
  - **Impact**: The generated `.deb` installer will fail to install on ARM-based Linux hosts (e.g., Raspberry Pi) or distributions using other packaging managers (like RPM on Fedora/RHEL).
  - **Mitigation**: Provide the raw standalone binary zip fallback for non-Debian environments.

---

## 🔒 3. Vault Persistence, Encryption, and Hardware Identity

APMultitool locks local decrypted cases using hardware-bound keys and encrypts license configuration details.

- [ ] **Hardware Identification (Motherboard UUID) Compatibility (High Risk)**:
  - **Issue**: The current motherboard hashing logic relies on Windows WMI queries (`wmic baseboard get serialnumber` or PowerShell equivalents).
  - **Impact**: Hardware identification queries will throw shell command exceptions or return empty strings on macOS/Linux.
  - **Mitigation**: Abstract the hardware identifier collector. Use `ioreg -rd1 -c IOPlatformExpertDevice | grep IOPlatformUUID` on macOS, and read `/sys/class/dmi/id/product_uuid` (requiring sudo) or check machine ID files (`/etc/machine-id`) on Linux.
- [ ] **System Directory Differences**:
  - **Issue**: Telemetry and configuration state storage paths.
  - **Impact**: Telemetry writes directly to `Path.home() / ".access_paralegal_telemetry.json"`, which is cross-platform safe. However, registry calls for launcher shortcuts or PATH modifications are strictly Win32-bound.
  - **Mitigation**: Ensure all registry keys and environment variable writes (like `WM_SETTINGCHANGE` broadcasts) are guarded by `sys.platform == "win32"` conditions.
