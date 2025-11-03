"""Utility service that exposes the available races grouped by alignment."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Mapping, Optional

from app.domain.alignment import Alignment
from app.domain.race import BENEVOLENT_RACES, MALEVOLENT_RACES, Race


@dataclass
class RaceCatalog:
    """Provides read-only access to the registered races."""

    _by_alignment: Mapping[Alignment, tuple[Race, ...]] = field(init=False)

    def __post_init__(self) -> None:
        self._by_alignment = {
            Alignment.BENEVOLENT: BENEVOLENT_RACES,
            Alignment.MALEVOLENT: MALEVOLENT_RACES,
        }

    def list_all(self, alignment: Alignment) -> tuple[Race, ...]:
        return self._by_alignment[alignment]

    def find_by_name(self, name: str) -> Optional[Race]:
        normalized = name.strip().lower()
        for races in self._by_alignment.values():
            for race in races:
                if race.name.lower() == normalized:
                    return race
        return None

    def names_for(self, alignment: Alignment) -> Iterable[str]:
        return (race.name for race in self.list_all(alignment))
