---
title: APMultitool Architecture
type: reference
status: active
updated_at: "2026-05-18T00:00:00Z"
---

# APMultitool — Product Architecture

## Identity

APMultitool is a **local-first document manipulation workbench** for paralegals and legal support professionals. It is not an accounts-payable tool, not a cloud service, and not a pile of one-off scripts. It is a craftsman's multi-tool for handling the real document work of legal practice: assembling, splitting, numbering, packaging, converting, and preparing document sets with precision and confidence.

The product's core promise: everything stays on the user's machine, everything is auditable, and every operation feels sharp rather than scary.

---

## Module Families

The product is organized into discrete module families. Each family owns a coherent slice of document work. They share the same job model and operation engine.

### 1. PDF Manipulation
Core document operations on PDF files. The heart of the workbench.

| Operation | Description | Status |
|---|---|---|
| Merge | Combine multiple PDFs/documents into one | ✅ Implemented |
| Split | Divide a PDF into parts by page range or count | 🔲 Scaffolded |
| Extract | Pull a subset of pages into a new PDF | 🔲 Scaffolded |
| Reorder | Change page order within a PDF | 🔲 Scaffolded |
| Rotate | Rotate individual or all pages | 🔲 Scaffolded |
| Compress | Reduce file size for PACER/ECF filing | ✅ Implemented (grayscale) |

### 2. Document-Set Assembly
Composing coherent document packets from mixed sources, with cover pages, dividers, and exhibit structure.

| Operation | Description | Status |
|---|---|---|
| Packet assembly | Multi-source ordered bundle with bookmarks | ✅ Implemented (as merge) |
| Cover page insertion | Auto-generated or custom cover | 🔲 Planned |
| Exhibit dividers | Labeled separator pages | 🔲 Planned |
| Table of contents | Auto-generated TOC page | 🔲 Future |

### 3. Numbering & Stamping
Adding permanent, auditable identifiers to document sets.

| Operation | Description | Status |
|---|---|---|
| Bates stamping | Vector-fused sequential numbering with prefix | ✅ Implemented |
| Page numbering | Simple page numbers without legal serial format | 🔲 Planned |
| Watermarking | DRAFT / CONFIDENTIAL / COPY overlays | 🔲 Future |
| Redline/lock | Flatten annotations, lock content | 🔲 Future |

### 4. Email-to-PDF
Converting email-format source material into litigation-ready PDFs.

| Operation | Description | Status |
|---|---|---|
| EML to PDF | Standard email with attachment policy | ✅ Implemented |
| MSG to PDF | Outlook MSG with attachment policy | ✅ Implemented |
| Batch harvest | Folder of emails → merged PDF | ✅ Implemented |
| Attachment policy | Include/exclude/flatten attachment types | ✅ Implemented |
| Grayscale mode | PACER-compliant compression | ✅ Implemented |

### 5. File Room & Case Organizer
Local case folder scaffolding and document vault management.

| Feature | Description | Status |
|---|---|---|
| Case scaffold | Generate standard folder tree | ✅ Implemented |
| Case vault | Encrypted, hardware-bound case registry | ✅ Implemented |
| Workspace routing | Named case → working directory | ✅ Implemented |

---

## Layer Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    GUI Layer (CustomTkinter)              │
│   gui_apmultitool.py — tabs, controls, queue, progress   │
├──────────────────────────────────────────────────────────┤
│                    Engine Layer (core/)                   │
│   DocEngine — runs jobs, dispatches operations           │
│   Job model — inputs, ops, output, provenance, status    │
├──────────────────────────────────────────────────────────┤
│                  Operations Layer (core/operations/)      │
│   merge  split  extract  rotate  reorder  stamp  email   │
├──────────────────────────────────────────────────────────┤
│                    Library Layer                          │
│   pypdf  reportlab  Pillow  extract-msg  customtkinter   │
└──────────────────────────────────────────────────────────┘
```

The GUI layer should depend only on the Engine layer. The Engine layer should have no GUI imports. Operations are pure Python functions that accept file paths and parameters and return results. This separation means the engine can be tested headlessly, wrapped in a CLI, or eventually exposed via a local API.

---

## Technology Stack Decision

**Current platform: CustomTkinter + PyInstaller → Windows `.exe`**

This is the correct stack for the current product stage. Rationale:

1. **The product already ships.** v1.0.0 is packaged and in field use. Stability beats elegance in an active user's hands.
2. **Windows-first paralegal market.** Law firms and legal support staff are overwhelmingly Windows users. CustomTkinter produces a native-feeling Windows app without requiring a browser or Electron.
3. **Air-gapped requirement is real.** A local desktop app is the honest technical expression of the product's core promise. A web stack (even locally served) introduces complexity and trust questions with legal users.
4. **PyInstaller packaging is proven.** The existing `.spec` and `installer.iss` pipeline already works.

**Engine abstraction is the priority investment.** Moving processing logic out of `gui_apmultitool.py` and into `core/` is the right architectural step. It enables headless testing, future CLI wrappers, and eventual API exposure without touching the GUI.

**Web-first is the v2 premium play, not v1.** A locally-served FastAPI + browser UI could be a polished future tier, but it is a different product surface, not a refactor of this one. Defer until the core engine is stable and the user journey is fully mapped.

**Tauri is not the right path.** It would require rewriting all processing code in a non-Python runtime. The existing Python ecosystem (pypdf, reportlab, etc.) is the engine. Don't abandon it.

---

## Expansion Principles

1. New operations plug into the job model — they don't become new apps.
2. The GUI gets new tabs or controls, not new windows.
3. Licensing gates features, not access to the app itself.
4. Every operation that touches documents must log provenance.
5. Root stays sparse. Heavy logic belongs in `core/`. Docs belong in `docs/`.
