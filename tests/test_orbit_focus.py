import math
import unittest

import _path  # noqa: F401

from gravity_courier.app import GravityCourierApp, OrbitProgress, orbit_track_display_radius
from gravity_courier.camera import Camera
from gravity_courier.constants import (
    COLOR_HUD,
    COLOR_TRAJECTORY,
    ORBIT_FOCUS_LINE_ORBIT_MARGIN,
    ORBIT_FOCUS_LINE_JITTER,
    ORBIT_FOCUS_MAX_LINES,
    ORBIT_FOCUS_MAX_ZOOM,
    ORBIT_FOCUS_PLANET_SWITCH_RELEASE_FRAMES,
)
from gravity_courier.entities import Vec2


class LineRecordingPyxel:
    def __init__(self) -> None:
        self.lines: list[tuple[int, ...]] = []

    def line(self, *args: int) -> None:
        self.lines.append(args)


class CameraZoomTest(unittest.TestCase):
    def test_camera_zoom_round_trips_screen_and_world_coordinates(self) -> None:
        camera = Camera(position=Vec2(100.0, -200.0), zoom=1.12)
        world = Vec2(130.0, -250.0)

        screen = camera.world_to_screen(world)

        self.assertEqual(camera.screen_to_world(screen), world)
        self.assertGreater(screen.distance_to(camera.anchor), world.distance_to(camera.position))


