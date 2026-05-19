# 🏁 APMultitool: Definition of Done (DoD) for Rename & Polish Phase

This document establishes the final, non-negotiable checklist that must be satisfied before the repository is formally declared **ready for renaming, packaging, and visual restyling**.

---

## 📋 1. Root & Directory Cleanliness
- [ ] **Sacred Sparse Root**: Root directory contains only active product code (`gui_apmultitool.py`, `config.py`), primary configuration specs (`ap_multitool.spec`, `installer.iss`), and the navigational gatekeeper `README.md`.
- [ ] **Sandbox Isolation**: All experimental scripts, manual testing harness suites, and license generation files are relocated to `scratch/`.
- [ ] **Legacy Preservation**: Stale/deprecated individual script processors (e.g. older `eml_to_pdf.py` or `outlook_to_pdf.py` modules) are archived under `archive/legacy/` to maintain history.
- [ ] **Out-of-Scope Decommissioning**: Legacy mobile/tablet directories (`access_tablet_suite/`) and loose zip attachments are moved to `archive/`.

---

## 🔤 2. Unified Naming Prep
- [ ] **Consistent Global Variable**: `config.APP_NAME` is renamed to `"APMultitool"` (or `"AP Multitool"`).
- [ ] **User-Facing Label Audits**: Every Tkinter label, header widget, and about window has been audited to confirm no dangling instances of "Access Paralegal PDF Merger" exist.
- [ ] **Dynamic Paths Updated**: Defaults for input/output folders and temporary data directories point to `ap_outputs/` rather than legacy paths.
- [ ] **Installer Registry Keys Prepared**: App paths inside `installer.iss` point to the new `{autopf}\APMultitool` location.

---

## 🔒 3. Sovereign Security Integrity
- [ ] **Motherboard UUID Hashing Preserved**: Cryptographic WMIC salt checks are untouched to guarantee existing offline locked databases and case vaults remain decipherable.
- [ ] **Keygen Account Tokens Untouched**: Online Keygen.sh account IDs and product credentials are preserved in full to prevent license activation failures.

---

## 📑 4. High-Fidelity Documentation
- [ ] **Docs Index Operational**: `docs/README.md` is complete and lists clickable `file:///` pathways to every specification, manual, and strategic research note in the repository.
- [ ] **Handoff Provenance Up-to-Date**: Sprints are fully cataloged under `docs/handoffs/` with comprehensive task summaries.
- [ ] **STAX CLI Indexed**: The central STAX properties scanner database registers no errors or un-indexed markdown targets.

---

*System State: STAX ALIGNED | Phase: RENAME PREPARATION CHECKLIST ACTIVE*
