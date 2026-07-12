import unittest

import _path  # noqa: F401

from gravity_courier.app import GravityCourierApp, TITLE_SHOOTING_STAR_FIRST_FRAME, title_shooting_star_phase
from gravity_courier.audio import (
    AudioManager,
    MUSIC_CRUISE,
    MUSIC_RESULT,
    MUSIC_TITLE,
    SFX_CHANNEL,
    SOUND_LAP_1,
    SOUND_LAP_3,
    SOUND_ORBIT_ENTER,
    SOUND_RESULT,
    SOUND_NOTE_SEQUENCES,
    SOUND_TITLE_SHOOTING_STAR,
)


class FakeSound:
    def __init__(self) -> None:
        self.set_calls: list[tuple[tuple[object, ...], dict[str, object]]] = []

    def set(self, *args: object, **kwargs: object) -> None:
        self.set_calls.append((args, kwargs))


class FakeMusic:
    def __init__(self) -> None:
        self.set_calls: list[tuple[tuple[object, ...], dict[str, object]]] = []

    def set(self, *args: object, **kwargs: object) -> None:
        self.set_calls.append((args, kwargs))


class FakePyxelAudio:
    def __init__(self) -> None:
        self.sounds = [FakeSound() for _ in range(24)]
        self._music = [FakeMusic() for _ in range(4)]
        self.play_calls: list[tuple[int, int]] = []
        self.playm_calls: list[tuple[int, bool]] = []
        self.stop_calls: list[tuple[object, ...]] = []

    def music(self, index: int) -> FakeMusic:
        return self._music[index]

    def play(self, channel: int, sound_index: int) -> None:
        self.play_calls.append((channel, sound_index))

    def playm(self, music_index: int, loop: bool = False) -> None:
        self.playm_calls.append((music_index, loop))

    def stop(self, *args: object) -> None:
        self.stop_calls.append(args)


class RecordingAudio:
    def __init__(self) -> None:
        self.events: list[tuple[str, int | None]] = []
        self.enabled = True

    def start_bgm(self, _pyxel: object) -> None:
        self.events.append(("bgm", None))

    def start_result_bgm(self, _pyxel: object) -> None:
        self.events.append(("result_bgm", None))

    def start_title_bgm(self, _pyxel: object) -> None:
        self.events.append(("title_bgm", None))

    def stop_bgm(self, _pyxel: object) -> None:
        self.events.append(("stop_bgm", None))

    def play_lap(self, _pyxel: object, lap: int) -> None:
        self.events.append(("lap", lap))

    def play_transfer(self, _pyxel: object) -> None:
        self.events.append(("transfer", None))

    def play_orbit_enter(self, _pyxel: object) -> None:
        self.events.append(("orbit_enter", None))

    def play_result(self, _pyxel: object) -> None:
        self.events.append(("result", None))

    def play_title_shooting_star(self, _pyxel: object) -> None:
        self.events.append(("title_shooting_star", None))


class AudioManagerTest(unittest.TestCase):
    def test_configure_registers_sounds_and_music(self) -> None:
        pyxel = FakePyxelAudio()
        audio = AudioManager()

        audio.configure(pyxel)

        self.assertTrue(audio.configured)
        self.assertTrue(pyxel.sounds[SOUND_LAP_1].set_calls)
        self.assertTrue(pyxel.sounds[SOUND_LAP_3].set_calls)
        self.assertTrue(pyxel.sounds[SOUND_ORBIT_ENTER].set_calls)
        self.assertTrue(pyxel.sounds[SOUND_TITLE_SHOOTING_STAR].set_calls)
        self.assertTrue(pyxel.music(MUSIC_CRUISE).set_calls)
        self.assertTrue(pyxel.music(MUSIC_RESULT).set_calls)
        self.assertTrue(pyxel.music(MUSIC_TITLE).set_calls)

    def test_sound_notes_stay_inside_pyxel_supported_octaves(self) -> None:
        for sequence in SOUND_NOTE_SEQUENCES:
            self.assertNotRegex(sequence, r"[a-gr][5-9]")

    def test_start_bgm_uses_looping_music_once(self) -> None:
        pyxel = FakePyxelAudio()
        audio = AudioManager()

        audio.start_bgm(pyxel)
        audio.start_bgm(pyxel)

        self.assertEqual(pyxel.playm_calls, [(MUSIC_CRUISE, True)])
        self.assertEqual(audio.current_music, MUSIC_CRUISE)

    def test_result_bgm_uses_looping_music_and_can_switch_back_to_cruise(self) -> None:
        pyxel = FakePyxelAudio()
        audio = AudioManager()

        audio.start_bgm(pyxel)
        audio.start_result_bgm(pyxel)
        audio.start_result_bgm(pyxel)
        audio.start_bgm(pyxel)

        self.assertEqual(
            pyxel.playm_calls,
            [(MUSIC_CRUISE, True), (MUSIC_RESULT, True), (MUSIC_CRUISE, True)],
        )
        self.assertEqual(audio.current_music, MUSIC_CRUISE)

    def test_title_bgm_uses_low_accompaniment_only(self) -> None:
        pyxel = FakePyxelAudio()
        audio = AudioManager()

        audio.start_title_bgm(pyxel)
        audio.start_title_bgm(pyxel)

        self.assertEqual(pyxel.playm_calls, [(MUSIC_TITLE, True)])
        self.assertEqual(audio.current_music, MUSIC_TITLE)
        args, _kwargs = pyxel.music(MUSIC_TITLE).set_calls[-1]
        self.assertEqual(args[0], [17, 19])
        self.assertEqual(args[1], [])
        self.assertEqual(args[2], [])
        self.assertEqual(args[3], [])

    def test_switching_from_title_to_gameplay_stops_lingering_title_channels(self) -> None:
        pyxel = FakePyxelAudio()
        audio = AudioManager()

        audio.start_title_bgm(pyxel)
        audio.start_bgm(pyxel)

        self.assertEqual(pyxel.stop_calls, [(0,), (1,), (2,)])
        self.assertEqual(pyxel.playm_calls, [(MUSIC_TITLE, True), (MUSIC_CRUISE, True)])
        self.assertEqual(audio.current_music, MUSIC_CRUISE)

    def test_title_shooting_star_sound_plays_as_short_effect(self) -> None:
        pyxel = FakePyxelAudio()
        audio = AudioManager()

        audio.play_title_shooting_star(pyxel)

        self.assertEqual(pyxel.play_calls[-1], (SFX_CHANNEL, SOUND_TITLE_SHOOTING_STAR))
        self.assertEqual(audio.last_event, "title_shooting_star")

    def test_lap_sound_clamps_to_three_stages(self) -> None:
        pyxel = FakePyxelAudio()
        audio = AudioManager()

        audio.play_lap(pyxel, 7)

        self.assertEqual(pyxel.play_calls[-1], (SFX_CHANNEL, SOUND_LAP_3))
        self.assertEqual(audio.last_event, "lap_3")

    def test_disabled_audio_records_event_without_playing(self) -> None:
        pyxel = FakePyxelAudio()
        audio = AudioManager(enabled=False)

        audio.play_supply(pyxel)

        self.assertEqual(audio.last_event, "supply")
        self.assertFalse(pyxel.play_calls)

    def test_toggle_off_stops_audio(self) -> None:
        pyxel = FakePyxelAudio()
        audio = AudioManager()

        enabled = audio.toggle_enabled(pyxel)

        self.assertFalse(enabled)
        self.assertFalse(audio.enabled)
        self.assertEqual(pyxel.stop_calls, [()])