class OrbitFocusTest(unittest.TestCase):
    def test_orbit_focus_starts_after_minimum_lap_progress(self) -> None:
        app = GravityCourierApp()
        app.rocket.position = app.planets[0].position + Vec2(72.0, 0.0)
        app.orbit_progress[0] = OrbitProgress(
            accumulated_angle=math.tau * 0.10,
            in_orbit=True,
        )

        self.assertEqual(app._target_orbit_focus_strength(), 0.0)

        app.orbit_progress[0].accumulated_angle = math.tau * 0.30

        self.assertGreater(app._target_orbit_focus_strength(), 0.0)

    def test_orbit_focus_is_reduced_while_cutin_is_active(self) -> None:
        app = GravityCourierApp()
        app.rocket.position = app.planets[0].position + Vec2(72.0, 0.0)
        app.orbit_progress[0] = OrbitProgress(
            accumulated_angle=math.tau * 0.50,
            visit_laps=1,
            in_orbit=True,
        )

        normal_strength = app._target_orbit_focus_strength()
        app.cutin.active = True

        self.assertLess(app._target_orbit_focus_strength(), normal_strength)

    def test_orbit_focus_zoom_never_exceeds_safe_maximum(self) -> None:
        app = GravityCourierApp()
        app.rocket.position = app.planets[0].position + Vec2(72.0, 0.0)
        app.orbit_progress[0] = OrbitProgress(
            accumulated_angle=math.tau * 0.95,
            visit_laps=3,
            in_orbit=True,
        )

        for _ in range(160):
            app._update_orbit_focus()

        self.assertLessEqual(app.camera.zoom, ORBIT_FOCUS_MAX_ZOOM)
        self.assertGreater(app.camera.zoom, 1.0)

    def test_transfer_boost_releases_orbit_focus(self) -> None:
        app = GravityCourierApp()
        app.rocket.position = app.planets[0].position + Vec2(72.0, 0.0)
        app.orbit_progress[0] = OrbitProgress(
            accumulated_angle=math.tau * 0.95,
            visit_laps=2,
            in_orbit=True,
        )
        app.orbit_focus_strength = 0.8
        app.camera.zoom = 1.10
        app.transfer_boost_timer = 10

        app._update_orbit_focus()

        self.assertLess(app.orbit_focus_strength, 0.8)
        self.assertLess(app.camera.zoom, 1.10)

    def test_planet_switch_releases_zoom_before_reacquiring_focus(self) -> None:
        app = GravityCourierApp()
        app.orbit_focus_planet_index = 0
        app.orbit_focus_strength = 0.8
        app.camera.zoom = 1.10
        app.rocket.position = app.planets[1].position + Vec2(72.0, 0.0)
        app.orbit_progress[0] = OrbitProgress(
            accumulated_angle=math.tau * 0.95,
            visit_laps=2,
            in_orbit=False,
        )
        app.orbit_progress[1] = OrbitProgress(
            accumulated_angle=math.tau * 0.80,
            visit_laps=1,
            in_orbit=True,
        )

        app._update_orbit_focus()

        self.assertEqual(app.orbit_focus_planet_index, 1)
        self.assertEqual(app.orbit_focus_switch_release_timer, ORBIT_FOCUS_PLANET_SWITCH_RELEASE_FRAMES - 1)
        self.assertEqual(app.orbit_focus_strength, 0.0)
        self.assertLess(app.camera.zoom, 1.10)
        self.assertEqual(app._target_orbit_focus_strength(), 0.0)

    def test_orbit_focus_lines_are_limited_and_screen_space(self) -> None:
        app = GravityCourierApp()
        pyxel = LineRecordingPyxel()
        app.pyxel = pyxel
        app.rocket.position = app.planets[0].position + Vec2(72.0, 0.0)
        app.orbit_progress[0] = OrbitProgress(
            accumulated_angle=math.tau * 0.80,
            visit_laps=2,
            in_orbit=True,
        )
        app.orbit_focus_strength = 1.0

        app._draw_orbit_focus_lines()

        self.assertGreaterEqual(len(pyxel.lines), 8)
        self.assertLessEqual(len(pyxel.lines), ORBIT_FOCUS_MAX_LINES)

    def test_orbit_focus_lines_target_planet_center_and_clear_orbit_track(self) -> None:
        app = GravityCourierApp()
        pyxel = LineRecordingPyxel()
        app.pyxel = pyxel
        planet = app.planets[0]
        app.rocket.position = planet.position + Vec2(72.0, 0.0)
        app.orbit_progress[0] = OrbitProgress(
            accumulated_angle=math.tau * 0.80,
            visit_laps=2,
            in_orbit=True,
        )
        app.orbit_focus_strength = 1.0
        planet_screen = app.camera.world_to_screen(planet.position)
        stop_radius = int(orbit_track_display_radius(planet) * ORBIT_FOCUS_MAX_ZOOM) + ORBIT_FOCUS_LINE_ORBIT_MARGIN

        app._draw_orbit_focus_lines()

        self.assertTrue(pyxel.lines)
        end_distances: list[float] = []
        colors: set[int] = set()
        for start_x, start_y, end_x, end_y, _color in pyxel.lines:
            start_distance = Vec2(start_x - planet_screen.x, start_y - planet_screen.y).length()
            end_distance = Vec2(end_x - planet_screen.x, end_y - planet_screen.y).length()
            self.assertGreaterEqual(end_distance, stop_radius - ORBIT_FOCUS_LINE_JITTER - 2)
            self.assertLess(end_distance, start_distance)
            end_distances.append(end_distance)
            colors.add(_color)
        self.assertGreater(max(end_distances) - min(end_distances), 8.0)
        self.assertIn(COLOR_HUD, colors)
        self.assertIn(COLOR_TRAJECTORY, colors)

    def test_orbit_focus_lines_ignore_stale_past_orbit_planet(self) -> None:
        app = GravityCourierApp()
        pyxel = LineRecordingPyxel()
        app.pyxel = pyxel
        past_planet = app.planets[0]
        current_planet = app.planets[1]
        app.rocket.position = current_planet.position + Vec2(74.0, 0.0)
        app.orbit_progress[0] = OrbitProgress(
            accumulated_angle=math.tau * 0.90,
            visit_laps=2,
            in_orbit=True,
        )
        app.orbit_progress[1] = OrbitProgress(
            accumulated_angle=math.tau * 0.80,
            visit_laps=1,
            in_orbit=True,
        )
        app.orbit_focus_strength = 1.0
        past_screen = app.camera.world_to_screen(past_planet.position)
        current_screen = app.camera.world_to_screen(current_planet.position)

        app._draw_orbit_focus_lines()

        self.assertTrue(pyxel.lines)
        first_line = pyxel.lines[0]
        end = Vec2(first_line[2], first_line[3])
        self.assertLess(end.distance_to(current_screen), end.distance_to(past_screen))

    def test_orbit_focus_lines_are_static_without_camera_motion(self) -> None:
        app = GravityCourierApp()
        pyxel = LineRecordingPyxel()
        app.pyxel = pyxel
        planet = app.planets[0]
        app.rocket.position = planet.position + Vec2(72.0, 0.0)
        app.orbit_progress[0] = OrbitProgress(
            accumulated_angle=math.tau * 0.80,
            visit_laps=2,
            in_orbit=True,
        )
        app.orbit_focus_strength = 1.0

        app._draw_orbit_focus_lines()
        first_lines = tuple(pyxel.lines)

        app.frame += 17
        pyxel.lines = []
        app._draw_orbit_focus_lines()

        self.assertEqual(tuple(pyxel.lines), first_lines)

    def test_orbit_focus_lines_follow_current_planet_screen_center(self) -> None:
        app = GravityCourierApp()
        pyxel = LineRecordingPyxel()
        app.pyxel = pyxel
        planet = app.planets[0]
        app.rocket.position = planet.position + Vec2(72.0, 0.0)
        app.orbit_progress[0] = OrbitProgress(
            accumulated_angle=math.tau * 0.80,
            visit_laps=2,
            in_orbit=True,
        )
        app.orbit_focus_strength = 1.0
        app.camera.position = app.camera.position + Vec2(12.0, -18.0)
        app.camera.zoom = 1.10
        planet_screen = app.camera.world_to_screen(planet.position)

        app._draw_orbit_focus_lines()

        self.assertTrue(pyxel.lines)
        for start_x, start_y, end_x, end_y, _color in pyxel.lines:
            start_distance = Vec2(start_x - planet_screen.x, start_y - planet_screen.y).length()
            end_distance = Vec2(end_x - planet_screen.x, end_y - planet_screen.y).length()
            self.assertLess(end_distance, start_distance)

    def test_orbit_focus_line_outer_endpoints_stay_fixed_as_center_moves(self) -> None:
        app = GravityCourierApp()
        pyxel = LineRecordingPyxel()
        app.pyxel = pyxel
        planet = app.planets[0]
        app.rocket.position = planet.position + Vec2(72.0, 0.0)
        app.orbit_progress[0] = OrbitProgress(
            accumulated_angle=math.tau * 0.80,
            visit_laps=2,
            in_orbit=True,
        )
        app.orbit_focus_strength = 1.0

        app._draw_orbit_focus_lines()
        first_starts = tuple((start_x, start_y) for start_x, start_y, _end_x, _end_y, _color in pyxel.lines)
        first_ends = tuple((end_x, end_y) for _start_x, _start_y, end_x, end_y, _color in pyxel.lines)

        app.camera.position = app.camera.position + Vec2(12.0, -18.0)
        pyxel.lines = []
        app._draw_orbit_focus_lines()
        second_starts = tuple((start_x, start_y) for start_x, start_y, _end_x, _end_y, _color in pyxel.lines)
        second_ends = tuple((end_x, end_y) for _start_x, _start_y, end_x, end_y, _color in pyxel.lines)

        self.assertEqual(second_starts, first_starts)
        self.assertNotEqual(second_ends, first_ends)


if __name__ == "__main__":
    unittest.main()
