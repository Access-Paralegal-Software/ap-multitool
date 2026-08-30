"""Run the doc-chameleon pipeline on each sample source document.

Usage:
    python scripts/convert_samples.py

Reads from  samples/source/
Writes to   samples/output/
"""
from __future__ import annotations

from pathlib import Path

from doc_chameleon.engine.export import save
from doc_chameleon.engine.ingest import load
from doc_chameleon.engine.report import write_report
from doc_chameleon.rules.ca.transformer import transform as transform_ca
from doc_chameleon.rules.ca.transformer_2111 import AttorneyInfo, transform_2111 as transform_ca_2111
from doc_chameleon.rules.ca.validator import (
    validate as validate_ca,
    validate_2111 as validate_ca_2111,
    validate_source_assumptions as validate_ca_source,
)
from doc_chameleon.rules.tx.transformer import transform as transform_tx
from doc_chameleon.rules.tx.validator import (
    validate as validate_tx,
    validate_source_assumptions as validate_tx_source,
)

ROOT = Path(__file__).parent.parent
SRC = ROOT / "samples" / "source"
OUT = ROOT / "samples" / "output"

CA_ATTORNEY = AttorneyInfo(
    name="Elena R. Vasquez",
    sbn="287451",
    firm="Vasquez & Kimura LLP",
    address="350 S. Grand Avenue, Suite 3400",
    city_state_zip="Los Angeles, CA 90071",
    phone="(213) 555-0188",
    email="evasquez@vklawfirm.com",
    client="Plaintiff, Meridian Pacific Holdings, LLC",
)


def convert_ca(src_name: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    src = SRC / src_name
    out = OUT / src_name.replace(".docx", "_ca.docx")

    doc, record = load(src)
    warnings = validate_ca_source(doc, record)
    doc = transform_ca(doc)
    doc = transform_ca_2111(doc, attorney=CA_ATTORNEY)
    warnings += validate_ca(doc, record)
    warnings += validate_ca_2111(doc, record)
    warnings = list(dict.fromkeys(warnings))

    save(doc, out)
    rpt = write_report(out, src, "ca", warnings)

    print(f"CA: {src.name} -> {out.name}")
    print(f"    report: {rpt.name}")
    if warnings:
        for w in warnings:
            print(f"    WARNING: {w}")
    else:
        print("    no warnings")


def convert_tx(src_name: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    src = SRC / src_name
    out = OUT / src_name.replace(".docx", "_tx.docx")

    doc, record = load(src)
    warnings = validate_tx_source(doc, record)
    doc = transform_tx(doc)
    warnings += validate_tx(doc, record)
    warnings = list(dict.fromkeys(warnings))

    save(doc, out)
    rpt = write_report(out, src, "tx", warnings)

    print(f"TX: {src.name} -> {out.name}")
    print(f"    report: {rpt.name}")
    if warnings:
        for w in warnings:
            print(f"    WARNING: {w}")
    else:
        print("    no warnings")


if __name__ == "__main__":
    convert_ca("ca_motion.docx")
    convert_tx("tx_motion.docx")
