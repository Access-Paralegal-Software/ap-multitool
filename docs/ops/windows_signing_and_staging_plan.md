---
id: windows_signing_and_staging_plan
title: Windows Signing and Staging Plan
type: ops-doctrine
---

# Windows Signing & Staging Plan

## Purpose
To outline the organizational structure for code signing APMultitool artifacts and the release channels used for phased testing and deployment. This ensures that the STAX fleet standard of high trust and verifiable chain-of-custody is met at the distribution layer.

## Certificate Strategy
- **Certificate Type:** Organization Validation (OV) Authenticode Certificate.
- **Why OV over EV?** While an EV (Extended Validation) certificate provides immediate SmartScreen reputation, it requires physical hardware tokens (YubiKey) which complicates automated CI/CD pipelines. We will use a standard OV certificate to sign artifacts, understanding that Microsoft SmartScreen will temporarily flag the binary as "unrecognized" during an initial reputation-building phase.
- **Universality Note:** This Windows Authenticode model conceptually mirrors the macOS Developer ID Application certificate signing that will be required later.

## Pipeline Integration
Code signing must occur at two discrete phases within `packaging/windows/build_installer.ps1`:
1. **Post-PyInstaller:** The raw standalone `Access_Paralegal_Multitool.exe` and `apmultitool.exe` must be signed before they are bundled by Inno Setup.
2. **Post-InnoSetup:** The final `APMultitool_Setup_vX.X.X.exe` installer must be signed.

## Staging & Release Channels
We maintain three primary deployment channels:
1. **Alpha (`-alphaX`):** Internal STAX fleet testing. Unsigned or self-signed.
2. **Release Candidate (`-rcX`):** Closed testing cohort (Paralegal Alpha Group). Fully signed with the OV certificate to build SmartScreen reputation.
3. **Stable (`vX.X.X`):** General production release. Fully signed, verified, and distributed to end users.

## Managing SmartScreen
During the rollout of `-rc1`, testers must be explicitly instructed on how to bypass the initial Windows Defender SmartScreen ("Windows protected your PC") warning. Over a period of several dozen downloads and executions, the OV certificate will automatically accrue trust and the prompt will vanish for future Stable releases.
