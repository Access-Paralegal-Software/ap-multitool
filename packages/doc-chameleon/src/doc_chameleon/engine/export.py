from __future__ import annotations

from pathlib import Path

import docx


def save(doc: docx.Document, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(path))
