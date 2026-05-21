---
id: macos_packaging_overview
title: macOS Packaging Overview — Build, Sign, Notarize, Staple
type: ops
status: in-progress
project: Access Paralegal / APMultitool
created: 2026-05-21
---

# macOS Packaging Overview

## 1. Current State

### Pipeline Modes

The pipeline operates in one of three modes, determined entirely by which credentials are passed to `build_app.sh` (or present as CI secrets):

| Mode | Trigger | Output | macOS support claimed? |
|---|---|---|---|
| **Unsigned Probe** (default) | No credentials provided | Unsigned `.dmg` — not Gatekeeper-approved | No |
| **Signing Only** | `SIGN_IDENTITY` provided, no notarization params | Signed `.app` + `.dmg` — Gatekeeper-approved with bypass | No |
| **Activated** | All 5 secrets configured | Signed, notarized, stapled `.dmg` — Gatekeeper-approved, distributable | Only after end-to-end validation |

**Current default:** Unsigned Probe. No credentials are provisioned. macOS is not a supported release platform.

### Script Scaffold

A shell script scaffold exists at `packaging/macos/build_app.sh`. It implements the full four-phase pipeline with graceful degradation — phases are skipped when required credentials are absent:

- **PyInstaller compilation** of the CLI binary (`apmultitool`) and GUI app bundle (`Access_Paralegal_Multitool.app`).
- **Codesigning** using `codesign --options runtime` (skipped when no signing identity is passed). See `SIGNING_HOOK_START / SIGNING_HOOK_END` markers in the script.
- **DMG creation** via native `hdiutil` with an `/Applications` symlink for drag-and-drop installation.
- **Notarization and stapling** via `xcrun notarytool submit` + `xcrun stapler staple` (skipped when credentials are absent). See `NOTARIZATION_HOOK_START / NOTARIZATION_HOOK_END` markers in the script.

**Entry point:** `build_app.sh` targets `gui_apmultitool_qt.py` (PySide6 Qt edition). The legacy CustomTkinter entry point (`gui_apmultitool.py`) is no longer referenced in the macOS pipeline. This correction was applied in lane ho_0046.

**CI status prior to this lane:** The legacy `build.yml` included a `macos-latest` matrix job but had no signing or notarization hooks and referenced an outdated entry point (`gui_merger.py`). No dedicated macOS signing workflow existed.

### Build Script Parameters

```bash
bash packaging/macos/build_app.sh [AppVersion] [ReleaseChannel] [SignIdentity] [TeamId] [AppleID] [ApplePasswordVarName]
```

| Parameter | Default | Description |
|---|---|---|
| `AppVersion` | `1.0.0` | Semantic version string |
| `ReleaseChannel` | `-alpha1` | Channel suffix appended to version |
| `SignIdentity` | _(empty)_ | Developer ID Application cert common name; omit to skip signing |
| `TeamId` | _(empty)_ | 10-character Apple Team ID |
| `AppleID` | _(empty)_ | Apple Developer account email |
| `ApplePasswordVarName` | _(empty)_ | Name of env var holding the app-specific password |

---

## 1a. Verified on Host

**Status as of 2026-05-21 (lane ho_0046): No bare-metal macOS run has been performed yet.**

The development environment is Windows 11. This lane performed a static review of the pipeline and corrected two blocking script issues (see below). A bare-metal dry-run is deferred until a macOS host is available.

Host profile template and first-run observation checklist: see `docs/ops/macos_host_profile_apmultitool.md`.

### Static review corrections applied (ho_0046)

| File | Issue Corrected |
|---|---|
| `packaging/macos/build_app.sh` | Entry point changed from `gui_apmultitool.py` (legacy CustomTkinter) to `gui_apmultitool_qt.py` (active PySide6 Qt) |
| `.github/workflows/macos_packaging_probe.yml` | pip install updated: `customtkinter` → `PySide6` |
| `docs/ops/qt_macos_packaging_readiness.md` | Stale claim "No build scripts exist in `packaging/macos/`" removed |

These corrections ensure the pipeline targets the active codebase. A local unsigned DMG build should be run to validate end-to-end behavior once a macOS host is available.

---

## 2. Target Output

| Artifact | Description |
|---|---|
| `dist/Access_Paralegal_Multitool.app` | Signed macOS GUI app bundle |
| `dist/apmultitool` | Signed CLI binary |
| `dist/APMultitool_Setup_v<version>.dmg` | Notarized and stapled disk image for distribution |

---

## 3. High-Level Pipeline Steps

### Step 1 — Build

