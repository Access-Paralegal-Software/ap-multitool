---
id: windows_codesigning_prereqs_and_verification
title: Windows Codesigning Prerequisites and Verification
type: ops-manual
---

# Codesigning Prerequisites & Verification

## Prerequisites
To successfully sign APMultitool artifacts on a Windows build machine, the following must be configured:
1. **Windows SDK:** Ensure the Windows 10/11 SDK is installed to provide `signtool.exe`.
2. **Certificate Provisioning:** The OV Authenticode `.pfx` file (or certificate stored in the Windows Certificate Manager `Cert:CurrentUser\My`) must be available on the build host.
3. **Timestamp Server:** A reliable timestamp authority (e.g., `http://timestamp.digicert.com`) must be used to ensure the signature remains valid even after the original certificate expires.

## Manual Signing Command
If you need to manually sign an artifact outside of the PowerShell pipeline:

```powershell
# Using a PFX file
& "C:\Program Files (x86)\Windows Kits\10\bin\10.0.19041.0\x64\signtool.exe" sign /f "path\to\cert.pfx" /p "YourPassword" /t http://timestamp.digicert.com /fd SHA256 "dist\Access_Paralegal_Multitool.exe"

# Using Certificate Thumbprint (Preferred for automation)
& "C:\Program Files (x86)\Windows Kits\10\bin\10.0.19041.0\x64\signtool.exe" sign /sha1 "YOUR_THUMBPRINT_HERE" /t http://timestamp.digicert.com /fd SHA256 "dist\Access_Paralegal_Multitool.exe"
```

## Signature Verification
To verify that an artifact is correctly signed and timestamped:
1. **Right-Click Method:** Right-click the `.exe` -> Properties -> Digital Signatures tab. Verify the signer name and timestamp.
2. **CLI Method:**
```powershell
Get-AuthenticodeSignature -FilePath "dist\APMultitool_Setup_v1.0.0.exe"
```
The status should return `Valid`. If it returns `UnknownError`, the certificate chain may be untrusted on the local machine.

## Expected Behavior for Testers
When the `-rc1` installer is distributed to the initial staging cohort:
- Users will likely see a blue Windows SmartScreen modal: "Windows protected your PC."
- They must click **"More info"** and verify that the Publisher matches the name on the OV Certificate.
- They then click **"Run anyway"**.
- STAX operators must document when this warning ceases, indicating sufficient reputation has been gained.
