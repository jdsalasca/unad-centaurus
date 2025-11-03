"""Optional retro music playback using pygame if available."""

from __future__ import annotations

import random
from abc import ABC, abstractmethod
from array import array
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional, Sequence


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

    audio_path: Optional[Path] = None
    sample_rate: int = 22_050
    bpm: int = 120
    bars: int = 8
    steps_per_bar: int = 16
    seed: Optional[int] = None
    _pygame: Optional[object] = field(init=False, default=None)
    _available: bool = field(init=False, default=False)
    _sound: Optional[object] = field(init=False, default=None)
    _channel: Optional[object] = field(init=False, default=None)

    def __post_init__(self) -> None:
        try:
            import pygame

            self._pygame = pygame
            pygame.mixer.init(
                frequency=self.sample_rate,
                size=-16,
                channels=1,
                buffer=512,
            )

            if self.audio_path and self.audio_path.exists():
                pygame.mixer.music.load(self.audio_path.as_posix())
                self._available = True
                return

            generator = ProceduralChiptune(
                sample_rate=self.sample_rate,
                bpm=self.bpm,
                bars=self.bars,
                steps_per_bar=self.steps_per_bar,
                seed=self.seed,
            )
            payload = generator.render_loop()
            self._sound = pygame.mixer.Sound(buffer=payload)
            self._available = True
        except Exception:
            self._available = False
            self._pygame = None
            self._sound = None
            self._channel = None

    def play(self) -> bool:
        if not self._available or not self._pygame:
            return False
        try:
            if self._sound is not None:
                self._channel = self._sound.play(loops=-1)
            else:
                self._pygame.mixer.music.play(loops=-1)
            return True
        except Exception:
            self._channel = None
            return False

    def stop(self) -> None:
        if not self._available or not self._pygame:
            return

        try:
            if self._channel is not None:
                self._channel.stop()
                self._channel = None
            elif self._sound is not None:
                self._sound.stop()
                self._channel = None
            else:
                self._pygame.mixer.music.stop()
        except Exception:
            pass

    @property
    def is_available(self) -> bool:
        return self._available


