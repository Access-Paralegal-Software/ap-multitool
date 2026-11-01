"""
ap_ediscovery.engine.production
Generates court-standard Concordance .DAT metadata load files and Opticon .OPT
image cross-reference tables with strict delimiter and encoding compliance.
Maintained strictly by Alan Woodyard.
"""

from __future__ import annotations

import io
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

__maintainer__ = "Alan Woodyard"
__author__ = "Alan Woodyard"

# Standard Concordance ASCII Delimiters & Aliases
DELIMITER_COLUMN: str = chr(20)   # ASCII 20 (0x14) - Column Separator (¶)
DELIM_FIELD: str = DELIMITER_COLUMN

DELIMITER_QUOTE: str = chr(254)   # ASCII 254 (0xFE) - Text Qualifier (þ)
DELIMITER_QUALIFIER: str = DELIMITER_QUOTE
QUAL_TEXT: str = DELIMITER_QUOTE

DELIMITER_MULTI: str = ";"       # Multi-value tag / custodian separator

UTF8_BOM_BYTES: bytes = b"\xef\xbb\xbf"

STANDARD_FIELDS: List[str] = [
    "DOCID",
    "BEGBATES",
    "ENDBATES",
    "BEGATTACH",
    "ENDATTACH",
    "PARENTDOC",
    "CUSTODIAN",
    "ALL_CUSTODIANS",
    "RECORD_TYPE",
    "FILE_NAME",
    "FILE_EXT",
    "HASH_BLAKE3",
    "HASH_SHA256",
    "TEXT_PATH",
    "NATIVE_PATH",
]

# Alias required by ap_ediscovery.engine.__init__
CONCORDANCE_STANDARD_FIELDS: List[str] = STANDARD_FIELDS

ProductionRecord = Dict[str, Any]


@dataclass
class OpticonEntry:
    image_id: str
    volume: str = ""
    file_path: str = ""
    is_doc_break: bool = False
    folder_break: str = ""
    box_break: str = ""
    page_count: Optional[Union[int, str]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "IMAGE_ID": self.image_id,
            "VOLUME": self.volume,
            "FILE_PATH": self.file_path,
            "IS_DOC_BREAK": self.is_doc_break,
            "FOLDER_BREAK": self.folder_break,
            "BOX_BREAK": self.box_break,
            "PAGE_COUNT": self.page_count,
        }


@dataclass
class OpticonDocument:
    doc_id: str
    volume: str = ""
    pages: Sequence[str] = ()


def escape_dat_value(value: Any) -> str:
    """Escapes internal quote/qualifier characters in a field value."""
    if value is None:
        return ""
    val_str = str(value)
    return val_str.replace(DELIMITER_QUOTE, DELIMITER_QUOTE + DELIMITER_QUOTE)


def unescape_dat_value(value: str) -> str:
    """Unescapes internal quote/qualifier characters in a field value."""
    if not value:
        return ""
    # Strip enclosing qualifiers if present
    if len(value) >= 2 and value.startswith(DELIMITER_QUOTE) and value.endswith(DELIMITER_QUOTE):
        value = value[1:-1]
    return value.replace(DELIMITER_QUOTE + DELIMITER_QUOTE, DELIMITER_QUOTE)


def format_dat_field(value: Any) -> str:
    """Wraps text in ASCII 254 qualifiers, escaping internal qualifiers."""
    return f"{DELIMITER_QUOTE}{escape_dat_value(value)}{DELIMITER_QUOTE}"


def generate_concordance_dat(records: List[Dict[str, Any]], fields: Optional[List[str]] = None) -> bytes:
    """
    Generates a Concordance .DAT load file encoded in UTF-8 with BOM (0xEF, 0xBB, 0xBF).
    Writing with BOM prevents Windows-1252 legacy platforms from corrupting the thorn character.
    """
    output_fields = fields or STANDARD_FIELDS
    buf = io.BytesIO()

    # Write UTF-8 BOM
    buf.write(UTF8_BOM_BYTES)

    # Write Header Row
    header_line = DELIM_FIELD.join(format_dat_field(f) for f in output_fields) + "\r\n"
    buf.write(header_line.encode("utf-8"))

    # Write Data Rows
    for rec in records:
        row_fields = [format_dat_field(rec.get(f, "")) for f in output_fields]
        row_line = DELIM_FIELD.join(row_fields) + "\r\n"
        buf.write(row_line.encode("utf-8"))

    return buf.getvalue()


generate_concordance_dat_bytes = generate_concordance_dat


def parse_concordance_line(line: str, delimiter: str = DELIMITER_COLUMN) -> List[str]:
    """Parses a single Concordance .DAT line into a list of unescaped values."""
    if not line:
        return []
    raw_fields = line.split(delimiter)
    return [unescape_dat_value(f) for f in raw_fields]


