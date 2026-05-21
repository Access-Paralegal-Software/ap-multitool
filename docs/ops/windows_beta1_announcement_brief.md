---
id: windows-beta1-announcement-brief
title: Windows Beta1 Announcement Brief
type: ops-copy
status: draft
project: APMultitool
created_at: 2026-05-21
audience: internal / announcement
---

# APMultitool v1.0.0-beta1 — Announcement Brief

*Compact internal send or post-ready summary. Use as-is or as the basis for a first-contact email to the beta cohort.*

---

## What Is Beta1

APMultitool v1.0.0-beta1 is the first public beta release of the Access Paralegal document workbench for Windows. It supersedes the v1.0.0-alpha1 test build and includes meaningful UI and stability improvements based on alpha cohort feedback.

Beta means: the core functionality is working and tested, but you may encounter rough edges. That is expected and wanted at this stage — your feedback directly shapes what gets fixed before the 1.0 release.

---

## Who It Is For

Paralegals, legal assistants, and legal support professionals who regularly work with:

- PDF production sets (compilation, Bates numbering)
- Matter intake (building standardized folder structures)
- Word or Excel files that need to land in a PDF

This is a Windows-only release. macOS and Linux are not available in this build.

---

## What Is New Since Alpha1

- **Cleaner interface.** Button labels and panel text throughout the app have been revised for plain language. No more jargon.
- **Smoother workflows.** The unnecessary "Confirm Merge Order" dialog has been removed from the Document Compiler. The overwrite protection is still there — the extra click before every run is gone.
- **More stable edge-case handling.** Guards were added to the Bates Stamping and File Room tools to prevent unexpected crashes on malformed input.
- **Better diagnostics.** The support bundle tool is reliably available from both the GUI and the command line.

---

## Where to Download

Download: **`APMultitool_Setup_v1.0.0-beta1.exe`** from [accessparalegal.com](https://accessparalegal.com)

*(Replace with the versioned direct download link before sending.)*

**First-time install note:** Windows will show a security warning because the installer is not yet code-signed. Click "More info," then "Run anyway" to proceed. This is expected and safe.

---

## How to Report Issues

1. In the app, go to **Help & About** and click **Export Support Bundle**.
2. Or, from any terminal, run: `apmultitool support-bundle`
3. Send the ZIP file to your operator contact.

The support bundle includes application logs and system environment details. It does not include any case files, document contents, or personal data.

Alternatively, report directly via the issue tracker if you have access to the repository.

---

## What Beta1 Is Not

- Not a production release. Version 1.0 stable is the goal after beta feedback is addressed.
- Not cross-platform yet. Windows only at this time.
- Not code-signed yet. The SmartScreen bypass step is still required.
