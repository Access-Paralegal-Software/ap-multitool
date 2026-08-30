---
id: discovery-batch-01-doc-chameleon
title: Discovery Batch 01 — doc-chameleon
type: discovery
status: active
project: doc-chameleon
created: 2026-05-20
---

# Discovery Batch 01 — doc-chameleon

## 1. Repo Readiness & Intake

At the start of this batch the `doc-chameleon` repository was cloned as a completely empty repository. There was no pre-existing STAX structure, no documentation conventions, no YAML frontmatter patterns, and no index files. We initialized the full STAX-compliant folder structure from scratch with a sparse root and partitioned `/docs`.

**Baseline state before this batch:** Empty repository (only `.git`).

**State after this batch:**
```
doc-chameleon/
├── README.md
└── docs/
    ├── genesis/
    ├── discovery/
    ├── architecture/
    ├── ops/
    ├── roadmap/
    └── handoffs/
```

---

## 2. California Jurisdiction Rules Matrix

California is treated as the primary proof-of-concept jurisdiction. Its statewide formatting rules are unusually specific and must be implemented with structural precision, not approximation.

### California Rule of Court 2.111 — First-Page Requirements

| Element | Requirement | Implementation Consequence |
|---------|-------------|---------------------------|
| Attorney information block | Must appear in the upper-left of the first page | Requires precise margin and paragraph placement control in the `.docx` structure |
| Clerk space | A reserved blank area must appear on the right side of the first page | Must inject a blank right-column block or table structure — cannot be simulated with simple spacing |
| Case caption / court title | Must be positioned below the attorney block with specific alignment | Requires reliable paragraph-level style targeting |

### California Rule of Court 2.108 — Spacing and Line Numbering

| Element | Requirement | Implementation Consequence |
|---------|-------------|---------------------------|
| Left-margin line numbers | Consecutively numbered, beginning at 1 on each page | Must be injected at the Word structure level — not a margin decoration. Number alignment with body text is fragile |
| Spacing | Specific line-height rules that must align with numbered lines | Font size, line-height, and paragraph spacing must all be locked together to prevent drift |

### California Risk Notes

- Automated line number injection is the highest-fragility operation in the CA module. Even small font or margin changes by the end user can break visual alignment.
- The engine must emit warnings if the input document contains conflicting page-setup styles.
- California formatting is monolithic and statewide: there is no meaningful local variation for the pleading paper format itself, which simplifies the rule model.

---

## 3. Texas Jurisdiction Baseline Matrix

Texas must not be treated as a cosmetically reskinned version of California. The underlying formatting model is different, and the architecture must reflect that.

### Texas Statewide Baseline

The Texas Rules of Civil Procedure (TRCP) and the Texas Judicial Branch rules resources form the statewide baseline. These govern pleadings and filing standards at the state level.

Unlike California, Texas does not have a single dominant pleading-paper convention with prescriptive left-margin line numbering. Texas formatting is principally governed by content structure, caption requirements, and attorney certification requirements rather than a locked visual page format.

### Texas vs. California Comparison

| Dimension | California | Texas |
|-----------|------------|-------|
| Statewide formatting rules | Highly prescriptive and distinctive | Moderate — content and structure focused |
| Left-margin line numbers | Required (Rule 2.108) | Not required statewide |
| First-page layout | Tightly specified (Rule 2.111) | Caption and party block required, but layout is less prescriptive |
| Local rule variation | Minimal — statewide rules dominate | Significant — local rules matter and vary by venue |
| Architecture model | Monolithic statewide module | Statewide baseline with local-overlay capability |

### Texas Architecture Implication

Texas should be implemented as a layered package:
1. **Statewide baseline** — handles TRCP and Texas Judicial Branch requirements
2. **Local overlay slot** — reserved but empty at MVP. Future venue-specific packs (e.g., Harris County, Travis County) can slot in here

This is structurally different from California and must remain architecturally separate.

---

## 4. .docx-First Strategy

The canonical output of every conversion must be an editable `.docx` file. PDF is a secondary convenience export only.

**Rationale:** Paralegals need to review, adjust, and finalize documents after conversion. A hard PDF output removes that editability and creates a second round of reformatting work — defeating the purpose of the tool.

**Approach:** Direct manipulation of the OpenXML structure within the `.docx` container, rather than rendering to an intermediate format or painting a page layout. See the [Architecture Options doc](../architecture/doc-chameleon-architecture-options.md) for library evaluation.

---

## 5. Offline-First Implications

- No cloud sync, no SaaS backend, no network dependency for core function.
- All document processing occurs locally on the user's machine.
- Jurisdiction rule packs are installed locally and updated manually or via a controlled update workflow.
- This is non-negotiable for legal confidentiality reasons: client documents must not leave the user's machine.

---

## 6. CLI / Desktop / Tablet Roadmap Logic

| Phase | Interface | Rationale |
|-------|-----------|-----------|
| MVP | Python CLI | Fastest path to testing the core engine |
| Beta | Offline desktop app (Tauri or Electron) | Provides non-technical user access |
| Later | iPad and Android tablet | Courtroom and on-site use cases |
| Not planned | Web app | Conflicts with offline-first mandate; deferred indefinitely |

---

## 7. Rules Monitoring Approach

See the dedicated [Rules Monitoring Plan](../ops/doc-chameleon-rules-monitoring-plan.md). Key principle: rule changes never go into production automatically. Every change requires manual review and explicit approval.

---

## 8. Pricing and Packaging Direction

- **Base product:** California + Texas
- **Add-on packs:** Future states sold individually as paid expansions
- **Value proposition:** Time savings on manual reformatting, editable output preservation, local-first trust (no cloud)
- **Caution:** Must not overstate compliance guarantees. The product assists formatting; it does not certify filings.

---

## 9. Scope Boundaries

The following are explicitly out of scope and must not drift in:

- General legal AI assistant or chat interface
- Automated legal research or advice
- Direct court e-filing integration (at MVP)
- Cloud storage or SaaS backend
- Web application (not now, possibly never)
- Full local-rule coverage for Texas at MVP
