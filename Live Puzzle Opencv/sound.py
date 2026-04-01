"""
Simple sound effects for the puzzle game.

The sounds are generated in memory, so the project does not need extra
audio files.
"""

import array
import math

import pygame


class SoundPlayer:
    """
    Small wrapper around pygame.mixer with graceful fallback.
    """

    def __init__(self):
        self.enabled = False
        self.sample_rate = 44100
        self.sounds = {}

        try:
            pygame.mixer.init(frequency=self.sample_rate, size=-16, channels=1)
            self.enabled = True
            self.sounds = {
                "capture": self._build_sound([(880, 0.05), (660, 0.08)]),
                "pick": self._build_sound([(740, 0.05)]),
                "drop": self._build_sound([(520, 0.04), (620, 0.06)]),
                "win": self._build_sound(
                    [(523, 0.10), (659, 0.10), (784, 0.14), (1047, 0.22)]
                ),
            }
        except pygame.error:
            self.enabled = False

    def _build_sound(self, notes):
        """
        Build a short waveform from a list of (frequency, duration) notes.
        """
        samples = array.array("h")

        for frequency, duration in notes:
            frame_count = int(self.sample_rate * duration)
            fade_count = max(1, int(frame_count * 0.12))

            for index in range(frame_count):
                amplitude = 0.35

                if index < fade_count:
                    amplitude *= index / fade_count
                elif index >= frame_count - fade_count:
                    amplitude *= (frame_count - index - 1) / fade_count

                sample = int(
                    32767
                    * amplitude
                    * math.sin(2 * math.pi * frequency * index / self.sample_rate)
                )
                samples.append(sample)

        return pygame.mixer.Sound(buffer=samples.tobytes())

    def play(self, name):
        """
        Play a named sound if audio is available.
        """
        if not self.enabled:
            return

        sound = self.sounds.get(name)
        if sound is not None:
            sound.play()


_PLAYER = SoundPlayer()


def play_capture_sound():
    _PLAYER.play("capture")


def play_pick_sound():
    _PLAYER.play("pick")


def play_drop_sound():
    _PLAYER.play("drop")


def play_win_sound():
    _PLAYER.play("win")
