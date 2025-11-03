"""Persistence layer for storing army configurations."""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict

from app.domain.alignment import Alignment


class ArmyStorage(ABC):
    """Persistence abstraction for saving and loading army rosters."""

    @abstractmethod
    def save(self, alignment: Alignment, roster: Dict[str, int]) -> None:  # pragma: no cover - interface
        ...

    @abstractmethod
    def load(self, alignment: Alignment) -> Dict[str, int]:  # pragma: no cover - interface
        ...


@dataclass
class JsonArmyStorage(ArmyStorage):
    """Simple JSON-based storage mechanism."""

    filepath: Path = field(default_factory=lambda: Path("data/armies.json"))

    def save(self, alignment: Alignment, roster: Dict[str, int]) -> None:
        data = self._read_all()
        data[alignment.name] = {name: int(count) for name, count in roster.items() if count > 0}
        self._write_all(data)

    def load(self, alignment: Alignment) -> Dict[str, int]:
        data = self._read_all()
        saved = data.get(alignment.name, {})
        return {name: int(count) for name, count in saved.items() if count > 0}

    def _read_all(self) -> Dict[str, Dict[str, int]]:
        if not self.filepath.exists():
            return {}
        try:
            return json.loads(self.filepath.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}

    def _write_all(self, data: Dict[str, Dict[str, int]]) -> None:
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        self.filepath.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
