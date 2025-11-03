"""Entry point for the Centaurus war simulation game."""

from __future__ import annotations

import argparse
from typing import Callable

from app.controllers.game_controller import GameController
from app.infrastructure.music import RetroMusicPlayer
from app.infrastructure.persistence import JsonArmyStorage
from app.services.battle_service import BattleService
from app.services.race_catalog import RaceCatalog
from app.ui.base import UserInterface
from app.ui.console import ConsoleUI
from app.ui.menu import InterfaceMode, prompt_mode
from app.utils.dependencies import ensure_optional_dependencies


def build_controller(enable_music: bool) -> GameController:
    """Wire up dependencies for the game controller."""

    battle_service = BattleService()
    catalog = RaceCatalog()
    storage = JsonArmyStorage()
    music_player = RetroMusicPlayer() if enable_music else None
    return GameController(
        battle_service=battle_service,
        race_catalog=catalog,
        storage=storage,
        music_player=music_player,
    )


def build_ui(mode: InterfaceMode, controller: GameController) -> UserInterface:
    if mode is InterfaceMode.CONSOLE:
        return ConsoleUI(controller)

    try:
        from app.ui.gui import GameWindow
    except ModuleNotFoundError as exc:  # pragma: no cover - optional dependency
        print(
            "No se encontró Tkinter, se continuará automáticamente en modo consola.\n"
            "Sugerencias para habilitar la interfaz gráfica:\n"
            "  • Windows: instala Python desde https://www.python.org/downloads/ asegurándote de "
            "incluir la opción 'tcl/tk and IDLE'.\n"
            "  • macOS: `brew install python-tk`.\n"
            "  • Linux Debian/Ubuntu: `sudo apt install python3-tk`.\n"
            "  • Fedora/RHEL: `sudo dnf install python3-tkinter`.\n"
        )
        return ConsoleUI(controller)

    return GameWindow(controller)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Simulador de la batalla por Centauro")
    parser.add_argument(
        "--mode",
        choices=[mode.value for mode in InterfaceMode] + ["menu"],
        default="menu",
        help="Modo de interacción: console, gui o menu (por defecto)",
    )
    parser.add_argument(
        "--no-music",
        action="store_true",
        help="Desactiva la carga del reproductor de música retro",
    )
    return parser.parse_args()


def main() -> None:
    ensure_optional_dependencies()
    args = parse_args()
    if args.mode == "menu":
        mode = prompt_mode()
    else:
        mode = InterfaceMode(args.mode)

    controller = build_controller(enable_music=not args.no_music)
    ui = build_ui(mode, controller)
    ui.start()


if __name__ == "__main__":
    main()
