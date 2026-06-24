---
id: ho_0042_2026_06_24_trial_license_paywall
title: Handoff - P1 First-Dollar Trial + License Paywall (feature-flagged)
type: handoff
status: completed
project: APMultitool
lane: licensing-paywall
created_at: 2026-06-24
---

# Trial + License Paywall Handoff

## Purpose

Ship the P1 "first-dollar" slice: a trial-then-license access gate behind a
feature flag, layered on top of the existing (license-only) entitlement
boundary. The gate ships **dark** — unlicensed users are never blocked until
the rollout flag is flipped on.

## What changed

- `config.py` — added two settings:
  - `PAYWALL_ENFORCED` (env `APM_PAYWALL_ENFORCED`, default **off**) — rollout flag.
  - `TRIAL_DURATION_DAYS` (env `APM_TRIAL_DAYS`, default **14**).
- `core/licensing.py` — added `TrialState` (machine-bound, started on first run),
  `calculate_trial_signature`, `AccessDecision`, and the pure `evaluate_access()`
  decision: rollout flag → license → active trial → blocked. Also fixed a missing
  `timedelta` import.
- `core/licensing_store.py` — added tamper-evident, machine-bound trial persistence
  (`load_or_start_trial`, `clear_trial`, `TRIAL_FILE_PATH` at
  `~/.access_paralegal_trial.json`). A missing/tampered/foreign trial file fails
  **open** (fresh clock issued) rather than locking out a legitimate user.
- `apmultitool_qt/security.py` — `VaultSecurityManager` now exposes
  `access_granted` / `access_reason` / `trial_days_remaining` via `_evaluate_access()`,
  combining license state + trial clock + flag. Re-evaluated after `activate_license`.
- `apmultitool_qt/shell.py` — launch gate now keys on `vault.access_granted`
  (license OR active trial OR flag-off) and surfaces "Free trial — N days remaining".
- `tests/test_trial.py` — 12 new tests (TrialState, evaluate_access, signed
  persistence + tamper reset).

## Decision model

| Flag | License | Trial | Result |
|------|---------|-------|--------|
| off  | any     | any   | granted (`disabled`) — ships dark |
| on   | valid   | any   | granted (`licensed`) |
| on   | none    | active| granted (`trial`, N days) |
| on   | none    | expired| **blocked** (`trial_expired`) |

## Validation

- `pytest tests/test_trial.py tests/test_licensing.py tests/test_qt_license_gate.py` → **27 passed**.
- Full fast suite (`-m "not slow and not libreoffice and not integration*"`) → **108 passed**.
- End-to-end `VaultSecurityManager` probe: flag-off → granted/disabled;
  flag-on fresh → granted/trial/14d; flag-on exhausted → blocked/trial_expired.

## Follow-ups (not in this slice)

- Server side `/v1/license/verify` is assumed; trial has no server component (local clock).
- No in-app "buy / upgrade" CTA yet — expired-trial path reuses the activation dialog.
- Trial clock is local-only; a determined user can reset by deleting the signed
  file. Acceptable for first-dollar; server-anchored trials are a later hardening.
