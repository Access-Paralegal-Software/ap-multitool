---
handoff_id: ho_next_feedback_cycle
date: 2026-05-21
title: APMultitool Windows Beta 1 – Post-feedback implementation lane
project: APMultitool
status: planned
tags:
  - beta1
  - feedback
  - portal
  - product
  - cloudflare-r2
  - github-pages
  - docs
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

# APMultitool Windows Beta 1 – Post-feedback implementation lane

## 0. Current snapshot (what's true *now*)

This section describes the baseline as of the end of the 2026‑05‑21 session. Treat this as the "frozen state" that feedback will be responding to.

### 0.1. Product and repos

- **Product name:** APMultitool
- **Release:** Windows `v1.0.0-beta1`
- **Product repo:** `woodyardae/ap-multitool`
  - Branch used last: `master`
  - Contains the application code, release artifacts (via GitHub Releases), and product-facing docs (including `docs/FAQ.md`).
- **Portal/marketing repo:** `woodyardae/ap-multitool-portal`
  - Branch: `main`
  - Hosts the public portal, SEO landing pages, A/B templates, FAQ page, and handoff/PM docs for the website.

Local working copies were deliberately deleted at the end of the last session; only GitHub remotes are canonical.

### 0.2. Hosting and domains

**Portal website**

- Public URL (custom domain, GitHub Pages):

  - `https://software.accessparalegalservices.com/`

- Behavior:
  - Served via GitHub Pages from `ap-multitool-portal`'s `main` branch.
  - Custom domain configured in repo Pages settings.
  - GitHub Pages "Enforce HTTPS" is ON.
  - DNS is managed by Cloudflare for `accessparalegalservices.com`:
    - `software.accessparalegalservices.com` → GitHub Pages IPs via A records (proxied).

**Download hosting**

- Artifact hosting: Cloudflare R2.
- Bucket: `aps-downloads`.
- Object key for stable Windows beta installer:

  - `ap-multitool/windows/APMultitool-windows-beta.exe`

- Custom domain for R2 public access:

  - `download.accessparalegalservices.com` → R2 bucket `aps-downloads`.

- Canonical public download URL (this must not change lightly):

  - `https://download.accessparalegalservices.com/ap-multitool/windows/APMultitool-windows-beta.exe`

- This URL has been verified to:
  - Serve over HTTPS.
  - Return HTTP `200 OK`.
  - Deliver ~131 MB installer payload (`Content-Length` ~137,387,139 bytes).

### 0.3. Release artifacts and integrity

- Canonical dev-facing artifact lives on GitHub Releases:

  - Repo: `woodyardae/ap-multitool`
  - Release: `v1.0.0-beta1`
  - File: `APMultitool_Setup_v1.0.0-beta1.exe`
  - SHA‑256: `BB9A661D3672D5750C7AD834C5929AD014D7CFCF464E9B2225773784F6864D5B`

- The R2 stable object (`APMultitool-windows-beta.exe`) is conceptually the same build, surfaced through a nicer URL for normie users.

### 0.4. Portal content and structure

**Homepage (`index.html`)**

- Lives in `ap-multitool-portal`.
- Key characteristics:
  - Hero explaining APMultitool as an **offline, local** document suite for legal support.
  - Windows-only, Beta 1 positioning is explicit.
  - Windows Defender SmartScreen warning is described, including "More info" → "Run anyway".
  - Microsoft Office requirement explained for Word/Excel workflows.
  - Download card/button for Windows:
    - `href` → `https://download.accessparalegalservices.com/ap-multitool/windows/APMultitool-windows-beta.exe`.
    - Filename shown as `APMultitool-windows-beta.exe`.
    - Integrity/verification details reference the GitHub Release checksum.
  - "How to report beta issues" card points to the feedback channel (see below).

**FAQ page**

- URL: `https://software.accessparalegalservices.com/faq.html`
- Backed by `faq.html` in `ap-multitool-portal`.
- Covers at least these ten questions in plain language:
  1. What is APMultitool?
  2. Who should use this beta?
  3. Is this release Windows-only?
  4. Is this software production-ready?
  5. Why might Windows SmartScreen warn me?
  6. Do I need Microsoft Office installed?
  7. Where do I download the current beta?
  8. Does the download link stay stable between beta updates?
  9. Where do I send bug reports and feedback?
  10. What information should I include in a bug report?
