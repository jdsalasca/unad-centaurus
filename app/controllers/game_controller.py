"""Application layer controller orchestrating the simulation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from app.domain.alignment import Alignment
from app.domain.army import Army
from app.domain.battle import BattleResult
from app.domain.race import Race
from app.infrastructure.music import MusicPlayer
from app.infrastructure.persistence import ArmyStorage
from app.services.battle_service import BattleService
from app.services.race_catalog import RaceCatalog


@dataclass
class GameController:
    """Coordinates UI requests with domain services."""

    battle_service: BattleService
    race_catalog: RaceCatalog
    storage: Optional[ArmyStorage] = None
    music_player: Optional[MusicPlayer] = None
    _armies: Dict[Alignment, Army] = field(init=False)

    def __post_init__(self) -> None:
        self._armies = {
            Alignment.BENEVOLENT: Army(Alignment.BENEVOLENT),
            Alignment.MALEVOLENT: Army(Alignment.MALEVOLENT),
        }
        if self.storage:
            self._load_persisted_armies()

    def list_races(self, alignment: Alignment) -> tuple[Race, ...]:
        return self.race_catalog.list_all(alignment)

    def set_units(self, race: Race, count: int) -> None:
        army = self._armies[race.alignment]
        army.set_units(race, count)

    def army_snapshot(self, alignment: Alignment) -> dict[str, int]:
        return self._armies[alignment].snapshot()

    def army_stats(self, alignment: Alignment) -> tuple[int, int]:
        """Return (total_units, total_power) for the requested army."""

        army = self._armies[alignment]
        return army.total_units(), army.total_power()

    def simulate_battle(self) -> BattleResult:
        result = self.battle_service.resolve(
            good_army=self._armies[Alignment.BENEVOLENT],
            evil_army=self._armies[Alignment.MALEVOLENT],
        )
        self._persist_armies()
        return result

    def _persist_armies(self) -> None:
        if not self.storage:
            return
        for alignment, army in self._armies.items():
            self.storage.save(alignment, army.snapshot())

    def _load_persisted_armies(self) -> None:
        assert self.storage is not None
        for alignment in (Alignment.BENEVOLENT, Alignment.MALEVOLENT):
            saved = self.storage.load(alignment)
            for name, count in saved.items():
                race = self.race_catalog.find_by_name(name)
                if race and race.alignment is alignment:
                    self._armies[alignment].set_units(race, count)

    def play_music(self) -> bool:
        if not self.music_player:
            return False
        if not self.music_player.is_available:
            return False
        return self.music_player.play()

    def stop_music(self) -> None:
        if self.music_player:
            self.music_player.stop()

    def reset_armies(self) -> None:
        for army in self._armies.values():
            army.roster.clear()
        self._persist_armies()
