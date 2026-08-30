---
id: doc-chameleon-readme
title: doc-chameleon Root Index
type: index
status: active
project: doc-chameleon
---

> **STAX Format** ? Lifecycle: `Active ? Improving` ? Security: `Strong` ? [Governance](.orchestration/agent-instructions.md)

# doc-chameleon

> [!IMPORTANT]
> **FOR AI AGENTS, CODING COMPANIONS, AND AUTOMATED SYSTEMS:**
> This repository is governed by the **STAX Operating System**. Before taking any action, analyzing files, or proposing modifications, read and strictly adhere to:
> 1. [ops/soul.md](ops/soul.md) (Philosophical Compass)
> 2. [ops/agent-rules.md](ops/agent-rules.md) (Enforceable Rules and the 7-Step Sequence)
>
> Required sequence: Inventory -> Summarize -> Classify -> Propose -> Implement -> Update Docs -> Archive Leftovers.

**doc-chameleon** is an offline-first legal document formatting and standards-conversion engine for paralegals and legal staff.

Ingest an ordinary `.docx` working draft. Receive a jurisdiction-compliant, editable `.docx` output plus a conversion report. No cloud, no AI legal advice, no PDF-only output.

---

## Jurisdiction Status

| Code | Jurisdiction | Status | Rules Implemented |
|------|-------------|--------|-------------------|
| `ca` | California | Implemented | CRC 2.108 (line numbering), CRC 2.111 (first-page layout) |
| `tx` | Texas | Implemented | TRCP statewide baseline |

Texas local venue overlays (Harris County, Travis County, etc.) are architecturally reserved but not yet implemented.

---

## CLI Usage

```sh
# Show version
doc-chameleon --version

# List available jurisdictions and implementation status
doc-chameleon list-jurisdictions

# Convert a document to California pleading-paper format
doc-chameleon convert --input brief.docx --jurisdiction ca --output brief_ca.docx

# Convert a document to Texas statewide baseline format
doc-chameleon convert --input motion.docx --jurisdiction tx --output motion_tx.docx

# Validate a document against California formatting rules
doc-chameleon validate --input brief_ca.docx --jurisdiction ca

# Validate a document against Texas formatting rules
doc-chameleon validate --input motion_tx.docx --jurisdiction tx
```

`convert` always writes a companion `<output_stem>_report.txt` alongside the output `.docx`. The report lists all warnings and includes the legal posture disclaimer.

### Installation (development)

```sh
pip install -e ".[dev]"
pytest tests/
```

---

## What California Conversion Does

1. Locks page geometry: 8.5 Ã— 11 in, left margin 1.25 in, right/top/bottom 1 in.
2. Normalizes body style to Times New Roman 12 pt, exactly 24 pt line spacing, zero paragraph spacing.
3. Installs a header-anchored VML text box with 28 consecutively numbered lines in the left margin (CRC 2.108).
4. Enables a separate first-page header containing a borderless two-column attorney/clerk table (CRC 2.111). Attorney information is pre-filled with `[Placeholder]` text â€” the user fills in their details.
5. Warns on tables, embedded objects, non-standard spacing, and any post-transform geometry drift.

## What Texas Conversion Does

1. Sets page geometry: 8.5 Ã— 11 in, 1 in margins all sides.
2. Normalizes body style to Times New Roman 12 pt, double-spaced, zero paragraph spacing.
3. Validates that a court caption is present in the opening paragraphs.
4. Always notes that output reflects statewide baseline only â€” local venue rules are not applied.

---

## Project Structure

