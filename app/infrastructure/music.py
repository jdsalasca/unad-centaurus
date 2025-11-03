"""Optional retro music playback using pygame if available."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


class MusicPlayer(ABC):
    """Interface to control background music."""

    @abstractmethod
    def play(self) -> bool:  # pragma: no cover - interface method
        ...

    @abstractmethod
    def stop(self) -> None:  # pragma: no cover - interface method
        ...

    @property
    def is_available(self) -> bool:  # pragma: no cover - default implementation
        return True


@dataclass
class RetroMusicPlayer(MusicPlayer):
    """Best-effort retro music player using pygame's mixer."""

    audio_path: Path = field(default_factory=lambda: Path("assets/retro_theme.mp3"))
    _pygame: Optional[object] = field(init=False, default=None)
    _available: bool = field(init=False, default=False)

    def __post_init__(self) -> None:
        try:
            import pygame

            self._pygame = pygame
            if self.audio_path.exists():
                pygame.mixer.init()
                pygame.mixer.music.load(self.audio_path.as_posix())
                self._available = True
        except Exception:
            self._available = False
            self._pygame = None

    def play(self) -> bool:
        if not self._available or not self._pygame:
            return False
        try:
            self._pygame.mixer.music.play(loops=-1)
            return True
        except Exception:
            return False

    def stop(self) -> None:
        if self._available and self._pygame:
            try:
                self._pygame.mixer.music.stop()
            except Exception:
                pass

    @property
    def is_available(self) -> bool:
        return self._available
