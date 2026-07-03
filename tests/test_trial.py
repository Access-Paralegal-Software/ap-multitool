import json
from datetime import datetime, timedelta, timezone

import pytest

from core.licensing import (
    TrialState,
    evaluate_access,
    get_machine_fingerprint,
    calculate_trial_signature,
)
from core.licensing_store import (
    load_or_start_trial,
    clear_trial,
    TRIAL_FILE_PATH,
)


@pytest.fixture(autouse=True)
def clean_trial():
    clear_trial()
    yield
    clear_trial()


def _now():
    return datetime.now(timezone.utc)


# --- TrialState ------------------------------------------------------------

def test_trial_active_within_window():
    started = (_now() - timedelta(days=3)).isoformat()
    trial = TrialState(started, get_machine_fingerprint())
    assert trial.is_active(14) is True
    assert trial.days_remaining(14) == 11


def test_trial_expired_after_window():
    started = (_now() - timedelta(days=20)).isoformat()
    trial = TrialState(started, get_machine_fingerprint())
    assert trial.is_active(14) is False
    assert trial.days_remaining(14) == 0


def test_trial_wrong_machine_is_inactive():
    started = (_now() - timedelta(days=1)).isoformat()
    trial = TrialState(started, "SOME-OTHER-MACHINE-UUID")
    assert trial.is_active(14) is False


# --- evaluate_access (pure decision) ---------------------------------------

def test_access_disabled_when_flag_off():
    # Paywall not yet rolled out: everyone gets through regardless of trial/license.
    decision = evaluate_access(licensed=False, trial=None, enforced=False, trial_duration_days=14)
    assert decision.allowed is True
    assert decision.reason == "disabled"


def test_access_licensed_when_enforced():
    decision = evaluate_access(licensed=True, trial=None, enforced=True, trial_duration_days=14)
    assert decision.allowed is True
    assert decision.reason == "licensed"


def test_access_trial_when_enforced_and_unlicensed():
    started = (_now() - timedelta(days=2)).isoformat()
    trial = TrialState(started, get_machine_fingerprint())
    decision = evaluate_access(licensed=False, trial=trial, enforced=True, trial_duration_days=14)
    assert decision.allowed is True
    assert decision.reason == "trial"
    assert decision.trial_days_remaining == 12


def test_access_blocked_when_trial_expired_and_unlicensed():
    started = (_now() - timedelta(days=30)).isoformat()
    trial = TrialState(started, get_machine_fingerprint())
    decision = evaluate_access(licensed=False, trial=trial, enforced=True, trial_duration_days=14)
    assert decision.allowed is False
    assert decision.reason == "trial_expired"


def test_access_license_beats_expired_trial():
    started = (_now() - timedelta(days=30)).isoformat()
    trial = TrialState(started, get_machine_fingerprint())
    decision = evaluate_access(licensed=True, trial=trial, enforced=True, trial_duration_days=14)
    assert decision.allowed is True
    assert decision.reason == "licensed"


# --- Trial persistence (store) ---------------------------------------------

def test_first_run_starts_trial_clock():
    assert not TRIAL_FILE_PATH.exists()
    trial = load_or_start_trial()
    assert trial is not None
    assert TRIAL_FILE_PATH.exists()
    assert trial.is_active(14) is True


def test_trial_clock_persists_across_loads():
    first = load_or_start_trial()
    second = load_or_start_trial()
    assert first.started_at == second.started_at


def test_tampered_trial_resets_clock():
    load_or_start_trial()

    with open(TRIAL_FILE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Backdate the start to fake an exhausted trial without re-signing.
    forged = (_now() - timedelta(days=999)).isoformat()
    data["trial"]["started_at"] = forged
    with open(TRIAL_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f)

    reloaded = load_or_start_trial()
    # Signature mismatch -> fresh trial issued, forged expiry rejected.
    assert reloaded.started_at != forged
    assert reloaded.is_active(14) is True


def test_trial_signature_changes_with_payload():
    fp = get_machine_fingerprint()
    t1 = TrialState(_now().isoformat(), fp)
    t2 = TrialState((_now() - timedelta(days=5)).isoformat(), fp)
    assert calculate_trial_signature(t1) != calculate_trial_signature(t2)


def test_trial_clock_rollback_resistance():
    started = _now().isoformat()
    trial = TrialState(started, get_machine_fingerprint())
    # System clock is set to 1 hour before trial started
    rollback_time = _now() - timedelta(hours=1)
    assert trial.is_active(14, now=rollback_time) is False
