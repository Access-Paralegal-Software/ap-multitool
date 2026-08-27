"""Conversion report writer — writes a companion .txt file alongside the output .docx."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path


def write_report(
    output_path: Path,
    input_path: Path,
    jurisdiction: str,
    warnings: list[str],
) -> Path:
    report_path = output_path.with_name(output_path.stem + "_report.txt")

    lines = [
        "doc-chameleon Conversion Report",
        "=" * 40,
        f"Input:        {input_path.name}",
        f"Output:       {output_path.name}",
        f"Jurisdiction: {jurisdiction}",
        f"Generated:    {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
    ]

    if warnings:
        lines.append(f"Warnings ({len(warnings)}):")
        for warning in warnings:
            lines.append(f"  - {warning}")
    else:
        lines.append("No warnings — all controlled assumptions satisfied.")

    lines += [
        "",
        "─" * 40,
        "This tool assists document formatting and workflow preparation.",
        "It does not provide legal advice and does not guarantee court acceptance.",
        "Review all output before filing.",
        "",
    ]

    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path
