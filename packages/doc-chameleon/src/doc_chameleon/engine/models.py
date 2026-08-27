from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ParagraphRecord:
    index: int
    text: str
    style_name: str | None


@dataclass
class SectionRecord:
    page_width_emu: int
    page_height_emu: int
    left_margin_emu: int
    right_margin_emu: int
    top_margin_emu: int
    bottom_margin_emu: int


@dataclass
class DocumentRecord:
    source_path: Path | None
    paragraphs: list[ParagraphRecord] = field(default_factory=list)
    sections: list[SectionRecord] = field(default_factory=list)
