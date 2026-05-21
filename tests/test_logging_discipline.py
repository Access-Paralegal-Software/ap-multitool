from __future__ import annotations

import importlib
import zipfile
from pathlib import Path
from unittest import mock


def test_get_logger_uses_apmultitool_prefix(monkeypatch, tmp_path):
    log_path = tmp_path / "apmultitool.log"
    monkeypatch.setenv("APMULTITOOL_LOG_FILE", str(log_path))

    import core.logging_config as logging_config

    logging_config = importlib.reload(logging_config)
    logging_config.configure_logging(force=True)
    logger = logging_config.get_logger("core.conversion")
    logger.info("logger_test")
    logging_config.flush_handlers()

    assert logger.name == "apmultitool.core.conversion"
    assert log_path.exists()
    assert "apmultitool.core.conversion INFO logger_test" in log_path.read_text(encoding="utf-8")


def test_safe_filename_removes_sensitive_path_segments():
    from core.logging_config import safe_filename

    assert safe_filename(r"C:\Users\tester\Client-Alpha\Matter-123\report.docx") == "report.docx"


def test_run_soffice_convert_logs_redacted_filename(monkeypatch, tmp_path):
    log_path = tmp_path / "apmultitool.log"
    monkeypatch.setenv("APMULTITOOL_LOG_FILE", str(log_path))

    import core.logging_config as logging_config
    import core.operations._conversion_backend as conversion_backend

    logging_config = importlib.reload(logging_config)
    conversion_backend = importlib.reload(conversion_backend)
    logging_config.configure_logging(force=True)

    src_dir = tmp_path / "Client-Alpha" / "Matter-123"
    src_dir.mkdir(parents=True)
    src = src_dir / "report.docx"
    src.write_bytes(b"fake content")
    out = tmp_path / "result.pdf"

    def fake_run(cmd, **kwargs):
        out_dir = Path(cmd[cmd.index("--outdir") + 1])
        (out_dir / "report.pdf").write_bytes(b"%PDF-1.4 minimal")
        return mock.MagicMock(returncode=0)

    with mock.patch("subprocess.run", side_effect=fake_run):
        conversion_backend.run_soffice_convert(src, out)

    logging_config.flush_handlers()
    content = log_path.read_text(encoding="utf-8")
    assert "report.docx" in content
    assert "Client-Alpha" not in content
    assert "Matter-123" not in content


def test_support_bundle_copies_log_and_telemetry(monkeypatch, tmp_path):
    log_path = tmp_path / "apmultitool.log"
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    telemetry_path = tmp_path / ".access_paralegal_telemetry.json"
    telemetry_path.write_text(
        '{"build_id":"v1","total_runs":0,"success_runs":0,"failed_runs":0,"cancelled_runs":0,"operations":{},"last_error":"","last_error_time":""}',
        encoding="utf-8",
    )
    monkeypatch.setenv("APMULTITOOL_LOG_FILE", str(log_path))

    import core.logging_config as logging_config
    import core.support as support

    logging_config = importlib.reload(logging_config)
    support = importlib.reload(support)
    logging_config.configure_logging(force=True)
    logging_config.get_logger("support.bundle.test").info("bundle_test_message")
    logging_config.flush_handlers()

    bundle_path = support.create_support_bundle(target_dir=tmp_path, display_scaling="100%")

    assert bundle_path.exists()
    assert bundle_path.suffix == ".zip"
    with zipfile.ZipFile(bundle_path) as bundle_zip:
        names = set(bundle_zip.namelist())
    assert "telemetry.json" in names
    assert "metadata.json" in names
    assert any(name.startswith("logs/apmultitool.log") for name in names)
