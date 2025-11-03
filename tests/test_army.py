import unittest

from app.domain.alignment import Alignment
from app.domain.army import Army
from app.domain.race import Race


class ArmyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.osito = Race(name="Osito", alignment=Alignment.BENEVOLENT, battle_value=1, pixel_color="#fff")
        self.hoggin = Race(name="Hoggin", alignment=Alignment.MALEVOLENT, battle_value=2, pixel_color="#333")
        self.good_army = Army(Alignment.BENEVOLENT)

    def test_set_units_validates_alignment_and_updates_roster(self) -> None:
        with self.assertRaises(ValueError):
            self.good_army.set_units(self.hoggin, 2)

        self.good_army.set_units(self.osito, 3)
        self.assertEqual(3, self.good_army.total_units())
        self.assertEqual({"Osito": 3}, self.good_army.snapshot())

        # Setting to zero removes the race from the roster.
        self.good_army.set_units(self.osito, 0)
        self.assertEqual({}, self.good_army.snapshot())
