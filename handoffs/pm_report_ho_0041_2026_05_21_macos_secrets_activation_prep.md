---
handoff_id: pm_report_ho_0041_2026_05_21
date: 2026-05-21
title: PM Report — macOS Secrets Activation Prep Lane
project: APMultitool
status: completed
type: pm_report
lane: macos-secrets-activation-prep
tags:
  - macos
  - packaging
  - signing
  - ci
  - secrets
---

# PM Report — macOS Secrets Activation Prep Lane (ho_0041)

## Executive Summary

This lane hardened the macOS packaging pipeline so that an operator with Apple Developer credentials can flip from unsigned probe to fully signed/notarized builds by adding five GitHub Actions secrets — with no code changes required. The pipeline now self-describes its mode in every CI run, fails loudly on partial credentials rather than silently degrading, and provides a complete operator checklist for provisioning, validating, and rotating secrets.

No secrets were committed. macOS remains a probe/preparation platform. Windows alpha is the active release track.

---

## Task Status

| # | Task | Status | Notes |
|---|---|---|---|
| 1 | Confirm current CI and packaging posture | ✅ Completed | Summarized below in §4 |
| 2 | Draft operator-facing secrets activation checklist | ✅ Completed | New file: `docs/ops/macos_secrets_activation_checklist.md` |
| 3 | Add secrets dry-run validation step in CI | ✅ Completed | Phase 1 of updated `macos_packaging_probe.yml` |
| 4 | Refine `build_app.sh` with signing/notarization hooks | ✅ Completed | Hook markers + partial-credential detection + loud failure |
| 5 | Align ops docs with probe vs activated states | ✅ Completed | Both overview and signing requirements updated |
| 6 | Optional local dry-run | ⏭️ Deferred | No macOS host available in this environment |
| 7 | CI validation and operator quick-start | ✅ Completed | Quick-start section added to `macos_packaging_overview.md` §8 |

---

## Files Changed

### Created

| File | Description |
|---|---|
| `docs/ops/macos_secrets_activation_checklist.md` | Step-by-step operator guide: Apple asset requirements, CI secret naming, provisioning steps, validation, rotation/revocation |
| `handoffs/pm_report_ho_0041_2026_05_21_macos_secrets_activation_prep.md` | This report |

### Modified

| File | Changes |
|---|---|
| `.github/workflows/macos_packaging_probe.yml` | Added Phase 1 secrets dry-run check; exposes `MACOS_SIGNING_ACTIVE` env var; improved header comments distinguishing probe vs activated mode |
| `packaging/macos/build_app.sh` | Added `SIGNING_HOOK_START/END` and `NOTARIZATION_HOOK_START/END` markers; added credential pre-flight that fails loudly on partial notarization params; pipeline mode log at startup; no credential values printed |
| `docs/ops/macos_packaging_overview.md` | Added Pipeline Modes table (probe / signing-only / activated); updated §1 to reference hook markers; added §8 Operator Quick-Start (reading logs, diagnosing failures); renamed old §8 Status to §9; updated status table |
| `docs/ops/macos_signing_requirements.md` | Added cross-reference to activation checklist; clarified that no private keys/certs are committed |

---

## Current CI Posture (Task 1 Summary)

**Workflow:** `.github/workflows/macos_packaging_probe.yml`
- **Triggers:** `workflow_dispatch` + push to `release/**`
- **Phase 1 (NEW):** Secrets dry-run check — logs `present: true/false` for each of the 5 secrets; sets `MACOS_SIGNING_ACTIVE`; always passes
- **Phase 2–3 (ACTIVE):** Setup → unsigned build via `build_app.sh` → uploads `macos-dmg-unsigned` artifact
- **Phase 4–6 (GUARDED):** Cert import, codesign, notarytool, stapler — each behind `if: ${{ secrets.XXX != '' }}` guards; silently skip until secrets are configured

**Script:** `packaging/macos/build_app.sh`
- Full four-phase pipeline: build → codesign → DMG → notarize/staple
- Graceful degradation with explicit mode logging
- **New:** Partial credential detection (fails loudly with non-zero exit instead of silently skipping)
- **New:** `SIGNING_HOOK_START/END` and `NOTARIZATION_HOOK_START/END` markers for operator navigation

**Secrets referenced in workflow (none configured):**
- `APPLE_DEV_ID_CERT`
- `APPLE_DEV_ID_CERT_PASSWORD`
- `APPLE_TEAM_ID`
- `APPLE_APPLE_ID`
- `APPLE_APP_SPECIFIC_PASSWORD`

---

## Caveats and Remaining Manual Steps

### CI configuration

- The secrets dry-run check uses `${{ secrets.XXX != '' }}` expressions, which evaluate to `true`/`false` strings. These are safe — they do not expose secret values and work correctly on `workflow_dispatch` and `push` triggers.
- On pull requests from forks, secrets are not available; the dry-run step will log all secrets as `present: false` and the workflow will run in unsigned probe mode. This is the correct and safe behavior.

### Expected secrets naming

The canonical secret names used throughout the pipeline:

| Secret | Purpose |
|---|---|
| `APPLE_DEV_ID_CERT` | Base64-encoded `.p12` certificate bundle |
| `APPLE_DEV_ID_CERT_PASSWORD` | Password protecting the `.p12` |
| `APPLE_TEAM_ID` | 10-character Apple Team ID |
| `APPLE_APPLE_ID` | Apple Developer account email |
| `APPLE_APP_SPECIFIC_PASSWORD` | App-specific password for notarytool |

These names are consistent across `macos_packaging_probe.yml`, `macos_signing_requirements.md`, and `macos_secrets_activation_checklist.md`.

### Remaining manual steps for operators

1. **Apple Developer Program enrollment** — Must be done by a business/legal owner. Cannot be automated.
2. **Developer ID Application certificate** — Must be created from a macOS workstation with Keychain Access. Follow `docs/ops/macos_secrets_activation_checklist.md` §2A.
3. **App-specific password** — Must be generated at appleid.apple.com by the account holder. Follow §2C.
4. **Add secrets to GitHub** — Repository admin role required. Follow §3.
5. **Trigger and validate** — Run the probe workflow manually and confirm all 6 validation checkboxes in §4.
6. **Update `build_app.sh` entry point** — Still targets legacy `gui_apmultitool.py`. Must be updated to `gui_apmultitool_qt.py` before a production macOS release (Engineering scope, separate lane).

---

## Confirmations

- ✅ No secrets, private keys, certificates, or `.p12` files were committed to the repository.
- ✅ macOS remains "probe / preparation" from a support standpoint. No macOS support is claimed.
- ✅ Windows alpha behavior was not modified.
- ✅ Vault, encryption, and hardware identity logic were not touched.
- ✅ Engine/UI boundary maintained throughout.
