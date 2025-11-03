"""Helper utilities to select which UI front-end to use."""

from __future__ import annotations

from enum import Enum


class InterfaceMode(str, Enum):
    CONSOLE = "console"
    GUI = "gui"


def prompt_mode() -> InterfaceMode:
    """Ask the user to choose the interface mode via console input."""

    while True:
        print(
            """
Selecciona el modo de interacción:
  1) Consola
  2) Interfaz gráfica (Tkinter)
            """
        )
        choice = input("Opción [1-2]: ").strip()
        if choice == "1":
            return InterfaceMode.CONSOLE
        if choice == "2":
            return InterfaceMode.GUI
        print("Opción inválida. Intenta nuevamente.\n")
