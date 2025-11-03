import unittest

from app.domain.alignment import Alignment
from app.services.race_catalog import RaceCatalog


class RaceCatalogTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.catalog = RaceCatalog()

    def test_names_exist_for_both_alignments(self) -> None:
        good_names = list(self.catalog.names_for(Alignment.BENEVOLENT))
        evil_names = list(self.catalog.names_for(Alignment.MALEVOLENT))
        self.assertGreater(len(good_names), 0)
        self.assertGreater(len(evil_names), 0)
        self.assertNotEqual(set(good_names), set(evil_names))

    def test_lookup_is_case_insensitive(self) -> None:
        race = self.catalog.find_by_name("osito")
        self.assertIsNotNone(race)
        self.assertEqual("Osito", race.name)

    def test_lookup_unknown_returns_none(self) -> None:
        self.assertIsNone(self.catalog.find_by_name("desconocido"))