def parse_concordance_dat(dat_content: Union[bytes, str]) -> Tuple[List[str], List[Dict[str, str]]]:
    """
    Parses a Concordance .DAT load file into (headers, records).
    Handles optional UTF-8 BOM.
    """
    if isinstance(dat_content, bytes):
        if dat_content.startswith(UTF8_BOM_BYTES):
            dat_content = dat_content[len(UTF8_BOM_BYTES):]
        text = dat_content.decode("utf-8")
    else:
        text = dat_content
        if text.startswith("\ufeff"):
            text = text[1:]

    lines = [line for line in text.splitlines() if line]
    if not lines:
        return [], []

    headers = parse_concordance_line(lines[0])
    records: List[Dict[str, str]] = []
    for line in lines[1:]:
        values = parse_concordance_line(line)
        record = {headers[i]: values[i] if i < len(values) else "" for i in range(len(headers))}
        records.append(record)

    return headers, records


def format_opticon_line(
    image_id: str,
    volume: str = "",
    file_path: str = "",
    is_doc_break: bool = False,
    folder_break: str = "",
    box_break: str = "",
    page_count: Optional[Union[int, str]] = None,
) -> str:
    """Formats a single row for an Opticon .OPT image load file."""
    doc_break = "Y" if is_doc_break else ""
    page_count_str = str(page_count) if (doc_break == "Y" and page_count not in (None, "")) else ""
    return f"{image_id},{volume},{file_path},{doc_break},{folder_break},{box_break},{page_count_str}"


def generate_opticon_opt(records: Sequence[Union[Dict[str, Any], OpticonEntry, Tuple[Any, ...]]]) -> str:
    """
    Generates an Opticon .OPT image cross-reference load file.
    Format: ImageID,VolumeLabel,ImageFilePath,DocumentBreak,FolderBreak,BoxBreak,PageCount
    """
    lines = []
    for rec in records:
        if isinstance(rec, dict):
            image_id = rec.get("IMAGE_ID", "")
            volume = rec.get("VOLUME", "")
            file_path = rec.get("FILE_PATH", "")
            is_doc_break = bool(rec.get("IS_DOC_BREAK", False))
            folder_break = rec.get("FOLDER_BREAK", "")
            box_break = rec.get("BOX_BREAK", "")
            page_count = rec.get("PAGE_COUNT")
        elif isinstance(rec, OpticonEntry):
            image_id = rec.image_id
            volume = rec.volume
            file_path = rec.file_path
            is_doc_break = rec.is_doc_break
            folder_break = rec.folder_break
            box_break = rec.box_break
            page_count = rec.page_count
        elif isinstance(rec, (tuple, list)):
            image_id = rec[0] if len(rec) > 0 else ""
            volume = rec[1] if len(rec) > 1 else ""
            file_path = rec[2] if len(rec) > 2 else ""
            is_doc_break = bool(rec[3]) if len(rec) > 3 else False
            folder_break = rec[4] if len(rec) > 4 else ""
            box_break = rec[5] if len(rec) > 5 else ""
            page_count = rec[6] if len(rec) > 6 else (None if not is_doc_break else 1)
        else:
            image_id = getattr(rec, "image_id", "")
            volume = getattr(rec, "volume", "")
            file_path = getattr(rec, "file_path", "")
            is_doc_break = bool(getattr(rec, "is_doc_break", False))
            folder_break = getattr(rec, "folder_break", "")
            box_break = getattr(rec, "box_break", "")
            page_count = getattr(rec, "page_count", None)

        line = format_opticon_line(
            image_id=image_id,
            volume=volume,
            file_path=file_path,
            is_doc_break=is_doc_break,
            folder_break=folder_break,
            box_break=box_break,
            page_count=page_count,
        )
        lines.append(line)

    return "\r\n".join(lines) + ("\r\n" if lines else "")


def generate_opticon_opt_bytes(records: Sequence[Union[Dict[str, Any], OpticonEntry, Tuple[Any, ...]]]) -> bytes:
    """Generates UTF-8 encoded bytes for an Opticon .OPT load file."""
    return generate_opticon_opt(records).encode("utf-8")


