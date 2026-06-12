from __future__ import annotations

from pathlib import Path

import click

from doc_chameleon.engine.export import save
from doc_chameleon.engine.ingest import load
from doc_chameleon.engine.report import write_report
from doc_chameleon.rules.ca.transformer import transform as transform_ca
from doc_chameleon.rules.ca.transformer_2111 import transform_2111 as transform_ca_2111
from doc_chameleon.rules.ca.validator import validate as validate_ca
from doc_chameleon.rules.ca.validator import validate_2111 as validate_ca_2111
from doc_chameleon.rules.ca.validator import validate_source_assumptions as validate_ca_source_assumptions

JURISDICTIONS: dict[str, str] = {
    "ca": "California (CRC 2.108 line numbering, CRC 2.111 first-page format)",
    "tx": "Texas (TRCP statewide baseline - local venue overlays not yet implemented)",
}


@click.group()
def main() -> None:
    """doc-chameleon - offline-first legal document formatting engine."""


@main.command()
@click.option("--input", "input_path", required=True, type=click.Path(exists=True, path_type=Path), help="Source .docx file")
@click.option("--jurisdiction", required=True, type=click.Choice(list(JURISDICTIONS)), help="Target jurisdiction pack")
@click.option("--output", "output_path", required=True, type=click.Path(path_type=Path), help="Output .docx file")
def convert(input_path: Path, jurisdiction: str, output_path: Path) -> None:
    """Convert a .docx to jurisdiction-compliant formatting."""
    doc, record = load(input_path)
    warnings: list[str] = []

    if jurisdiction == "ca":
        warnings.extend(validate_ca_source_assumptions(doc, record))
        doc = transform_ca(doc)
        doc = transform_ca_2111(doc)
        warnings.extend(validate_ca(doc, record))
        warnings.extend(validate_ca_2111(doc, record))
        warnings = list(dict.fromkeys(warnings))
    else:
        click.echo("NOTE: Texas transformer not yet implemented. Passing document through unchanged.")

    save(doc, output_path)
    report_path = write_report(output_path, input_path, jurisdiction, warnings)

    click.echo(f"Loaded:      {input_path.name} ({len(record.paragraphs)} paragraphs, {len(record.sections)} sections)")
    click.echo(f"Jurisdiction: {jurisdiction}")
    click.echo(f"Output:      {output_path}")
    click.echo(f"Report:      {report_path}")

    if warnings:
        click.echo()
        click.echo(f"Warnings ({len(warnings)}):")
        for warning in warnings:
            click.echo(f"  - {warning}")


@main.command()
@click.option("--input", "input_path", required=True, type=click.Path(exists=True, path_type=Path), help="Source .docx file")
@click.option("--jurisdiction", required=True, type=click.Choice(list(JURISDICTIONS)), help="Jurisdiction to validate against")
def validate(input_path: Path, jurisdiction: str) -> None:
    """Validate a .docx against jurisdiction formatting rules."""
    doc, record = load(input_path)
    click.echo(f"Loaded:      {input_path.name}")
    click.echo(f"Paragraphs:  {len(record.paragraphs)}")
    click.echo(f"Sections:    {len(record.sections)}")
    click.echo(f"Jurisdiction: {jurisdiction}")
    click.echo()

    if jurisdiction == "ca":
        warnings = validate_ca(doc, record) + validate_ca_2111(doc, record)
        warnings = list(dict.fromkeys(warnings))
        if warnings:
            click.echo(f"Warnings ({len(warnings)}):")
            for warning in warnings:
                click.echo(f"  - {warning}")
        else:
            click.echo("No California formatting warnings detected.")
    else:
        click.echo("NOTE: Texas validator not yet implemented.")


@main.command("list-jurisdictions")
def list_jurisdictions() -> None:
    """List all available jurisdiction packs."""
    click.echo("Available jurisdictions:\n")
    for code, description in JURISDICTIONS.items():
        click.echo(f"  {code}  {description}")
