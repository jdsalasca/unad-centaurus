"""Pixel-art sprites to represent the races of Centauro."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Sequence


@dataclass(frozen=True)
class PixelSprite:
    palette: Dict[str, str]
    rows: Sequence[str]

    @property
    def height(self) -> int:
        return len(self.rows)

    @property
    def width(self) -> int:
        return max((len(row) for row in self.rows), default=0)


SPRITES: Dict[str, PixelSprite] = {
    "Osito": PixelSprite(
        palette={"X": "#f7c8d0", "O": "#fddde4", "E": "#2b2b2b"},
        rows=(
            "..OOO..",
            ".OXXXO.",
            "OXXEXXO",
            "OXXXXXO",
            ".OXXXO.",
            "..O O..".replace(" ", "O"),
            "..OOO..",
        ),
    ),
    "Príncipe": PixelSprite(
        palette={"X": "#95c0ff", "C": "#ffe27a", "E": "#2b2b2b"},
        rows=(
            "...C...",
            "..CCC..",
            ".CXXXC.",
            "CXXEXXC",
            "CXXXXX C".replace(" ", "C"),
            ".CXXXC.",
            "..CCC..",
        ),
    ),
    "Enano": PixelSprite(
        palette={"X": "#fbe29f", "B": "#c68642", "E": "#2b2b2b"},
        rows=(
            "..BBB..",
            ".BXXXB.",
            "BXXEXXB",
            "BXXXXXB",
            ".BXXXB.",
            "..B B..".replace(" ", "B"),
            "..BBB..",
        ),
    ),
    "Cari": PixelSprite(
        palette={"X": "#e87956", "E": "#2b2b2b", "L": "#ffe6d5"},
        rows=(
            "..LLL..",
            ".LXXX L".replace(" ", "L"),
            "LXXEXXL",
            "LXXXXX L".replace(" ", "L"),
            ".LXXX L".replace(" ", "L"),
            "..L L..".replace(" ", "L"),
            "..LLL..",
        ),
    ),
    "Fulo": PixelSprite(
        palette={"X": "#8870ff", "S": "#5b4dd6", "E": "#fdf7ff"},
        rows=(
            "..SSS..",
            ".SXXXSS",
            "SXXEXXS",
            "SXXXXX S".replace(" ", "S"),
            ".SXXXSS",
            "..S S..".replace(" ", "S"),
            "..SSS..",
        ),
    ),
    "Lolo": PixelSprite(
        palette={"X": "#ff6f91", "E": "#200014", "H": "#ff9fb4"},
        rows=(
            "..HHH..",
            ".HXXXH.",
            "HXXEXXH",
            "HXXXXXH",
            ".HXXXH.",
            "..H H..".replace(" ", "H"),
            "..HHH..",
        ),
    ),
    "Fulano": PixelSprite(
        palette={"X": "#ff9671", "E": "#301205", "H": "#ffba92"},
        rows=(
            "..HHH..",
            ".HXXXH.",
            "HXXEXXH",
            "HXXXXXH",
            ".HXXXH.",
            "..H H..".replace(" ", "H"),
            "..HHH..",
        ),
    ),
    "Hoggin": PixelSprite(
        palette={"X": "#ffc75f", "E": "#3a2400", "H": "#ffe6a1"},
        rows=(
            "..HHH..",
            ".HXXXH.",
            "HXXEXXH",
            "HXXXXXH",
            ".HXXXH.",
            "..H H..".replace(" ", "H"),
            "..HHH..",
        ),
    ),
    "Lurco": PixelSprite(
        palette={"X": "#a17fe0", "E": "#1c0f33", "H": "#c4a8ff"},
        rows=(
            "..HHH..",
            ".HXXXH.",
            "HXXEXXH",
            "HXXXXXH",
            ".HXXXH.",
            "..H H..".replace(" ", "H"),
            "..HHH..",
        ),
    ),
    "Trolli": PixelSprite(
        palette={"X": "#5c5470", "E": "#f0f0f0", "H": "#8e85a6"},
        rows=(
            "..HHH..",
            ".HXXXH.",
            "HXXEXXH",
            "HXXXXXH",
            ".HXXXH.",
            "..H H..".replace(" ", "H"),
            "..HHH..",
        ),
    ),
}


def render_sprite(canvas, sprite: PixelSprite, origin_x: int, origin_y: int, pixel_size: int) -> None:
    """Draw ``sprite`` onto ``canvas`` using ``pixel_size`` squares."""

    for y, row in enumerate(sprite.rows):
        for x, code in enumerate(row):
            if code == ".":
                continue
            color = sprite.palette.get(code)
            if not color:
                continue
            x0 = origin_x + x * pixel_size
            y0 = origin_y + y * pixel_size
            canvas.create_rectangle(x0, y0, x0 + pixel_size, y0 + pixel_size, fill=color, outline="")


def sprite_names() -> Iterable[str]:
    return SPRITES.keys()


def get_sprite(name: str, default_color: str) -> PixelSprite:
    sprite = SPRITES.get(name)
    if sprite:
        return sprite
    return PixelSprite(palette={"X": default_color}, rows=("XXXX", "XXXX", "XXXX", "XXXX"))
