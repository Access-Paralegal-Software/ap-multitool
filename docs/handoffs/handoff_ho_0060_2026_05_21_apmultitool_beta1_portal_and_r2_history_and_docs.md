---
handoff_id: ho_0060_2026_05_21
date: 2026-05-21
title: APMultitool Beta 1 – Portal, R2 Hosting, and Beta Feedback Docs
project: APMultitool
status: planned
tags:
  - docs
  - beta1
  - portal
  - cloudflare-r2
  - github-pages
  - feedback
stax_rules:
  - Repo and core docs are the source of truth.
  - Root must stay sparse and intentional.
  - README stays short; heavy details belong in docs/ops/ and handoffs/.
  - YAML frontmatter is required where applicable.
  - Do not keep shippable large binary artifacts inside the portal repo.
  - Maintain explicit beta and warning language on user-facing pages.
  - Prefer branded, normie-friendly download URLs over raw hosting links.
  - YOUR PROJECT MANAGER REPORT MUST BE SAVED TO THE REPO AND PRINTED INLINE AS THE FINAL STEP IN YOUR BATCH OR TASK.
---

# APMultitool Beta 1 – Portal, R2 Hosting, and Beta Feedback Docs

## 0. Narrative summary (what we did today)

This section is a historical log of the last couple of hours so that the repo itself tells the story of how the beta portal and downloads are wired.

### 0.1. Portal repo made public and GitHub Pages enabled

- The `ap-multitool-portal` repository was made **public** so that GitHub Pages could serve it on a custom domain.
- GitHub Pages was enabled for the repo (branch-based deploy from `main`).
- A custom domain was configured for the portal:

  - `software.accessparalegalservices.com`

- Initial DNS was not yet in Cloudflare; GitHub’s own Pages/Pages+DNS setup briefly served the custom domain.

### 0.2. GitHub Enterprise trial and UI confusion

- A 30‑day GitHub Enterprise/Advanced Security trial banner appeared, leading to time spent in the **enterprise account** settings instead of the **repo** settings.
- This caused confusion around where the “Pages” configuration lived.
- Resolution: use the repo-level **Settings → Pages** and direct URLs (e.g. `/settings/pages`) to confirm GitHub Pages configuration, ignoring the enterprise trial banner.

### 0.3. Cloudflare R2 storage and branded download domain

- A Cloudflare R2 account was set up on the Access Paralegal Cloudflare tenant.
- An R2 bucket was created:

  - `aps-downloads`

- Folder structure for APMultitool artifacts was created inside the bucket:

  - `ap-multitool/windows/`

- The Windows Beta 1 installer was uploaded into that folder:

  - Original filename: `APMultitool_Setup_v1.0.0-beta1.exe`
  - Stable filename chosen for public beta: `APMultitool-windows-beta.exe`

- A custom domain was configured on the bucket for public access:

  - `download.accessparalegalservices.com` → bucket `aps-downloads`

- Nameservers for `accessparalegalservices.com` were moved to Cloudflare to allow R2 to attach the custom domain.

### 0.4. R2 public access, object paths, and working URL

- The main failure mode encountered was using a URL that incorrectly included the **bucket name** in the path (e.g. `.../ap-multitool-bucket/...`), which yielded 404s from R2.
- The correct model for R2 custom domains was confirmed:

  - Hostname (`download.accessparalegalservices.com`) points to the bucket.
  - The **path** is just the object key inside that bucket, not including the bucket name.

- Final object key for the stable installer:

  - `ap-multitool/windows/APMultitool-windows-beta.exe`

- Final canonical branded download URL:

  - `https://download.accessparalegalservices.com/ap-multitool/windows/APMultitool-windows-beta.exe`

- This URL was verified to return a `200 OK` response over HTTPS and deliver the full installer payload (≈131 MB).

### 0.5. Choosing a stable “windows-beta” URL

- Two URL styles were considered:

  - Versioned: `.../APMultitool_Setup_v1.0.0-beta1.exe`
  - Stable: `.../APMultitool-windows-beta.exe`

- Decision:

  - Use the **stable** `APMultitool-windows-beta.exe` object as the public URL.
  - Future betas will replace the object at that key while keeping the URL stable.
  - GitHub Releases remains the canonical source of the versioned artifacts and checksums.

### 0.6. Cloudflare HTTPS behavior

- Cloudflare’s **Always Use HTTPS** was found under:

  - Domain `accessparalegalservices.com` → SSL/TLS → Edge Certificates → “Always Use HTTPS”

- That toggle was enabled to ensure HTTP requests to the domain are redirected to HTTPS at the edge.
- GitHub Pages **Enforce HTTPS** was also enabled for the portal’s custom domain once the certificate became available.