class ProceduralChiptune:
    """Synthesize lightweight 8-bit style background music on the fly."""

    _MAJOR_SCALE: Sequence[int] = (0, 2, 4, 5, 7, 9, 11)
    _MINOR_SCALE: Sequence[int] = (0, 2, 3, 5, 7, 8, 10)

    def __init__(
        self,
        sample_rate: int,
        bpm: int,
        bars: int,
        steps_per_bar: int,
        seed: Optional[int] = None,
    ) -> None:
        self.sample_rate = sample_rate
        self.bpm = bpm
        self.bars = bars
        self.steps_per_bar = steps_per_bar
        self._rng = random.Random(seed)

    def render_loop(self) -> bytes:
        """Return a loopable waveform payload."""

        total_steps = self.bars * self.steps_per_bar
        seconds_per_step = (60.0 / self.bpm) / (self.steps_per_bar / 4)
        samples_per_step = max(1, int(self.sample_rate * seconds_per_step))

        key_root = self._rng.randint(48, 60)
        scale = self._MAJOR_SCALE if self._rng.random() < 0.5 else self._MINOR_SCALE
        progression = self._build_progression(key_root, scale)
        melody_pattern = self._build_melody_pattern(progression, scale, total_steps)
        bass_pattern = self._build_bass_pattern(progression, total_steps)

        data = array("h")
        for step in range(total_steps):
            melody_note = melody_pattern[step]
            bass_note = bass_pattern[step]
            step_samples = self._render_step(
                melody_note=melody_note,
                bass_note=bass_note,
                samples_per_step=samples_per_step,
            )
            data.extend(step_samples)

        return data.tobytes()

    # Internal helpers -----------------------------------------------------

    def _build_progression(self, root: int, scale: Sequence[int]) -> Sequence[int]:
        bars = self.bars
        progression = []
        last = root
        chord_choices = [0, 5, 7, -5, 12]
        for _ in range(bars):
            if self._rng.random() < 0.35:
                delta = self._rng.choice(chord_choices)
                last = root + delta
            progression.append(last)
        return progression

    def _build_melody_pattern(
        self,
        progression: Sequence[int],
        scale: Sequence[int],
        total_steps: int,
    ) -> Sequence[Optional[int]]:
        pattern: list[Optional[int]] = []
        current_note: Optional[int] = None

        for step in range(total_steps):
            bar = step // self.steps_per_bar
            is_new_phrase = step % 4 == 0 or current_note is None
            if is_new_phrase:
                if self._rng.random() < 0.2:
                    current_note = None
                else:
                    chord_root = progression[bar]
                    interval = self._rng.choice(scale)
                    octave = self._rng.choice([0, 12, 24])
                    current_note = chord_root + interval + octave
            elif self._rng.random() < 0.15:
                current_note = None
            pattern.append(current_note)
        return pattern

    def _build_bass_pattern(
        self,
        progression: Sequence[int],
        total_steps: int,
    ) -> Sequence[Optional[int]]:
        pattern: list[Optional[int]] = []
        current_note: Optional[int] = None

        for step in range(total_steps):
            bar = step // self.steps_per_bar
            if step % self.steps_per_bar == 0 or current_note is None:
                chord_root = progression[bar]
                offset = self._rng.choice([0, 7, -5])
                current_note = chord_root + offset - 12

            if step % 4 == 0:
                bass_note = current_note
            elif self._rng.random() < 0.6:
                bass_note = None
            else:
                bass_note = current_note
            pattern.append(bass_note)

        return pattern

    def _render_step(
        self,
        melody_note: Optional[int],
        bass_note: Optional[int],
        samples_per_step: int,
    ) -> array:
        attack_ratio = 0.1
        release_ratio = 0.2

        melody_env = self._envelope_generator(
            samples_per_step,
            attack_ratio,
            release_ratio,
            sustain_level=0.75,
        )
        bass_env = self._envelope_generator(
            samples_per_step,
            attack_ratio / 2,
            release_ratio / 2,
            sustain_level=0.6,
        )

        melody_state = self._oscillator_state(melody_note)
        bass_state = self._oscillator_state(bass_note, detune_cents=-12)

        data = array("h")
        for idx in range(samples_per_step):
            sample = 0.0
            if melody_state is not None:
                sample += 0.6 * melody_env(idx) * self._sample_square(melody_state)
            if bass_state is not None:
                sample += 0.4 * bass_env(idx) * self._sample_square(bass_state)
            sample = max(-1.0, min(1.0, sample))
            data.append(int(sample * 32767))
        return data

    def _oscillator_state(
        self,
        midi_note: Optional[int],
        detune_cents: float = 0.0,
    ) -> Optional[dict[str, float]]:
        if midi_note is None:
            return None

        frequency = midi_to_frequency(midi_note) * (2 ** (detune_cents / 1200.0))
        increment = frequency / self.sample_rate
        duty_primary = self._rng.choice((0.5, 0.25, 0.75))
        duty_secondary = self._rng.choice((0.5, 0.33, 0.66))
        return {
            "phase": 0.0,
            "increment": increment,
            "harmonic_phase": 0.0,
            "harmonic_increment": min(0.9, increment * 2),
            "duty_primary": duty_primary,
            "duty_secondary": duty_secondary,
        }

    def _sample_square(
        self,
        state: dict[str, float],
    ) -> float:
        state["phase"] = (state["phase"] + state["increment"]) % 1.0
        state["harmonic_phase"] = (state["harmonic_phase"] + state["harmonic_increment"]) % 1.0

        primary = 1.0 if state["phase"] < state["duty_primary"] else -1.0
        harmonic = 1.0 if state["harmonic_phase"] < state["duty_secondary"] else -1.0
        sample = 0.7 * primary + 0.3 * harmonic
        return sample

    def _envelope_generator(
        self,
        samples: int,
        attack_ratio: float,
        release_ratio: float,
        sustain_level: float,
    ) -> Callable[[int], float]:
        attack = max(1, int(samples * attack_ratio))
        release = max(1, int(samples * release_ratio))
        sustain_start = attack
        release_start = max(sustain_start + 1, samples - release)

        def envelope(idx: int) -> float:
            if idx < attack:
                return idx / attack
            if idx >= release_start:
                tail = max(1, samples - release_start + 1)
                return sustain_level * (samples - idx) / tail
            return sustain_level

        return envelope


def midi_to_frequency(midi_note: int) -> float:
    """Convert a MIDI note number to its frequency in Hz."""

    return 440.0 * (2 ** ((midi_note - 69) / 12))
