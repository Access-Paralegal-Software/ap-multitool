---
repo_name: ap-multitool-portal
repo_type: Tool Portal / Front-end
security_tier: 2
lifecycle: "Active ? Planning"
updated: "2026-06-19"
---

# Agent Instructions ? ap-multitool-portal

## Security Tier: Strong (2)
Standard agent autonomy. All work via PR ? never push directly to main. No secrets in code or commit messages.

## What this repo does
Portal and UI layer for ap-multitool.

## Cluster
Legal Tools

## Upstream dependencies
ap-multitool services and APIs

## Downstream consumers
Legal tool users and operators

## Active horizon
```yaml
horizon:
  goal: "Apply STAX Format Wave 2 governance to ap-multitool-portal and establish baseline agent rules"
  active_sub_state: "Planning"
  next_milestone: "First productive agent task under governance in ap-multitool-portal"
  blockers: []
```

## Agent rules
1. Read this file before any action in this repo.
2. All changes via PR to main. No direct pushes.
3. No credentials, tokens, or secrets in any file tracked by git.
4. Portfolio-wide rules: `stax/ops/stax-format.md`
5. If uncertain about scope, check `stax/handoffs/handoff-current.md` for orchestration context.