### 0.7. GitHub Pages + Cloudflare DNS wiring

- DNS for `software.accessparalegalservices.com` was moved into Cloudflare.
- Initially, A records for `software` were missing in Cloudflare, causing intermittent resolution failures.
- A records were then created for `software.accessparalegalservices.com` pointing to the standard GitHub Pages IPs:

  - `185.199.108.153`
  - `185.199.109.153`
  - `185.199.110.153`
  - `185.199.111.153`

- These records were set to **Proxied** through Cloudflare.
- GitHub’s repo-level **Settings → Pages** eventually reported **“DNS check successful”** for `software.accessparalegalservices.com`, confirming DNS and Pages alignment.
- AG verified that querying the GitHub Pages edge IP with a `Host: software.accessparalegalservices.com` header returned the live homepage, confirming that:

  - The site builds correctly.
  - The custom domain mapping is valid at the GitHub edge.
  - Local resolution issues are due to DNS propagation/caching, not a broken build.

### 0.8. Portal updates to use branded R2 URL

- The portal’s Windows beta download CTAs were updated to use the branded Cloudflare R2 URL instead of the GitHub Releases URL.
- Changes included:

  - `index.html`
    - Download button `href` updated to:
      - `https://download.accessparalegalservices.com/ap-multitool/windows/APMultitool-windows-beta.exe`
    - Displayed filename updated to `APMultitool-windows-beta.exe`.
    - Integrity details updated to reference the new filename while keeping the original checksum data from the GitHub Release.
  - `generate_pages.py`
    - Template for the download options bar updated to use the branded URL.
  - `generate_ab_pages.py`
    - A/B test templates updated to use the branded URL.

- Generators were re-run:

  - `python generate_pages.py`
  - `python generate_ab_pages.py`

- Verified outcomes:

  - All generated pages now use the branded R2 URL.
  - No `.exe` or large binaries were added to the portal repo; only URLs changed.
  - All Windows-only, SmartScreen, and beta disclaimers remain intact.

### 0.9. Confirmation of live behavior

- The branded R2 URL has been fully verified:

  - `https://download.accessparalegalservices.com/ap-multitool/windows/APMultitool-windows-beta.exe`
  - Returns the ≈131 MB installer with `HTTP/1.1 200 OK` over HTTPS.
- The portal build using this URL has been validated via GitHub Pages edge IP plus Host header.
- DNS and HTTPS enforcement are in place; some local resolution issues are expected to clear as DNS propagates.

---

## 1. Current desired state (for AG and future lanes)

**Portal site**

- Hostname: `software.accessparalegalservices.com`
- Hosting: GitHub Pages (branch `main` in `ap-multitool-portal`)
- DNS: Managed by Cloudflare for `accessparalegalservices.com` via A records pointing to GitHub Pages IPs, currently **Proxied**.
- HTTPS:
  - GitHub Pages **Enforce HTTPS**: ON.
  - Cloudflare **Always Use HTTPS**: ON.

**Windows beta installer**

- Storage: Cloudflare R2 bucket `aps-downloads`
- Object key: `ap-multitool/windows/APMultitool-windows-beta.exe`
- Public access: Enabled for bucket via R2 public bucket + custom domain.
- Branded download domain: `download.accessparalegalservices.com`
- Canonical public URL:

  - `https://download.accessparalegalservices.com/ap-multitool/windows/APMultitool-windows-beta.exe`

**Artifact truth**

- Canonical dev-facing artifact and checksum live on GitHub Releases:

  - Repo: `woodyardae/ap-multitool`
  - Tag/release: `v1.0.0-beta1`
  - File: `APMultitool_Setup_v1.0.0-beta1.exe`
  - SHA-256: `BB9A661D3672D5750C7AD834C5929AD014D7CFCF464E9B2225773784F6864D5B`

**User-facing docs**

- Homepage and generated pages clearly state:

  - Windows-only support for this beta.
  - Expected SmartScreen warnings and how to handle them.
  - Beta nature of the build and known limitations.

- **All** beta bug reports, install issues, and UX feedback should be sent to:

  - `info@accessparalegalservices.com`

---

## 2. Tasks for this lane (docs + feedback)

This is the actionable part of the handoff for AG.

### 2.1. Consolidate and formalize today’s history in the repo

1. Create this handoff file (or equivalent) in the repo, for example:

   - `docs/handoffs/handoff_ho_0060_2026_05_21_apmultitool_beta1_portal_and_r2_history_and_docs.md`

2. Include:

   - The full narrative summary above (0.x sections).
   - The current desired state summary (1.0).
   - Any additional implementation details you discover while double-checking the repo and
