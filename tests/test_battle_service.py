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
        good_army = self._army_with(
            Alignment.BENEVOLENT,
            {"Fulo": 1, "Cari": 1, "Enano": 1, "Príncipe": 1},
        )
        evil_army = self._army_with(
            Alignment.MALEVOLENT,
            {"Trolli": 1, "Lurco": 1, "Hoggin": 1, "Fulano": 1, "Lolo": 1},
        )
        result = self.service.resolve(good_army, evil_army)
        self.assertEqual(BattleOutcome.TIE, result.outcome)


if __name__ == "__main__":
    unittest.main()
