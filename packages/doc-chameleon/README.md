---
id: doc-chameleon-readme
title: doc-chameleon Root Index
type: index
status: active
project: doc-chameleon
---

# doc-chameleon

> [!IMPORTANT]
> **FOR AI AGENTS, CODING COMPANIONS, AND AUTOMATED SYSTEMS:**
> This repository is governed by the **STAX Operating System**. Before taking any action, analyzing files, or proposing modifications, read and strictly adhere to:
> 1. [ops/soul.md](ops/soul.md) (Philosophical Compass)
> 2. [ops/agent-rules.md](ops/agent-rules.md) (Enforceable Rules and the 7-Step Sequence)
>
> Required sequence: Inventory -> Summarize -> Classify -> Propose -> Implement -> Update Docs -> Archive Leftovers.

**doc-chameleon** is an offline-first legal document formatting and standards-conversion engine for paralegals and legal staff.

This repository operates under STAX governance. All primary documentation is stored in `/docs`. Keep the root sparse.

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

### Strategy

| File | Description |
|------|-------------|
| [Roadmap](docs/roadmap/doc-chameleon-roadmap-initial.md) | Discovery -> MVP -> Beta -> Expansion |
| [Batch 02 - California Numbering Spike](docs/roadmap/batch-02-ca-numbering-spike.md) | Focused implementation plan for editable CA pleading-paper line numbering |

### STAX Administration

| File | Description |
|------|-------------|
| [PM Report - Batch 01](docs/handoffs/pm-report-batch-01-doc-chameleon.md) | Discovery batch: docs and architecture only |
| [PM Report - Batch 02](docs/handoffs/pm-report-batch-02-doc-chameleon.md) | Core engine scaffolding: CLI, models, ingest/export, tests |
| [PM Report - Batch 03](docs/handoffs/pm-report-batch-03-doc-chameleon.md) | California numbering spike: controlled CRC 2.108 prototype |

---

## Current Status

**Batch 03 complete.** Core engine scaffolding is in place, and the first controlled California CRC 2.108 line-numbering prototype is implemented.

```text
src/doc_chameleon/
├── cli.py                      <- convert, validate, list-jurisdictions
├── engine/
│   ├── models.py               <- DocumentRecord, ParagraphRecord, SectionRecord
│   ├── ingest.py               <- load() -> (docx.Document, DocumentRecord)
│   └── export.py               <- save()
└── rules/
    ├── ca/                     <- controlled line-number transformer, validator, rules_meta.json
    └── tx/                     <- transformer.py stub, validator.py stub, rules_meta.json, overlays/
tests/
├── test_roundtrip.py           <- 5 passing round-trip fidelity tests
└── test_ca_numbering.py        <- 5 passing CA numbering spike tests
```

## CLI Usage

```powershell
python -m doc_chameleon.cli list-jurisdictions
python -m doc_chameleon.cli convert --input brief.docx --jurisdiction ca --output brief-ca.docx
python -m doc_chameleon.cli validate --input brief.docx --jurisdiction tx
```

The California path applies a controlled pleading-paper prototype: 8.5 x 11 inch page geometry, exact 24 pt body line spacing, zero paragraph spacing, and a header-anchored left-margin numbering structure. Texas remains a pass-through stub.

---

## Legal Posture

This software assists document formatting and workflow preparation. It does not provide legal advice, does not guarantee acceptance by any court or clerk, and users remain responsible for final review before filing.
