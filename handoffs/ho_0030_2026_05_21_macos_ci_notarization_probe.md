---
id: ho_0030_2026_05_21_macos_ci_notarization_probe
title: Handoff — macOS CI Packaging and Notarization Probe
type: handoff
status: completed
project: Access Paralegal / APMultitool
lane: macos-ci-packaging
created: 2026-05-21
---

# Handoff: macOS CI Packaging and Notarization Probe

## 1. Summary

This handoff covers the macOS CI packaging and notarization probe lane completed on 2026-05-21. A dedicated GitHub Actions workflow was designed and committed to probe the macOS build pipeline using the existing `packaging/macos/build_app.sh` scaffold. The workflow produces an unsigned DMG artifact in active probe mode and contains guarded placeholder steps for full Apple Developer signing and notarization, which activate automatically once credentials are provisioned.

No new engine features were added. No macOS support is claimed as production-ready. The Windows alpha release pipeline remains the active release track. macOS packaging is in the **probe/credentialing** phase.

---

## 2. What Is Ready

| Deliverable | Location | Status |
|---|---|---|
| macOS packaging ops overview | `docs/ops/macos_packaging_overview.md` | ✅ Created |
| Secrets and credentials inventory | `docs/ops/macos_signing_requirements.md` | ✅ Created |
| macOS CI probe workflow | `.github/workflows/macos_packaging_probe.yml` | ✅ Created |
| Unsigned DMG build in CI | CI artifact `macos-dmg-unsigned` | ✅ Active |
| Certificate import placeholder | Guarded step in probe workflow | ✅ Ready to activate |
| Codesigning placeholder | Guarded step in probe workflow | ✅ Ready to activate |
| Notarization placeholder | Guarded step in probe workflow | ✅ Ready to activate |
| Stapling placeholder | Guarded step in probe workflow | ✅ Ready to activate |
| Notarization command sequence | `docs/ops/macos_packaging_overview.md` §3 | ✅ Documented |
| Runner options analysis | `docs/ops/macos_packaging_overview.md` §6 | ✅ Documented |
| CI gating strategy | `workflow_dispatch` + `release/**` | ✅ Implemented |

---

## 3. What Is Blocked

| Blocker | Required Action | Owner |
|---|---|---|
| **Apple Developer Program membership** | Enroll at developer.apple.com; required to obtain any Developer ID certificate | Business / Legal |
| **Developer ID Application certificate** | Create via Apple Developer portal → Certificates; export as `.p12` | Developer (on enrolled account) |
| **Apple Team ID** | Retrieve from Apple Developer portal → Account → Membership | Whoever holds the Developer account |
| **App-Specific Password** | Generate at appleid.apple.com → Security → App-Specific Passwords | Developer account holder |
| **GitHub Actions secrets** | Add all 5 secrets to repo Settings → Secrets and variables → Actions | DevOps |
| **Qt entrypoint in build_app.sh** | `build_app.sh` targets `gui_apmultitool.py` (legacy); must be updated to `gui_apmultitool_qt.py` before a production macOS release | Engineering |

macOS support **cannot be declared** until at minimum the certificate is provisioned and the notarization path is validated end-to-end.

---

## 4. Architecture of the Probe Workflow

```
Trigger: workflow_dispatch OR push to release/**
        │
        ▼
  [Setup] Checkout + Python 3.11 + pip dependencies
        │
        ▼
  [Build — ACTIVE] build_app.sh (no signing args)
    → dist/APMultitool_Setup_v*.dmg  (unsigned)
        │
        ▼
  [Upload — ACTIVE] artifact: macos-dmg-unsigned
        │
        ▼  ← GUARDED: APPLE_DEV_ID_CERT + APPLE_DEV_ID_CERT_PASSWORD secrets present
  [FUTURE] Import cert → ephemeral keychain ($RUNNER_TEMP/build.keychain)
        │
        ▼  ← GUARDED: APPLE_DEV_ID_CERT + APPLE_TEAM_ID secrets present
  [FUTURE] codesign inner libs → CLI → outer app bundle (Hardened Runtime)
           Rebuild signed DMG
        │
        ▼  ← GUARDED: all 4 notarization secrets present
  [FUTURE] xcrun notarytool submit --wait
        │
        ▼  ← GUARDED: same condition
  [FUTURE] xcrun stapler staple
        │
        ▼
  [FUTURE] Upload artifact: macos-dmg-signed-notarized
```

---

## 5. Enabling Full Signing and Notarization

