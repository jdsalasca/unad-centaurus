"""UI abstractions to support multiple front-ends."""

from __future__ import annotations

from abc import ABC, abstractmethod


class UserInterface(ABC):
    """Common contract for UI front-ends."""

    @abstractmethod
    def start(self) -> None:  # pragma: no cover
        ...
