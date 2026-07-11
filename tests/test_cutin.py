import unittest

import _path  # noqa: F401

from gravity_courier.cutin import CUTIN_SIDE_LEFT, CUTIN_SIDE_RIGHT, CutInState, cutin_side_for_planet_x
from gravity_courier.constants import CUTIN_DURATION_FRAMES
from gravity_courier.planet_types import PLANET_TYPE_FOREST, PLANET_TYPE_ROCK, PLANET_TYPE_WATER


class CutInStateTest(unittest.TestCase):
    def test_starting_cutin_activates_it_with_payload(self) -> None:
        cutin = CutInState()

        cutin.start(PLANET_TYPE_FOREST, lap_count=2, score_gain=150, reward_text="FUEL +25%")

        self.assertTrue(cutin.active)
        self.assertEqual(cutin.timer, CUTIN_DURATION_FRAMES)
        self.assertIsNotNone(cutin.payload)
        assert cutin.payload is not None
        self.assertEqual(cutin.payload.planet_type, PLANET_TYPE_FOREST)
        self.assertEqual(cutin.payload.resident_id, "forest_leaf")
        self.assertEqual(cutin.payload.lap_count, 2)
        self.assertEqual(cutin.payload.score_gain, 150)
        self.assertEqual(cutin.payload.reward_text, "FUEL +25%")
        self.assertEqual(cutin.payload.cheer_stage, 2)
        self.assertEqual(cutin.payload.side, CUTIN_SIDE_RIGHT)
        self.assertTrue(cutin.payload.cheer_line)

    def test_timer_counts_down_and_deactivates_after_duration(self) -> None:
        cutin = CutInState(duration=3)
        cutin.start(PLANET_TYPE_ROCK, lap_count=1, score_gain=100)

        cutin.tick()
        self.assertTrue(cutin.active)
        self.assertEqual(cutin.timer, 2)

        cutin.tick()
        cutin.tick()

        self.assertFalse(cutin.active)
        self.assertEqual(cutin.timer, 0)

    def test_lap_three_plus_uses_stage_three(self) -> None:
        cutin = CutInState()

        cutin.start(PLANET_TYPE_ROCK, lap_count=8, score_gain=300)

        assert cutin.payload is not None
        self.assertEqual(cutin.payload.cheer_stage, 3)
        self.assertEqual(cutin.payload.sub_message, "LAP 3+  +300")

    def test_cutin_side_selects_opposite_planet_side(self) -> None:
        self.assertEqual(cutin_side_for_planet_x(80, screen_width=393), CUTIN_SIDE_RIGHT)
        self.assertEqual(cutin_side_for_planet_x(320, screen_width=393), CUTIN_SIDE_LEFT)
        self.assertEqual(cutin_side_for_planet_x(196.5, screen_width=393), CUTIN_SIDE_LEFT)

    def test_start_accepts_side_and_target_y(self) -> None:
        cutin = CutInState()

        cutin.start(PLANET_TYPE_WATER, lap_count=1, score_gain=100, side=CUTIN_SIDE_LEFT, target_y=260)

        assert cutin.payload is not None
        self.assertEqual(cutin.payload.side, CUTIN_SIDE_LEFT)
        self.assertEqual(cutin.payload.target_y, 260)


if __name__ == "__main__":
    unittest.main()
