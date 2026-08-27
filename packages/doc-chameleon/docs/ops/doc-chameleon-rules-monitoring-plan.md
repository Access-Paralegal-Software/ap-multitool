---
id: doc-chameleon-rules-monitoring-plan
title: Rules Monitoring Plan
type: operations
status: active
project: doc-chameleon
created: 2026-05-20
---

# Rules Monitoring Plan — doc-chameleon

---

## Overview

Jurisdiction formatting rules change. This plan defines the workflow for tracking, evaluating, and integrating rule changes into jurisdiction packs. The guiding principle is: **no rule change goes into production without human review and explicit approval.**

---

## Source Classification

### Hard Authority (Primary Sources)
These are binding legal authorities. Only these sources can authorize changes to rule-pack logic.

| Jurisdiction | Source | URL / Notes |
|-------------|---------|-------------|
| California | Judicial Council of California — California Rules of Court | [courts.ca.gov](https://www.courts.ca.gov/rules.htm) |
| California | Superior Court local rules (by county) | Individual court websites |
| Texas | Texas Judicial Branch — Texas Rules of Civil Procedure (TRCP) | [txcourts.gov](https://www.txcourts.gov/rules-forms/rules-standards/) |
| Texas | Texas Supreme Court Orders and Rules | [txcourts.gov](https://www.txcourts.gov) |
| Texas | Local court rules (by county/venue) | Individual court websites |

### Secondary Guidance (Implementation Aids Only)
These sources may help interpret or implement rules but do not override hard authority.

| Source Type | Examples | Usage |
|-------------|----------|-------|
| Filing-vendor guidance | OneLegal, FileTime, Tyler EFile | Practical formatting tips, not binding |
| Law library practice notes | Research guides from courthouse or law school libraries | Context and common practice |
| Legal support training materials | Paralegal training handbooks | Workflow context only |

> **Rule:** If a secondary source conflicts with hard authority, hard authority wins. Secondary sources must never be cited as the basis for rule-pack logic.

---

## Rule Pack Metadata Schema

Each jurisdiction pack must include a `rules_meta.json` file tracking:

```json
{
  "jurisdiction_id": "ca_statewide",
  "display_name": "California Statewide",
  "version": "0.1.0",
  "last_reviewed_date": "2026-05-20",
  "effective_date": "2024-01-01",
  "primary_sources": [
    {
      "name": "California Rules of Court — Rule 2.108",
      "url": "https://www.courts.ca.gov/rules/index.cfm?title=two&linkid=rule2_108",
      "last_checked": "2026-05-20"
    },
    {
      "name": "California Rules of Court — Rule 2.111",
      "url": "https://www.courts.ca.gov/rules/index.cfm?title=two&linkid=rule2_111",
      "last_checked": "2026-05-20"
    }
  ],
  "change_log": [
    {
      "version": "0.1.0",
      "date": "2026-05-20",
      "summary": "Initial implementation of CA statewide baseline."
    }
  ]
}
```

---

## Monitoring Workflow

### Step 1 — Monitor
Routine review of hard authority sources for announced changes. Frequency: at minimum quarterly, or whenever a user reports a potential compliance issue.

### Step 2 — Triage
Determine whether the change affects formatting logic covered by an existing jurisdiction pack. Document the finding in the rule pack's change log draft.

### Step 3 — Impact Assessment
Assess the technical impact: Does this change require a new transformer rule? A modification to an existing validator? A metadata update only?

### Step 4 — Implement
Update the affected jurisdiction pack. Do not merge to the main branch yet.

### Step 5 — Review
Manual review by the project manager and/or a qualified legal subject-matter expert. The reviewer confirms:
- The change reflects hard authority only
- The implementation correctly captures the rule
- Test documents reflect the updated expected output

### Step 6 — Approve and Merge
Explicit written approval required before the updated pack is merged to the production branch.

### Step 7 — Publish
Update `rules_meta.json` with the new version, effective date, and change log entry. Release the updated pack.

---

## Failure Mode

If a rule change is identified but not yet implemented, the jurisdiction pack's `rules_meta.json` must flag this:

```json
"pending_changes": [
  {
    "summary": "Texas Supreme Court Misc. Docket No. XXXX — pending review",
    "identified_date": "2026-06-01",
    "status": "under_review"
  }
]
```

The CLI and desktop interface must surface this flag to users so they know the pack may be outdated.
