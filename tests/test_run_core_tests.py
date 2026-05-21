from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


pytestmark = [pytest.mark.core]


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "run_core_tests.py"


def load_module():
    spec = importlib.util.spec_from_file_location("run_core_tests", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_fast_dry_run_targets_core_subset(capsys):
    module = load_module()

    exit_code = module.main(["--fast", "--dry-run"])

    out = capsys.readouterr().out
    assert exit_code == 0
    assert "-m core" in out


def test_list_subsets_prints_known_entries(capsys):
    module = load_module()

    exit_code = module.main(["--list-subsets"])

    out = capsys.readouterr().out
    assert exit_code == 0
    assert "all: (all tests)" in out
    assert "core: core" in out
    assert "qt: qt" in out


def test_extra_pytest_args_require_separator():
    module = load_module()

    with pytest.raises(SystemExit) as exc_info:
        module.main(["--subset", "core", "-q"])

    assert exc_info.value.code == 2
