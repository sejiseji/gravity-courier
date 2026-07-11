import unittest

import _path  # noqa: F401

from gravity_courier.scoring import (
    GravityAssistState,
    cheer_stage_for_lap,
    cheer_text_for_stage,
    is_gravity_assist,
    lap_display_text,
    lap_multiplier,
    score_gain_for_assist,
    update_gravity_assist,
)


class ScoringTest(unittest.TestCase):
    def test_gravity_assist_detects_speed_gain(self) -> None:
        self.assertTrue(is_gravity_assist(1.0, 1.2, min_gain=0.15))

    def test_gravity_assist_rejects_small_gain(self) -> None:
        self.assertFalse(is_gravity_assist(1.0, 1.1, min_gain=0.15))

    def test_gravity_assist_triggers_on_well_exit_with_speed_gain(self) -> None:
        state = GravityAssistState()

        self.assertFalse(update_gravity_assist(state, 0, True, 2.0, min_gain=0.3))
        self.assertTrue(update_gravity_assist(state, 0, False, 2.4, min_gain=0.3))

    def test_gravity_assist_rejects_exit_without_speed_gain(self) -> None:
        state = GravityAssistState()

        self.assertFalse(update_gravity_assist(state, 0, True, 2.0, min_gain=0.3))
        self.assertFalse(update_gravity_assist(state, 0, False, 2.1, min_gain=0.3))

    def test_gravity_assist_does_not_repeat_after_one_exit(self) -> None:
        state = GravityAssistState()

        update_gravity_assist(state, 0, True, 2.0, min_gain=0.3)
        self.assertTrue(update_gravity_assist(state, 0, False, 2.4, min_gain=0.3))
        self.assertFalse(update_gravity_assist(state, 0, False, 2.5, min_gain=0.3))

    def test_lap_multiplier_uses_provisional_grc003_formula(self) -> None:
        self.assertEqual(lap_multiplier(1), 1.0)
        self.assertEqual(lap_multiplier(2), 1.5)
        self.assertEqual(lap_multiplier(3), 2.0)
        self.assertEqual(lap_multiplier(4), 2.25)
        self.assertEqual(lap_multiplier(5), 2.5)

    def test_score_gain_uses_lap_and_planet_bonus_multipliers(self) -> None:
        self.assertEqual(score_gain_for_assist(1), 100)
        self.assertEqual(score_gain_for_assist(2), 150)
        self.assertEqual(score_gain_for_assist(3), 200)
        self.assertEqual(score_gain_for_assist(4), 225)
        self.assertEqual(score_gain_for_assist(2, planet_bonus_multiplier=1.2), 180)
        self.assertEqual(score_gain_for_assist(2, planet_bonus_multiplier=1.25), 188)

    def test_lap_display_caps_at_three_plus(self) -> None:
        self.assertEqual(lap_display_text(0), "")
        self.assertEqual(lap_display_text(1), "1")
        self.assertEqual(lap_display_text(2), "2")
        self.assertEqual(lap_display_text(3), "3+")
        self.assertEqual(lap_display_text(8), "3+")

    def test_cheer_stage_caps_at_stage_three(self) -> None:
        self.assertEqual(cheer_stage_for_lap(1), 1)
        self.assertEqual(cheer_stage_for_lap(2), 2)
        self.assertEqual(cheer_stage_for_lap(3), 3)
        self.assertEqual(cheer_stage_for_lap(9), 3)
        self.assertEqual(cheer_text_for_stage(1), "WAA!")
        self.assertEqual(cheer_text_for_stage(2), "CLAP! CLAP!")
        self.assertEqual(cheer_text_for_stage(3), "WOOO! WHISTLE!")
