---
id: doc-chameleon-genesis-brief
title: doc-chameleon Genesis Brief
type: genesis
status: active
project: doc-chameleon
created: 2026-05-20
---

# doc-chameleon Genesis Brief

## Project Identity

**Codename:** doc-chameleon
**Repo:** [woodyardae/doc-chameleon](https://github.com/woodyardae/doc-chameleon)
**Parent environment:** STAX, with STAX rules in force for planning, implementation discipline, documentation hygiene, and mandatory PM reports after every batch completion.

## Mission

Build an offline-first legal document formatting engine for paralegals and legal staff that converts ordinarily formatted working documents into jurisdiction-compliant litigation-ready formatting while preserving editability in Word-compatible formats. The launch jurisdictions are California and Texas, with future jurisdictions sold as add-on rule packs.

This product is not a general legal AI assistant. It is a document standards conversion and workflow preparation tool focused on practical legal production work.

## Day-One Jurisdiction Scope

### California

California is the primary proof-of-concept jurisdiction because its statewide formatting rules are highly distinctive. California Rule of Court 2.111 governs first-page format, including placement of attorney information, clerk-space reservation, and court title positioning. California Rule of Court 2.108 governs spacing and consecutively numbered lines on the left margin, beginning with line 1 on each page.

### Texas

Texas must be included from day one, but its implementation should not be treated as a clone of California. Texas statewide rules and rules resources provide the baseline, while important pleading and formatting practices may also depend on local court rules and venue-specific overlays. Texas should therefore be implemented as a statewide baseline jurisdiction package with architecture ready for future local overlays.

## Core Product Principles

- Offline first, with local processing as the default operating mode.
- Editable output first, with `.docx` or equivalent editable artifacts as the canonical result.
- Human-review centered, with visible warnings, assumptions, and unresolved formatting issues.
- CLI and desktop-first roadmap, with Linux and macOS in scope and tablet interfaces planned later.
- Jurisdiction-pack architecture from the beginning, rather than a pile of one-off templates.

## MVP Definition

The MVP should ingest `.docx` legal working documents, apply jurisdiction-specific formatting transformations for California or Texas, and export editable `.docx` outputs along with a conversion report. Initial supported document classes should include common litigation papers such as motions, declarations, notices, oppositions, and similar text-heavy filings.

PDF export may exist as a secondary convenience feature, but PDF should not be the primary or only working output.

## Architecture Direction

The system should separate:
- document ingestion and parsing
- style normalization
- layout transformation
- validation and warning generation
- jurisdiction rules packages
- rules metadata/versioning
- CLI execution
- desktop application shell

The system should prefer direct manipulation of Word-compatible document structure over brittle page-painting or PDF-style rendering approaches, especially for California line numbering and editable pleading output.

## Rule Monitoring and Compliance Updates

Each jurisdiction package should track authoritative sources, last-reviewed dates, effective dates, change history, and publication status. Rule changes should not automatically go into production without human review.

Sources must be separated into:
- **Hard authority:** judicial branch rules, official court rules, official forms, filing specifications.
- **Secondary guidance:** filing-vendor guidance, law-library practice notes, and legal support training materials used as implementation aids rather than authoritative legal rules.

## Legal Posture

The product and documentation should consistently state that:
- the software assists document formatting and workflow preparation
- it does not provide legal advice
- it does not guarantee acceptance by every court or clerk
- users remain responsible for final review before filing
- jurisdiction packs may lag newly adopted or locally implemented changes pending review and release

## Commercial Framing

Base product includes California and Texas. Additional states sold as paid rule-pack expansions. This matches the maintenance burden of jurisdiction-specific logic and creates a recurring value model tied to rule upkeep.

## Product Success Standard

The first real success state is a credible local application that lets a paralegal take an ordinary working `.docx`, choose California or Texas, run a local conversion, receive an editable output plus warnings, and save meaningful time compared with manual reformatting while retaining confidence in the resulting working draft.