```bash
bash packaging/macos/build_app.sh <APP_VERSION> <RELEASE_CHANNEL>
```

Runs PyInstaller for both the GUI app bundle and the CLI binary. Stages the `.app` into a DMG layout with an `/Applications` symlink and packages it using `hdiutil`. No signing arguments are passed in probe mode.

### Step 2 — Codesign

Signing requires a **Developer ID Application** certificate from the Apple Developer Program. All inner binaries must be signed before the outer bundle, and the Hardened Runtime flag is required by Apple's notarization service.

```bash
# 1. Sign inner .so / .dylib / Python libraries
find dist/Access_Paralegal_Multitool.app -type f \( -name "*.so" -o -name "*.dylib" -o -name "Python" \) | \
    while read -r lib; do
        codesign --force --options runtime --sign "$SIGN_IDENTITY" "$lib"
    done

# 2. Sign CLI binary
codesign --force --options runtime --sign "$SIGN_IDENTITY" dist/apmultitool

# 3. Sign outer app bundle
codesign --force --options runtime --deep --sign "$SIGN_IDENTITY" dist/Access_Paralegal_Multitool.app

# 4. Verify
codesign --verify --verbose=2 dist/Access_Paralegal_Multitool.app
```

`$SIGN_IDENTITY` takes the form `Developer ID Application: <Org Name> (<TEAM_ID>)`.

### Step 3 — Notarize

Submit the final signed DMG to Apple's notarization service using the modern `notarytool` interface (Xcode 13+, replaces the deprecated `altool`):

```bash
xcrun notarytool submit dist/APMultitool_Setup_v<version>.dmg \
    --apple-id "$APPLE_ID" \
    --password "$APP_SPECIFIC_PASSWORD" \
    --team-id "$TEAM_ID" \
    --wait
```

The `--wait` flag blocks until Apple returns a result (typically seconds to a few minutes). To retrieve the full log for a submission:

```bash
xcrun notarytool log <SUBMISSION_ID> \
    --apple-id "$APPLE_ID" \
    --password "$APP_SPECIFIC_PASSWORD" \
    --team-id "$TEAM_ID"
```

### Step 4 — Staple

After successful notarization, staple the ticket directly to the DMG so Gatekeeper can verify it offline without a network check:

```bash
xcrun stapler staple dist/APMultitool_Setup_v<version>.dmg
```

Stapling is required for distribution outside the Mac App Store. Without it, opening the DMG on a machine without internet access triggers a Gatekeeper failure.

---

## 4. Required Dependencies

| Dependency | Purpose |
|---|---|
| Developer ID Application certificate | Identifies the app to macOS Gatekeeper; issued under the Apple Developer Program |
| Apple ID | Used for notarytool authentication |
| App-Specific Password | Generated at appleid.apple.com; replaces raw Apple ID password for notarytool |
| Team ID | 10-character alphanumeric identifier from the Apple Developer portal |
| Xcode Command Line Tools | Provides `codesign`, `xcrun`, `notarytool`, `stapler`, `hdiutil` |
| Python 3.11 + PyInstaller | Compiles the app bundle and CLI binary |

Full secrets inventory: see `docs/ops/macos_signing_requirements.md`.

---

## 5. CI Gating Strategy

**Chosen strategy: manual trigger (`workflow_dispatch`) + push to `release/**` branches.**

The macOS packaging probe workflow (`.github/workflows/macos_packaging_probe.yml`) is **not triggered on every push to `master`**. Rationale:

- GitHub-hosted macOS runners are billed at approximately 10× the Linux runner rate.
- A full macOS build job on every commit to `master` would generate significant unnecessary cost during the Windows-primary alpha phase.
- The existing `build.yml` handles smoke-testing on `master`; the probe workflow is a dedicated packaging and notarization gate.

The `release/**` trigger ensures the probe runs automatically when a release branch is cut, which is the natural checkpoint for macOS artifact readiness.

---

## 6. Runner Options Analysis

### Option A: GitHub-Hosted `macos-latest`

| Factor | Assessment |
|---|---|
| **Latency** | Queuing adds several minutes; no persistent disk cache across runs |
| **Reliability** | High; GitHub-managed with SLA |
| **Environment control** | Limited; Xcode and macOS versions change with image updates |
| **Certificate handling** | Must import `.p12` into an ephemeral keychain each job; destroyed automatically after the run |
| **Cost** | ~10× Linux rate; expensive at high frequency |
| **Maintenance burden** | None; no hardware to manage |

**Best for:** CI probe, infrequent release packaging, teams without macOS hardware.

### Option B: Self-Hosted Mac Mini

