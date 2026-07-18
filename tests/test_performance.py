import unittest
from unittest.mock import patch

import _path  # noqa: F401

from gravity_courier.app import GravityCourierApp, STATE_PLAYING
from gravity_courier.constants import (
    GAMEPLAY_STARFIELD_STRIDE,
    HEIGHT,
    STAR_COUNT,
    TRAJECTORY_RECALC_INTERVAL_FRAMES,
    WIDTH,
)
from gravity_courier.entities import Vec2


class RecordingPyxel:
    def __init__(self) -> None:
        self.psets: list[tuple[int, int, int]] = []

    def pset(self, *args: int) -> None:
        self.psets.append(args)


class PerformanceOptimizationTest(unittest.TestCase):
    def test_vec2_distance_squared_matches_expected_value(self) -> None:
        self.assertEqual(Vec2(0.0, 0.0).distance_squared_to(Vec2(3.0, 4.0)), 25.0)

    def test_trajectory_preview_is_cached_between_recalc_frames(self) -> None:
        app = GravityCourierApp()
        points = [Vec2(1.0, 2.0)]

        with patch("gravity_courier.app.simulate_preview", return_value=points) as simulate:
            app.frame = 10
            self.assertEqual(app._trajectory_preview_points(), points)
            self.assertEqual(simulate.call_count, 1)

            app.frame = 10 + TRAJECTORY_RECALC_INTERVAL_FRAMES - 1
            self.assertEqual(app._trajectory_preview_points(), points)
            self.assertEqual(simulate.call_count, 1)

            app.frame = 10 + TRAJECTORY_RECALC_INTERVAL_FRAMES
            self.assertEqual(app._trajectory_preview_points(), points)
            self.assertEqual(simulate.call_count, 2)

    def test_gameplay_starfield_draws_with_stride(self) -> None:
        app = GravityCourierApp()
        pyxel = RecordingPyxel()
        app.pyxel = pyxel
        app.game_state = STATE_PLAYING

        app._draw_starfield()

        expected_count = len(range(0, STAR_COUNT, GAMEPLAY_STARFIELD_STRIDE))
        self.assertEqual(len(pyxel.psets), expected_count)

    def test_planet_lod_prefers_full_detail_near_camera_anchor(self) -> None:
        app = GravityCourierApp()
        near_anchor = app.camera.anchor
        far_from_anchor = Vec2(WIDTH * 0.5, HEIGHT * 2.0)

        self.assertEqual(app._planet_detail_lod(near_anchor), 3)
        self.assertEqual(app._planet_detail_lod(far_from_anchor), 0)

    def test_screen_circle_visibility_uses_margin(self) -> None:
        app = GravityCourierApp()

        self.assertTrue(app._screen_circle_visible(Vec2(-5.0, HEIGHT * 0.5), radius=1.0, margin=8.0))
        self.assertFalse(app._screen_circle_visible(Vec2(-20.0, HEIGHT * 0.5), radius=1.0, margin=8.0))


if __name__ == "__main__":
    unittest.main()
