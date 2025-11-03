import json
import tempfile
import unittest
from pathlib import Path

from app.domain.alignment import Alignment
from app.infrastructure.persistence import JsonArmyStorage


class JsonArmyStorageTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.path = Path(self.tmpdir.name) / "armies.json"
        self.storage = JsonArmyStorage(filepath=self.path)

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_save_and_load_roundtrip(self) -> None:
        roster = {"Osito": 3, "Principe": 2, "Invalido": 0}
        self.storage.save(Alignment.BENEVOLENT, roster)
        loaded = self.storage.load(Alignment.BENEVOLENT)
        self.assertEqual({"Osito": 3, "Principe": 2}, loaded)

    def test_load_handles_missing_and_invalid_files(self) -> None:
        # Missing file returns empty dict.
        self.assertEqual({}, self.storage.load(Alignment.MALEVOLENT))

        # Invalid JSON should be treated as empty.
        self.path.write_text("not-json", encoding="utf-8")
        self.assertEqual({}, self.storage.load(Alignment.MALEVOLENT))

    def test_save_creates_parent_directory(self) -> None:
        nested_path = Path(self.tmpdir.name) / "nested" / "armies.json"
        storage = JsonArmyStorage(filepath=nested_path)
        storage.save(Alignment.MALEVOLENT, {"Hoggin": 1})
        self.assertTrue(nested_path.exists())
        data = json.loads(nested_path.read_text(encoding="utf-8"))
        self.assertIn("MALEVOLENT", data)
