"""Domain model for characters and races in Centaurus."""

from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import Final

from .alignment import Alignment


@dataclass(frozen=True)
class Race(ABC):
    """Base abstraction for any race that can fight in Centaurus."""

    name: str
    alignment: Alignment
    battle_value: int
    pixel_color: str

    def compute_power(self, troops: int) -> int:
        """Return the total power contributed by ``troops`` units of this race."""

        return self.battle_value * max(0, troops)


class BenevolentRace(Race):
    """Marker class for benevolent races."""

    def __init__(self, name: str, battle_value: int, pixel_color: str) -> None:
        super().__init__(name=name, alignment=Alignment.BENEVOLENT, battle_value=battle_value, pixel_color=pixel_color)


class MalevolentRace(Race):
    """Marker class for malevolent races."""

    def __init__(self, name: str, battle_value: int, pixel_color: str) -> None:
        super().__init__(name=name, alignment=Alignment.MALEVOLENT, battle_value=battle_value, pixel_color=pixel_color)


class Osito(BenevolentRace):
    def __init__(self) -> None:
        super().__init__("Osito", 1, "#f7c8d0")


class Principe(BenevolentRace):
    def __init__(self) -> None:
        super().__init__("Príncipe", 2, "#95c0ff")


class Enano(BenevolentRace):
    def __init__(self) -> None:
        super().__init__("Enano", 3, "#fbe29f")


class Cari(BenevolentRace):
    def __init__(self) -> None:
        super().__init__("Cari", 4, "#e87956")


class Fulo(BenevolentRace):
    def __init__(self) -> None:
        super().__init__("Fulo", 5, "#8870ff")


class Lolo(MalevolentRace):
    def __init__(self) -> None:
        super().__init__("Lolo", 2, "#ff6f91")


class Fulano(MalevolentRace):
    def __init__(self) -> None:
        super().__init__("Fulano", 2, "#ff9671")


class Hoggin(MalevolentRace):
    def __init__(self) -> None:
        super().__init__("Hoggin", 2, "#ffc75f")


class Lurco(MalevolentRace):
    def __init__(self) -> None:
        super().__init__("Lurco", 3, "#a17fe0")


class Trolli(MalevolentRace):
    def __init__(self) -> None:
        super().__init__("Trolli", 5, "#5c5470")


BENEVOLENT_RACES: Final[tuple[Race, ...]] = (
    Osito(),
    Principe(),
    Enano(),
    Cari(),
    Fulo(),
)

MALEVOLENT_RACES: Final[tuple[Race, ...]] = (
    Lolo(),
    Fulano(),
    Hoggin(),
    Lurco(),
    Trolli(),
)
