---
id: doc-chameleon-roadmap-initial
title: Initial Roadmap
type: roadmap
status: active
project: doc-chameleon
created: 2026-05-20
---

# doc-chameleon Roadmap

> This roadmap reflects deliberate phasing. Phases are not unlocked until explicitly authorized by a STAX batch.

---

## Phase 1: Discovery *(Current — Batch 01)*

**Goal:** Establish the repository, define architecture options, document jurisdiction constraints, and identify risks before any implementation begins.

**Deliverables:**
- Genesis brief
- Repo structure initialized
- CA/TX jurisdiction rules matrices
- Architecture options memo
- Risk register
- Rules monitoring plan
- Initial roadmap

**Interface:** None — documentation only.

---

## Phase 2: MVP

**Goal:** A functional Python CLI capable of ingesting a `.docx` and producing a jurisdiction-formatted `.docx` output with a validation report.

**Scope:**
- California Rule 2.108 line-number injection
- California Rule 2.111 first-page format
- Texas statewide baseline formatting (TRCP-aligned)
- Validation step with warning output
- CLI with `convert`, `validate`, and `list-jurisdictions` commands
- Conversion report (human-readable warnings appended to output or exported as a companion file)
- Common litigation documents: motions, declarations, notices, oppositions

**Interface:** CLI only.

**What MVP does not include:**
- GUI or desktop shell
- Local Texas venue overlays
- PDF export (may be added as convenience feature late in phase)
- Any cloud connectivity

---

## Phase 3: Beta

**Goal:** Transition from CLI-only to an offline-first desktop application usable by non-technical legal staff.

**Scope:**
- Desktop shell wrapping the core Python engine (Tauri or Electron — to be decided in a future batch)
- File picker, jurisdiction selector, and warnings display
- User testing with paralegals and legal support staff
- Initial local Texas venue overlay (one or two pilot venues based on user feedback)
- Improved validation reporting

**Interface:** Desktop application (Windows primary, macOS secondary).

---

## Phase 4: Expansion

**Goal:** Broaden jurisdiction coverage and extend platform support based on validated demand.

**Scope:**
- Additional U.S. state rule packs (sold as paid add-ons)
- Expanded Texas local venue overlays
- iPad support
- Android tablet support
- macOS and Linux desktop parity

**Interface:** Desktop + Tablet.

---

## Not Planned / Out of Scope

| Item | Status | Notes |
|------|--------|-------|
| Web application | Not planned | Conflicts with offline-first mandate |
| AI legal assistant | Never | Out of scope by design |
| Direct court e-filing | Deferred | May be explored post-Expansion |
| Automatic rule updates | Never | Manual review required before any rule-pack change |
