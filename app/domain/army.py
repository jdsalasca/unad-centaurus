"""Army representation for the Centaurus simulation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

from .alignment import Alignment
from .race import Race


@dataclass
class Army:
    """An army composed of a number of units for each race."""

    alignment: Alignment
    roster: Dict[Race, int] = field(default_factory=dict)

    def set_units(self, race: Race, count: int) -> None:
        """Set the number of units for ``race`` ensuring non-negative counts."""

        if race.alignment is not self.alignment:
            raise ValueError("Race alignment does not match the army alignment")
        sanitized = max(0, int(count))
        if sanitized:
            self.roster[race] = sanitized
        else:
            self.roster.pop(race, None)

    def total_units(self) -> int:
        return sum(self.roster.values())

    def total_power(self) -> int:
        return sum(race.compute_power(count) for race, count in self.roster.items())

    def snapshot(self) -> dict[str, int]:
        """Return a serialisable view of the roster keyed by race name."""

        return {race.name: count for race, count in self.roster.items()}
