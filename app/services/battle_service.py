"""Application service to resolve battles between armies."""

from __future__ import annotations

from dataclasses import dataclass

from app.domain.alignment import Alignment
from app.domain.army import Army
from app.domain.battle import BattleResult


@dataclass
class BattleService:
    """Pure service that evaluates the strength of two armies."""

    def resolve(self, good_army: Army, evil_army: Army) -> BattleResult:
        if good_army.alignment is not Alignment.BENEVOLENT:
            raise ValueError("El ejército del bien debe estar compuesto por razas benévolas")
        if evil_army.alignment is not Alignment.MALEVOLENT:
            raise ValueError("El ejército del mal debe estar compuesto por razas malévolas")
        return BattleResult(good_power=good_army.total_power(), evil_power=evil_army.total_power())
