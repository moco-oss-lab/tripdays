"""tripdays: multi-leg trip day planner.

Given a list of stays (place, arrival date, departure date), tripdays
computes nights per stay, total trip days, gaps between stays, and
flags overlaps and same-day turnovers. Dates are ISO ``YYYY-MM-DD``.
Only the standard library is used.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

__all__ = ["Leg", "Stay", "Gap", "TripReport", "parse_leg", "assess_trip"]
__version__ = "0.1.0"


@dataclass(frozen=True)
class Leg:
    """One stay: arrive on ``arrive``, leave on ``depart``."""

    place: str
    arrive: date
    depart: date

    @property
    def nights(self) -> int:
        return (self.depart - self.arrive).days


@dataclass(frozen=True)
class Stay:
    leg: Leg
    nights: int


@dataclass(frozen=True)
class Gap:
    """Days between one departure and the next arrival."""

    after: str
    before: str
    days: int


@dataclass
class TripReport:
    stays: list[Stay]
    gaps: list[Gap]
    warnings: list[str]
    total_nights: int
    total_days: int

    def format(self) -> str:
        lines = ["Place  Arrive  Depart  Nights"]
        for stay in self.stays:
            leg = stay.leg
            lines.append(f"{leg.place}  {leg.arrive}  {leg.depart}  {stay.nights}")
        lines.append(f"Total nights: {self.total_nights}")
        lines.append(f"Total trip days: {self.total_days}")
        for gap in self.gaps:
            lines.append(
                f"Gap: {gap.days} day(s) between {gap.after} and {gap.before} "
                "(unaccounted / travel days)"
            )
        for warning in self.warnings:
            lines.append(f"Warning: {warning}")
        if not self.gaps and not self.warnings:
            lines.append("OK: stays are continuous with no overlaps.")
        return "\n".join(lines)


def parse_leg(raw: dict) -> Leg:
    """Parse one leg dict, raising ValueError on bad input."""
    try:
        place = str(raw["place"])
        arrive = date.fromisoformat(str(raw["arrive"]))
        depart = date.fromisoformat(str(raw["depart"]))
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"invalid leg: {raw!r}") from exc
    if depart < arrive:
        raise ValueError(
            f"departure before arrival for {place}: {arrive} -> {depart}"
        )
    return Leg(place=place, arrive=arrive, depart=depart)


def assess_trip(legs: list[Leg]) -> TripReport:
    """Assess sorted stays, detecting overlaps, gaps and turnovers."""
    if not legs:
        raise ValueError("itinerary has no legs")
    ordered = sorted(legs, key=lambda leg: (leg.arrive, leg.depart, leg.place))
    stays = [Stay(leg=leg, nights=leg.nights) for leg in ordered]
    gaps: list[Gap] = []
    warnings: list[str] = []
    for prev, nxt in zip(ordered, ordered[1:]):
        if nxt.arrive < prev.depart:
            warnings.append(
                f"overlap: {nxt.place} arrives {nxt.arrive} before "
                f"{prev.place} departs {prev.depart}"
            )
        elif nxt.arrive > prev.depart:
            gaps.append(
                Gap(after=prev.place, before=nxt.place,
                    days=(nxt.arrive - prev.depart).days)
            )
        else:  # same-day turnover
            warnings.append(
                f"same-day move: {prev.place} -> {nxt.place} on {prev.depart}"
            )
    for stay in stays:
        if stay.nights == 0:
            warnings.append(f"day visit (0 nights): {stay.leg.place}")
    total_nights = sum(stay.nights for stay in stays)
    total_days = (ordered[-1].depart - ordered[0].arrive).days
    return TripReport(
        stays=stays, gaps=gaps, warnings=warnings,
        total_nights=total_nights, total_days=total_days,
    )
