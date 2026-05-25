from __future__ import annotations

from pathlib import Path

import click

from doc_chameleon.engine.export import save
from doc_chameleon.engine.ingest import load

JURISDICTIONS: dict[str, str] = {
    "ca": "California (CRC 2.108 line numbering, CRC 2.111 first-page format)",
    "tx": "Texas (TRCP statewide baseline — local venue overlays not yet implemented)",
}


@click.group()
def main() -> None:
    """doc-chameleon — offline-first legal document formatting engine."""


@main.command()
@click.option("--input", "input_path", required=True, type=click.Path(exists=True, path_type=Path), help="Source .docx file")
@click.option("--jurisdiction", required=True, type=click.Choice(list(JURISDICTIONS)), help="Target jurisdiction pack")
@click.option("--output", "output_path", required=True, type=click.Path(path_type=Path), help="Output .docx file")
def convert(input_path: Path, jurisdiction: str, output_path: Path) -> None:
    """Convert a .docx to jurisdiction-compliant formatting."""
    doc, record = load(input_path)
    # Transformation stub — jurisdiction rules not applied until Phase 2 MVP
    save(doc, output_path)
    click.echo(f"Loaded:      {input_path.name} ({len(record.paragraphs)} paragraphs, {len(record.sections)} sections)")
    click.echo(f"Jurisdiction: {jurisdiction}")
    click.echo(f"Output:      {output_path}")
    click.echo()
    click.echo("NOTE: No formatting rules applied. Jurisdiction transformer not yet implemented.")


@main.command()
@click.option("--input", "input_path", required=True, type=click.Path(exists=True, path_type=Path), help="Source .docx file")
@click.option("--jurisdiction", required=True, type=click.Choice(list(JURISDICTIONS)), help="Jurisdiction to validate against")
def validate(input_path: Path, jurisdiction: str) -> None:
    """Validate a .docx against jurisdiction formatting rules."""
    _doc, record = load(input_path)
    click.echo(f"Loaded:      {input_path.name}")
    click.echo(f"Paragraphs:  {len(record.paragraphs)}")
    click.echo(f"Sections:    {len(record.sections)}")
    click.echo(f"Jurisdiction: {jurisdiction}")
    click.echo()
    click.echo("NOTE: No validation rules implemented. Jurisdiction validator not yet implemented.")


@main.command("list-jurisdictions")
def list_jurisdictions() -> None:
    """List all available jurisdiction packs."""
    click.echo("Available jurisdictions:\n")
    for code, description in JURISDICTIONS.items():
        click.echo(f"  {code}  {description}")
