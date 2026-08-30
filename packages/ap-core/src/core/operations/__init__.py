import sys as _sys
from importlib import import_module as _import_module

from ap_core.operations import *

for _name in (
    '_conversion_backend',
    'bates_stamp',
    'docx_to_pdf',
    'email_to_pdf',
    'extract',
    'folder_tree',
    'merge',
    'reorder',
    'rotate',
    'split',
    'xlsx_to_pdf',
):
    _sys.modules[f"{__name__}.{_name}"] = _import_module(f"ap_core.operations.{_name}")
