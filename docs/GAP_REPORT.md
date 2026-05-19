---
title: APMultitool Gap Report — Batch 3 Inventory
type: reference
status: active
updated_at: "2026-05-18T00:00:00Z"
---

# APMultitool — Gap Report

Produced during Batch 3 inventory pass. Covers what exists, what can be reused, what should be retired, and what needs to be built.

---

## What Exists and Is Working

| File / Component | What It Does | Keep? |
|---|---|---|
| `gui_apmultitool.py` | Full CustomTkinter GUI: merger, bates, file room, licensing | ✅ Keep, refactor engine out |
| `email_processing.py` | Unified EML/MSG → PDF engine (ReportLab, grayscale, bookmarks) | ✅ Keep, migrate into `core/` |
| `config.py` | Version + app name constants | ✅ Keep |
| `logo_small.png` | Brand asset, referenced at runtime | ✅ Keep in root |
| `installer.iss` | Inno Setup installer script | ✅ Keep |
| `Access_Paralegal_Multitool.spec` | PyInstaller spec | ✅ Keep |
| `gui_apmultitool.spec` | PyInstaller spec (older) | ⚠️ Review — may be a duplicate of the above |
| `docs/handoffs/` | 3 prior handoff docs in correct naming format | ✅ Keep |
| `scratch/test_email_processing.py` | Email processing tests | ✅ Keep in `scratch/` until migrated to `tests/` |
| `scratch/test_gui_integration.py` | GUI integration tests | ✅ Keep in `scratch/` until migrated |

---

## What Can Be Reused In The New Architecture

| File | Reuse Plan |
|---|---|
| `email_processing.py` | The `UnifiedEmail`, `email_to_pdf`, and `attachment_to_pdf` functions become the `EmailToPdfOperation` in `core/operations/`. The logic is already clean and can be wrapped with minimal changes. |
| Merge logic in `gui_apmultitool.py:execute_audit_merge()` | The core pikepdf merge logic should be extracted into `core/operations/merge.py`. The GUI method becomes a thin wrapper that builds a `Job` and calls the engine. |
| Bates logic in `gui_apmultitool.py:execute_bates_production()` | Extract into `core/operations/bates.py`. The coordinate-visitor scanner and smart-shrink logic is non-trivial and is already working — migrate rather than rewrite. |
| `generate_audit_log()` in `gui_apmultitool.py` | Becomes the basis of `JobResult` serialization in `core/engine.py`. |
| `_convert_image_to_pdf()`, `_convert_word_to_pdf()`, `_convert_excel_to_pdf()`, `_convert_text_to_pdf()` | Move into `core/operations/convert.py` as format adapters. |

---

## What Should Be Retired

| File | Reason | Action |
|---|---|---|
| `outlook_to_pdf.py` | Legacy BeautifulSoup + xhtml2pdf pipeline, superseded by `email_processing.py` | Move to `archive/legacy/` |
| `eml_to_pdf.py` | Standalone CLI script with its own dep bootstrap; the logic is duplicated in `email_processing.py` | Move to `archive/legacy/`. A future CLI wrapper over the engine replaces this. |

---

## Root Hygiene Violations (STAX: Root Is Sacred)

The following files in root violate the STAX rule that root contains only core system files. They should be moved in a cleanup pass (not in this batch — flagged here for the next cleanup sprint).

| File | Should Move To |
|---|---|
| `brute_force_key.py` | `scratch/` |
| `add_anthropic_provider.py` | `scratch/` or delete |
| `deploy_and_run_test.py` | `scratch/` |
| `remote_test.py` | `scratch/` |
| `locate_flutter.py` | `access_tablet_suite/` or `scratch/` |
| `raw_exhibit.pdf` | `tests/fixtures/` |
| `startup_log.txt` | Delete (ephemeral log) |
| `scratch_push_script.txt` | Delete |
| `demo.html` | `docs/` or `scratch/` |
| `archivist_core.zip` | This is a different project's artifact — remove from this repo entirely |
| `water_texture.png` | `assets/` if still needed, otherwise delete |
| `DEVELOPMENT_AUDIT_LOG.md` | `docs/` |
| `STAX_RULES_POLICY.md` | `docs/` |
| `Access_Paralegal_Release.md` | `docs/` |
| `Reddit_Paralegal_Pain_Points.md` | `docs/` or `Marketing_Assets/` |
| `keygen_free_licensing_guide.md` | `docs/` |

---

## Out-of-Scope Directories (Should Not Live In This Repo)

| Directory | What It Is | Recommendation |
|---|---|---|
| `access_tablet_suite/` | Flutter mobile app (Android + iOS) | Separate repo. Move out of APMultitool. |
| `archivist-core/` | Separate pipeline project with its own database and adapters | Separate repo. Move out of APMultitool. |
| `antigravity-base/` | Appears to be an architecture sketch or template directory | Clarify with owner. Move or delete. |
| `web_portal/` | Landing page / marketing site | Already mirrored in `Access_Paralegal_Portal` repo. Verify which is canonical. |

---

## What Needs To Be Built (This Batch Scaffolds)

| Component | Location | Tasks |
|---|---|---|
| `core/engine.py` | `core/engine.py` | Job runner, dispatch, status tracking |
| `core/job.py` | `core/job.py` | Job, InputSpec, OutputSpec, JobResult dataclasses |
| `core/operations/merge.py` | `core/operations/` | Extracted merge logic |
| `core/operations/split.py` | `core/operations/` | New — PDF split by range/count |
| `core/operations/extract.py` | `core/operations/` | New — page extraction |
| `core/operations/rotate.py` | `core/operations/` | New — page rotation |
| `core/operations/reorder.py` | `core/operations/` | New — page reorder |
| `core/operations/convert.py` | `core/operations/` | Extracted format adapters |
| `tests/fixtures/` | `tests/fixtures/` | Realistic test scenarios |

---

## Open Questions From Inventory

1. `gui_apmultitool.spec` and `Access_Paralegal_Multitool.spec` — are both needed or is one stale?
2. `web_portal/` vs `Access_Paralegal_Portal/` — which is the canonical source for the marketing site?
3. `access_tablet_suite/` — is the Flutter app an active or shelved track?
4. `archivist-core/` — what project does this belong to? (It has its own pipeline/database structure.)
