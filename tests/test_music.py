from __future__ import annotations

import sys
import tempfile
import types
from pathlib import Path
from unittest import TestCase

from app.infrastructure.music import ProceduralChiptune, RetroMusicPlayer


class FakeChannel:
    def __init__(self) -> None:
        self._busy = False
        self.stop_calls = 0
        self.raise_on_get_busy = False
        self.raise_on_stop = False

    def start(self) -> None:
        self._busy = True

    def stop(self) -> None:
        self.stop_calls += 1
        if self.raise_on_stop:
            self.raise_on_stop = False
            raise RuntimeError("channel stop failure")
        self._busy = False

    def get_busy(self) -> bool:
        if self.raise_on_get_busy:
            self.raise_on_get_busy = False
            raise RuntimeError("busy check failure")
        return self._busy


class FakeSound:
    def __init__(self, buffer: bytes) -> None:
        self.buffer = buffer
        self.play_calls = 0
        self.stop_calls = 0
        self._channel = FakeChannel()
        self.raise_on_play = False

    def play(self, loops: int = -1) -> FakeChannel:
        if self.raise_on_play:
            self.raise_on_play = False
            raise RuntimeError("sound play failure")
        self.play_calls += 1
        self._channel.start()
        return self._channel

    def stop(self) -> None:
        self.stop_calls += 1
        self._channel.stop()


class FakeMusic:
    def __init__(self) -> None:
        self.play_calls = 0
        self.stop_calls = 0
        self.loaded_paths: list[str] = []

    def load(self, *_args, **_kwargs) -> None:
        if _args:
            self.loaded_paths.append(_args[0])

    def play(self, loops: int = -1) -> None:
        self.play_calls += 1

    def stop(self) -> None:
        self.stop_calls += 1


class FakeMixer:
    def __init__(self) -> None:
        self.init_calls = []
        self.sound_instances: list[FakeSound] = []
        self.music = FakeMusic()
        self.raise_on_sound = False

    def init(self, **kwargs) -> None:
        self.init_calls.append(kwargs)

    def Sound(self, buffer: bytes) -> FakeSound:
        if self.raise_on_sound:
            raise RuntimeError("Sound init failure")
        sound = FakeSound(buffer)
        self.sound_instances.append(sound)
        return sound


class RetroMusicPlayerTestCase(TestCase):
    def setUp(self) -> None:
        RetroMusicPlayer._reset_singleton()
        sys.modules.pop("pygame", None)
        self.tmpdir = tempfile.TemporaryDirectory()

        fake_pygame = types.SimpleNamespace()
        fake_pygame.mixer = FakeMixer()
        sys.modules["pygame"] = fake_pygame
        self.fake_mixer = fake_pygame.mixer

    def tearDown(self) -> None:
        RetroMusicPlayer._reset_singleton()
        sys.modules.pop("pygame", None)
        self.tmpdir.cleanup()

    def test_singleton_reuses_same_instance(self) -> None:
        player_a = RetroMusicPlayer(audio_path=Path("nonexistent.mp3"))
        player_b = RetroMusicPlayer()
        self.assertIs(player_a, player_b)
        # mixer.init called only once even with repeated instantiation
        self.assertEqual(1, len(self.fake_mixer.init_calls))

    def test_play_does_not_overlap_existing_channel(self) -> None:
        player = RetroMusicPlayer(audio_path=None)
        self.assertTrue(player.play())
        sound = self.fake_mixer.sound_instances[0]
        self.assertEqual(1, sound.play_calls)

        # Second play while channel busy should not trigger another call.
        self.assertTrue(player.play())
        self.assertEqual(1, sound.play_calls, "sound.play should not be called again while playing")

        # After stopping, playing resumes and increments call counter.
        player.stop()
        self.assertFalse(sound._channel.get_busy())

        self.assertTrue(player.play())
        self.assertEqual(2, sound.play_calls)

    def test_reset_singleton_creates_new_instance(self) -> None:
        first = RetroMusicPlayer()
        RetroMusicPlayer._reset_singleton()
        second = RetroMusicPlayer()

        self.assertIsNot(first, second)
        self.assertEqual(
            2,
            len(self.fake_mixer.init_calls),
            "pygame mixer should initialize again after resetting singleton",
        )

    def test_uses_existing_audio_file_and_music_channel(self) -> None:
        audio_file = Path(self.tmpdir.name) / "theme.mp3"
        audio_file.write_bytes(b"stub")

        player = RetroMusicPlayer(audio_path=audio_file)
        self.assertTrue(player.is_available)
        self.assertEqual([], self.fake_mixer.sound_instances)
        self.assertIn(audio_file.as_posix(), self.fake_mixer.music.loaded_paths)

        self.assertTrue(player.play())
        self.assertEqual(1, self.fake_mixer.music.play_calls)
        player.stop()
        self.assertEqual(1, self.fake_mixer.music.stop_calls)

    def test_initialization_failure_marks_player_unavailable(self) -> None:
        self.fake_mixer.raise_on_sound = True
        RetroMusicPlayer._reset_singleton()
        sys.modules["pygame"].mixer = self.fake_mixer

        player = RetroMusicPlayer(audio_path=None)
        self.assertFalse(player.is_available)
        self.assertFalse(player.play())
        self.fake_mixer.raise_on_sound = False

    def test_channel_get_busy_exception_is_ignored(self) -> None:
        player = RetroMusicPlayer(audio_path=None)
        player.play()
        sound = self.fake_mixer.sound_instances[0]
        sound._channel.raise_on_get_busy = True

        self.assertTrue(player.play())
        self.assertEqual(2, sound.play_calls)

    def test_sound_play_exception_returns_false(self) -> None:
        player = RetroMusicPlayer(audio_path=None)
        sound = self.fake_mixer.sound_instances[0]
        sound.raise_on_play = True

        self.assertFalse(player.play())

    def test_stop_handles_channel_errors(self) -> None:
        player = RetroMusicPlayer(audio_path=None)
        player.play()
        sound = self.fake_mixer.sound_instances[0]
        sound._channel.raise_on_stop = True

        player.stop()  # Should swallow the exception and not raise.

    def test_reset_singleton_handles_stop_errors(self) -> None:
        player = RetroMusicPlayer()

        def failing_stop() -> None:
            raise RuntimeError("boom")

        player.stop = failing_stop  # type: ignore[assignment]
        RetroMusicPlayer._reset_singleton()

    def test_minor_progression_adjusts_dominant(self) -> None:
        generator = ProceduralChiptune(sample_rate=22050, bpm=80, bars=1, steps_per_bar=4, seed=1)
        original_progressions = ProceduralChiptune._PROGRESSIONS
        try:
            ProceduralChiptune._PROGRESSIONS = (("v",),)
            generator._scale_mode = "minor"
            progression = generator._build_progression(root=50)
        finally:
            ProceduralChiptune._PROGRESSIONS = original_progressions
        self.assertEqual([58], progression)

    def test_harmony_and_bass_skip_when_remaining_zero(self) -> None:
        generator = ProceduralChiptune(sample_rate=22050, bpm=80, bars=1, steps_per_bar=4, seed=1)
        progression = [60]
        harmony = generator._build_harmony_pattern(progression, total_steps=0)
        bass = generator._build_bass_pattern(progression, total_steps=0)
        self.assertEqual([], harmony)
        self.assertEqual([], bass)
