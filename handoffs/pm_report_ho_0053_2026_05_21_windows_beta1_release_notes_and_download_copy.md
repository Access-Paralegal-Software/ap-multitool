---
handoff_id: pm_report_ho_0053_2026_05_21
date: 2026-05-21
title: PM Report — Windows Beta1 Release Notes & Public Download Copy Lane
project: APMultitool
status: completed
type: pm_report
lane: windows-beta1-release-notes-and-download-copy
tags:
  - windows
  - beta1
  - release-notes
  - download-page
  - copy
---

# PM Report — Windows Beta1 Release Notes & Public Download Copy Lane (ho_0053)

## Executive Summary

This lane produced a complete set of public-facing and internal release materials for the Windows `v1.0.0-beta1` release: release notes, download-page copy, and an announcement brief. All three documents are written to the actual product state — no over-claims on platform support, signing status, or feature maturity. Beta posture is clearly communicated throughout.

Two pre-build gaps were identified during the naming/version consistency check: `core/__init__.py` and `packaging/windows/apmultitool_installer.iss` still reference `-alpha1` and must be updated before the beta1 installer can be compiled. These are documented in the release notes as a pre-build checklist.

---

## Documents Created

| File | Description |
|---|---|
| `docs/ops/release_notes_v1.0.0-beta1.md` | Full release notes: product summary, alpha1→beta1 changelog, known limitations, before-you-install steps, reporting guide, pre-build version-bump checklist |
| `docs/ops/windows_beta1_download_page_copy.md` | Public download page copy: headline, subhead, capability bullets, Before You Install section (SmartScreen, Office dependency), download block, page-editor notes |
| `docs/ops/windows_beta1_announcement_brief.md` | Internal/send-ready announcement brief: what beta1 is, who it is for, what is new, where to download, how to report issues, what beta1 is not |
| `handoffs/pm_report_ho_0053_2026_05_21_windows_beta1_release_notes_and_download_copy.md` | This report |

---

## Naming and Version Consistency Check

### Verified consistent across all new materials

| Element | Value used |
|---|---|
| Product name | APMultitool |
| Publisher | Access Paralegal Systems |
| Version string | `v1.0.0-beta1` |
| Installer filename | `APMultitool_Setup_v1.0.0-beta1.exe` |
| Install path | `%LocalAppData%\Programs\APMultitool` |
| Support URL | `https://accessparalegal.com` |
| GUI exe name | `Access_Paralegal_Multitool.exe` |
| CLI command | `apmultitool` |

### Known mismatches requiring action before beta1 build

| File | Field | Current Value | Required for Beta1 | Priority |
|---|---|---|---|---|
| `core/__init__.py` | `__channel__` | `"-alpha1"` | `"-beta1"` | **Build blocker** — version string displayed in app title bar and About view |
| `packaging/windows/apmultitool_installer.iss` | `AppVersionSuffix` | `"-alpha1"` | `"-beta1"` | **Build blocker** — controls installer filename and wizard branding |

These are not fixed in this lane — they are engineering pre-build steps outside the copy/documentation scope. They are documented in `docs/ops/release_notes_v1.0.0-beta1.md` under "Version Bump Prerequisites."

### Documented mismatch (out of lane scope)

`README.md` references `gui_apmultitool.py` (the abandoned CustomTkinter entry point) and contains stale file paths pointing to an older machine. This does not affect the beta1 release materials but should be addressed before public launch. Noted here for engineering follow-up.

---

## Platform Claim Review

All three documents were reviewed for platform over-claims:

- **Release notes:** "Windows 10 / 11 (64-bit)" stated explicitly; macOS and Linux described as "not available in this release."
- **Download page copy:** "Windows 10 or 11 (64-bit) required" in Before You Install; macOS/Linux download not referenced.
- **Announcement brief:** "This is a Windows-only release. macOS and Linux are not available in this build." stated explicitly in its own paragraph.
- **No unsupported SmartScreen claims introduced.** All three documents accurately describe the SmartScreen situation: unsigned installer, expected warning, bypass steps (More info → Run anyway). No language implies the bypass is a security risk or that the app is permanently unsigned.

---

## Beta Posture Review

All three documents communicate beta posture clearly and consistently:

- Release notes: "Beta status — This release is stable enough for everyday use, but you may encounter rough edges."
- Download page: "This is a beta release. It is stable for regular use, but you may run into rough edges."
- Announcement brief: Dedicated "What Beta1 Is Not" section; "Beta means: the core functionality is working and tested, but you may encounter rough edges."

No document uses the words "production," "final," "v1.0," or "stable release" to describe beta1.

---

## Content Sourcing Notes

All capability descriptions and known limitations were derived from:
- `docs/ops/release_notes_v1.0.0-alpha1.md` (baseline product state and alpha1 changelog)
- `docs/ops/alpha_operator_brief_v1.0.0-alpha1.md` (support bundle documentation and troubleshooting)
- `packaging/windows/apmultitool_installer.iss` (naming, publisher, install path)
- `core/__init__.py` (version string)
- `docs/ops/windows_smartscreen_alpha_notes.md` (SmartScreen bypass steps)
- `docs/ops/doc_conversion_fallback_design.md` (LibreOffice fallback architecture status)

The LibreOffice fallback is described accurately in the release notes as "not enabled in this build" — not as a user-facing feature.

---

## Confirmations

- ✅ Platform claims are accurate: Windows beta, not macOS or Linux.
- ✅ Beta posture is clearly communicated across all three documents.
- ✅ No unsupported SmartScreen claims were introduced. The SmartScreen bypass instructions are factually accurate and unchanged from alpha1 guidance.
- ✅ Publisher name, version string, installer filename, and install path are consistent across all materials.
- ✅ Two pre-build version-bump gaps documented (`core/__init__.py`, `apmultitool_installer.iss`) — not blocking the copy docs, but blocking the actual installer build.
- ✅ Windows alpha behavior, vault/encryption, and hardware identity logic were not touched.
- ✅ No secrets committed.
