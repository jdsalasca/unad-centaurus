import unittest

from app.domain.alignment import Alignment


class AlignmentTestCase(unittest.TestCase):
    def test_label_property(self) -> None:
        self.assertEqual("Bien", Alignment.BENEVOLENT.label)
        self.assertEqual("Mal", Alignment.MALEVOLENT.label)
