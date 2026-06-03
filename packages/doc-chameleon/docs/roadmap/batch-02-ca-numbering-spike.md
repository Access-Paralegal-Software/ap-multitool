---
id: batch-02-ca-numbering-spike
title: Batch 02 - California Numbering Spike
type: roadmap
status: proposed
project: doc-chameleon
created: 2026-06-02
---

# Batch 02 - California Numbering Spike

## Objective

Batch 02 should keep a tight focus on the hardest technical problem in the product: editable California pleading-paper line numbering.

The batch should still create the minimum Python engine scaffold needed to test `.docx` input and output, but every implementation choice should be judged by whether it helps prove a reliable California numbering strategy. Generic framework work, desktop UI work, and broad jurisdiction expansion should wait.

## Primary Success Standard

Given a controlled synthetic `.docx` fixture, the engine can produce an editable `.docx` with California-style line numbers that remain structurally inspectable and visually aligned under known page, margin, font, and line-height constraints.

This does not require full legal-document conversion yet. It requires a credible line-numbering mechanism that can become the foundation for California Rule of Court 2.108 support.

## Scope

- Initialize a minimal Python project structure.
- Add a small CLI entrypoint only if it helps exercise the spike.
- Build `.docx` ingest and export around `python-docx` plus direct OpenXML access where needed.
- Generate synthetic test documents for controlled cases.
- Implement a California pleading-paper layout prototype.
- Test at least one line-numbering strategy against generated `.docx` output.
- Emit warnings when input structure is incompatible with controlled numbering assumptions.
- Document which assumptions are required for alignment to hold.

## Out of Scope

- Desktop application shell.
- Texas formatting implementation.
- Additional state rule packs.
- Full California first-page caption automation.
- Real client document ingestion.
- PDF export.
- Cloud or web behavior.

## Candidate Numbering Strategies

The spike should compare strategies by editability, Word compatibility, implementation complexity, and alignment stability.

| Strategy | Description | Likely Role |
|---|---|---|
| Positioned text boxes or frames | Inject left-margin line numbers in a positioned structure anchored to the page. | Strong candidate if Word preserves editability and alignment. |
| Header-based left-margin structure | Place repeated numbering structure in page header with fixed positioning. | Strong candidate for page-repeat behavior, but must be tested for body-text alignment. |
| Left-column table layout | Represent each numbered page as a two-column structure: narrow numbering column plus body column. | Useful for controlled output, but may be invasive for existing documents. |
| Paragraph-level numbering | Apply numbering to body paragraphs directly. | Likely insufficient because California line numbers refer to page lines, not logical paragraphs. |

The batch should avoid pretending there is only one answer before testing. The deliverable is a chosen implementation direction with evidence.

## Fit-Into-California Pipeline

Other input formats and document styles should not each invent their own California formatter. They should normalize into a shared California layout pipeline:

```text
Input .docx
  -> ingest document structure
  -> classify layout complexity
  -> normalize supported content into a controlled body flow
  -> apply California page geometry
  -> apply California line-number system
  -> validate alignment assumptions and unsupported structures
  -> export editable .docx plus warnings
```

The key design point is that "fit other formats into this" means converting supported document shapes into the controlled California body flow before numbering is applied. The numbering layer should not need to understand every source style.

## Supported Format Classes for Early Testing

Batch 02 should use synthetic fixtures for these classes:

- Plain motion-style body text with headings and paragraphs.
- Declaration-style numbered paragraphs.
- Notice-style short filing with sparse text.
- A hostile fixture with tables, images, or manual spacing overrides that should trigger warnings rather than silent conversion.

## Validation Requirements

The validator should check and report:

- Page size.
- Margins.
- Body font size.
- Exact line spacing.
- Paragraph spacing before and after.
- Section breaks.
- Tables, images, text boxes, embedded objects, or other layout-affecting elements.
- Whether the document appears to require manual review before filing.

## Deliverables

- Minimal Python project scaffold.
- Synthetic `.docx` fixture generator or committed test fixtures.
- Prototype California line-numbering implementation.
- Tests that inspect generated `.docx` structure.
- A short implementation report documenting:
  - chosen numbering strategy,
  - strategies rejected,
  - known failure modes,
  - assumptions required for alignment,
  - next steps for full California Rule 2.108 support.

## Exit Criteria

Batch 02 is complete when the project can demonstrate one reliable California numbering path for controlled documents and can clearly warn when a source document falls outside the supported shape.