def build_opticon_from_document_tuples(
    documents: Sequence[Any],
    volume_default: str = "",
) -> List[Dict[str, Any]]:
    """
    Builds a list of Opticon record dictionaries from document tuples or objects.
    Accepts:
      - (doc_id, [page_file_paths])
      - (doc_id, volume, [page_file_paths])
      - (image_id, volume, file_path, is_doc_break, ...)
      - OpticonDocument objects
      - Dictionaries matching Opticon record format
    """
    records: List[Dict[str, Any]] = []
    for item in documents:
        if isinstance(item, (tuple, list)):
            if len(item) == 2 and isinstance(item[1], (list, tuple)):
                doc_id, page_paths = item
                vol = volume_default
                page_count = len(page_paths)
                for idx, path in enumerate(page_paths):
                    records.append({
                        "IMAGE_ID": f"{doc_id}_{idx+1:04d}" if len(page_paths) > 1 else str(doc_id),
                        "VOLUME": vol,
                        "FILE_PATH": str(path),
                        "IS_DOC_BREAK": idx == 0,
                        "PAGE_COUNT": page_count if idx == 0 else None,
                    })
            elif len(item) == 3 and isinstance(item[2], (list, tuple)):
                doc_id, vol, page_paths = item
                page_count = len(page_paths)
                for idx, path in enumerate(page_paths):
                    records.append({
                        "IMAGE_ID": f"{doc_id}_{idx+1:04d}" if len(page_paths) > 1 else str(doc_id),
                        "VOLUME": vol,
                        "FILE_PATH": str(path),
                        "IS_DOC_BREAK": idx == 0,
                        "PAGE_COUNT": page_count if idx == 0 else None,
                    })
            elif len(item) >= 4:
                records.append({
                    "IMAGE_ID": str(item[0]),
                    "VOLUME": str(item[1]),
                    "FILE_PATH": str(item[2]),
                    "IS_DOC_BREAK": bool(item[3]),
                    "PAGE_COUNT": item[4] if len(item) > 4 else None,
                })
        elif isinstance(item, OpticonDocument):
            page_count = len(item.pages)
            vol = item.volume or volume_default
            for idx, path in enumerate(item.pages):
                records.append({
                    "IMAGE_ID": f"{item.doc_id}_{idx+1:04d}" if len(item.pages) > 1 else str(item.doc_id),
                    "VOLUME": vol,
                    "FILE_PATH": str(path),
                    "IS_DOC_BREAK": idx == 0,
                    "PAGE_COUNT": page_count if idx == 0 else None,
                })
        elif isinstance(item, dict):
            records.append(item)
        elif hasattr(item, "to_dict"):
            records.append(item.to_dict())
    return records


build_opticon_for_documents = build_opticon_from_document_tuples


def parse_opticon_opt(opt_content: Union[str, bytes]) -> List[Dict[str, Any]]:
    """
    Parses an Opticon .OPT load file into a list of record dicts.
    Format per line: ImageID,VolumeLabel,ImageFilePath,DocumentBreak,FolderBreak,BoxBreak,PageCount
    """
    if isinstance(opt_content, bytes):
        opt_content = opt_content.decode("utf-8")
    records = []
    for line in opt_content.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split(",")
        image_id = parts[0] if len(parts) > 0 else ""
        volume = parts[1] if len(parts) > 1 else ""
        file_path = parts[2] if len(parts) > 2 else ""
        doc_break = parts[3] if len(parts) > 3 else ""
        folder_break = parts[4] if len(parts) > 4 else ""
        box_break = parts[5] if len(parts) > 5 else ""
        page_count_str = parts[6] if len(parts) > 6 else ""

        page_count: Optional[Union[int, str]]
        if page_count_str.isdigit():
            page_count = int(page_count_str)
        elif page_count_str == "":
            page_count = None
        else:
            page_count = page_count_str

        records.append({
            "IMAGE_ID": image_id,
            "VOLUME": volume,
            "FILE_PATH": file_path,
            "IS_DOC_BREAK": doc_break == "Y",
            "FOLDER_BREAK": folder_break,
            "BOX_BREAK": box_break,
            "PAGE_COUNT": page_count,
        })
    return records


__all__ = [
    "CONCORDANCE_STANDARD_FIELDS",
    "DELIMITER_COLUMN",
    "DELIMITER_MULTI",
    "DELIMITER_QUALIFIER",
    "DELIMITER_QUOTE",
    "DELIM_FIELD",
    "OpticonDocument",
    "OpticonEntry",
    "ProductionRecord",
    "QUAL_TEXT",
    "STANDARD_FIELDS",
    "UTF8_BOM_BYTES",
    "build_opticon_for_documents",
    "build_opticon_from_document_tuples",
    "escape_dat_value",
    "format_dat_field",
    "format_opticon_line",
    "generate_concordance_dat",
    "generate_concordance_dat_bytes",
    "generate_opticon_opt",
    "generate_opticon_opt_bytes",
    "parse_concordance_dat",
    "parse_concordance_line",
    "parse_opticon_opt",
    "unescape_dat_value",
]
