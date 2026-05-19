"""
core/operations — Operation registry.

Each operation is a callable:
    def handle(job: Job, progress: Callable[[str, float], None]) -> JobResult

Add new operations here and they become available to the engine.
"""

from core.operations.merge import handle as _merge
from core.operations.split import handle as _split
from core.operations.extract import handle as _extract
from core.operations.rotate import handle as _rotate
from core.operations.reorder import handle as _reorder
from core.operations.email_to_pdf import handle as _email_to_pdf
from core.operations.docx_to_pdf import handle as _docx_to_pdf
from core.operations.xlsx_to_pdf import handle as _xlsx_to_pdf
from core.operations.bates_stamp import handle as _bates_stamp

OPERATION_REGISTRY: dict = {
    "merge":   _merge,
    "split":   _split,
    "extract": _extract,
    "rotate":  _rotate,
    "reorder": _reorder,
    "email_to_pdf": _email_to_pdf,
    "docx_to_pdf": _docx_to_pdf,
    "xlsx_to_pdf": _xlsx_to_pdf,
    "bates_stamp": _bates_stamp,
}

