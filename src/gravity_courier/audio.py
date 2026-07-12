"""Lightweight Pyxel audio manager for Gravity Courier."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


SOUND_LAP_1 = 0
SOUND_LAP_2 = 1
SOUND_LAP_3 = 2
SOUND_TRANSFER = 3
SOUND_SUPPLY = 4
SOUND_DAMAGE = 5
SOUND_RESULT = 6
SOUND_CRASH = 7
SOUND_ORBIT_ENTER = 10
SOUND_TITLE_SHOOTING_STAR = 16
MUSIC_CRUISE = 0
MUSIC_RESULT = 1
MUSIC_TITLE = 2
SFX_CHANNEL = 3
BGM_CHANNELS = (0, 1, 2)
SOUND_NOTE_SEQUENCES = (
    "c3e3g3",
    "e3g3c4",
    "g3c4e4g4",
    "c3g3c4g4",
    "e4c4g3",
    "c2c1",
    "c3e3g3c4",
    "f2d2c2",
    "c2e2g2c3g3",
    "c2g2c3g2",
    "e2b2e3b2",
    "c3e3g3e3d3g3b3g3",
    "a2c3e3c3g2b2d3b2",
    "f2a2c3a2e2g2c3g2",
    "d2f2a2f2c2e2g2e2",
    "c2rg1ra1rf1r",
    "c2rg1ra1rf1r",
    "a1re1rf1rg1r",
    "c4e4g4b4a4g4e4c4",
)


@dataclass
class AudioManager:
    enabled: bool = True
    configured: bool = False
    bgm_playing: bool = False
    current_music: int | None = None
    last_event: str = ""

    def configure(self, pyxel: Any) -> None:
        if self.configured:
            return
        try:
            pyxel.sounds[SOUND_LAP_1].set(SOUND_NOTE_SEQUENCES[0], "t", "5", "n", 12)
            pyxel.sounds[SOUND_LAP_2].set(SOUND_NOTE_SEQUENCES[1], "t", "5", "n", 12)
            pyxel.sounds[SOUND_LAP_3].set(SOUND_NOTE_SEQUENCES[2], "t", "5", "n", 14)
            pyxel.sounds[SOUND_TRANSFER].set(SOUND_NOTE_SEQUENCES[3], "p", "6", "f", 18)
            pyxel.sounds[SOUND_SUPPLY].set(SOUND_NOTE_SEQUENCES[4], "s", "5", "n", 10)
            pyxel.sounds[SOUND_DAMAGE].set(SOUND_NOTE_SEQUENCES[5], "n", "7", "f", 8)
            pyxel.sounds[SOUND_RESULT].set(SOUND_NOTE_SEQUENCES[6], "t", "6", "n", 18)
            pyxel.sounds[SOUND_CRASH].set(SOUND_NOTE_SEQUENCES[7], "n", "7", "f", 16)
            pyxel.sounds[SOUND_ORBIT_ENTER].set(SOUND_NOTE_SEQUENCES[8], "p", "6", "s", 16)
            pyxel.sounds[8].set(SOUND_NOTE_SEQUENCES[9], "s", "2", "n", 26)
            pyxel.sounds[9].set(SOUND_NOTE_SEQUENCES[10], "s", "1", "n", 26)
            pyxel.sounds[11].set(SOUND_NOTE_SEQUENCES[11], "t", "43334334", "nnnnnnnn", 28)
            pyxel.sounds[12].set(SOUND_NOTE_SEQUENCES[12], "t", "33334333", "nnnnnnnn", 28)
            pyxel.sounds[13].set(SOUND_NOTE_SEQUENCES[13], "t", "33333333", "nnnnnnnn", 30)
            pyxel.sounds[14].set(SOUND_NOTE_SEQUENCES[14], "t", "33333333", "nnnnnnnn", 30)
            pyxel.sounds[15].set(SOUND_NOTE_SEQUENCES[15], "s", "22112211", "nnnnnnnn", 34)
            pyxel.sounds[SOUND_TITLE_SHOOTING_STAR].set(SOUND_NOTE_SEQUENCES[18], "t", "23455432", "nnnnffff", 18)
            pyxel.sounds[17].set(SOUND_NOTE_SEQUENCES[16], "s", "33222222", "nnnnnnnn", 40)
            pyxel.sounds[19].set(SOUND_NOTE_SEQUENCES[17], "s", "22222222", "nnnnnnnn", 40)
            pyxel.music(MUSIC_CRUISE).set([8, 9], [], [], [])
            pyxel.music(MUSIC_RESULT).set([11, 12, 13, 14, 13, 12], [15], [], [])
            pyxel.music(MUSIC_TITLE).set([17, 19], [], [], [])
        except Exception:
            self.configured = False
            return
        self.configured = True

    def toggle_enabled(self, pyxel: Any | None = None) -> bool:
        self.enabled = not self.enabled
        if not self.enabled and pyxel is not None:
            self.stop(pyxel)
        elif self.enabled and pyxel is not None:
            self.start_bgm(pyxel)
        return self.enabled

    def start_bgm(self, pyxel: Any) -> None:
        self._start_music(pyxel, MUSIC_CRUISE)

    def start_result_bgm(self, pyxel: Any) -> None:
        self._start_music(pyxel, MUSIC_RESULT)

    def start_title_bgm(self, pyxel: Any) -> None:
        self._start_music(pyxel, MUSIC_TITLE)

    def _start_music(self, pyxel: Any, music_index: int) -> None:
        if not self.enabled:
            return
        self.configure(pyxel)
        if not self.configured or self.current_music == music_index:
            return
        if self.bgm_playing or self.current_music is not None:
            self._stop_bgm_channels(pyxel)
        try:
            pyxel.playm(music_index, loop=True)
        except (Exception, TypeError):
            return
        self.bgm_playing = True
        self.current_music = music_index

    def stop(self, pyxel: Any) -> None:
        try:
            pyxel.stop()
        except (Exception, TypeError):
            pass
        self.bgm_playing = False
        self.current_music = None

    def stop_bgm(self, pyxel: Any) -> None:
        self._stop_bgm_channels(pyxel)
        self.bgm_playing = False
        self.current_music = None

    def _stop_bgm_channels(self, pyxel: Any) -> None:
        for channel in BGM_CHANNELS:
            try:
                pyxel.stop(channel)
            except (Exception, TypeError):
                pass

    def play_lap(self, pyxel: Any, lap: int) -> None:
        stage = max(1, min(3, lap))
        self._play(pyxel, f"lap_{stage}", SOUND_LAP_1 + stage - 1)

    def play_transfer(self, pyxel: Any) -> None:
        self._play(pyxel, "transfer", SOUND_TRANSFER)

    def play_supply(self, pyxel: Any) -> None:
        self._play(pyxel, "supply", SOUND_SUPPLY)

    def play_damage(self, pyxel: Any) -> None:
        self._play(pyxel, "damage", SOUND_DAMAGE)

    def play_result(self, pyxel: Any) -> None:
        self._play(pyxel, "result", SOUND_RESULT)

    def play_crash(self, pyxel: Any) -> None:
        self._play(pyxel, "crash", SOUND_CRASH)

    def play_orbit_enter(self, pyxel: Any) -> None:
        self._play(pyxel, "orbit_enter", SOUND_ORBIT_ENTER)

    def play_title_shooting_star(self, pyxel: Any) -> None:
        self._play(pyxel, "title_shooting_star", SOUND_TITLE_SHOOTING_STAR)

    def _play(self, pyxel: Any, event: str, sound_index: int) -> None:
        self.last_event = event
        if not self.enabled:
            return
        self.configure(pyxel)
        if not self.configured:
            return
        try:
            pyxel.play(SFX_CHANNEL, sound_index)
        except (Exception, TypeError):
            return
