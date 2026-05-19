---
title: Batch 3 Project Manager Report
type: reference
status: complete
updated_at: "2026-05-18T00:00:00Z"
---

# APMultitool — Batch 3 Project Manager Report

**Batch:** 3 — Architecture & Foundation  
**Date:** 2026-05-18  
**Executed by:** Claude Code  
**Project owner:** Alan Woodyard

---

## Executive Summary

Batch 3 established the product spine for APMultitool as a modular local-first document workbench. The product identity was sharpened (craftsman's tool for paralegals — not a script collection, not enterprise software). A complete architecture document, user journey map, canonical job model, working engine scaffold, UI wireframe and visual spec, output/audit model, module contracts for Bates and Email-to-PDF, and a test fixture library were produced. No existing code was broken. The engine scaffold introduces five new PDF operations (split, extract, rotate, reorder, merge abstraction) that are ready to be wired into the GUI in the next batch.

---

## Files Created / Modified

### Created (new)
| File | Task | Type |
|---|---|---|
| `docs/ARCHITECTURE.md` | 1, 3 | Architecture doc |
| `docs/USER_JOURNEYS.md` | 2 | User journey map |
| `docs/JOB_MODEL.md` | 4 | Canonical job model |
| `docs/GAP_REPORT.md` | 5 | Gap/audit report |
| `docs/UI_WIREFRAME.md` | 7 | UI wireframe |
| `docs/UI_SPEC.md` | 8 | Visual & interaction spec |
| `docs/OUTPUT_AUDIT_MODEL.md` | 9 | Output/audit model |
| `docs/MODULE_CONTRACTS.md` | 10, 11 | Bates + email module contracts |
| `docs/BATCH_3_PM_REPORT.md` | 13 | This report |
| `docs/handoffs/ho_0004_b3cc0518_arch-foundation.md` | 13 | Handoff document |
| `core/__init__.py` | 6 | Package marker |
| `core/job.py` | 4, 6 | Job model dataclasses |
| `core/engine.py` | 6 | DocEngine |
| `core/operations/__init__.py` | 6 | Operation registry |
| `core/operations/merge.py` | 6 | Merge operation |
| `core/operations/split.py` | 6 | Split operation |
| `core/operations/extract.py` | 6 | Extract operation |
| `core/operations/rotate.py` | 6 | Rotate operation |
| `core/operations/reorder.py` | 6 | Reorder operation |
| `tests/fixtures/README.md` | 12 | Fixture index (12 scenarios) |
| `tests/fixtures/scenario_01_basic_merge.md` | 12 | Golden path merge |
| `tests/fixtures/scenario_03_rotated_scan.md` | 12 | Rotation edge cases |
| `tests/fixtures/scenario_11_corrupt_input.md` | 12 | Partial failure handling |

### Modified
None.

---

## Decisions Made

| Decision | Rationale |
|---|---|
| Stay with CustomTkinter + PyInstaller | Product is already shipping; Windows-first market; air-gapped requirement is real; web-first is v2, not a refactor |
| Abstract engine into `core/` | Enables headless testing, future CLI, and eventual API without GUI changes |
| All operations output new files (non-destructive default) | Source preservation is a legal workflow requirement — users must be able to produce the same output again from the same inputs |
| JSON audit sidecar per output file | Lightweight, no database dependency, survives file moves, durable provenance |
| Engine's `merge.py` depends on email_processing.py for EML/MSG | Reuse existing tested logic rather than duplicate; migration to `core/` is the right next step |
| Add "Manipulate" as a new tab (not a mode inside Merger) | The operations (split/extract/rotate/reorder) have a fundamentally different input model — one PDF in, manipulated PDF out — vs. the merger's many-in/one-out model |

---

## Open Questions

1. `gui_apmultitool.spec` vs `Access_Paralegal_Multitool.spec` — duplicate specs?
2. `web_portal/` vs `Access_Paralegal_Portal/` repo — canonical source?
3. `access_tablet_suite/` Flutter app — active track?
4. Split by blank-page detection — real paralegal workflow or drop?
5. Manipulate tab: new top-level tab or mode inside Document Merger?
6. Word-to-PDF on Windows: LibreOffice or win32com as primary path in the engine?
7. Page thumbnail rendering library for Manipulate tab UI?

---

## Risks / Blockers

| Risk | Severity | Mitigation |
|---|---|---|
| Engine not wired to GUI yet | Medium | Wire in next batch; no user-visible change until done |
| `_word_to_pdf()` uses LibreOffice; GUI uses win32com | Medium | Add win32com fallback to engine before merging with GUI |
| 9 of 12 fixture scenario detail files not yet written | Low | Index + 3 representative scenarios written; fill remaining next batch |
| Root hygiene violations not yet cleaned | Low | Documented in GAP_REPORT.md; schedule cleanup batch |
| `archivist-core/` and `access_tablet_suite/` in wrong repo | Low | Flagged; needs owner decision to move |

---

## Recommended Next Batch

**Batch 4 — Engine Integration & Manipulate Tab**

1. Wire `DocEngine` into `gui_apmultitool.py` for the merge operation — replace `execute_audit_merge()` internals with a `Job` + engine call
2. Add win32com fallback to `core/operations/merge.py:_word_to_pdf()`
3. Build the Manipulate tab UI: operation switcher + options panel for Split, Extract, Rotate, Reorder
4. Wire all four Manipulate operations to their engine handlers
5. Write the remaining 9 fixture scenario detail files
6. Root hygiene cleanup pass per GAP_REPORT.md
7. Migrate `email_processing.py` → `core/operations/email_to_pdf.py`

---

## Confirmation: Logs Committed

All work committed to repo docs per STAX policy:
- ✅ Handoff document written: `docs/handoffs/ho_0004_b3cc0518_arch-foundation.md`
- ✅ PM report written: `docs/BATCH_3_PM_REPORT.md`
- ✅ Architecture decisions documented in `docs/ARCHITECTURE.md`
- ✅ Gap analysis documented in `docs/GAP_REPORT.md`
