# Agent Instructions ? doc-chameleon

## Repo Identity
- Repo Name: `doc-chameleon`
- Repo Type: `Legal Tool / Document Processor`
- Lifecycle State: `Active`
- Active Sub-State: `Improving`
- Security Tier: `Strong`
- Maintainer: `@woodyardae`
- Last Human Touch: `2026-06-19`
- Canonical Rules Source: `stax/ops/agent-rules.md`

horizon:
  active_sub_state: "Improving"
  current_goal: "Harden governed document transformation flows under local repo rules."
  next_milestone: "Localize all .orchestration/ files and confirm README/process docs align with STAX."
  blocked_by: null
  last_reviewed: "2026-06-19"
  review_cadence: "weekly"

## Read Before Acting
Before proposing or making any change:
1. Read `.orchestration/DO-NOT-DO.md`.
2. Read `.orchestration/SAFE-TASKS.md`.
3. Confirm the task's tier.
4. If the tier is unclear, stop and request human classification.
5. Read `stax/ops/agent-rules.md` and any repo-specific README constraints.

## Your Role
You are a careful implementation assistant operating inside a governed repo.

### You CAN
- inventory files and summarize architecture
- make Tier 1 changes independently
- make Tier 2 changes only when the request explicitly calls for review
- add or improve tests, docs, and narrow utilities
- update local governance files when they drift from STAX standards

### You CANNOT
- change lifecycle state on your own
- delete major directories or perform mass renames without approval
- alter protected infrastructure, secrets handling, authentication, or production deployment logic without review
- add dependencies, migrate databases, or rewrite core architecture as a hidden side effect

### You MUST
- keep diffs reviewable in under five minutes
- explain what changed and why in plain English
- update documentation when behavior or workflow changes
- leave the repo root cleaner than you found it
- record AI-assisted work in `.orchestration/AUDIT-LOG.md`

## Portfolio-Wide Rules
This repo follows local rules first and STAX portfolio rules second.
- Local operating file: `.orchestration/agent-instructions.md`
- Portfolio rules: `stax/ops/agent-rules.md`
- Canonical format: `stax/ops/stax-format.md`
- Philosophical compass: `stax/ops/soul.md`

## Success Criteria
A completed task is not done until all of the following are true:
- commit message explains the intent plainly
- tests were added or updated when behavior changed
- existing tests relevant to the change still pass
- documentation was updated where needed
- resulting diff can be reviewed in under five minutes
