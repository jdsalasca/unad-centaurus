"""Domain service objects for resolving battles."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

from .alignment import Alignment


class BattleOutcome(Enum):
    """Possible outcomes of a battle."""

    GOOD = auto()
    EVIL = auto()
    TIE = auto()

    @property
    def message(self) -> str:
        if self is BattleOutcome.GOOD:
            return "¡Gana el Bien!"
        if self is BattleOutcome.EVIL:
            return "Gana el Mal..."
        return "La batalla termina en empate."


@dataclass(frozen=True)
class BattleResult:
    """Value object holding the score for both armies."""

    good_power: int
    evil_power: int

    @property
    def outcome(self) -> BattleOutcome:
        if self.good_power > self.evil_power:
            return BattleOutcome.GOOD
        if self.evil_power > self.good_power:
            return BattleOutcome.EVIL
        return BattleOutcome.TIE

    @property
    def winner_alignment(self) -> Optional[Alignment]:
        if self.outcome is BattleOutcome.GOOD:
            return Alignment.BENEVOLENT
        if self.outcome is BattleOutcome.EVIL:
            return Alignment.MALEVOLENT
        return None
