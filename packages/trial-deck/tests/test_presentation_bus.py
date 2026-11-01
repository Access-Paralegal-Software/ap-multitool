"""Tests for PresentationBus and courtroom display safety modes."""

from trial_deck.bus.presentation_bus import (
    DisplayMode,
    ExhibitCallout,
    PresentationBus,
    PresentationState,
)


def test_presentation_bus_default_safety_blackout():
    bus = PresentationBus()
    # Presentation bus must default to BLACKOUT for courtroom privacy
    assert bus.state.display_mode == DisplayMode.BLACKOUT
    assert bus.state.current_exhibit_id is None


def test_presentation_bus_state_notification():
    bus = PresentationBus()
    updates: list[PresentationState] = []
    bus.subscribe(lambda st: updates.append(PresentationState(
        current_exhibit_id=st.current_exhibit_id,
        page_number=st.page_number,
        display_mode=st.display_mode,
        active_callouts=list(st.active_callouts),
    )))

    bus.set_exhibit("EXHIBIT-P-001", page=3)
    assert len(updates) == 1
    assert updates[0].current_exhibit_id == "EXHIBIT-P-001"
    assert updates[0].page_number == 3

    bus.set_mode(DisplayMode.NORMAL)
    assert len(updates) == 2
    assert updates[1].display_mode == DisplayMode.NORMAL

    bus.add_callout(ExhibitCallout(x=100.0, y=200.0, width=300.0, height=150.0, zoom_factor=2.5))
    assert len(updates) == 3
    assert len(updates[2].active_callouts) == 1
    assert updates[2].active_callouts[0].zoom_factor == 2.5
