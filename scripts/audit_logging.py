"""Audit logging and direct diagnostic output usage.

Scans the core engine, Qt layer, CLI, and legacy email processing module for
direct print calls, logging.basicConfig usage, and logger usage. This script is
read-only and does not import application modules.

Usage:
    python scripts/audit_logging.py
    python scripts/audit_logging.py --json
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SCAN_TARGETS = [
    REPO_ROOT / "packages" / "ap-core" / "src" / "ap_core",
    REPO_ROOT / "apps" / "desktop" / "apmultitool_qt",
    REPO_ROOT / "apps" / "cli" / "src" / "ap_cli" / "main.py",
]

LOGGER_METHODS = {"debug", "info", "warning", "warn", "error", "exception", "critical"}


def layer_for(path: Path) -> str:
    relative = path.relative_to(REPO_ROOT).as_posix()
    if relative.startswith("packages/ap-core/src/ap_core/"):
        return "core"
    if relative.startswith("apps/desktop/apmultitool_qt/"):
        return "qt"
    if relative == "apps/cli/src/ap_cli/main.py":
        return "cli"
    return "unknown"


def severity_for(layer: str, finding_type: str, detail: str) -> str:
    if finding_type == "logging.basicConfig":
        return "high"
    if finding_type == "print":
        if layer == "core":
            return "high"
        if layer == "qt":
            return "medium"
        return "low"
    if finding_type == "logger_call":
        if detail in {"error", "exception", "critical"}:
            return "medium"
        if detail in {"warning", "warn"}:
            return "low"
    return "info"


def call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = call_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    return ""


def iter_python_files(targets: list[Path]) -> list[Path]:
    files: list[Path] = []
    for target in targets:
        if target.is_file() and target.suffix == ".py":
            files.append(target)
        elif target.is_dir():
            files.extend(path for path in target.rglob("*.py") if "__pycache__" not in path.parts)
    return sorted(files)


def add_finding(findings: list[dict[str, Any]], path: Path, node: ast.AST, finding_type: str, detail: str) -> None:
    layer = layer_for(path)
    findings.append(
        {
            "path": path.relative_to(REPO_ROOT).as_posix(),
            "line": getattr(node, "lineno", 0),
            "column": getattr(node, "col_offset", 0),
            "layer": layer,
            "severity": severity_for(layer, finding_type, detail),
            "type": finding_type,
            "detail": detail,
        }
    )


def audit_file(path: Path) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
    except (OSError, SyntaxError, UnicodeDecodeError) as exc:
        return [
            {
                "path": path.relative_to(REPO_ROOT).as_posix(),
                "line": 0,
                "column": 0,
                "layer": layer_for(path),
                "severity": "high",
                "type": "parse_error",
                "detail": str(exc),
            }
        ]

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        name = call_name(node.func)
        if name == "print":
            add_finding(findings, path, node, "print", "direct print call")
        elif name == "logging.basicConfig":
            add_finding(findings, path, node, "logging.basicConfig", "global logging configuration")
        elif name == "logging.getLogger":
            add_finding(findings, path, node, "logger_setup", "logging.getLogger")
        elif isinstance(node.func, ast.Attribute) and node.func.attr in LOGGER_METHODS:
            add_finding(findings, path, node, "logger_call", node.func.attr)

    return findings


def summarize(findings: list[dict[str, Any]]) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "total": len(findings),
        "by_layer": {},
        "by_severity": {},
        "by_type": {},
    }
    for finding in findings:
        for key, value in (
            ("by_layer", finding["layer"]),
            ("by_severity", finding["severity"]),
            ("by_type", finding["type"]),
        ):
            bucket = summary[key]
            bucket[value] = bucket.get(value, 0) + 1
    return summary


def render_markdown(findings: list[dict[str, Any]]) -> str:
    summary = summarize(findings)
    lines = [
        "# Logging Audit Report",
        "",
        f"Scanned from: `{REPO_ROOT}`",
        f"Total findings: {summary['total']}",
        "",
        "## Summary",
        "",
        f"- By layer: `{json.dumps(summary['by_layer'], sort_keys=True)}`",
        f"- By severity: `{json.dumps(summary['by_severity'], sort_keys=True)}`",
        f"- By type: `{json.dumps(summary['by_type'], sort_keys=True)}`",
        "",
        "## Findings",
        "",
    ]

    if not findings:
        lines.append("No logging or direct print findings detected.")
        return "\n".join(lines)

    lines.extend(["| Severity | Layer | Type | Location | Detail |", "| --- | --- | --- | --- | --- |"])
    for finding in findings:
        location = f"{finding['path']}:{finding['line']}"
        lines.append(
            f"| {finding['severity']} | {finding['layer']} | {finding['type']} | "
            f"`{location}` | {finding['detail']} |"
        )
    return "\n".join(lines)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit APMultitool logging usage.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    findings: list[dict[str, Any]] = []
    for path in iter_python_files(SCAN_TARGETS):
        findings.extend(audit_file(path))

    findings.sort(key=lambda item: (item["severity"], item["layer"], item["path"], item["line"]))
    if args.json:
        print(json.dumps({"summary": summarize(findings), "findings": findings}, indent=2))
    else:
        print(render_markdown(findings))
    return 1 if any(item["type"] == "parse_error" for item in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
