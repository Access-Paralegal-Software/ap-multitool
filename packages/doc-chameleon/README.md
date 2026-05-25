---
id: doc-chameleon-readme
title: doc-chameleon Root Index
type: index
status: active
project: doc-chameleon
---

# doc-chameleon


> [!IMPORTANT]
> **🤖 FOR AI AGENTS, CODING COMPANIONS, AND AUTOMATED SYSTEMS:**
> This repository is governed by the **STAX Operating System**. Before taking *any* action, analyzing files, or proposing modifications, you **must** read and strictly adhere to:
> 1. [ops/soul.md](ops/soul.md) (Philosophical Compass)
> 2. [ops/agent-rules.md](ops/agent-rules.md) (Enforceable Rules & the 7-Step Sequence)
>
> You are required to run through the **Inventory ➔ Summarize ➔ Classify ➔ Propose ➔ Implement ➔ Update Docs ➔ Archive Leftovers** sequence for every run.



**doc-chameleon** is an offline-first legal document formatting and standards-conversion engine for paralegals and legal staff.

This repository operates under STAX governance. All primary documentation is stored in `/docs`. Keep the root sparse.

---

## Documentation Index

### Discovery & Planning
| File | Description |
|------|-------------|
| [Genesis Brief](docs/genesis/doc-chameleon-genesis-brief.md) | Project identity, mission, and MVP definition |
| [Discovery Batch 01](docs/discovery/discovery-batch-01-doc-chameleon.md) | Repo intake, CA/TX rules matrix, scope boundaries |

### Architecture & Operations
| File | Description |
|------|-------------|
| [Architecture Options](docs/architecture/doc-chameleon-architecture-options.md) | Technical strategy, .docx-first pipeline, trade-offs |
| [Risk Register](docs/ops/doc-chameleon-risk-register.md) | Known risks and mitigations |
| [Rules Monitoring Plan](docs/ops/doc-chameleon-rules-monitoring-plan.md) | Workflow for tracking jurisdiction rule updates |

### Strategy
| File | Description |
|------|-------------|
| [Roadmap](docs/roadmap/doc-chameleon-roadmap-initial.md) | Discovery → MVP → Beta → Expansion |

### STAX Administration
| File | Description |
|------|-------------|
| [PM Report — Batch 01](docs/handoffs/pm-report-batch-01-doc-chameleon.md) | Discovery batch — docs and architecture only |
| [PM Report — Batch 02](docs/handoffs/pm-report-batch-02-doc-chameleon.md) | Core engine scaffolding — CLI, models, ingest/export, tests |

---

## Current Status

**Batch 02 complete.** Core engine scaffolding is in place. No jurisdiction formatting rules are implemented yet.

```
src/doc_chameleon/
├── cli.py                      ← convert, validate, list-jurisdictions
├── engine/
│   ├── models.py               ← DocumentRecord, ParagraphRecord, SectionRecord
│   ├── ingest.py               ← load() → (docx.Document, DocumentRecord)
│   └── export.py               ← save()
└── rules/
    ├── ca/                     ← transformer.py stub, validator.py stub, rules_meta.json
    └── tx/                     ← transformer.py stub, validator.py stub, rules_meta.json, overlays/
tests/
└── test_roundtrip.py           ← 5 passing round-trip fidelity tests
```

### CLI Usage (scaffolding — no rules applied yet)

```
python -m doc_chameleon.cli list-jurisdictions
python -m doc_chameleon.cli convert --input brief.docx --jurisdiction ca --output brief-ca.docx
python -m doc_chameleon.cli validate --input brief.docx --jurisdiction tx
```

---

## Legal Posture
This software assists document formatting and workflow preparation. It does not provide legal advice, does not guarantee acceptance by any court or clerk, and users remain responsible for final review before filing.
