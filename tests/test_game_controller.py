import unittest

from app.controllers.game_controller import GameController
from app.domain.alignment import Alignment
from app.domain.battle import BattleOutcome
from app.infrastructure.music import MusicPlayer
from app.infrastructure.persistence import ArmyStorage
from app.services.battle_service import BattleService
from app.services.race_catalog import RaceCatalog


class FakeStorage(ArmyStorage):
    def __init__(self) -> None:
        self.saved = {Alignment.BENEVOLENT.name: {}, Alignment.MALEVOLENT.name: {}}

    def save(self, alignment, roster):
        self.saved[alignment.name] = dict(roster)

    def load(self, alignment):
        return dict(self.saved.get(alignment.name, {}))


class FakeMusicPlayer(MusicPlayer):
    def __init__(self, available: bool) -> None:
        self._available = available
        self.play_calls = 0
        self.stop_calls = 0

    def play(self) -> bool:
        if not self._available:
            return False
        self.play_calls += 1
        return True

    def stop(self) -> None:
        self.stop_calls += 1

    @property
    def is_available(self) -> bool:
        return self._available


class GameControllerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.catalog = RaceCatalog()
        self.storage = FakeStorage()
        self.music = FakeMusicPlayer(available=True)
        self.controller = GameController(
            battle_service=BattleService(),
            race_catalog=self.catalog,
            storage=self.storage,
            music_player=self.music,
        )

    def test_simulate_battle_persists_state(self) -> None:
        osito = self.catalog.find_by_name("Osito")
        hoggin = self.catalog.find_by_name("Hoggin")
        assert osito and hoggin
        self.controller.set_units(osito, 3)
        self.controller.set_units(hoggin, 1)

        result = self.controller.simulate_battle()
        self.assertEqual(BattleOutcome.GOOD, result.outcome)
        self.assertEqual({"Osito": 3}, self.storage.saved[Alignment.BENEVOLENT.name])
        self.assertEqual({"Hoggin": 1}, self.storage.saved[Alignment.MALEVOLENT.name])

    def test_reset_armies_clears_storage(self) -> None:
        osito = self.catalog.find_by_name("Osito")
        hoggin = self.catalog.find_by_name("Hoggin")
        assert osito and hoggin
        self.controller.set_units(osito, 3)
        self.controller.set_units(hoggin, 1)
        self.controller.simulate_battle()

        self.controller.reset_armies()
        self.assertEqual({}, self.storage.saved[Alignment.BENEVOLENT.name])
        self.assertEqual({}, self.storage.saved[Alignment.MALEVOLENT.name])

    def test_music_controls_respect_availability(self) -> None:
        self.assertTrue(self.controller.play_music())
        self.controller.stop_music()
        self.assertEqual(1, self.music.play_calls)
        self.assertEqual(1, self.music.stop_calls)

        unavailable_player = FakeMusicPlayer(available=False)
        controller = GameController(
            battle_service=BattleService(),
            race_catalog=self.catalog,
            storage=self.storage,
            music_player=unavailable_player,
        )
        self.assertFalse(controller.play_music())
        self.assertEqual(0, unavailable_player.play_calls)

    def test_army_stats_reports_units_and_power(self) -> None:
        osito = self.catalog.find_by_name("Osito")
        hoggin = self.catalog.find_by_name("Hoggin")
        assert osito and hoggin
        self.controller.set_units(osito, 3)
        self.controller.set_units(hoggin, 1)
        good_units, good_power = self.controller.army_stats(Alignment.BENEVOLENT)
        evil_units, evil_power = self.controller.army_stats(Alignment.MALEVOLENT)
        self.assertEqual((3, 3), (good_units, good_power))
        self.assertEqual((1, 2), (evil_units, evil_power))


if __name__ == "__main__":
    unittest.main()
