import unittest

from app.domain.alignment import Alignment
from app.domain.army import Army
from app.domain.battle import BattleOutcome
from app.services.battle_service import BattleService
from app.services.race_catalog import RaceCatalog


class BattleServiceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.catalog = RaceCatalog()
        self.service = BattleService()

    def _army_with(self, alignment: Alignment, composition: dict[str, int]) -> Army:
        army = Army(alignment)
        for name, count in composition.items():
            race = self.catalog.find_by_name(name)
            assert race is not None
            army.set_units(race, count)
        return army

    def test_osito_vs_hoggin_examples(self) -> None:
        hoggin = {"Hoggin": 1}
        cases = [
            ({"Osito": 1}, BattleOutcome.EVIL),
            ({"Osito": 2}, BattleOutcome.TIE),
            ({"Osito": 3}, BattleOutcome.GOOD),
        ]
        evil_army = self._army_with(Alignment.MALEVOLENT, hoggin)

        for composition, expected in cases:
            good_army = self._army_with(Alignment.BENEVOLENT, composition)
            result = self.service.resolve(good_army, evil_army)
            self.assertEqual(
                expected,
                result.outcome,
                f"Composition {composition} should result in {expected} but produced {result.outcome}",
            )

    def test_mixed_armies(self) -> None:
        good_composition = {
            race.name: 1
            for race in self.catalog.list_all(Alignment.BENEVOLENT)
            if race.name != "Osito"
        }
        evil_composition = {race.name: 1 for race in self.catalog.list_all(Alignment.MALEVOLENT)}

        good_army = self._army_with(Alignment.BENEVOLENT, good_composition)
        evil_army = self._army_with(Alignment.MALEVOLENT, evil_composition)
        result = self.service.resolve(good_army, evil_army)

        # Strength of both compositions should be identical (14).
        self.assertEqual(BattleOutcome.TIE, result.outcome)

    def test_alignment_validation(self) -> None:
        good_army = self._army_with(Alignment.MALEVOLENT, {"Hoggin": 1})
        evil_army = self._army_with(Alignment.BENEVOLENT, {"Osito": 1})

        with self.assertRaises(ValueError):
            self.service.resolve(good_army, evil_army)

        good_army = self._army_with(Alignment.BENEVOLENT, {"Osito": 1})
        evil_army = self._army_with(Alignment.BENEVOLENT, {"Osito": 1})
        with self.assertRaises(ValueError):
            self.service.resolve(good_army, evil_army)
