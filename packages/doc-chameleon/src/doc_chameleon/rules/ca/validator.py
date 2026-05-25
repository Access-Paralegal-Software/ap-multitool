from __future__ import annotations

import docx

from doc_chameleon.engine.models import DocumentRecord


def validate(doc: docx.Document, record: DocumentRecord) -> list[str]:
    """Validate document against California formatting rules.

    Returns a list of warning strings. Not implemented — target: Phase 2 MVP.
    """
    raise NotImplementedError("California validator not implemented. Target: Phase 2 MVP.")