| Factor | Assessment |
|---|---|
| **Latency** | Near-zero queue; persistent build cache between runs |
| **Reliability** | Depends on local uptime and network; no GitHub SLA |
| **Environment control** | Full; pin Xcode version, manage keychain centrally |
| **Certificate handling** | Certificate can be pre-installed in a persistent keychain; avoids repeated import per job |
| **Cost** | Hardware CAPEX; no per-minute runner billing |
| **Maintenance burden** | High; runner agent, macOS updates, Xcode management |

**Best for:** High-frequency builds, production release pipelines, teams with macOS hardware already available.

### Recommendation

Use GitHub-hosted `macos-latest` for the probe and early release gating. Revisit self-hosted when macOS release frequency justifies the hardware investment.

---

## 7. Gatekeeper — Manual Bypass for Pre-Notarization Testers

If alpha testers receive a build that is signed but not yet notarized, Gatekeeper will block it with:

> **"Access_Paralegal_Multitool" cannot be opened because it is from an unidentified developer.**

One-time bypass procedure (macOS):
1. Double-click the DMG and drag `Access_Paralegal_Multitool` to `/Applications`.
2. Open `/Applications` in **Finder** (not Launchpad or terminal).
3. Right-click (or Control-click) → **Open**.
4. A dialog appears with an **Open** button. Click it.
5. macOS stores the exception; subsequent launches proceed normally.

This bypass is only for developer testing. Distribute only notarized + stapled builds to end users.

---

## 8. Operator Quick-Start: Reading CI Logs

### How to tell which mode is active

Every probe workflow run begins with a **Secrets Dry-Run Check** step that logs the pipeline mode without using any secret values:

**Probe mode (secrets missing):**
```
⚠️  One or more macOS signing secrets are missing.
   Pipeline running in UNSIGNED PROBE MODE — build and DMG only.
   To activate signing/notarization, follow:
   docs/ops/macos_secrets_activation_checklist.md
```

**Activated mode (all secrets present):**
```
✅ All macOS signing secrets present — pipeline will run in ACTIVATED mode.
   Signing and notarization steps will execute after the build.
```

The build script itself also logs mode at startup:
```
[mode] UNSIGNED PROBE — no credentials provided; producing unsigned DMG.
[mode] ACTIVATED — signing and notarization enabled.
```

### What to do if activation is intended but secrets are missing

1. Go to GitHub → Settings → Secrets and variables → Actions.
2. Check which of the 5 required secrets are present. The dry-run check step logs `present: true/false` for each.
3. Follow `docs/ops/macos_secrets_activation_checklist.md` to provision any that are missing.
4. Re-run the workflow (Actions → macOS Packaging Probe → Run workflow).

### What to do if a signing or notarization step fails

1. Expand the failing step in the GitHub Actions log.
2. Common causes:
   - **Keychain import error:** The `.p12` password (`APPLE_DEV_ID_CERT_PASSWORD`) does not match the one used when exporting. Re-export and update both secrets.
   - **notarytool authentication error:** The app-specific password is wrong or expired. Regenerate at appleid.apple.com and update `APPLE_APP_SPECIFIC_PASSWORD`.
   - **Notarization rejection:** Check the submission log URL printed by `notarytool`. Common causes: unsigned inner libraries, missing Hardened Runtime, quarantined attributes on bundled files.
3. Download the build log artifact for full details.

---

## 9. Status

| Item | Status |
|---|---|
| `build_app.sh` scaffold | ✅ Exists; hook markers added |
| Signing/notarization hooks | ✅ `SIGNING_HOOK_START/END`, `NOTARIZATION_HOOK_START/END` present |
| Partial-credential detection | ✅ Fails loudly rather than silently degrading |
| Secrets dry-run check in CI | ✅ Implemented (Phase 1 of probe workflow) |
| Unsigned build in CI | ✅ Active (probe mode) |
| Developer ID certificate | ❌ Not provisioned |
| Keychain import in CI | ⏳ Guarded step — activates when `APPLE_DEV_ID_CERT` is present |
| Codesigning in CI | ⏳ Guarded step — activates when `APPLE_DEV_ID_CERT` + `APPLE_TEAM_ID` present |
| Notarization in CI | ⏳ Guarded step — activates when all 4 notarization secrets present |
| Stapling in CI | ⏳ Guarded step — activates with notarization |
| Qt entrypoint in build_app.sh | ✅ Fixed — targets `gui_apmultitool_qt.py` (ho_0046) |
| macOS support declared | ❌ Not claimed — Windows alpha is the active release track |
