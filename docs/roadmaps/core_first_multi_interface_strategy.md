---
title: "APMultitool Roadmap Update: Core-First Multi-Interface Strategy"
date: 2026-05-19
tags: [ap_multitool, roadmap, cli, "browser-local", interfaces, architecture]
status: active
project: "Access Paralegal"
---

# APMultitool Roadmap Update: Core-First Multi-Interface Strategy

## 0. Context

APMultitool is a local-first legal/document utility lane inside STAX. The current primary product surface is the desktop GUI, but the long-term direction should maximize compatibility and deployment flexibility without sacrificing privacy, local processing, or clear operational structure.

Recent progress has improved:

- Core operational patterns (cancellation, temp-file staging, progress).
- UI consistency and accessibility.
- Test harness foundations.
- The first major step in turning email processing into a core-engine operation.

The roadmap now formalizes a **core-first, multi-interface** strategy.

---

## 1. Interface Priority Order

### 1.1 Core engine / headless operations (current foundation)

All meaningful business logic should live in core operations with:

- Structured params.
- Structured results.
- Shared cancellation semantics.
- Shared temp-output staging.
- Shared progress reporting.

This is the enabling layer for every future interface.

---

### 1.2 Desktop GUI (current primary UX)

The existing desktop application remains the main user‑facing surface for now.

Purpose:

- Best current fit for rich local workflows.
- Lowest disruption to current users.
- Fastest path to shipping improvements while the core engine matures.

---

### 1.3 CLI interface (mid‑roadmap, high priority)

A cross‑platform CLI is now an explicit roadmap item.

Purpose:

- Enable automation and scripting.
- Support power users and IT/admin deployment workflows.
- Provide a thin interface over the same core operations used by the GUI.
- Improve portability across Windows, macOS, and Linux without committing to a full GUI rewrite.

Planned characteristics:

- One consistent command namespace (e.g. `apmultitool ...`).
- Subcommands mapping cleanly onto core operations:
  - `compile`
  - `bates`
  - `email-to-pdf`
  - future operations as needed
- Argument conventions that map directly to operation param objects.

This should be treated as the most realistic next interface after the current desktop GUI.

---

### 1.4 Browser‑delivered local‑first interface (late‑roadmap feasibility track)

A browser‑based local‑first surface is added to the roadmap as a **feasibility track**, not a rewrite commitment.

Goal:

- Explore whether a browser‑delivered shell (PWA, localhost‑backed web UI, or similar) could increase compatibility in locked‑down or IT‑managed environments.

Conditions for future pursuit:

- Local file workflows remain practical.
- Sensitive legal documents stay local unless explicitly designed otherwise.
- Performance and reliability remain acceptable for real‑world document tasks.

This is a late‑roadmap investigation, not an immediate implementation lane.

---

### 1.5 Mobile shells (very late / speculative)

Mobile interfaces (iOS/Android) are noted as speculative and should only be considered after:

- Core operations are mature.
- Desktop GUI and CLI are solid.
- A real mobile use case exists.

These are not active commitments.

---

## 2. Architectural Guardrail

All future work should reinforce this rule:

**Every new capability must be implemented first as a reusable core operation before it gains or changes any interface.**

That includes:

- GUI features.
- CLI features.
- Any future browser‑local shell.
- Any future mobile wrapper.

This avoids shadow systems and makes the product family portable without duplicating logic.

---

## 3. Immediate Implication for Current Work

The ongoing email‑to‑PDF refactor is now explicitly recognized as an enabling architecture milestone because it:

- Moves behavior out of a legacy direct‑call path.
- Makes the engine, not the GUI, the owner of the behavior.
- Creates the right foundation for both CLI support and future alternate frontends.

This pattern should be repeated for other important operations over time.

---
