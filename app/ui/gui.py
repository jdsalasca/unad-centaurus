"""Tkinter-based interface for the Centaurus simulation."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Dict

from app.controllers.game_controller import GameController
from app.domain.alignment import Alignment
from app.domain.race import Race
from app.ui.base import UserInterface
from app.ui.pixel_art import get_sprite, render_sprite


class ArmySelectionPanel(ttk.LabelFrame):
    """Widget that lets the user choose troop counts for a given alignment."""

    def __init__(self, master: tk.Misc, controller: GameController, alignment: Alignment) -> None:
        super().__init__(master, text=f"Ejército del {alignment.label}", padding=12)
        self._controller = controller
        self._alignment = alignment
        self._vars: Dict[Race, tk.IntVar] = {}
        snapshot = controller.army_snapshot(alignment)

        for row, race in enumerate(controller.list_races(alignment)):
            self._vars[race] = tk.IntVar(value=snapshot.get(race.name, 0))

            ttk.Label(self, text=f"{race.name} (valor {race.battle_value})").grid(
                row=row, column=0, sticky=tk.W, padx=(0, 8), pady=4
            )

            sprite_canvas = tk.Canvas(self, width=42, height=42, bd=0, highlightthickness=1, highlightbackground="#333")
            sprite = get_sprite(race.name, race.pixel_color)
            render_sprite(sprite_canvas, sprite, 4, 4, pixel_size=4)
            sprite_canvas.grid(row=row, column=1, padx=(0, 8), pady=4)

            ttk.Spinbox(
                self,
                from_=0,
                to=200,
                textvariable=self._vars[race],
                width=5,
            ).grid(row=row, column=2, padx=(0, 8), pady=4)

        for column in (0, 1, 2):
            self.columnconfigure(column, weight=1)

    def commit_changes(self) -> None:
        for race, var in self._vars.items():
            self._controller.set_units(race, var.get())

    def reset(self) -> None:
        for var in self._vars.values():
            var.set(0)
        self.commit_changes()


class BattleCanvas(tk.Canvas):
    """Canvas that paints the armies using small coloured rectangles."""

    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master, width=760, height=260, bg="#0f0f0f", highlightthickness=0)

    def draw(self, controller: GameController) -> None:
        self.delete("all")
        good_snapshot = controller.army_snapshot(Alignment.BENEVOLENT)
        evil_snapshot = controller.army_snapshot(Alignment.MALEVOLENT)

        self.create_text(180, 20, text=f"Bien: {sum(good_snapshot.values())} tropas", fill="#ffffff", font=("Arial", 11, "bold"))
        self.create_text(580, 20, text=f"Mal: {sum(evil_snapshot.values())} tropas", fill="#ffffff", font=("Arial", 11, "bold"))

        self._draw_group(controller.list_races(Alignment.BENEVOLENT), good_snapshot, 40, 60, 280)
        self._draw_group(controller.list_races(Alignment.MALEVOLENT), evil_snapshot, 440, 60, 280)

    def _draw_group(
        self,
        races: tuple[Race, ...],
        roster: Dict[str, int],
        origin_x: int,
        origin_y: int,
        area_width: int,
    ) -> None:
        sprite_pixel = 4
        sprite_box = 7 * sprite_pixel
        padding = 6
        per_row = max(1, area_width // (sprite_box + padding))

        index = 0
        for race in races:
            count = roster.get(race.name, 0)
            if count <= 0:
                continue
            sprite = get_sprite(race.name, race.pixel_color)
            for _ in range(count):
                row, col = divmod(index, per_row)
                x0 = origin_x + col * (sprite_box + padding)
                y0 = origin_y + row * (sprite_box + padding)
                render_sprite(self, sprite, x0, y0, sprite_pixel)
                index += 1


class GameWindow(UserInterface):
    """Concrete UI implementation backed by Tkinter."""

    def __init__(self, controller: GameController) -> None:
        self._controller = controller
        self._root = tk.Tk()
        self._root.title("Batalla por Centauro")
        self._root.resizable(False, False)
        self._music_enabled = tk.BooleanVar(value=False)
        self._build_layout()

    def start(self) -> None:
        self._root.mainloop()

    def _build_layout(self) -> None:
        style = ttk.Style()
        style.configure("Header.TLabel", font=("Helvetica", 14, "bold"))

        main_frame = ttk.Frame(self._root, padding=16)
        main_frame.grid(row=0, column=0)

        header = ttk.Label(
            main_frame,
            text="Universidad Nacional Abierta y a Distancia - UNAD\nProyecto Centauro por Juan David Salas Camargo",
            style="Header.TLabel",
            justify=tk.CENTER,
        )
        header.grid(row=0, column=0, columnspan=2, pady=(0, 12))

        self._good_panel = ArmySelectionPanel(main_frame, self._controller, Alignment.BENEVOLENT)
        self._good_panel.grid(row=1, column=0, sticky=tk.N)

        self._evil_panel = ArmySelectionPanel(main_frame, self._controller, Alignment.MALEVOLENT)
        self._evil_panel.grid(row=1, column=1, sticky=tk.N, padx=(16, 0))

        buttons = ttk.Frame(main_frame, padding=(0, 16, 0, 0))
        buttons.grid(row=2, column=0, columnspan=2, sticky=tk.EW)

        ttk.Button(buttons, text="Simular batalla", command=self._on_simulate).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(buttons, text="Reiniciar", command=self._on_reset).grid(row=0, column=1, padx=(0, 8))

        ttk.Checkbutton(
            buttons,
            text="Música retro",
            variable=self._music_enabled,
            command=self._toggle_music,
        ).grid(row=0, column=2, padx=(0, 8))

        self._result_label = ttk.Label(buttons, text="Selecciona las tropas y presiona Simular.")
        self._result_label.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(8, 0))

        self._canvas = BattleCanvas(main_frame)
        self._canvas.grid(row=3, column=0, columnspan=2, pady=(16, 0))
        self._canvas.draw(self._controller)

    def _on_simulate(self) -> None:
        self._good_panel.commit_changes()
        self._evil_panel.commit_changes()
        result = self._controller.simulate_battle()
        self._result_label.configure(
            text=f"Resultado: {result.outcome.message} (Bien: {result.good_power} vs Mal: {result.evil_power})"
        )
        self._canvas.draw(self._controller)
        if self._music_enabled.get():
            # Restart playback to ensure the loop continues.
            self._toggle_music()
            self._music_enabled.set(True)

    def _on_reset(self) -> None:
        self._controller.stop_music()
        self._controller.reset_armies()
        self._good_panel.reset()
        self._evil_panel.reset()
        self._result_label.configure(text="Selecciona las tropas y presiona Simular.")
        self._canvas.draw(self._controller)
        self._music_enabled.set(False)

    def _toggle_music(self) -> None:
        if self._music_enabled.get():
            if not self._controller.play_music():
                messagebox.showinfo(
                    "Música no disponible",
                    "No se pudo iniciar la música retro. Verifica pygame y assets/retro_theme.wav.",
                )
                self._music_enabled.set(False)
        else:
            self._controller.stop_music()
