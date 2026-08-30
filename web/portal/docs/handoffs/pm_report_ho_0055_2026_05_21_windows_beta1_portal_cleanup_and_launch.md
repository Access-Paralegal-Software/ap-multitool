---
handoff_id: ho_0055_2026_05_21
date: 2026-05-21
title: Windows Beta1 Portal Cleanup & Live Launch PM Report
project: APMultitool Portal
status: completed
tags:
  - windows
  - beta1
  - portal
  - landing-page
  - release
---

# Project Manager Report: Windows Beta1 Portal Cleanup & Live Launch

This report documents the resolution of the blocked static portal push due to git hosting limits, the relocation of the 131MB Windows installer binary to a proper hosting location, template and script updates, sitemap and page regeneration, and final push.

## Repo State Before Fix
* **Branch name:** `main`
* **Last commit hash (before cleanup):** `d01cdc1` (Summary: `feat: windows beta1 landing page and download wiring`)
* **Push Block Confirmation:** The commit `d01cdc1` contained the 131MB native installer binary (`APMultitool_Setup_v1.0.0-beta1.exe`), which exceeded GitHub's strict 100MB file limit and caused git push rejections.

## Installer Handling & Relocation
* **Removal from Repo:** 
  - Ran `git reset HEAD~1` to remove the large binary from tracking history.
  - Deleted `APMultitool_Setup_v1.0.0-beta1.exe` from the portal repository root.
  - Created a `.gitignore` containing `*.exe` to prevent accidental commits of binaries in the future.
* **New Hosting Location:** 
  - Created a GitHub Release tagged as `v1.0.0-beta1` in the product repository `woodyardae/ap-multitool`.
  - Uploaded the installer binary (`APMultitool_Setup_v1.0.0-beta1.exe`) and its SHA-256 checksum (`APMultitool_Setup_v1.0.0-beta1.exe.sha256`) as release assets.
* **Final Public Download URL:** 
  - `https://github.com/woodyardae/ap-multitool/releases/download/v1.0.0-beta1/APMultitool_Setup_v1.0.0-beta1.exe`
* **SHA-256 Checksum:** `BB9A661D3672D5750C7AD834C5929AD014D7CFCF464E9B2225773784F6864D5B`

## Portal Updates
* **Template & Landing Page Files Modified:**
  - Modified [index.html](file:///c:/Users/aewoo/Desktop/Repos/ap-multitool-portal/index.html) to repoint the Windows download button to the hosted release URL.
  - Modified [generate_pages.py](file:///c:/Users/aewoo/Desktop/Repos/ap-multitool-portal/generate_pages.py) template to point the Windows download card to the hosted release URL.
* **Rebuild & Synthesis:**
  - Re-ran `python generate_pages.py` to regenerate all 5,000 localized SEO landing pages.
  - Re-ran `python generate_ab_pages.py` to regenerate the 6 A/B test variations.
  - Generated an updated XML sitemap containing all 5,000 page URLs.
* **Beta Labeling & Warning Posture (Preserved):**
  - The main landing page and all 5,000+ generated pages explicitly present the Windows-only beta status.
  - Explicit warning copy regarding Windows Defender SmartScreen ("Windows protected your PC") is prominently displayed with instructions to click "More info" and "Run anyway".
  - Feedback guidelines are maintained, asking users for descriptive feedback and providing instructions on how to generate and export local offline Support Bundles from the "Help & About" view of the app.

## Deployment Status
* **Git Push:** Staged all regenerated static files, `.gitignore`, and script changes, and successfully committed them (`6214734`).
* **Remote Sync:** Successfully pushed `main` to `origin/main` (GitHub Pages remote).
* **Live Site Deploy Alert:** 
  > [!WARNING]
  > Although the push to `origin/main` succeeded and triggered the Notion real-time sync action, the automated GitHub Pages deployment for the private repository is currently blocked. GitHub API reports: `"Your current plan does not support GitHub Pages for this repository."` (HTTP 422). To resolve this and go live on the custom domain `software.accessparalegalservices.com`, the repository visibility must be set to Public, or the GitHub account upgraded to a plan supporting Pages on private repositories.

## Safety & Compliance Confirmations
* **No Large Binaries:** Verified that no files over 100MB are tracked or staged.
* **No Weakening of Warnings:** All SmartScreen warnings and beta disclaimers remain fully intact.
* **No Tracking/Telemetry:** No telemetry or user tracking mechanisms were added to the site.
