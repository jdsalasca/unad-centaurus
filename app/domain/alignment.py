"""Domain value objects for the Centaurus war simulation."""

from __future__ import annotations

from enum import Enum, auto


class Alignment(Enum):
    """Represents the side of the conflict a race belongs to."""

    BENEVOLENT = auto()
    MALEVOLENT = auto()

    @property
    def label(self) -> str:
        """Friendly label for UI purposes."""

        return "Bien" if self is Alignment.BENEVOLENT else "Mal"
