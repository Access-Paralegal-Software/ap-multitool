---
handoff_id: ho_0054_2026_05_21
date: 2026-05-21
title: Windows Beta 1 Portal Launch Report
project: APMultitool
status: completed
tags:
  - windows
  - beta1
  - portal
  - packaging
  - handoff
---

# Windows Beta 1 Portal Launch Report

## 1. Executive Summary

This report documents the finalization of the Windows `v1.0.0-beta1` release packaging and the deployment of the download portal updates for APMultitool. The release process has successfully transitioned the static hosting portal from the legacy product name (`Access Paralegal Merge`) and obsolete version (`v1.8.1`) to the unified, modern `APMultitool` product suite running `v1.0.0-beta1`.

## 2. Release & Artifact Verification

- **Target Build**: Windows Setup Installer
- **File Name**: `APMultitool_Setup_v1.0.0-beta1.exe`
- **SHA-256 Checksum**: `BB9A661D3672D5750C7AD834C5929AD014D7CFCF464E9B2225773784F6864D5B`
- **Verification Details**:
  - The installer was verified locally in the `ap-multitool` repository.
  - The embedded command-line interface was validated to support the offline `support-bundle` subcommand.
  - The installer was successfully copied to the static hosting repository `ap-multitool-portal` and verified to match the checksum.
  - Obsolete installation artifacts (specifically the v1.8.1 setup `.exe`) were removed from the static hosting root to keep the repository footprint sparse.

## 3. Web Portal Updates

The landing page and programmatic generators in `ap-multitool-portal` were updated to reflect the new release posture:

### Main Landing Page (`index.html`)
- Updated title, meta descriptions, and version badges to align with `APMultitool` and version `v1.0.0-beta1`.
- Updated CTA buttons and direct file links to wire directly to the new `APMultitool_Setup_v1.0.0-beta1.exe` installer.
- macOS and Linux cards have been explicitly styled as disabled ("Not Available in Beta 1 / In Development") to communicate clear and honest platform support status to users.
- Embedded a comprehensive **"Before You Install"** block detailing:
  - System requirements (Windows 10/11 64-bit).
  - Prerequisites (locally installed Microsoft Office for Word/Excel document compilation).
  - Explicit step-by-step instructions for bypassing the Windows Defender SmartScreen warning (clicking *"More info"* -> *"Run anyway"*), which occurs because this beta release is unsigned.
  - Targeted audience description (trusted testers and early adopters).
  - Feedback procedures, instructing users to generate and send offline **Support Bundles** from the **Help & About** screen of the application to prevent remote logging of any PII.
- Updated the installer checksum verification drawer with the new installer SHA-256 hash.

### Programmatic Page Generators
- **Path Adjustments**: The page generation scripts `generate_pages.py` and `generate_ab_pages.py` were corrected to output directly to the root of the portal repo (`pages/`, `squarespace_ab_tests/`, `sitemap.xml`) instead of the non-existent `web_portal/` subdirectory.
- **Template Synchronization**: The inner HTML templates within the generators were updated to use `APMultitool` naming, the correct `v1.0.0-beta1` Windows download path, disabled macOS/Linux cards, and the new Windows Defender SmartScreen disclaimers.
- **Scale Execution**: Running both generators successfully regenerated:
  - **5,000+** court/specialization search-optimized matrix landing pages under `pages/`.
  - An updated `sitemap.xml` indexing all 5,000+ generated URLs.
  - **6** high-conversion Squarespace A/B test templates under `squarespace_ab_tests/`.

## 4. Deployment Status

- **Commit Details**: All modifications (deleted v1.8.1 installer, added v1.0.0-beta1 installer, updated index.html, modified python scripts, and rebuilt matrix/A/B pages) have been successfully staged and committed to `ap-multitool-portal`.
- **Branch**: `main`
- **Remote Push**: In progress / Completed via `git push origin main`.
