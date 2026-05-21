---
id: windows-alpha-support-bundle-spec
title: Windows Alpha Support Bundle Specification
type: operations
status: active
project: APMultitool
created_at: 2026-05-21T07:30:00Z
tags:
  - windows
  - alpha
  - support-bundle
  - specification
  - privacy
---

# 📦 Windows Alpha Support Bundle Specification

This document defines the structure, file schemas, privacy boundaries, and transmission guidelines for the APMultitool Support Bundle diagnostic package.

---

## 🎯 1. Privacy and Anonymization Boundaries

APMultitool operates under a **100% offline data guarantee**. The support bundle is designed strictly to aid developers in resolving crash or conversion errors without compromising attorney-client privilege or security keys.

### 🚫 Forbidden Contents
The support bundle **must not** contain, copy, or reference:
- Case file contents (raw document text, email bodies, attachments, or PDFs).
- Secret vault files: `%USERPROFILE%\.access_cases_vault.enc` or similar database paths.
- Active license files: `%USERPROFILE%\.access_paralegal_license.json`.
- Secret encryption keys, salts, or passwords.
- Hardware identity details (raw MAC addresses, motherboard serials, etc.) that are not pre-hashed.

### 🟢 Allowed Contents
The support bundle is restricted to:
- Application performance metrics and aggregation logs (from `%USERPROFILE%\.access_paralegal_telemetry.json`).
- Environment variables affecting document engines (e.g., `APM_CONVERSION_BACKEND`, `APM_MULTITOOL_USE_LIBREOFFICE_FALLBACK`).
- Non-sensitive metadata: OS version, display scale factor, PySide6 version, python runtime environment.
- Standard application rotation logs (`apmultitool.log`), which contain execution tracebacks, status messages, and timing benchmarks.

### 🧹 Path Scrubbing Rule
To avoid leaking usernames or network folder names (e.g., `C:\Users\AttorneyName\Documents\ConfidentialClient\...`), the generation helper must:
- Sanitize paths written into `metadata.json`.
- Replace user profile paths (e.g., `C:\Users\JohnDoe`) with `<USERPROFILE>`.
- Truncate full document directories, displaying only the file extension and base name (e.g., `document.docx`) in warning logs if necessary.

---

## 📂 2. Directory and File Layout

The support bundle is generated as a standard compressed ZIP archive:

```
apmultitool_support_bundle_<YYYYMMDD>_<HHMMSS>.zip
├── metadata.json
├── telemetry.json
└── logs/
    ├── apmultitool.log
    ├── apmultitool.log.1 (if present)
    └── apmultitool.log.2 (if present)
```

### 📄 2.1 metadata.json Schema

```json
{
  "timestamp": "2026-05-21T07:35:12Z",
  "app": {
    "version": "1.0.0",
    "channel": "-alpha1",
    "build_id": "v1.0.0-alpha1"
  },
  "environment": {
    "os_platform": "Windows-10-10.0.19045-SP0",
    "os_release": "10",
    "python_version": "3.11.2",
    "display_scaling": "125%"
  },
  "engines": {
    "office_installed": true,
    "word_present": true,
    "excel_present": true,
    "libreoffice_path": "C:\\Program Files\\LibreOffice\\program\\soffice.exe",
    "libreoffice_fallback_enabled": true,
    "active_backend_override": null
  }
}
```

### 📄 2.2 telemetry.json
Direct copy of `%USERPROFILE%\.access_paralegal_telemetry.json`. Contains overall operation success rates, start count metrics, and the last error message string with timestamp.

---

## 🚚 3. Transmission and Transport Protocol

- **No Auto-Upload**: The application will never perform any HTTP/HTTPS, FTP, or cloud upload of the support bundle.
- **Manual Hand-off**: When a tester clicks "Export Support Bundle...", the system packages the files locally and opens the directory in Windows Explorer (or outputs the file path in CLI).
- **Communication instructions**: The tester is instructed to attach the zip file to their email or upload it directly to the designated cohort OneDrive folder.
