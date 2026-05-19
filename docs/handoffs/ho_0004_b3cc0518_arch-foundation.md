---
title: "ho_0004_b3cc0518_arch-foundation"
type: reference
status: active
updated_at: "2026-05-18T00:00:00Z"
---

# 🤝 STAX Session Handoff Document

- **Handoff Reference**: `ho_0004_b3cc0518_arch-foundation.md`
- **Conversation ID**: `b3cc0518` (Batch 3, Claude Code, 2026-05-18)
- **From**: Claude Code (Batch 3 execution)
- **To**: Next Session Agent / Developer
- **Timestamp**: 2026-05-18T00:00:00Z

---

## 🎯 SESSION OVERVIEW

Batch 3 established APMultitool's architectural foundation as a **modular local-first document workbench**. The product identity was clarified (not an accounts-payable tool, not a script pile — a craftsman's multi-tool for legal document work). Architecture docs, user journeys, a canonical job model, an operation engine scaffold, UI wireframe, visual spec, output/audit model, module contracts, and test fixtures were all produced.

No existing code was modified. All deliverables are additive.

---

## 🛠️ WORK ACCOMPLISHED

### Docs Created (`docs/`)
| File | Purpose |
|---|---|
| `ARCHITECTURE.md` | Product identity, module families, layer diagram, tech stack decision |
| `USER_JOURNEYS.md` | 6 core journeys with release classification (MVP / next-wave / research) |
| `JOB_MODEL.md` | Canonical job model with all param dataclasses, lifecycle, reversibility labels |
| `GAP_REPORT.md` | Inventory of what exists, what's reusable, what should retire, root hygiene violations |
| `UI_WIREFRAME.md` | ASCII wireframe for Merger tab + new Manipulate tab + Bates tab |
| `UI_SPEC.md` | Color system, typography, control specs, interaction patterns, anti-patterns |
| `OUTPUT_AUDIT_MODEL.md` | Output naming rules, sidecar JSON, error reporting, reversibility labels |
| `MODULE_CONTRACTS.md` | Architecture contracts for Bates and Email-to-PDF modules |

### Engine Scaffold Created (`core/`)
| File | Purpose |
|---|---|
| `core/__init__.py` | Package marker |
| `core/job.py` | Job, InputSpec, OutputSpec, all Params dataclasses, JobResult, JobStatus |
| `core/engine.py` | DocEngine: submit(), provenance filling, audit sidecar writing |
| `core/operations/__init__.py` | OPERATION_REGISTRY — maps operation names to handlers |
| `core/operations/merge.py` | Merge operation: multi-format inputs → single PDF via pikepdf |
| `core/operations/split.py` | Split operation: ranges / fixed / blank_page modes |
| `core/operations/extract.py` | Extract pages: non-contiguous selection, source preserved |
| `core/operations/rotate.py` | Rotate pages: 90/180/270, per-page or all |
| `core/operations/reorder.py` | Reorder pages: arbitrary page_order list |

### Test Fixtures Created (`tests/fixtures/`)
| File | Coverage |
|---|---|
| `README.md` | 12-scenario index with fixture format spec |
| `scenario_01_basic_merge.md` | Golden path merge, 3 PDFs |
| `scenario_03_rotated_scan.md` | Non-contiguous rotation, composed rotation metadata |
| `scenario_11_corrupt_input.md` | Partial failure in batch — must not abort |

Scenarios 02, 04–10, 12 are documented in the README index; detailed files ready to be written next batch.

---

## 📂 CURRENT REPOSITORY STATE

### Files modified
None. All work is new files.

### Files flagged for cleanup (not yet moved — next batch)
See `docs/GAP_REPORT.md` for the full list. Key items:
- ~10 root-level files violating STAX sparse-root rule
- `outlook_to_pdf.py` and `eml_to_pdf.py` to be retired to `archive/legacy/`
- `access_tablet_suite/`, `archivist-core/`, `antigravity-base/` are out-of-scope for this repo

---

## 📋 RECOMMENDED NEXT STEPS

1. **Wire the engine into the GUI** — `gui_apmultitool.py:execute_audit_merge()` should build a `MergeParams` and a `Job`, call `DocEngine.submit()`, and use the result. This decouples business logic from UI and enables headless testing.

2. **Add a Manipulate tab** — Implement the UI wireframe for Split / Extract / Rotate / Reorder (one tab, operation switcher, options panel beneath). Wire to the engine operations already scaffolded.

3. **Complete test fixture scenario files** — Fill in the 9 remaining scenario detail files (scenarios 02, 04–10, 12).

4. **Root hygiene pass** — Move the flagged files from root per the gap report. This is a cleanup batch of its own, ~30 minutes.

5. **Migrate email_processing into core/** — Wrap `email_processing.py` as `core/operations/email_to_pdf.py` per the module contract.

6. **Page thumbnail preview** — For the Manipulate tab, page thumbnails will require rendering pages to images. Evaluate `pypdfium2` or `pdf2image` (requires poppler on Windows) for this.

---

## ❓ OPEN QUESTIONS

1. `gui_apmultitool.spec` vs `Access_Paralegal_Multitool.spec` — are both needed or is one stale?
2. `web_portal/` vs `Access_Paralegal_Portal/` repo — which is canonical for the marketing site?
3. `access_tablet_suite/` Flutter app — active or shelved?
4. Split by blank-page — is this a real paralegal workflow? Worth implementing or drop from the map?
5. Should the Manipulate tab be a new top-level tab, or a mode within the Document Merger tab?

---

## ⚠️ RISKS / BLOCKERS

- The `core/` engine is not yet wired to the GUI. Until it is, the scaffold has no user-visible effect.
- `core/operations/merge.py:_word_to_pdf()` depends on LibreOffice (`soffice`) being on PATH. The existing GUI uses `win32com` for Word conversion on Windows — the engine needs the same fallback for production use on Windows machines without LibreOffice.
- Page thumbnail rendering for the Manipulate tab needs a library decision before UI work begins.

---

*Handoff signed by: Claude Code (Batch 3)*  
*Project owner: Alan Woodyard*
