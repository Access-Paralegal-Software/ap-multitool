"""Monitor detection and output assignment."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class MonitorInfo:
    id: int
    name: str
    is_primary: bool
    width: int
    height: int


class CourtroomMonitorRouter:
    """Routes counsel control to primary display and jury feed to secondary display."""

    def __init__(self, displays: list[MonitorInfo] | None = None) -> None:
        self.displays = displays or [
            MonitorInfo(id=0, name="Counsel Deck (Primary)", is_primary=True, width=1920, height=1080),
            MonitorInfo(id=1, name="Jury / Witness Feed (Secondary)", is_primary=False, width=1920, height=1080),
        ]

    def get_counsel_display(self) -> MonitorInfo:
        for d in self.displays:
            if d.is_primary:
                return d
        return self.displays[0]

    def get_jury_display(self) -> MonitorInfo:
        for d in self.displays:
            if not d.is_primary:
                return d
        return self.displays[-1]
