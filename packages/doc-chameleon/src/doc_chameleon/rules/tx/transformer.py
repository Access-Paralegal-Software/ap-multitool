from __future__ import annotations

import docx


def transform(doc: docx.Document, venue_overlay: str | None = None) -> docx.Document:
    """Apply Texas formatting rules (TRCP statewide baseline).

    venue_overlay: optional local venue code (e.g. 'harris', 'travis'). Overlay
    architecture is reserved but empty at MVP — not implemented.

    Not implemented — target: Phase 2 MVP.
    """
    raise NotImplementedError("Texas transformer not implemented. Target: Phase 2 MVP.")
