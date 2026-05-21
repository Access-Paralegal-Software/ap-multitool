---
id: release-notes-v1.0.0-beta1
title: Release Notes — v1.0.0-beta1 (Windows Beta)
type: operations
status: draft
project: APMultitool
created_at: 2026-05-21
tags:
  - release
  - beta
  - windows
---

# APMultitool Release Notes — v1.0.0-beta1 (Windows Beta)

**Version:** v1.0.0-beta1
**Release Date:** 2026-05-21
**Platform:** Windows 10 / 11 (64-bit)
**Installer:** `APMultitool_Setup_v1.0.0-beta1.exe`
**SHA256:** *(generated at build time — see release artifact)*
**Signature status:** Unsigned. Windows SmartScreen will display a warning on first launch. See "Before You Install" below.

---

## What APMultitool Does

APMultitool is a local document workbench for paralegals and legal support professionals. Every operation runs on your machine — no files, case data, or personal information leave your device.

**Current capabilities:**

- **Document Compiler** — Select and order PDF, Word, and Excel files; compile them into a single merged PDF in one click. Includes overwrite protection so you cannot accidentally replace an existing file.
- **Bates Stamping** — Apply Bates numbers to PDF production sets. Configure the prefix, starting number, padding, and font style. Long jobs can be cancelled mid-run without leaving partial output files behind.
- **File Room** — Create standardized legal matter folder structures from preconfigured blueprints. Preview the folder tree before building it.
- **CLI Companion** — All core operations are available from the command line via `apmultitool` for scripted or automated workflows.
- **Support Bundle** — Export a diagnostic ZIP file from the Help & About tab (or via `apmultitool support-bundle`) that includes logs and environment metadata. No case data or document contents are ever included.

---

## What Changed Since Alpha1

### 1. UI / Flow Polish

All primary action labels and panel headings have been revised for plain language and consistency. Examples:

| Location | Alpha1 Label | Beta1 Label |
|---|---|---|
| Document Compiler | "Combine & Merge Files" | "Compile Documents" |
| Document Compiler | Success message: "Document merge completed successfully!" | "Documents compiled successfully!" |
| Bates Stamping | "FLATTEN & APPLY BATES STAMPS" | "Apply Bates Numbers" |
| Bates Stamping | "ADVANCED STAMP OPTIONS" | "Stamp Options..." |
| Bates Stamping | "BATES OUTPUT TERMINAL" panel | "BATES STAMP LOG" |
| Bates Stamping | "CANCEL PRODUCTION" | "Cancel" |
| File Room | "Spin Up Folder Tree" | "Create Folder Structure" |
| File Room | "FOLDER TREE ARCHITECTURE PREVIEW" | "FOLDER STRUCTURE PREVIEW" |
| Activation dialog | "Enterprise Security requires hardware lock." | "A license key is required to activate APMultitool." |

The "Confirm Merge Order" dialog that appeared before every Document Compiler run has been removed. It was friction without protective value — the overwrite protection dialog is still in place for all cases where the output file already exists.

### 2. Stability Improvements

- **Bates Stamping:** Added a guard against malformed or empty engine results in the post-run handler. Previously, an edge-case engine failure could raise an unhandled exception in the UI thread. Now shows a clear error dialog instead.
- **File Room:** Added a result guard before attempting to open the created folder in Explorer. Prevents a silent failure when the engine returns an unexpected empty result.
- **Bates matter ledger lookup:** Wrapped the cross-view widget access in a `try/except` to prevent a crash if the widget hierarchy is in an unexpected state at job completion.

### 3. Diagnostics and Support

Support bundles are now prominently documented and reliably available through both the GUI and CLI. The bundle contents are scrubbed — no absolute user paths or system usernames are included in exported logs.

Support bundle export path: Help & About tab → "Export Support Bundle..." or `apmultitool support-bundle` in any terminal.

### 4. Document Conversion Architecture (Internal)

An abstraction layer was introduced between the document conversion operations (Word/Excel to PDF) and the underlying conversion backend. This separates the engine from COM automation details and lays the groundwork for a LibreOffice fallback in a future release. The fallback is not enabled in this build — Word/Excel conversion still requires Microsoft Office installed locally.

### 5. Installer and Packaging Maturity

The Inno Setup installer structure continues to improve:
- Clean uninstallation removes all installed files and registry PATH entries without leaving orphaned data.
- User-space installation (no administrator privileges required by default).
- Silent deployment switches (`/SILENT`, `/VERYSILENT /SUPPRESSMSGBOXES`) remain supported.

---

## Known Limitations

- **Windows only.** macOS and Linux builds are not available in this release.
- **Beta status.** This release is stable enough for everyday use, but you may encounter rough edges. Please report issues — your feedback helps.
- **Unsigned installer.** The installer is not yet code-signed. Windows SmartScreen will block it on first launch. See "Before You Install" below for the bypass steps.
- **Word/Excel to PDF requires Microsoft Office.** If you compile a Word or Excel file and Microsoft Office is not installed, that file will be skipped or fail with a clear error. A LibreOffice fallback is in development but not yet enabled.
- **CLI PATH refresh.** If you select "Add to PATH" during installation, open a new terminal window before running `apmultitool`. Existing terminal sessions will not see the updated PATH.
- **Multi-user machines.** PATH adjustments apply only to the current user's profile (HKCU). Other users on the same machine must install separately if they want CLI access.

---

## Before You Install

1. Download `APMultitool_Setup_v1.0.0-beta1.exe`.
2. *(Optional)* Verify the SHA256 checksum matches the value listed in the release artifact before running.
3. Run the installer. When Windows SmartScreen blocks it:
   - Click **"More info"**
   - Click **"Run anyway"**
4. Follow the setup wizard. The default install location is `%LocalAppData%\Programs\APMultitool` — no administrator rights required.
5. If you choose "Add APMultitool to local environment PATH," open a new terminal window after installation for the `apmultitool` CLI command to be recognized.

---

## Reporting Issues

Export a support bundle from Help & About or run `apmultitool support-bundle` and send the resulting ZIP to your operator contact. The bundle contains application logs and system environment metadata. It does not contain any case files, document contents, or identifying user data.

---

## Version Bump Prerequisites (Pre-Build Checklist)

Before cutting the beta1 installer, the following files must be updated:

| File | Field | Current Value | Required Value |
|---|---|---|---|
| `core/__init__.py` | `__channel__` | `"-alpha1"` | `"-beta1"` |
| `packaging/windows/apmultitool_installer.iss` | `AppVersionSuffix` | `"-alpha1"` | `"-beta1"` |
