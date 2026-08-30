"""
core/operations — Operation registry.

Each operation is a callable:
    def handle(job: Job, progress: Callable[[str, float], None]) -> JobResult

Add new operations here and they become available to the engine.
"""

from ap_core.operations.merge import handle as _merge
from ap_core.operations.split import handle as _split
from ap_core.operations.extract import handle as _extract
from ap_core.operations.rotate import handle as _rotate
from ap_core.operations.reorder import handle as _reorder
from ap_core.operations.email_to_pdf import handle as _email_to_pdf
from ap_core.operations.docx_to_pdf import handle as _docx_to_pdf
from ap_core.operations.xlsx_to_pdf import handle as _xlsx_to_pdf
from ap_core.operations.bates_stamp import handle as _bates_stamp
from ap_core.operations.folder_tree import handle as _folder_tree

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
    "folder_tree": _folder_tree,
}