- The FAQ reinforces:
  - Windows-only support for Beta 1.
  - Unsigned nature of the build and SmartScreen warning.
  - Office requirement for DOCX/XLSX compilation.
  - Stable download URL.
  - Feedback email and what to include (steps, Windows version, screenshots, support bundle).

**SEO landing pages**

- Generated from `generate_pages.py` into `pages/` (5,000+ localized court/SEO pages).
- All Windows download CTAs point to the branded R2 URL.
- Templates include a feedback/bug-report note pointing to the same email address.

**A/B test templates**

- `generate_ab_pages.py` outputs 6 A/B templates in `squarespace_ab_tests/`.
- Each template includes:
  - Windows beta positioning.
  - Download button using the branded R2 URL.
  - Support/feedback call-to-action referencing the info@ email.

### 0.5. Feedback channel and bug-report expectations

- **Official beta feedback address:**

  - `info@accessparalegalservices.com`

- All user-facing surfaces (homepage, FAQ, localized pages, A/B templates, QA docs) were updated to direct bug reports and feedback here.

- Users are encouraged to include:
  - What they were trying to do.
  - What happened instead (errors, unexpected behavior).
  - Windows version.
  - Screenshots of any UI or error dialogs.
  - Offline Support Bundle (exported from the app's "Help & About → Export Support Bundle"), which contains logs/config, not document contents.

### 0.6. Docs and PM reports

- Multiple PM reports and handoff docs have been committed, documenting:
  - R2 setup and custom domain wiring.
  - Portal URL/CTA changes.
  - Feedback doc/FAQ updates.
  - Final push verification and local repo cleanup.

These are stored across the two repos in `docs/handoffs/` and similar folders (e.g., `handoff_ho_0060_...`, `pm_report_ho_0058_...`, `pm_report_ho_0061_...`, `pm_report_ho_0062_...`).

---

## 1. What this *next* lane is for

This lane is intended to be run later, after there is real tester feedback in the `info@accessparalegalservices.com` inbox and/or GitHub Issues.

**Goal:**

- Ingest Beta 1 feedback.
- Classify and prioritize issues.
- Implement a small, well-scoped batch of improvements (product + portal docs), while preserving:
  - R2/Pages architecture,
  - Stable download URL,
  - Clear beta messaging,
  - No binaries in the portal repo.

Think of this as "Beta 1.1 polish and responsiveness," not a full rewrite.

---

## 2. Inputs this lane expects from future you

Before starting, assemble:

1. **A feedback dump** from testers:
   - Emails from `info@accessparalegalservices.com` related to APMultitool.
   - Any GitHub Issues filed.
   - Notes from your own tests or calls.

2. **Optional:** a quick list of **known issues** you already agree are valid that may or may not have been reported yet.

You can paste that into the new session or summarize it as bullet points.

---

## 3. Tasks for the future lane

These are the concrete steps the future session should perform.

### 3.1. Synthesize feedback and decide what to change

1. **Aggregate feedback.**
   - Cluster by theme:
     - Installation/SmartScreen issues.
     - Office/format support issues.
     - UX and flow confusion.
     - Performance problems.
     - Crashes or data edge cases.
     - "Nice-to-have" feature requests.

2. **Prioritize.**
   - Label each item as:
     - P0: blocking/critical (crash, data corruption, totally blocked install).
     - P1: serious but not blocking (high friction, serious usability problem).
     - P2: minor issues/polish.
     - P3: feature requests / future roadmap.

3. **Decide scope for this lane.**
   - Choose a small, realistic batch (e.g., 1–3 P0/P1s + a small number of P2 doc/UX tweaks), not "fix everything".

4. **Produce a short "Feedback Synthesis" note** in Markdown that:
   - Lists the input sources (emails, issues).
   - Summarizes key themes.
   - Identifies the items you will handle in this lane vs. defer.

This synthesis doc should be checked into `ap-multitool` or `ap-multitool-portal` under `docs/handoffs/`.

### 3.2. Product changes (if any)

If some prioritized items require changes in the actual app (not just portal/docs):

1. Update `woodyardae/ap-multitool`:
   - Implement the minimal code changes needed for the selected feedback items.
   - Update any in-app copy that should align with portal/FAQ language (e.g., SmartScreen explanation, support bundle wording).
   - Bump an internal version identifier if appropriate (e.g., `v1.0.0-beta1+patch1`), but **do not** change the public-facing `windows-beta` URL; plan to replace the binary behind that alias when ready.

2. Add or update product docs:
   - `docs/FAQ.md` to match any new behavior.
   - Optionally create `docs/known_issues_beta1.md` listing confirmed issues you are not yet fixing.

3. Prepare a new build and upload to:
   - GitHub Releases (versioned filename + checksum).
   - Cloudflare R2, replacing `APMultitool-windows-beta.exe` with the new binary (same object key) once tested.

4. Verify:
   - The R2 stable URL still downloads the new build.
   - The GitHub Release remains the source of truth for versioned artifacts and checksums.

If you decide *not* to ship a new binary in this lane (e.g., first pass only updates docs and FAQ based on feedback), explicitly record that decision.

### 3.3. Portal / docs changes

Whether or not you ship a new build, some feedback will likely be best addressed through documentation and UX text:

1. Update the portal homepage (`index.html`), templates, and `faq.html` to:
   - Clarify any points of confusion testers hit repeatedly.
   - Add a small "Known issues in Beta 1" callout if appropriate.
   - Update SmartScreen, Office requirements, or workflow steps if the behavior or recommended path changed.

2. Update FAQ entries:
   - Add Q&A entries for new common questions.
   - Update existing answers if behavior changed.
   - Keep answers short and focused.

3. Ensure:
   - Download button still points to the same stable URL.
   - Feedback email is unchanged (`info@accessparalegalservices.com`).
   - You do not add binary artifacts to the portal repo.

4. Regenerate:
   - `generate_pages.py` → rebuild `pages/`.
   - `generate_ab_pages.py` → rebuild A/B templates.
   - `sitemap.xml` if the URL set changed.

5. Verify:
   - Main portal loads correctly on `software.accessparalegalservices.com`.
   - FAQ page loads at `/faq.html`.
   - All references to the app's behavior are consistent across homepage, FAQ, and product docs.

### 3.4. "Known issues" + "What's next" doc

Create a short doc in `ap-multitool` such as:

- `docs/known_issues_and_roadmap_beta1.md`

Include:

- Known issues that are:
  - Confirmed and reproducible.
  - Not yet fixed or intentionally deferred.
- A short "next steps" / roadmap outline for Beta 2 (even if rough).

This doc is mainly for you and future lanes, but can also be used to drive future portal/FAQ updates.

### 3.5. Commit, push, and PM report

For any repo touched:

1. Commit with clear messages (e.g., `fix: address beta feedback on installer flow`, `docs: update faq and known issues from beta1 feedback`).
2. Push to the appropriate branches (`master`/`main`).
3. Create a PM report for this lane, for example:

   - `docs/handoffs/pm_report_ho_next_feedback_cycle.md`

Include:

- Summary of feedback sources and themes.
- List of items addressed in this lane, with IDs if you tracked them.
- Summary of product changes (code + new build, if any).
- Summary of portal/FAQ/doc changes.
- Confirmation of:
  - Stable R2 URL and download behavior.
  - Feedback channel still `info@accessparalegalservices.com`.
  - No binaries added to portal repo.

Print the full PM report inline at the end of the run, per usual STAX-style rules.

---

## 4. How to use this handoff later

When you're ready to act on real feedback:

1. Start a **fresh session**.
2. Paste this entire handoff document into the new session.
3. Add:
   - Your actual feedback bullets (from testers) under a short heading like "Feedback inputs".
4. Ask the assistant to:
   - First summarize and prioritize that feedback.
   - Then execute this lane step-by-step, starting from section **3.1** above.

That future session will pick up from exactly the stable baseline described here.
