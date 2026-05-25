from __future__ import annotations

import docx

from doc_chameleon.engine.models import DocumentRecord


def validate(doc: docx.Document, record: DocumentRecord, venue_overlay: str | None = None) -> list[str]:
    """Validate document against Texas formatting rules.

    venue_overlay: optional local venue code. Overlay architecture reserved but
    empty at MVP — statewide baseline only.

    Returns a list of warning strings. Not implemented — target: Phase 2 MVP.
    """
    raise NotImplementedError("Texas validator not implemented. Target: Phase 2 MVP.")
