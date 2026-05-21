---
id: windows-beta1-smartscreen-operator-guide
title: Windows Beta1 SmartScreen Operator Guide
type: operations
status: active
project: APMultitool
created_at: 2026-05-21T09:27:00Z
tags:
  - windows
  - smartscreen
  - operations
  - support
---

# 📖 Windows Defender SmartScreen Operator & Support Guide

This guide is designed for support personnel and operators coordinating the `v1.0.0-beta1` release of APMultitool. It provides a non-alarmist, plain-language walkthrough for assisting early testers when Windows Defender SmartScreen blocks installation.

---

## 🛡️ The Support Posture: Calm and Objective

When a tester reports a security block, do not dismiss the warning or tell them to disable Windows Defender. Windows Defender is doing its job by filtering unrecognized software. 

Use this clear, reassuring explanation:
> *"Windows Defender SmartScreen flags new software because it doesn't have a long history of downloads yet. Because we are in a selective beta, Microsoft hasn't seen this file enough times to verify it automatically. We manually audit and verify every build's integrity before distribution."*

---

## 🛠️ Step-by-Step Installation Walkthrough

Guide the tester through the standard bypass flow:

1. **Verify the File Name**: Ensure they are running the official installer executable:
   - `APMultitool_Setup_v1.0.0-beta1.exe`
2. **Access Hidden Options**: On the blue SmartScreen popup, click the **"More info"** hyperlink. This link is placed directly beneath the primary text warning.
3. **Execute the File**: Once expanded, click the **"Run anyway"** button that appears at the bottom.
4. **Approve UAC Prompt**: The User Account Control (UAC) dialog will query whether to allow the unknown publisher to make changes. Click **"Yes"** to launch the setup wizard.

*Note: This bypass procedure is standard for unrecognized files and should only be performed for trusted, internally audit-verified applications. Avoid encouraging users to genericize this bypass behavior for other software.*

---

## 🔍 How to Perform Checksum Verification

For testers who want complete reassurance, or to verify that a file has not been corrupted or tampered with in transit, guide them through a hash check using PowerShell:

1. Open **PowerShell** on the local Windows PC.
2. Run the `Get-FileHash` command targeting the downloaded installer:
   ```powershell
   Get-FileHash -Path "$env:USERPROFILE\Downloads\APMultitool_Setup_v1.0.0-beta1.exe" -Algorithm SHA256
   ```
3. Compare the printed hash value against the official signature file:
   - **Target Hash**: Compare this with the SHA256 checksum printed in the official `APMultitool_Setup_v1.0.0-beta1.exe.sha256` release metadata file.
   - If the hashes match, the file is identical to the one compiled by our pipeline and is safe to execute.