class AppAudioIntegrationTest(unittest.TestCase):
    def test_restart_starts_bgm_when_pyxel_is_ready(self) -> None:
        app = GravityCourierApp()
        app.pyxel = object()
        app.audio = RecordingAudio()  # type: ignore[assignment]

        app.restart()

        self.assertIn(("bgm", None), app.audio.events)  # type: ignore[attr-defined]

    def test_lap_completion_plays_lap_stage_sound(self) -> None:
        app = GravityCourierApp()
        app.pyxel = object()
        app.audio = RecordingAudio()  # type: ignore[assignment]

        app._handle_lap_completed(0)

        self.assertIn(("lap", 1), app.audio.events)  # type: ignore[attr-defined]

    def test_transfer_boost_plays_transfer_sound(self) -> None:
        app = GravityCourierApp()
        app.pyxel = object()
        app.audio = RecordingAudio()  # type: ignore[assignment]

        app._trigger_transfer_boost(0)

        self.assertIn(("transfer", None), app.audio.events)  # type: ignore[attr-defined]

    def test_starting_orbit_visit_plays_orbit_enter_sound(self) -> None:
        app = GravityCourierApp()
        app.pyxel = object()
        app.audio = RecordingAudio()  # type: ignore[assignment]
        app.rocket.position = app.planets[0].position + app.planets[0].position.normalized() * 80.0

        app._start_orbit_visit(0)

        self.assertIn(("orbit_enter", None), app.audio.events)  # type: ignore[attr-defined]

    def test_demo_orbit_start_plays_orbit_enter_sound_once_per_planet(self) -> None:
        app = GravityCourierApp()
        app.pyxel = object()
        app.audio = RecordingAudio()  # type: ignore[assignment]
        planet = app.planets[0]
        app.rocket.position = planet.position + planet.position.normalized() * 80.0

        app._apply_demo_orbit(planet, 0)
        app._apply_demo_orbit(planet, 0)

        self.assertEqual(app.audio.events.count(("orbit_enter", None)), 1)  # type: ignore[attr-defined]

    def test_reaching_result_starts_result_bgm_and_arrival_sound(self) -> None:
        pyxel = FakePyxelAudio()
        app = GravityCourierApp()
        app.pyxel = pyxel
        app.audio = AudioManager()
        app.rocket.position = app.final_goal.position

        self.assertTrue(app._try_complete_final_goal())

        self.assertIn((MUSIC_RESULT, True), pyxel.playm_calls)
        self.assertIn((SFX_CHANNEL, SOUND_RESULT), pyxel.play_calls)
        self.assertEqual(app.audio.current_music, MUSIC_RESULT)

    def test_title_ambient_starts_title_bgm_without_immediate_effect(self) -> None:
        app = GravityCourierApp()
        app.pyxel = object()
        app.audio = RecordingAudio()  # type: ignore[assignment]

        app.enter_title()
        app._update_title_ambient(object())

        self.assertIn(("title_bgm", None), app.audio.events)  # type: ignore[attr-defined]
        self.assertGreaterEqual(app.audio.events.count(("title_bgm", None)), 1)  # type: ignore[attr-defined]
        self.assertTrue(
            all(event in {("title_bgm", None), ("stop_bgm", None)} for event in app.audio.events)  # type: ignore[attr-defined]
        )

    def test_title_ambient_triggers_shooting_star_effect_on_cycle(self) -> None:
        app = GravityCourierApp()
        app.pyxel = object()
        app.audio = RecordingAudio()  # type: ignore[assignment]
        app.enter_title()
        app.frame = TITLE_SHOOTING_STAR_FIRST_FRAME

        app._update_title_ambient(object())

        self.assertEqual(title_shooting_star_phase(app.frame), 0)
        self.assertIn(("title_shooting_star", None), app.audio.events)  # type: ignore[attr-defined]


if __name__ == "__main__":
    unittest.main()
