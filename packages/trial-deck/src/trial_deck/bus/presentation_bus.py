"""Courtroom presentation bus managing presenter vs public/jury views."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, List, Optional


class DisplayMode(str, Enum):
    NORMAL = "normal"
    BLACKOUT = "blackout"   # Full blackout for sidebar conferences
    WHITEOUT = "whiteout"
    SEALED = "sealed"       # Only visible to counsel/court


@dataclass
class ExhibitCallout:
    """Represents a zoom callout highlight on an exhibit."""

    x: float
    y: float
    width: float
    height: float
    zoom_factor: float = 2.0


@dataclass
class PresentationState:
    """Synchronized state of the courtroom presentation."""

    current_exhibit_id: Optional[str] = None
    page_number: int = 1
    display_mode: DisplayMode = DisplayMode.BLACKOUT  # Safety default
    active_callouts: List[ExhibitCallout] = field(default_factory=list)


class PresentationBus:
    """Event bus broadcasting presentation updates to juror displays and local consoles."""

    def __init__(self) -> None:
        self.state = PresentationState()
        self._listeners: List[Callable[[PresentationState], None]] = []

    def subscribe(self, listener: Callable[[PresentationState], None]) -> None:
        """Register a subscriber callback for state updates."""
        self._listeners.append(listener)

    def _notify(self) -> None:
        for listener in self._listeners:
            listener(self.state)

    def set_exhibit(self, exhibit_id: str, page: int = 1) -> None:
        """Set active exhibit and page."""
        self.state.current_exhibit_id = exhibit_id
        self.state.page_number = page
        self.state.active_callouts.clear()
        self._notify()

    def set_mode(self, mode: DisplayMode) -> None:
        """Toggle display mode (e.g. blackout during sidebar)."""
        self.state.display_mode = mode
        self._notify()

    def add_callout(self, callout: ExhibitCallout) -> None:
        """Add an active zoom callout highlight."""
        self.state.active_callouts.append(callout)
        self._notify()

    def clear_callouts(self) -> None:
        """Remove all active callouts."""
        self.state.active_callouts.clear()
        self._notify()
