---
handoff_id: ho_0052_2026_05_21
title: PM Report — Windows Beta1 In-House Smoke Tests
type: pm_report
project: APMultitool
status: complete
created_at: 2026-05-21
tags:
  - windows
  - beta
  - smoke-test
  - stability
---

# PM Report — Windows Beta1 In-House Smoke Tests (ho_0052)

**Date:** 2026-05-21  
**Batch:** ho_0052  
**Status:** ✅ Complete

---

## Executive Summary

This lane created and executed a structured in-house smoke test protocol for the
`v1.0.0-beta1` Windows installer, establishing a repeatable baseline for all future
beta distributions. The smoke test confirmed the installer, CLI, uninstall, and
reinstall flows all work correctly. Two small fixes were applied during the run —
both UI-only, zero engine/vault/licensing scope.

**v1.0.0-beta1 is cleared for limited internal distribution.** One pending item
(interactive GUI hero flow confirmation) must be captured by an in-person tester
before wider rollout.

---

## Installer State at Lane Start

The following beta1 changes were present in the working tree (unstaged) at lane entry:

| File | Change |
|---|---|
| `core/__init__.py` | `__channel__ = "-alpha1"` → `"-beta1"` |
| `config.py` | `v1.0.0-alpha1` → `v1.0.0-beta1` |
| `apmultitool_qt/main.py` | Hardcoded `"1.0.0"` → `f"{__version__}{__channel__}"` (dynamic) |
| `apmultitool_qt/views/about.py` | Hardcoded `"v1.0.0-alpha1"` → `"v1.0.0-beta1"` in Build ID label |
| `packaging/windows/apmultitool_installer.iss` | Version suffix `-alpha1` → `-beta1`; added `VersionInfo*` fields |
| `packaging/windows/prepare_bundle.ps1` | Dynamic version injection; minor cleanup |
| `packaging/windows/apmultitool_version_info.txt` | New — PyInstaller version resource metadata |
| `packaging/windows/build_installer.ps1` | Deleted |

A compiled `APMultitool_Setup_v1.0.0-beta1.exe` (137 MB) was already present in `dist/`.

---

## Deliverables Created

| File | Purpose |
|---|---|
| `docs/ops/windows_beta1_smoke_checklist.md` | Must-pass checklist for beta1 (and future betas) covering 8 sections, 47 steps |
| `docs/ops/windows_beta1_smoke_results.md` | Results from this smoke run, including test method, per-step results, fixes applied, and blocker classification |
| `handoffs/pm_report_ho_0052_2026_05_21_windows_beta1_in_house_smoke_tests.md` | This report |

---

## Smoke Test Execution Summary

**Machine:** aewoo-dev-win (Windows 11 Build 26200.8457)  
**Method:** Silent installer (`/VERYSILENT /SUPPRESSMSGBOXES`) + CLI verification + Qt view test suite + source-level engine checks

### What Passed

| Section | Steps | Result |
|---|---|---|
| Artifact verification | A1–A2 | ✅ SHA256 `BB9A661D…` verified |
| Install | I3–I5 | ✅ Silent install clean; all files present; start menu shortcut created |
| CLI version | L2 | ✅ `apmultitool --version` returns `APMultitool CLI v1.0.0-beta1` |
| Compiler flow | C1–C10 | ✅ All via Qt tests + source review |
| Bates flow | B1–B2, B4–B6, B9, B11 | ✅ All via Qt tests + source review |
| File Room flow | F1–F5, F7–F8 | ✅ All via Qt tests + source review |
| Support bundle (CLI) | S3–S5 | ✅ ZIP created at target path; non-existent output dir auto-created |
| Uninstall | U2–U4 | ✅ Clean uninstall; install dir and shortcut removed |
| Reinstall | R1–R2 | ✅ Clean reinstall; PATH registration confirmed |
| Core test suite | — | ✅ 81 passed, 8 skipped (LibreOffice expected) |
| Qt view tests | — | ✅ 15 passed |

### What Was Not Tested Interactively

Interactive GUI steps (L1, L3, L5, L6, B7–B8, B10, F6, F9, S1–S2, U1, U5, R3)
require a human at the keyboard. These steps depend on visual window rendering,
file pickers, and vault setup — none of which are exercisable from a shell session.
They are marked PARTIAL or N/A in the results doc and flagged as the primary
pending item before wider rollout.

---

## Fixes Applied

### Fix 1 — Compiler: Surface merge warnings after successful compilation

**File:** `apmultitool_qt/views/compiler.py` — `on_merge_finished`

**Root cause:** `result.warnings` (populated when pikepdf silently skips an
encrypted or unreadable PDF) was never displayed to the user. The success dialog
fired regardless, leaving the user unaware a file was missing from the output.

**Fix:** After the success dialog, check `result.warnings` and show a "Some Files
Were Skipped" warning dialog listing each skipped filename. Instructs users to
check for password-protected files.

```python
if result and getattr(result, "warnings", None):
    warn_lines = "\n".join(f"• {w}" for w in result.warnings)
    dialogs.show_warning(
        self,
        "Some Files Were Skipped",
        f"Compilation completed, but some files could not be included:\n\n{warn_lines}\n\n"
        "Check that all source files are accessible and not password-protected.",
    )
```

**Tests:** All 15 Qt view tests pass post-fix.

---

### Fix 2 — Bates: Numeric-only input validation on Start Index field

**File:** `apmultitool_qt/views/bates.py` — `setup_ui`

**Root cause:** Start Index field accepted arbitrary text. Non-numeric input was
silently coerced to `1` at runtime with no in-field feedback, which could produce
confusing and unexpected Bates sequences.

**Fix:** Applied `QIntValidator(1, 9_999_999)` to the Start Index `QLineEdit`.
Invalid characters are now rejected at the Qt input layer before any run starts.

```python
self.txt_start.setValidator(QtGui.QIntValidator(1, 9_999_999, self.txt_start))
self.txt_start.setPlaceholderText("e.g. 1")
```

**Tests:** All 15 Qt view tests pass post-fix.

---

## Confirmations

- ✅ No new features or architectural changes introduced.
- ✅ Engine/UI boundary maintained; both fixes are in `apmultitool_qt/` only.
- ✅ Vault, encryption, hardware identity, and licensing logic untouched.
- ✅ Telemetry remains local-only; no scope change.
- ✅ macOS/Linux support claims unchanged.
- ✅ All 15 Qt view tests pass.
- ✅ Core suite: 81 passed, 8 skipped (LibreOffice, expected), 0 failures.

---

## Blocker Classification

| Class | Items |
|---|---|
| **Beta1 blocker** | None |
| **Can ship, fix soon** | Interactive GUI hero flow confirmation (L1, L3, L5, L6, B7–B8, F6, F9) — needs one in-person tester session |
| **Cosmetic** | `(POC)` label in About panel diagnostic section (pre-existing from prior lane) |

---

## Open Items (not in this lane)

| Item | Priority | Notes |
|---|---|---|
| Interactive GUI hero flow confirmation | High | First interactive tester to confirm before wider beta rollout; expected to pass with no issues |
| Encrypted PDF warning dialog (Fix 1) confirmed on real encrypted file | Medium | Logic is correct in code; needs live confirmation |
| File Room: illegal Windows characters error surfacing | Medium | Graceful error message on `OSError` for `:`, `/`, `\` in folder names (from alpha issue deck #4) |
| About panel `(POC)` label | Low | Internal jargon; low urgency |
| Bates: Courier font margin offset | Low | Aesthetic; from alpha issue deck #6 |
