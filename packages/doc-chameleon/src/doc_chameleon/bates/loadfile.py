"""
doc_chameleon.bates.loadfile
Litigation production load-file generator.
Produces Concordance (.DAT) and Opticon (.OPT) cross-reference files
for ingestion into Relativity, Everlaw, Disco, and litigation databases.
Maintained strictly by Alan Woodyard.
"""

from __future__ import annotations
import csv
from pathlib import Path
from typing import List, Dict, Any, Union, Optional

CONCORDANCE_QUOTE = chr(0xFE)   # þ (ASCII 254)
CONCORDANCE_DELIM = chr(0x14)   # ¶ (ASCII 20)

def format_dat_record(fields: List[str]) -> str:
    """Formats a row using Concordance thorn/pilcrow delimiters."""
    return CONCORDANCE_DELIM.join(f"{CONCORDANCE_QUOTE}{f}{CONCORDANCE_QUOTE}" for f in fields)

def generate_concordance_dat(
    documents: List[Dict[str, Any]],
    output_path: Union[str, Path]
) -> Path:
    """
    Generates a Concordance .DAT load file.
    Expected doc keys: 'doc_id', 'beg_bates', 'end_bates', 'page_count', 'file_name', 'file_size'
    """
    out_file = Path(output_path)
    headers = ["DOCID", "BEGBATES", "ENDBATES", "PAGECOUNT", "FILE_NAME", "FILE_SIZE_BYTES"]

    lines = [format_dat_record(headers)]
    for doc in documents:
        row = [
            str(doc.get("doc_id", "")),
            str(doc.get("beg_bates", "")),
            str(doc.get("end_bates", "")),
            str(doc.get("page_count", 1)),
            str(doc.get("file_name", "")),
            str(doc.get("file_size", 0)),
        ]
        lines.append(format_dat_record(row))

    out_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out_file

def generate_opticon_opt(
    documents: List[Dict[str, Any]],
    output_path: Union[str, Path],
    volume: str = "VOL0001",
    relative_img_dir: str = "IMAGES"
) -> Path:
    """
    Generates an Opticon .OPT image cross-reference file.
    Format: IMAGEKEY,VOLUME,FILEPATH,DOCBREAK,,,PAGECOUNT
    """
    out_file = Path(output_path)
    lines: List[str] = []

    for doc in documents:
        file_name = doc.get("dest_file", doc.get("file_name", ""))
        rel_path = f"{relative_img_dir}\\{file_name}"
        pages = doc.get("pages", [])
        page_count = len(pages) if pages else doc.get("page_count", 1)

        for idx, page in enumerate(pages):
            bates_id = page.get("bates_id", "")
            is_break = "Y" if idx == 0 else ""
            pg_cnt_str = str(page_count) if idx == 0 else ""

            # Opticon 7 standard fields
            line = f"{bates_id},{volume},{rel_path},{is_break},,,{pg_cnt_str}"
            lines.append(line)

    out_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out_file

def generate_production_manifest_csv(
    documents: List[Dict[str, Any]],
    output_path: Union[str, Path]
) -> Path:
    """Generates an Excel-friendly CSV manifest for attorney review."""
    out_file = Path(output_path)
    headers = ["DOCID", "BEGBATES", "ENDBATES", "PAGECOUNT", "FILE_NAME", "FILE_SIZE_BYTES"]
    with open(out_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for doc in documents:
            writer.writerow([
                doc.get("doc_id", ""),
                doc.get("beg_bates", ""),
                doc.get("end_bates", ""),
                doc.get("page_count", 1),
                doc.get("file_name", ""),
                doc.get("file_size", 0),
            ])
    return out_file

def generate_production_loadfiles(
    documents: List[Dict[str, Any]],
    output_dir: Union[str, Path],
    volume: str = "VOL0001"
) -> Dict[str, Path]:
    """Generates full suite of production load files (.DAT, .OPT, and .CSV)."""
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    dat_path = out_dir / f"{volume}.dat"
    opt_path = out_dir / f"{volume}.opt"
    csv_path = out_dir / f"{volume}.csv"

    generate_concordance_dat(documents, dat_path)
    generate_opticon_opt(documents, opt_path, volume=volume)
    generate_production_manifest_csv(documents, csv_path)

    return {"dat": dat_path, "opt": opt_path, "csv": csv_path}
