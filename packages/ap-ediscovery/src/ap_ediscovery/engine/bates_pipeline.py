"""
ap_ediscovery.engine.bates_pipeline
Coordinates sequential Bates stamping across document families and compiles
standardized court production file structures (IMAGES, TEXT, NATIVES, DATA).
Maintained strictly by Alan Woodyard.
"""

from pathlib import Path
from typing import List, Dict, Any, Tuple
import os
import shutil

from doc_chameleon.bates.stamper import BatesStampConfig, stamp_pdf_bytes
from ap_ediscovery.engine.production import (
    generate_concordance_dat,
    generate_opticon_opt,
    CONCORDANCE_STANDARD_FIELDS
)

class ProductionBatchRunner:
    """
    Executes sequential Bates stamping across a collection of document records,
    preserving family parent-child numbering and generating .DAT and .OPT outputs.
    """

    def __init__(self, prefix: str = "PROD_", start_num: int = 1, digits: int = 8):
        self.prefix = prefix
        self.current_seq = start_num
        self.digits = digits

    def process_production(
        self,
        documents: List[Dict[str, Any]],
        output_dir: Path,
        volume_label: str = "VOL001"
    ) -> Dict[str, Any]:
        """
        Processes a list of documents:
        - Writes stamped PDFs to IMAGES/
        - Copies native files to NATIVES/
        - Writes text transcripts to TEXT/
        - Compiles PRODUCTION.DAT and PRODUCTION.OPT to DATA/
        """
        output_dir = Path(output_dir)
        data_dir = output_dir / "DATA"
        images_dir = output_dir / "IMAGES"
        text_dir = output_dir / "TEXT"
        natives_dir = output_dir / "NATIVES"

        for d in (data_dir, images_dir, text_dir, natives_dir):
            d.mkdir(parents=True, exist_ok=True)

        dat_records: List[Dict[str, Any]] = []
        opt_records: List[Dict[str, Any]] = []

        # Sort documents: Custodian -> Family ID -> Parent Doc ID -> Doc ID
        sorted_docs = sorted(
            documents,
            key=lambda x: (
                x.get("custodian_id", 0),
                x.get("family_id") or x.get("doc_id", 0),
                x.get("parent_doc_id") or 0,
                x.get("doc_id", 0)
            )
        )

        # Track family attachment ranges: family_id -> (min_bates, max_bates)
        family_ranges: Dict[int, Dict[str, str]] = {}

        for doc in sorted_docs:
            raw_pdf_bytes = doc.get("pdf_bytes")
            if not raw_pdf_bytes:
                continue

            config = BatesStampConfig(
                prefix=self.prefix,
                start=self.current_seq,
                digits=self.digits
            )

            stamped_bytes, page_manifest = stamp_pdf_bytes(raw_pdf_bytes, config)
            page_count = len(page_manifest)

            beg_bates = page_manifest[0]["bates_id"]
            end_bates = page_manifest[-1]["bates_id"]
            self.current_seq += page_count

            doc_id_str = str(doc.get("doc_id", beg_bates))
            family_id = doc.get("family_id")

            # Update family span
            if family_id:
                if family_id not in family_ranges:
                    family_ranges[family_id] = {"beg": beg_bates, "end": end_bates}
                else:
                    family_ranges[family_id]["end"] = end_bates

            # Write stamped PDF image to IMAGES/
            img_rel_path = f"IMAGES\\{beg_bates}.PDF"
            (images_dir / f"{beg_bates}.PDF").write_bytes(stamped_bytes)

            # Write extracted text to TEXT/
            text_rel_path = f"TEXT\\{beg_bates}.TXT"
            text_content = doc.get("text_content", "")
            (text_dir / f"{beg_bates}.TXT").write_text(text_content, encoding="utf-8")

            # Copy Native if present
            native_rel_path = ""
            if doc.get("native_bytes") and doc.get("file_name"):
                file_name = doc["file_name"]
                native_rel_path = f"NATIVES\\{beg_bates}_{file_name}"
                (natives_dir / f"{beg_bates}_{file_name}").write_bytes(doc["native_bytes"])

            # Opticon page entries
            for p_idx, p_info in enumerate(page_manifest):
                opt_records.append({
                    "IMAGE_ID": p_info["bates_id"],
                    "VOLUME": volume_label,
                    "FILE_PATH": f"IMAGES\\{beg_bates}.PDF",
                    "IS_DOC_BREAK": (p_idx == 0),
                    "PAGE_COUNT": page_count if p_idx == 0 else ""
                })

            dat_records.append({
                "DOCID": beg_bates,
                "BEGBATES": beg_bates,
                "ENDBATES": end_bates,
                "BEGATTACH": "",  # Backfilled below
                "ENDATTACH": "",  # Backfilled below
                "PARENTDOC": doc.get("parent_bates", ""),
                "CUSTODIAN": doc.get("custodian", "Unknown"),
                "ALL_CUSTODIANS": doc.get("all_custodians", doc.get("custodian", "Unknown")),
                "RECORD_TYPE": doc.get("record_type", "Document"),
                "FILE_NAME": doc.get("file_name", f"{beg_bates}.PDF"),
                "FILE_EXT": doc.get("file_ext", "pdf"),
                "HASH_BLAKE3": doc.get("doc_hash", ""),
                "HASH_SHA256": doc.get("sha256", ""),
                "TEXT_PATH": text_rel_path,
                "NATIVE_PATH": native_rel_path,
                "_family_id": family_id
            })

        # Backfill family ranges into DAT records
        for rec in dat_records:
            fam_id = rec.pop("_family_id", None)
            if fam_id and fam_id in family_ranges:
                rec["BEGATTACH"] = family_ranges[fam_id]["beg"]
                rec["ENDATTACH"] = family_ranges[fam_id]["end"]
            else:
                rec["BEGATTACH"] = rec["BEGBATES"]
                rec["ENDATTACH"] = rec["ENDBATES"]

        # Emit load files to DATA/
        dat_bytes = generate_concordance_dat(dat_records)
        (data_dir / f"{volume_label}.DAT").write_bytes(dat_bytes)

        opt_text = generate_opticon_opt(opt_records)
        (data_dir / f"{volume_label}.OPT").write_text(opt_text, encoding="utf-8")

        return {
            "volume": volume_label,
            "document_count": len(dat_records),
            "total_pages": self.current_seq - 1,
            "dat_path": data_dir / f"{volume_label}.DAT",
            "opt_path": data_dir / f"{volume_label}.OPT"
        }
