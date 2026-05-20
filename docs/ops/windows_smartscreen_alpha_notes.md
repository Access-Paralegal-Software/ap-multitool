---
id: windows-smartscreen-alpha-notes
title: Windows SmartScreen Behavior & Bypass Notes
type: operations
status: active
project: APMultitool
created_at: 2026-05-20T11:20:00Z
tags:
  - windows
  - smartscreen
  - code-signing
  - alpha-testing
---

# 🛡️ Windows SmartScreen Behavior & Bypass Guide (Alpha Testing)

Since the Paralegal Alpha builds (`APMultitool_Setup_v1.0.0-alpha1.exe`) are distributed without an active commercial Authenticode signature, Windows SmartScreen will flag the installer upon download and initial execution. This is expected behavior.

## What Testers Will See
When a tester downloads and attempts to run the installer, Windows Defender SmartScreen will block execution and display a blue dialog with the warning:
> **Windows protected your PC**
> 
> Microsoft Defender SmartScreen prevented an unrecognized app from starting. Running this app might put your PC at risk.
> 
> **Publisher:** Unknown Publisher  
> **App:** `APMultitool_Setup_v1.0.0-alpha1.exe`

## How to Proceed Safely (Instructions for Testers)
To install the Alpha release, testers must manually bypass the SmartScreen warning. Provide these steps to the test cohort:

1. Click on the **"More info"** text link directly below the warning description in the SmartScreen popup.
2. The dialog will expand to reveal the **"Run anyway"** button.
3. Click **"Run anyway"** to launch the Inno Setup wizard.
4. The User Account Control (UAC) dialog will appear asking:
   > "Do you want to allow this app from an unknown publisher to make changes to your device?"
5. Click **"Yes"** to proceed with installation.

---

## 🔍 Cryptographic Integrity Verification (Optional)
To guarantee the file has not been tampered with or corrupted during transit, testers can verify the installer's SHA256 checksum in PowerShell:

```powershell
Get-FileHash -Path "path\to\APMultitool_Setup_v1.0.0-alpha1.exe" -Algorithm SHA256
```

Confirm that the output hash matches the release signature file:
- **Expected Hash:** `ADB7CC6B49A8B0026F87A65BF3FE7D24F31BEBE75DA360372B077F805C606564`
