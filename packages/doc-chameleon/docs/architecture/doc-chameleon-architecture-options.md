---
id: doc-chameleon-architecture-options
title: Architecture Options Memo
type: architecture
status: active
project: doc-chameleon
created: 2026-05-20
---

# Architecture Options Memo

> This document presents options and trade-offs. Nothing here is locked or decided unless explicitly authorized by a future STAX batch. Recommendations are labeled as such.

---

## 1. Core Language / Runtime Options

### Option A: Python (Recommended)

**Rationale:** Python has the most mature ecosystem for `.docx` manipulation (`python-docx`), strong data processing tooling, and broad developer availability. The CLI-first roadmap maps naturally to Python scripting.

**Trade-offs:**
- Slower raw execution than compiled alternatives
- Distribution requires bundling Python runtime (e.g., PyInstaller) for desktop delivery
- Well-understood, lower onboarding risk

### Option B: Rust

**Trade-offs:**
- Excellent performance and small binary distribution
- No mature `.docx` manipulation library comparable to `python-docx`
- Higher implementation cost for document processing logic
- Not recommended at this time unless `.docx` library ecosystem matures

### Option C: Node.js / TypeScript

**Trade-offs:**
- Good cross-platform desktop support via Electron
- `.docx` manipulation libraries exist (e.g., `docx`) but are less battle-tested for complex legal document structures
- May make sense later if the desktop shell drives the language choice

**Current direction:** Python for the core engine. Desktop shell language evaluated separately.

---

## 2. Document Processing Approaches

### Option A: Direct OpenXML Manipulation via python-docx (Recommended)

`python-docx` reads and writes the internal OpenXML structure of `.docx` files directly. This gives fine-grained control over paragraph styles, section properties, margins, and line formatting.

**Why this matters for CA:** California's Rule 2.108 line numbering requires injecting numbered lines at the Word structure level — not as a visual decoration. Only direct XML manipulation makes this reliably editable after conversion.

**Trade-offs:**
- Requires understanding Word's internal XML schema
- Some edge cases (e.g., complex tables spanning page breaks) require careful handling
- Preserves editability — the output is a real Word document, not a painted image

### Option B: Headless LibreOffice / Pandoc

Run headless LibreOffice or Pandoc as an external process to transform documents.

**Trade-offs:**
- Acts as a black box — difficult to control precise formatting outcomes
- Often destroys custom styles or fails on complex page setups
- Not suitable for the precision required by CA pleading paper format
- May be useful as a fallback for format conversion (e.g., converting `.odt` inputs) but not as the primary engine

### Option C: Word Automation via COM (Windows-only)

Drive Microsoft Word directly via the Windows COM interface.

**Trade-offs:**
- Requires Word to be installed — violates the offline-first, cross-platform mandate
- Fragile and platform-locked
- Not recommended

---

## 3. CLI Strategy

An initial Python CLI with a clear command structure:

```
doc-chameleon convert --input input.docx --jurisdiction ca --output output.docx
doc-chameleon validate --input output.docx --jurisdiction ca
doc-chameleon list-jurisdictions
```

The CLI is the MVP interface. It requires no GUI and can be tested rapidly with real documents.

---

## 4. Desktop Shell Strategy

### Option A: Tauri (Recommended for later phases)

Tauri wraps a web-based UI in a native Rust-compiled shell. Very small binary footprint. Requires writing a frontend in HTML/JS/CSS.

**Trade-offs:**
- Small, fast, offline-capable
- Requires maintaining a frontend and a backend bridge
- Good long-term fit for offline-first desktop

### Option B: Electron

More mature than Tauri, larger binary, same frontend approach.

**Trade-offs:**
- Larger distribution size
- Easier to find developers familiar with it
- Acceptable alternative if Tauri proves difficult

### Option C: Native Python GUI (Tkinter, PyQt, etc.)

Wrap the CLI logic in a Python-native GUI.

**Trade-offs:**
- Simpler bridge from CLI to GUI
- Less polished user experience
- Acceptable for early beta, not for a commercial product

---

## 5. Jurisdiction Rule-Pack Design

Each jurisdiction pack is an isolated Python module (or package) containing:
- Rule definitions and transformation logic
- Source metadata (`rules_meta.json`)
- A test suite of sample documents and expected outputs

Structure example:
```
rules/
├── ca/
│   ├── __init__.py
│   ├── transformer.py
│   ├── validator.py
│   └── rules_meta.json
├── tx/
│   ├── __init__.py
│   ├── transformer.py
│   ├── validator.py
│   ├── overlays/          ← Empty at MVP, reserved for local venue packs
│   └── rules_meta.json
```

This isolation ensures that adding a new jurisdiction does not require modifying core engine code.

---

## 6. Offline-First Storage Assumptions

- Document storage: local file system only
- Rule pack metadata: lightweight JSON files within each rule pack directory
- No database required at MVP
- Configuration (e.g., default jurisdiction, output paths): platform-appropriate config file (e.g., `~/.doc-chameleon/config.json`)

---

## 7. .docx-First Document Pipeline Summary

See also: [Discovery Batch 01](../discovery/discovery-batch-01-doc-chameleon.md)

```
[Input .docx]
     │
     ▼
[1. Ingest]         — Load and parse document structure (paragraphs, styles, sections)
     │
     ▼
[2. Normalize]      — Strip invalid styles, preserve semantic formatting
     │
     ▼
[3. Transform]      — Apply jurisdiction rule pack (CA or TX)
     │
     ▼
[4. Validate]       — Check output against rule constraints, generate warnings
     │
     ▼
[5. Export]         — Serialize to clean .docx + attach validation report
```

At each step, the intermediate representation remains structured and reversible. No step should silently destroy content.
