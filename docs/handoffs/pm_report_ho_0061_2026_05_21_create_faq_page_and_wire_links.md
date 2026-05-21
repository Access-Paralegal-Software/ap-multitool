---
handoff_id: ho_0061_2026_05_21
date: 2026-05-21
title: PM Report - Create FAQ page and wire FAQ links in portal
project: APMultitool
status: completed
tags:
  - faq
  - portal
  - github-pages
  - beta1
  - docs
---

# Project Manager Report — ho_0061_2026_05_21

## 0. Meta Information
- **Handoff ID:** `ho_0061_2026_05_21`
- **Date:** 2026-05-21
- **Project:** APMultitool Portal & Docs
- **Status:** COMPLETED

---

## 1. Summary of Work Done

### Files Created
- **Portal Repo (`ap-multitool-portal`):**
  - [faq.html](file:///c:/Users/aewoo/Desktop/Repos/ap-multitool-portal/faq.html): The new end-user FAQ page designed using the portal's custom CSS and visual theme, targeting the Windows Beta audience.

### Files Modified
- **Portal Repo (`ap-multitool-portal`):**
  - [index.html](file:///c:/Users/aewoo/Desktop/Repos/ap-multitool-portal/index.html): Repointed the primary hero secondary CTA button (`📖 Read FAQ`) from the external domain to the local `/faq.html` page.
  - [generate_pages.py](file:///c:/Users/aewoo/Desktop/Repos/ap-multitool-portal/generate_pages.py): Updated the template for the 5,000 localized SEO landing pages to link to the new FAQ page via `../faq.html`.
  - All 5,000+ generated landing pages inside the `pages/` directory were regenerated with the new template changes, referencing the local FAQ page.
  - [sitemap.xml](file:///c:/Users/aewoo/Desktop/Repos/ap-multitool-portal/sitemap.xml): Sitemap updated via page regeneration.
- **Product Repo (`ap-multitool`):**
  - [docs/FAQ.md](file:///c:/Users/aewoo/Desktop/Repos/ap-multitool/docs/FAQ.md): Updated the offline suite reference markdown FAQ to match the new Windows Beta questions and details, including standard frontmatter.

---

## 2. FAQ Content Coverage
The new FAQ covers the following ten required topics in clear, plain language:
1. **What is APMultitool?** (Offline 100% sandboxed document workbench)
2. **Who should use this beta?** (Paralegal assistants and early adopters testing pre-release software)
3. **Is this release Windows-only?** (Yes, Beta 1 is Windows-only. macOS/Linux in active development)
4. **Is this software production-ready?** (Early beta. Recommended to keep backups and verify outputs before court submission)
5. **Why might Windows SmartScreen warn me?** (Unsigned pre-release warning; instructions on clicking "More info" and "Run anyway")
6. **Do I need Microsoft Office installed?** (Required only for local Word/Excel compilation; PDF/image merging does not require it)
7. **Where do I download the current beta?** (Points to final branded download link)
8. **Does the download link stay stable between beta updates?** (Yes, it remains a stable endpoint for updates)
9. **Where do I send bug reports and feedback?** (Points to `info@accessparalegalservices.com`)
10. **What information should I include in a bug report?** (Checklist: action steps, Windows version, screenshots, and steps to export an offline Support Bundle)

---

## 3. Verification Checklist

- [x] **Final FAQ URL:** `https://software.accessparalegalservices.com/faq.html`
- [x] **FAQ Link Wiring:** Verified that the home page points to `faq.html` and all generated pages link to `../faq.html`.
- [x] **Download URL Integrity:** Confirmed that all download buttons point strictly to the stable branded URL:
  `https://download.accessparalegalservices.com/ap-multitool/windows/APMultitool-windows-beta.exe`
- [x] **Bug Report Address:** Verified that the feedback address is `info@accessparalegalservices.com` across all pages.
- [x] **Sitemap Integrity:** Re-run generator scripts cleanly and generated 5,000 pages and sitemap.xml.
- [x] **Push Status:** Successfully committed and pushed the changes to the portal's remote repository (`origin/main`).
- [x] **No Binary Pollution:** Confirmed that no large binaries or setup files were committed to the portal repository.
