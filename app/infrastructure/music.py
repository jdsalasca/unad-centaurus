"""Optional retro music playback using pygame if available."""

from __future__ import annotations

import math
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
    bpm: int = 82
    bars: int = 12
    steps_per_bar: int = 8
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

    PHI = (1.0 + math.sqrt(5.0)) / 2.0

    _MAJOR_SCALE: Sequence[int] = (0, 2, 4, 5, 7, 9, 11)
    _MINOR_SCALE: Sequence[int] = (0, 2, 3, 5, 7, 8, 10)

    _MAJOR_DEGREES = {"I": 0, "ii": 2, "iii": 4, "IV": 5, "V": 7, "vi": 9}
    _MINOR_DEGREES = {"i": 0, "ii": 2, "III": 3, "iv": 5, "v": 7, "VI": 8, "VII": 10}

    _PENTATONIC_MAJOR: Sequence[int] = (0, 2, 4, 7, 9)
    _PENTATONIC_MINOR: Sequence[int] = (0, 3, 5, 7, 10)

    _CHORD_INTERVALS = {"major": (0, 4, 7), "minor": (0, 3, 7)}

    _PROGRESSIONS: Sequence[Sequence[str]] = (
        ("I", "vi", "IV", "V"),
        ("I", "IV", "ii", "V"),
        ("I", "V", "vi", "IV"),
        ("I", "iii", "vi", "IV"),
    )

    _FIB_DURATIONS: Sequence[int] = (2, 3, 5, 8)

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

        self._scale_mode = "major" if self._rng.random() < 0.72 else "minor"
        self._scale = (
            self._MAJOR_SCALE if self._scale_mode == "major" else self._MINOR_SCALE
        )
        self._pentatonic = (
            self._PENTATONIC_MAJOR
            if self._scale_mode == "major"
            else self._PENTATONIC_MINOR
        )
        self._key_root = self._rng.randint(52, 60)

        progression = self._build_progression(self._key_root)
        melody_pattern = self._build_melody_pattern(progression, total_steps)
        harmony_pattern = self._build_harmony_pattern(progression, total_steps)
        bass_pattern = self._build_bass_pattern(progression, total_steps)
        pad_pattern = self._build_pad_pattern(progression, total_steps)

        data = array("h")
        for step in range(total_steps):
            step_samples = self._render_step(
                melody_note=melody_pattern[step],
                harmony_note=harmony_pattern[step],
                bass_note=bass_pattern[step],
                pad_note=pad_pattern[step],
                samples_per_step=samples_per_step,
            )
            data.extend(step_samples)

        return data.tobytes()

    # Internal helpers -----------------------------------------------------

    def _build_progression(self, root: int) -> Sequence[int]:
        template = list(self._rng.choice(self._PROGRESSIONS))
        degrees = (
            self._MAJOR_DEGREES
            if self._scale_mode == "major"
            else self._MINOR_DEGREES
        )

        progression: list[int] = []
        for bar in range(self.bars):
            symbol = template[bar % len(template)]
            normalized = self._normalize_symbol(symbol)
            interval = degrees.get(normalized, 0)
            chord_root = root + interval
            if self._scale_mode == "minor" and normalized in {"v"}:
                chord_root += 1  # Harmonic minor dominant
            progression.append(chord_root)
        return progression

    def _build_melody_pattern(
        self,
        progression: Sequence[int],
        total_steps: int,
    ) -> Sequence[Optional[int]]:
        pattern: list[Optional[int]] = [None] * total_steps
        phrase_steps = max(self.steps_per_bar, int(round(self.steps_per_bar * self.PHI)))
        step = 0
        last_note: Optional[int] = None
        direction = self._rng.choice((-1, 1))

        while step < total_steps:
            phrase_end = min(total_steps, step + phrase_steps)
            while step < phrase_end:
                remaining = phrase_end - step
                duration = self._choose_duration(remaining)
                bar = step // self.steps_per_bar
                chord_root = progression[bar]
                note = self._select_melody_note(chord_root, last_note, direction)

                for offset in range(duration):
                    if step + offset < total_steps:
                        pattern[step + offset] = note

                last_note = note
                step += duration
                if step >= phrase_end:
                    break
                if self._rng.random() < 1.0 / (2.0 * self.PHI):
                    direction *= -1

            if step < total_steps:
                rest_len = min(self._choose_duration(total_steps - step), self.steps_per_bar // 2 or 1)
                step += rest_len
                direction = self._rng.choice((-1, 1))
                last_note = None

        return pattern

    def _choose_duration(self, remaining: int) -> int:
        choices = [d for d in self._FIB_DURATIONS if d <= remaining]
        if not choices:
            return remaining
        weights = [math.pow(d, 1.0 / self.PHI) for d in choices]
        return self._rng.choices(choices, weights=weights, k=1)[0]

    def _select_melody_note(
        self,
        chord_root: int,
        last_note: Optional[int],
        direction: int,
    ) -> int:
        chord_tones = self._chord_tones(chord_root)
        chord_extensions = [tone + 12 for tone in chord_tones]
        pentatonic = [self._key_root + interval + 12 for interval in self._pentatonic]
        pentatonic += [note + 12 for note in pentatonic if note < self._key_root + 24]

        candidates = list(dict.fromkeys(chord_extensions + pentatonic))
        if last_note is not None:
            span = 7
            if direction > 0:
                filtered = [note for note in candidates if note >= last_note - 2 and note <= last_note + span]
            else:
                filtered = [note for note in candidates if note <= last_note + 2 and note >= last_note - span]
            if filtered:
                candidates = filtered

        weights: list[float] = []
        for note in candidates:
            weight = 1.0
            if note in chord_extensions:
                weight *= self.PHI
            if last_note is not None:
                interval = abs(note - last_note)
                weight *= 1.0 / (1.0 + interval / 6.0)
            weights.append(weight)
        return self._rng.choices(candidates, weights=weights, k=1)[0]

    def _build_harmony_pattern(
        self,
        progression: Sequence[int],
        total_steps: int,
    ) -> Sequence[Optional[int]]:
        pattern: list[Optional[int]] = [None] * total_steps
        for bar in range(self.bars):
            base_idx = bar * self.steps_per_bar
            remaining = min(self.steps_per_bar, total_steps - base_idx)
            if remaining <= 0:
                continue
            if self._rng.random() < 0.25:
                continue

            chord_root = progression[bar]
            chord_tones = self._chord_tones(chord_root)
            harmony_note = self._rng.choice([tone + 19 for tone in chord_tones])
            sustain = min(remaining, self.steps_per_bar)
            for offset in range(sustain):
                pattern[base_idx + offset] = harmony_note

        return pattern

    def _build_bass_pattern(
        self,
        progression: Sequence[int],
        total_steps: int,
    ) -> Sequence[Optional[int]]:
        pattern: list[Optional[int]] = [None] * total_steps
        for bar in range(self.bars):
            base_idx = bar * self.steps_per_bar
            remaining = min(self.steps_per_bar, total_steps - base_idx)
            if remaining <= 0:
                continue

            chord_root = progression[bar] - 12
            fifth = chord_root + 7
            walking = chord_root + self._rng.choice((0, 5, 7, 12))
            accent_points = [0, remaining // 2, remaining - 1]

            for offset in range(remaining):
                idx = base_idx + offset
                if offset in accent_points:
                    pattern[idx] = chord_root if offset != remaining // 2 else fifth
                elif offset % 3 == 1 and self._rng.random() < 0.35:
                    pattern[idx] = walking
                elif self._rng.random() < 0.1:
                    pattern[idx] = chord_root

        return pattern

    def _build_pad_pattern(
        self,
        progression: Sequence[int],
        total_steps: int,
    ) -> Sequence[Optional[int]]:
        pattern: list[Optional[int]] = [None] * total_steps
        for bar in range(self.bars):
            base_idx = bar * self.steps_per_bar
            remaining = min(self.steps_per_bar, total_steps - base_idx)
            if remaining <= 0 or self._rng.random() < 0.2:
                continue

            chord_root = progression[bar]
            chord_tones = self._chord_tones(chord_root)
            pad_note = self._rng.choice([tone + 24 for tone in chord_tones])
            swell = max(remaining - 1, 1)
            for offset in range(remaining):
                pattern[base_idx + offset] = pad_note
                if offset == swell and self._rng.random() < 0.4:
                    break

        return pattern

    def _render_step(
        self,
        melody_note: Optional[int],
        harmony_note: Optional[int],
        bass_note: Optional[int],
        pad_note: Optional[int],
        samples_per_step: int,
    ) -> array:
        melody_env = (
            self._envelope_generator(samples_per_step, 0.18, 0.42, sustain_level=0.72)
            if melody_note is not None
            else None
        )
        harmony_env = (
            self._envelope_generator(samples_per_step, 0.28, 0.35, sustain_level=0.6)
            if harmony_note is not None
            else None
        )
        bass_env = (
            self._envelope_generator(samples_per_step, 0.08, 0.3, sustain_level=0.78)
            if bass_note is not None
            else None
        )
        pad_env = (
            self._envelope_generator(samples_per_step, 0.55, 0.5, sustain_level=0.55)
            if pad_note is not None
            else None
        )

        melody_state = self._oscillator_state(melody_note, detune_cents=1.5, waveform="square")
        harmony_state = self._oscillator_state(harmony_note, detune_cents=-3.0, waveform="triangle")
        bass_state = self._oscillator_state(bass_note, detune_cents=-8.0, waveform="triangle")
        pad_state = self._oscillator_state(pad_note, detune_cents=2.0, waveform="sine")

        data = array("h")
        for idx in range(samples_per_step):
            sample = 0.0
            if melody_state is not None and melody_env is not None:
                sample += 0.42 * melody_env(idx) * self._sample_voice(melody_state)
            if harmony_state is not None and harmony_env is not None:
                sample += 0.28 * harmony_env(idx) * self._sample_voice(harmony_state)
            if pad_state is not None and pad_env is not None:
                sample += 0.22 * pad_env(idx) * self._sample_voice(pad_state)
            if bass_state is not None and bass_env is not None:
                sample += 0.32 * bass_env(idx) * self._sample_voice(bass_state)
            sample = max(-0.95, min(0.95, sample))
            data.append(int(sample * 32000))
        return data

    def _chord_tones(self, chord_root: int) -> list[int]:
        intervals = self._CHORD_INTERVALS["major" if self._scale_mode == "major" else "minor"]
        return [chord_root + interval for interval in intervals]

    def _normalize_symbol(self, symbol: str) -> str:
        if self._scale_mode == "major":
            return symbol
        minor_map = {
            "I": "i",
            "ii": "ii",
            "iii": "III",
            "IV": "iv",
            "V": "v",
            "vi": "VI",
            "VII": "VII",
        }
        return minor_map.get(symbol, symbol)

    def _oscillator_state(
        self,
        midi_note: Optional[int],
        detune_cents: float = 0.0,
        waveform: str = "square",
    ) -> Optional[dict[str, float]]:
        if midi_note is None:
            return None

        frequency = midi_to_frequency(midi_note) * (2 ** (detune_cents / 1200.0))
        increment = frequency / self.sample_rate
        state: dict[str, float] = {
            "phase": self._rng.random(),
            "increment": increment,
            "waveform": waveform,
            "vibrato_phase": 0.0,
            "vibrato_increment": math.tau * self._rng.uniform(3.5, 5.5) / self.sample_rate,
            "vibrato_depth": 0.0015 + self._rng.uniform(0.0, 0.0015),
        }

        if waveform == "square":
            state["duty"] = self._rng.uniform(0.42, 0.58)
            state["secondary_phase"] = self._rng.random()
            state["secondary_increment"] = min(0.95, increment * 2.0)
        elif waveform == "triangle":
            state["skew"] = self._rng.uniform(0.46, 0.54)
        elif waveform == "sine":
            state["phase_offset"] = self._rng.random() * math.tau

        return state

    def _sample_voice(self, state: dict[str, float]) -> float:
        vibrato = math.sin(state["vibrato_phase"]) * state["vibrato_depth"]
        state["vibrato_phase"] = (state["vibrato_phase"] + state["vibrato_increment"]) % math.tau
        phase_increment = state["increment"] * (1.0 + vibrato)
        state["phase"] = (state["phase"] + phase_increment) % 1.0

        waveform = state["waveform"]
        if waveform == "square":
            state["secondary_phase"] = (state["secondary_phase"] + state["secondary_increment"]) % 1.0
            pulse = 1.0 if state["phase"] < state["duty"] else -1.0
            harmonic = 1.0 if state["secondary_phase"] < 0.5 else -1.0
            return 0.68 * pulse + 0.32 * harmonic
        if waveform == "triangle":
            skew = state["skew"]
            if state["phase"] < skew:
                return (state["phase"] / max(skew, 1e-6)) * 2.0 - 1.0
            return (1.0 - (state["phase"] - skew) / max(1.0 - skew, 1e-6)) * 2.0 - 1.0
        return math.sin(state["phase"] * math.tau + state.get("phase_offset", 0.0))

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
