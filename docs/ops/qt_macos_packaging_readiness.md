---
id: qt_macos_packaging_readiness
title: macOS Packaging Readiness
type: ops-audit
updated: 2026-05-21
---

# macOS Packaging & Notarization Readiness

## Current Status

macOS packaging is **PROBE / PREPARATION** — build scripts exist and the CI workflow is wired up, but no live DMG has been produced on verified bare-metal macOS hardware yet.

- Build script: `packaging/macos/build_app.sh` — entry point is `gui_apmultitool_qt.py` (Qt edition)
- CI workflow: `.github/workflows/macos_packaging_probe.yml` — runs unsigned probe on `workflow_dispatch` / `release/**` push
- Signing/notarization: guarded steps wired in; inactive until 5 GitHub Actions secrets are provisioned (see `docs/ops/macos_secrets_activation_checklist.md`)

## Deployment Assumptions

- **Framework Compatibility:** PySide6 natively supports macOS (Intel and Apple Silicon). The core `EngineJobWorker` and `QThread` paradigms operate identically across platforms.
- **Path Restrictions:** macOS enforces App Sandbox constraints. If APMultitool writes Vault licensing data to system directories rather than `~/Library/Application Support/`, it will fail. This is currently untested on bare metal.
- **Packaging Format:** Target artifact is an `.app` bundle nested in a `.dmg`. Both are produced by `build_app.sh`.

## Pipeline State

| Step | Status |
|---|---|
| `build_app.sh` scaffold | ✅ Exists — targets `gui_apmultitool_qt.py` |
| Signing/notarization hooks | ✅ `SIGNING_HOOK_START/END`, `NOTARIZATION_HOOK_START/END` present |
| CI probe workflow | ✅ Active — unsigned probe on dispatch / release branches |
| Bare-metal local dry-run | ❌ Not yet performed — no macOS host in the development environment |
| Apple Developer credentials | ❌ Not provisioned |
| End-to-end notarized DMG | ❌ Not yet produced |

## Required Implementation Steps (Remaining)

1. **Run local unsigned build on real macOS hardware** — produce and inspect `.app` + `.dmg`.
2. **Validate vault/licensing path behavior** — confirm `~/Library/Application Support/` writes work under macOS sandbox constraints.
3. **Codesigning:** Execute `codesign` using a Developer ID Application certificate (see `docs/ops/macos_signing_requirements.md`).
4. **Notarization:** Run `xcrun notarytool` to submit the DMG to Apple's notary service. Unnotarized apps are blocked by Gatekeeper on modern macOS.

## Verdict

Do not advertise macOS support until an unsigned build has been produced and validated on bare-metal macOS hardware, and until notarization has been completed end-to-end. See `docs/ops/macos_packaging_overview.md` for the full pipeline reference.