```
src/doc_chameleon/
â”œâ”€â”€ __init__.py                 <- __version__
â”œâ”€â”€ cli.py                      <- convert, validate, list-jurisdictions, --version
â”œâ”€â”€ engine/
â”‚   â”œâ”€â”€ models.py               <- DocumentRecord, ParagraphRecord, SectionRecord
â”‚   â”œâ”€â”€ ingest.py               <- load() -> (docx.Document, DocumentRecord)
â”‚   â”œâ”€â”€ export.py               <- save()
â”‚   â””â”€â”€ report.py               <- write_report() -> companion _report.txt
â””â”€â”€ rules/
    â”œâ”€â”€ ca/
    â”‚   â”œâ”€â”€ transformer.py      <- CRC 2.108 line-number transform
    â”‚   â”œâ”€â”€ transformer_2111.py <- CRC 2.111 first-page layout transform
    â”‚   â”œâ”€â”€ validator.py        <- CA geometry, structure, cross-layer checks
    â”‚   â””â”€â”€ rules_meta.json
    â””â”€â”€ tx/
        â”œâ”€â”€ transformer.py      <- TRCP statewide baseline transform
        â”œâ”€â”€ validator.py        <- TX geometry, caption check, statewide disclaimer
        â”œâ”€â”€ rules_meta.json
        â””â”€â”€ overlays/           <- reserved for future local venue packs

tests/
â”œâ”€â”€ fixtures.py                 <- synthetic document factories (motion, declaration, notice, cover_page, hostile, tx_motion, tx_notice)
â”œâ”€â”€ test_roundtrip.py           <- 5 ingest/export fidelity tests
â”œâ”€â”€ test_ca_numbering.py        <- 5 CRC 2.108 structural tests
â”œâ”€â”€ test_ca_fixtures.py         <- 10 CA fixture + report tests
â”œâ”€â”€ test_ca_2111.py             <- 9 CRC 2.111 first-page tests
â”œâ”€â”€ test_tx_baseline.py         <- 12 TX baseline tests
â””â”€â”€ test_e2e_smoke.py           <- 12 end-to-end smoke tests (CA + TX, all fixtures)
```

**53 tests, all passing.**

---

## Documentation Index

### Discovery and Planning

| File | Description |
|------|-------------|
| [Genesis Brief](docs/genesis/doc-chameleon-genesis-brief.md) | Project identity, mission, and MVP definition |
| [Discovery Batch 01](docs/discovery/discovery-batch-01-doc-chameleon.md) | Repo intake, CA/TX rules matrix, scope boundaries |

### Architecture and Operations

| File | Description |
|------|-------------|
| [Architecture Options](docs/architecture/doc-chameleon-architecture-options.md) | Technical strategy, .docx-first pipeline, trade-offs |
| [Risk Register](docs/ops/doc-chameleon-risk-register.md) | Known risks and mitigations |
| [Rules Monitoring Plan](docs/ops/doc-chameleon-rules-monitoring-plan.md) | Workflow for tracking jurisdiction rule updates |
| [Roadmap](docs/roadmap/doc-chameleon-roadmap-initial.md) | Discovery â†’ MVP â†’ Beta â†’ Expansion |

### Batch PM Reports

| Batch | Description |
|-------|-------------|
| [Batch 01](docs/handoffs/pm-report-batch-01-doc-chameleon.md) | Discovery: docs and architecture only |
| [Batch 02](docs/handoffs/pm-report-batch-02-doc-chameleon.md) | Core engine scaffolding: CLI, models, ingest/export |
| [Batch 03](docs/handoffs/pm-report-batch-03-doc-chameleon.md) | CRC 2.108 line-numbering spike |
| [Batch 04](docs/handoffs/pm-report-batch-04-doc-chameleon.md) | Fixtures, conversion report, strategy comparison |
| [Batch 05](docs/handoffs/pm-report-batch-05-doc-chameleon.md) | CRC 2.111 first-page attorney/clerk layout |
| [Batch 06](docs/handoffs/pm-report-batch-06-doc-chameleon.md) | Texas statewide baseline transformer |
| [Batch 07](docs/handoffs/pm-report-batch-07-doc-chameleon.md) | CLI polish, --version, e2e smoke tests, README |

---

## Legal Posture

This software assists document formatting and workflow preparation. It does not provide legal advice, does not guarantee acceptance by any court or clerk, and users remain responsible for final review before filing. Jurisdiction packs may lag newly adopted rules pending manual review and release.
