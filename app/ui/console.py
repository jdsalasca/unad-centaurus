"""Console based UI for the Centaurus simulation."""

from __future__ import annotations

from dataclasses import dataclass

from app.controllers.game_controller import GameController
from app.domain.alignment import Alignment
from app.ui.base import UserInterface


@dataclass
class ConsoleUI(UserInterface):
    """Simple text interface to configure armies and run battles."""

    controller: GameController

    def start(self) -> None:
        self._print_header()
        while True:
            self._print_menu()
            option = input("Selecciona una opción: ").strip()
            if option == "1":
                self._configure_army(Alignment.BENEVOLENT)
            elif option == "2":
                self._configure_army(Alignment.MALEVOLENT)
            elif option == "3":
                self._simulate_battle()
            elif option == "4":
                self.controller.reset_armies()
                print("Los ejércitos han sido reiniciados.\n")
            elif option == "5":
                self._handle_music(True)
            elif option == "6":
                self._handle_music(False)
            elif option == "7":
                self._show_credits()
            elif option == "0":
                print("Hasta pronto, que Centauro permanezca en equilibrio.")
                break
            else:
                print("Opción inválida. Intenta nuevamente.\n")

    def _print_header(self) -> None:
        print(
            """
╔════════════════════════════════════════════════════════╗
║   Universidad Nacional Abierta y a Distancia - UNAD    ║
║  Proyecto Centaurus por Juan David Salas Camargo (JD)  ║
╠════════════════════════════════════════════════════════╣
║               Batalla por Centauro - CLI               ║
╚════════════════════════════════════════════════════════╝
            """
        )

    def _print_menu(self) -> None:
        good_units, good_power = self.controller.army_stats(Alignment.BENEVOLENT)
        evil_units, evil_power = self.controller.army_stats(Alignment.MALEVOLENT)
        print(
            f"""
Menú principal:
  1) Configurar ejército del Bien
  2) Configurar ejército del Mal
  3) Simular batalla
  4) Reiniciar ejércitos
  5) Activar música retro (si disponible)
  6) Detener música
  7) Ver creditos
  0) Salir

Resumen actual:
  Bien  -> tropas: {good_units:3d} | poder total: {good_power:3d}
  Mal   -> tropas: {evil_units:3d} | poder total: {evil_power:3d}

            """
        )

    def _configure_army(self, alignment: Alignment) -> None:
        print(f"Configura el ejército del {alignment.label}.")
        snapshot = self.controller.army_snapshot(alignment)
        races = self.controller.list_races(alignment)
        for idx, race in enumerate(races, start=1):
            current = snapshot.get(race.name, 0)
            prompt = f"  {idx}) {race.name} (valor {race.battle_value}) [actual {current}]: "
            count = self._ask_non_negative(prompt)
            self.controller.set_units(race, count)
        units, power = self.controller.army_stats(alignment)
        print(f"\n→ Ejército del {alignment.label}: {units} tropas con poder {power}.\n")

    def _simulate_battle(self) -> None:
        result = self.controller.simulate_battle()
        print(
            f"\nResultado: {result.outcome.message}\n"
            f"  Fuerza del Bien: {result.good_power}\n"
            f"  Fuerza del Mal:  {result.evil_power}\n"
        )

    def _handle_music(self, activate: bool) -> None:
        if activate:
            if self.controller.play_music():
                print("Música retro activada.\n")
            else:
                print("No fue posible reproducir la música retro.\n")
        else:
            self.controller.stop_music()
            print("Música retro detenida.\n")

    def _ask_non_negative(self, message: str) -> int:
        while True:
            raw = input(message).strip() or "0"
            if raw.isdigit():
                return int(raw)
            print(" Ingresa un número entero mayor o igual a cero.")

    def _show_credits(self) -> None:
        print("\n=== Creditos del proyecto ===")
        for line in self.controller.credits():
            print(f"  {line}")
        print()
