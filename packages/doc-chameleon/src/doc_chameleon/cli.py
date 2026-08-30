from __future__ import annotations

from pathlib import Path

import click

from doc_chameleon import __version__
from doc_chameleon.engine.export import save
from doc_chameleon.engine.ingest import load
from doc_chameleon.engine.report import write_report
from doc_chameleon.rules.ca.transformer import transform as transform_ca
from doc_chameleon.rules.ca.transformer_2111 import AttorneyInfo, transform_2111 as transform_ca_2111
from doc_chameleon.rules.ca.validator import validate as validate_ca
from doc_chameleon.rules.ca.validator import validate_2111 as validate_ca_2111
from doc_chameleon.rules.ca.validator import validate_source_assumptions as validate_ca_source_assumptions
from doc_chameleon.rules.tx.transformer import transform as transform_tx
from doc_chameleon.rules.tx.validator import validate as validate_tx
from doc_chameleon.rules.tx.validator import validate_source_assumptions as validate_tx_source_assumptions

JURISDICTIONS = ("ca", "tx")

_JURISDICTION_INFO = {
    "ca": {
        "display": "California",
        "status": "Implemented",
        "rules": [
            "CRC 2.108 — left-margin line numbering (all pages)",
            "CRC 2.111 — first-page attorney/clerk layout",
        ],
        "overlays": "N/A — statewide rules only",
    },
    "tx": {
        "display": "Texas",
        "status": "Implemented",
        "rules": [
            "TRCP statewide baseline — page geometry, double-spaced body, caption check",
        ],
        "overlays": "Reserved — Harris County, Travis County (not yet implemented)",
    },
}


@click.group()
@click.version_option(version=__version__, prog_name="doc-chameleon")
def main() -> None:
    """doc-chameleon — offline-first legal document formatting engine."""


@main.command()
@click.option("--input", "input_path", required=True, type=click.Path(exists=True, path_type=Path), help="Source .docx file")
@click.option("--jurisdiction", required=True, type=click.Choice(list(JURISDICTIONS)), help="Target jurisdiction pack")
@click.option("--output", "output_path", required=True, type=click.Path(path_type=Path), help="Output .docx file")
@click.option("--attorney-name", default=None, help="[CA] Attorney name for first-page header")
@click.option("--attorney-sbn", default=None, help="[CA] State Bar Number")
@click.option("--firm", default=None, help="[CA] Firm name")
@click.option("--address", default=None, help="[CA] Street address")
@click.option("--city-state-zip", "city_state_zip", default=None, help="[CA] City, State ZIP")
@click.option("--phone", default=None, help="[CA] Phone number")
@click.option("--email", default=None, help="[CA] Email address")
@click.option("--client", default=None, help="[CA] Client party (e.g. 'Plaintiff, ACME Corp')")
def convert(
    input_path: Path,
    jurisdiction: str,
    output_path: Path,
    attorney_name: str | None,
    attorney_sbn: str | None,
    firm: str | None,
    address: str | None,
    city_state_zip: str | None,
    phone: str | None,
    email: str | None,
    client: str | None,
) -> None:
    """Convert a .docx to jurisdiction-compliant formatting."""
    doc, record = load(input_path)
    warnings: list[str] = []

    if jurisdiction == "ca":
        attorney_kwargs = {
            k: v for k, v in {
                "name": attorney_name,
                "sbn": attorney_sbn,
                "firm": firm,
                "address": address,
                "city_state_zip": city_state_zip,
                "phone": phone,
                "email": email,
                "client": client,
            }.items() if v is not None
        }
        attorney = AttorneyInfo(**attorney_kwargs)
        warnings.extend(validate_ca_source_assumptions(doc, record))
        doc = transform_ca(doc)
        doc = transform_ca_2111(doc, attorney=attorney)
        warnings.extend(validate_ca(doc, record))
        warnings.extend(validate_ca_2111(doc, record))
    elif jurisdiction == "tx":
        warnings.extend(validate_tx_source_assumptions(doc, record))
        doc = transform_tx(doc)
        warnings.extend(validate_tx(doc, record))

    warnings = list(dict.fromkeys(warnings))

    save(doc, output_path)
    report_path = write_report(output_path, input_path, jurisdiction, warnings)

    click.echo(f"Loaded:       {input_path.name} ({len(record.paragraphs)} paragraphs, {len(record.sections)} sections)")
    click.echo(f"Jurisdiction: {jurisdiction.upper()}")
    click.echo(f"Output:       {output_path}")
    click.echo(f"Report:       {report_path}")

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
    click.echo(f"Loaded:       {input_path.name}")
    click.echo(f"Paragraphs:   {len(record.paragraphs)}")
    click.echo(f"Sections:     {len(record.sections)}")
    click.echo(f"Jurisdiction: {jurisdiction.upper()}")
    click.echo()

    if jurisdiction == "ca":
        warnings = list(dict.fromkeys(validate_ca(doc, record) + validate_ca_2111(doc, record)))
    else:
        warnings = list(dict.fromkeys(validate_tx(doc, record)))

    if warnings:
        click.echo(f"Warnings ({len(warnings)}):")
        for warning in warnings:
            click.echo(f"  - {warning}")
    else:
        click.echo("No formatting warnings detected.")


@main.command("list-jurisdictions")
def list_jurisdictions() -> None:
    """List all available jurisdiction packs and their implementation status."""
    click.echo("Available jurisdictions:\n")
    for code, info in _JURISDICTION_INFO.items():
        click.echo(f"  {code.upper()}  {info['display']}")
        click.echo(f"      Status:   {info['status']}")
        click.echo(f"      Rules:")
        for rule in info["rules"]:
            click.echo(f"                {rule}")
        click.echo(f"      Overlays: {info['overlays']}")
        click.echo()
