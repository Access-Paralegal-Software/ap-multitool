"""
core/job.py — APMultitool canonical job model.

Every document operation is described as a Job before it runs and inspected
as a JobResult after. The GUI, engine, and audit log all speak this language.
"""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path


# ---------------------------------------------------------------------------
# Status
# ---------------------------------------------------------------------------

class JobStatus(Enum):
    PENDING   = "pending"
    RUNNING   = "running"
    COMPLETE  = "complete"
    FAILED    = "failed"
    CANCELLED = "cancelled"


class OperationCancelled(Exception):
    """Exception raised when an operation is cooperatively cancelled."""
    pass



# ---------------------------------------------------------------------------
# Input
# ---------------------------------------------------------------------------

@dataclass
class InputSpec:
    path: Path
    kind: str                  # "pdf", "docx", "eml", "msg", "image", "text"
    order_index: int = 0
    label: str | None = None   # User-assigned exhibit label or display name
    page_range: str | None = None  # "1-5", "3,7,12" — None means all pages
    sha256: str = ""

    def __post_init__(self):
        self.path = Path(self.path)
        if not self.sha256 and self.path.exists():
            self.sha256 = _hash_file(self.path)

    @staticmethod
    def from_path(path: str | Path, order_index: int = 0, **kwargs) -> "InputSpec":
        p = Path(path)
        kind = _infer_kind(p)
        return InputSpec(path=p, kind=kind, order_index=order_index, **kwargs)


def _hash_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _infer_kind(path: Path) -> str:
    ext = path.suffix.lower()
    return {
        ".pdf": "pdf",
        ".docx": "docx", ".doc": "docx",
        ".eml": "eml",
        ".msg": "msg",
        ".png": "image", ".jpg": "image", ".jpeg": "image",
        ".gif": "image", ".bmp": "image", ".tiff": "image", ".tif": "image",
        ".txt": "text", ".csv": "text",
        ".xlsx": "xlsx", ".xls": "xlsx",
    }.get(ext, "unknown")


# ---------------------------------------------------------------------------
# Operation parameters (one dataclass per operation)
# ---------------------------------------------------------------------------

@dataclass
class MergeParams:
    bookmarks: bool = True
    enforce_page_size: bool = True
    grayscale: bool = False
    paper_size: str = "letter"      # "letter", "legal", "a4"
    output_name: str | None = None


@dataclass
class SplitParams:
    mode: str = "ranges"            # "ranges" | "fixed" | "blank_page"
    ranges: list[str] = field(default_factory=list)  # ["1-5", "6-12"]
    pages_per_chunk: int | None = None
    name_template: str = "{source}_part{n:03d}"


@dataclass
class ExtractParams:
    page_selection: str = ""        # "1-5", "3,7,12", "1,3-5,9"
    output_name: str | None = None


@dataclass
class RotateParams:
    angle: int = 90                 # 90, 180, 270
    page_selection: str = "all"     # "all", "1,3,5", "1-4"


@dataclass
class ReorderParams:
    page_order: list[int] = field(default_factory=list)  # 1-based new order


@dataclass
class BatesParams:
    prefix: str = ""
    start_number: int = 1
    padding: int = 7
    position: str = "Bottom Right"  # "Bottom Right", "Bottom Center", "Top Center", "Top Right", "Top Left", "Bottom Left"
    font_size: int = 10
    shrink_conflict: bool = True
    sep: str = "-"
    font_name: str = "Helvetica"  # "Arial", "Times New Roman", "Courier New"
    naming: str = "Prefix_Range"  # "Prefix_Range", "Prefix_StartOnly"
    output_name: str | None = None



@dataclass
class EmailToPdfParams:
    grayscale: bool = False
    include_attachments: bool = True
    paper_size: str = "letter"
    output_name: str | None = None


@dataclass
class DocxToPdfParams:
    grayscale: bool = False
    output_name: str | None = None


@dataclass
class XlsxToPdfParams:
    grayscale: bool = False
    output_name: str | None = None


# ---------------------------------------------------------------------------
# Output spec
# ---------------------------------------------------------------------------

@dataclass
class OutputSpec:
    directory: Path
    name_template: str = "{source}_{op}_{date}"
    overwrite: bool = False
    open_after: bool = False

    def __post_init__(self):
        self.directory = Path(self.directory)


# ---------------------------------------------------------------------------
# Provenance
# ---------------------------------------------------------------------------

@dataclass
class ProvenanceRecord:
    source_hashes: dict[str, str] = field(default_factory=dict)  # path → sha256
    tool_version: str = ""
    operator: str | None = None
    note: str | None = None


# ---------------------------------------------------------------------------
# Result
# ---------------------------------------------------------------------------

@dataclass
class JobResult:
    outputs: list[Path] = field(default_factory=list)
    duration_seconds: float = 0.0
    page_count_in: int = 0
    page_count_out: int = 0
    warnings: list[str] = field(default_factory=list)
    error: str | None = None


# ---------------------------------------------------------------------------
# Job
# ---------------------------------------------------------------------------

@dataclass
class Job:
    operation: str
    inputs: list[InputSpec]
    params: (MergeParams | SplitParams | ExtractParams | RotateParams |
             ReorderParams | BatesParams | EmailToPdfParams |
             DocxToPdfParams | XlsxToPdfParams)
    output: OutputSpec
    provenance: ProvenanceRecord = field(default_factory=ProvenanceRecord)
    job_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    status: JobStatus = JobStatus.PENDING
    result: JobResult | None = None

    def to_dict(self) -> dict:
        """Serialize to a JSON-compatible dict for audit log persistence."""
        return {
            "job_id": self.job_id,
            "created_at": self.created_at.isoformat(),
            "operation": self.operation,
            "status": self.status.value,
            "inputs": [
                {
                    "path": str(s.path),
                    "kind": s.kind,
                    "order_index": s.order_index,
                    "label": s.label,
                    "page_range": s.page_range,
                    "sha256": s.sha256,
                }
                for s in self.inputs
            ],
            "provenance": {
                "source_hashes": self.provenance.source_hashes,
                "tool_version": self.provenance.tool_version,
                "operator": self.provenance.operator,
                "note": self.provenance.note,
            },
            "result": {
                "outputs": [str(p) for p in (self.result.outputs if self.result else [])],
                "duration_seconds": self.result.duration_seconds if self.result else None,
                "page_count_in": self.result.page_count_in if self.result else None,
                "page_count_out": self.result.page_count_out if self.result else None,
                "warnings": self.result.warnings if self.result else [],
                "error": self.result.error if self.result else None,
            } if self.result else None,
        }
