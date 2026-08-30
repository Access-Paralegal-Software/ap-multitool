---
handoff_id: ho_0058_2026_05_21
date: 2026-05-21
title: Finalize branded Windows beta download URL in portal
project: APMultitool
status: completed
tags:
  - windows
  - beta1
  - portal
  - cloudflare-r2
  - download-url
---

# Project Manager Report: Finalize Branded Download URL

This report documents the configuration and switchover of the APMultitool Windows `v1.0.0-beta1` download link to the custom branded download subdomain powered by Cloudflare R2, ensuring a professional and secure user download experience.

## 1. Current State (Before Lane)
- **Windows Beta CTA Link:** `https://github.com/woodyardae/ap-multitool/releases/download/v1.0.0-beta1/APMultitool_Setup_v1.0.0-beta1.exe`
- **Integrity Checksum:** `BB9A661D3672D5750C7AD834C5929AD014D7CFCF464E9B2225773784F6864D5B`

## 2. Cloudflare R2 Hosting Configuration
- **R2 Bucket Name:** `aps-downloads`
- **Object Path:** `ap-multitool/windows/APMultitool-windows-beta.exe`
- **Public Access Mode:** Enabled (Access-Control-Allow-Origin: *)
- **Custom Domain:** Connected to `download.accessparalegalservices.com`

## 3. Branded & Stable Download URL
- **Final Canonical Download URL:** `https://download.accessparalegalservices.com/ap-multitool/windows/APMultitool-windows-beta.exe`
- **Mapping:** Points directly to the compiled executable setup in the R2 bucket.
- **HTTP/HTTPS Behavior:** The URL uses secure **HTTPS**. Direct requests for the object return `HTTP/1.1 200 OK` with a `Content-Length` of `137387139` bytes, confirming successful delivery of the installer.

## 4. Portal Updates
All Windows beta installer links were updated to point to the new branded URL. No changes were made to any text, warnings, or copy.

### Files Modified:
1. **[index.html](file:///c:/Users/aewoo/Desktop/Repos/ap-multitool-portal/index.html)**
   - Updated CTA button link to `https://download.accessparalegalservices.com/ap-multitool/windows/APMultitool-windows-beta.exe`.
   - Updated displayed filename in download card from `APMultitool_Setup_v1.0.0-beta1.exe` to `APMultitool-windows-beta.exe`.
   - Updated SHA-256 integrity details drawer to specify the target as `APMultitool-windows-beta.exe`.
2. **[generate_pages.py](file:///c:/Users/aewoo/Desktop/Repos/ap-multitool-portal/generate_pages.py)**
   - Updated the template string for the download options bar to use the branded Cloudflare R2 link.

### Rebuild and Synthesis:
- Executed `python generate_pages.py` to regenerate all **5,000** court/state landing pages in `pages/` using the updated download URL.
- Executed `python generate_ab_pages.py` to regenerate all **6** A/B test variations in `squarespace_ab_tests/`.
- Verified that all generated page templates have been updated with the new branded URL.

## 5. Live Verification
- **Branded URL Resolution:** Direct browser and curl queries to `https://download.accessparalegalservices.com/ap-multitool/windows/APMultitool-windows-beta.exe` return the `131 MB` installer payload over HTTPS with `200 OK`.
- **Portal Deploy Status:** Committed and pushed to `origin/main`. Although the custom domain `software.accessparalegalservices.com` does not resolve locally due to missing DNS setup, the live GitHub Pages build was verified directly. Querying the GitHub Pages edge IP (`185.199.108.153`) with the custom header `Host: software.accessparalegalservices.com` successfully returned the live homepage and sub-pages, proving successful compilation and injection of the HTTPS branded download link.
- **User Wording & Disclaimers:** All SmartScreen bypass instructions, Microsoft Office requirement notes, Beta 1 limitations, and feedback instructions remain fully intact on all pages.

## 6. Safety & Compliance Confirmations
- **No Large Binaries:** Verified that no `.exe` or large binary installers were added or committed to `ap-multitool-portal`.
- **GitHub Release Protection:** The original GitHub Release at `woodyardae/ap-multitool` remains untouched as the canonical developer archive.