Once an Apple Developer ID Application certificate is available, follow these steps to activate the full pipeline.

### Step 1: Obtain the Developer ID Application certificate

1. Log in to the Apple Developer portal (developer.apple.com).
2. Navigate to Certificates, Identifiers & Profiles → Certificates → + (Create).
3. Choose **Developer ID Application**.
4. Generate a Certificate Signing Request (CSR): open Keychain Access → Certificate Assistant → Request a Certificate from a Certificate Authority. Save to disk.
5. Upload the CSR to the Apple Developer portal and download the resulting `.cer` file.
6. Double-click the `.cer` to install it in Keychain Access.

### Step 2: Export the .p12 for CI

1. In Keychain Access, locate the certificate under **My Certificates**.
2. Right-click → Export → choose `.p12` format.
3. Set a strong password. Record this as `APPLE_DEV_ID_CERT_PASSWORD`.

```bash
# Encode the .p12 as a single-line base64 string for the GitHub secret:
base64 -i DeveloperID_Application.p12 | tr -d '\n' | pbcopy
# The clipboard now contains the value for APPLE_DEV_ID_CERT.
```

### Step 3: Generate an app-specific password

1. Sign in to appleid.apple.com with the Apple Developer account.
2. Navigate to Security → App-Specific Passwords → Generate.
3. Label it `APMultitool CI Notarization`.
4. Copy the generated password — this is `APPLE_APP_SPECIFIC_PASSWORD`.

### Step 4: Find the Team ID

1. Log in to the Apple Developer portal.
2. Navigate to Account → Membership.
3. Copy the **Team ID** (10-character alphanumeric string) — this is `APPLE_TEAM_ID`.

### Step 5: Add secrets to GitHub

In the repository on GitHub — Settings → Secrets and variables → Actions → New repository secret:

| Secret Name | Value Source |
|---|---|
| `APPLE_DEV_ID_CERT` | Base64-encoded `.p12` (Step 2) |
| `APPLE_DEV_ID_CERT_PASSWORD` | Password set during `.p12` export (Step 2) |
| `APPLE_TEAM_ID` | 10-character Team ID (Step 4) |
| `APPLE_APPLE_ID` | Apple Developer account email address |
| `APPLE_APP_SPECIFIC_PASSWORD` | App-specific password (Step 3) |

Once all 5 secrets are present, the guarded steps in `macos_packaging_probe.yml` activate automatically on the next run.

### Step 6: Update build_app.sh to the Qt entrypoint

`packaging/macos/build_app.sh` currently references `gui_apmultitool.py` (legacy CustomTkinter). Before shipping a production macOS release, update the script to target `gui_apmultitool_qt.py` and adjust hidden-imports to include the required PySide6 modules. This change is in Engineering scope, not the CI probe lane.

### Step 7: Trigger the workflow

- **Manual:** GitHub → Actions → macOS Packaging Probe → Run workflow.
- **Automatic:** Push any commit to a `release/**` branch.

### Step 8: Verify end-to-end notarization

After the full pipeline runs, download the notarized DMG artifact and validate on a Mac:

```bash
# Check Gatekeeper acceptance
spctl --assess --type open --context context:primary-signature -v APMultitool_Setup_v*.dmg
# Expected: "accepted  source=Notarized Developer ID"

# Confirm stapling
xcrun stapler validate APMultitool_Setup_v*.dmg
# Expected: "The staple and validate action worked!"
```

---

## 6. Files Created This Lane

| File | Description |
|---|---|
| `docs/ops/macos_packaging_overview.md` | Ops doc: build steps, notarization command sequence, runner options, CI gating |
| `docs/ops/macos_signing_requirements.md` | Secrets inventory and `.p12` export instructions |
| `.github/workflows/macos_packaging_probe.yml` | Probe CI workflow (build active; signing/notarization guarded) |
| `handoffs/ho_0030_2026_05_21_macos_ci_notarization_probe.md` | This handoff |

---

## 7. Suggested Next Steps for Future Lanes

1. Provision Apple Developer Program membership and Developer ID Application certificate.
2. Configure all 5 GitHub Actions secrets (§5 above).
3. Update `build_app.sh` to target the Qt entry point (`gui_apmultitool_qt.py`).
4. Trigger the probe workflow and validate the full unsigned → signed → notarized path end-to-end.
5. Once the notarized artifact is validated, promote macOS packaging into the main `build.yml` matrix with signing enabled.
6. Declare macOS alpha support and update README accordingly.
