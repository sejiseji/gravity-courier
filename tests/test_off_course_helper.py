import unittest

import _path  # noqa: F401

from gravity_courier.app import GravityCourierApp, edge_indicator_position
from gravity_courier.constants import (
    HEIGHT,
    OFF_COURSE_MARGIN,
    OFF_COURSE_SAFE_BOTTOM,
    OFF_COURSE_SAFE_TOP,
    OFF_COURSE_STALL_FRAMES,
    WIDTH,
)
from gravity_courier.entities import Planet, Vec2
from gravity_courier.goal import create_final_goal
from gravity_courier.planet_types import PLANET_TYPE_ROCK, PLANET_TYPE_WIND


def make_planet(position: Vec2, planet_type: str = PLANET_TYPE_ROCK) -> Planet:
    return Planet(
        position=position,
        mass=18.0,
        radius=18.0,
        gravity_well_radius=80.0,
        planet_type=planet_type,
    )


class IndicatorPyxel:
    def __init__(self) -> None:
        self.tris: list[tuple[int, ...]] = []
        self.lines: list[tuple[int, ...]] = []

    def tri(self, *args: int) -> None:
        self.tris.append(args)

    def line(self, *args: int) -> None:
        self.lines.append(args)

    def rect(self, *_args: int) -> None:
        pass


class OffCourseHelperTest(unittest.TestCase):
    def test_edge_indicator_position_clamps_to_screen_margin(self) -> None:
        right = edge_indicator_position(WIDTH + 500.0, HEIGHT * 0.5, WIDTH, HEIGHT, OFF_COURSE_MARGIN)
        left = edge_indicator_position(-500.0, HEIGHT * 0.5, WIDTH, HEIGHT, OFF_COURSE_MARGIN)
        top = edge_indicator_position(WIDTH * 0.5, -500.0, WIDTH, HEIGHT, OFF_COURSE_MARGIN)

        self.assertEqual(right[0], WIDTH - OFF_COURSE_MARGIN)
        self.assertEqual(left[0], OFF_COURSE_MARGIN)
        self.assertEqual(top[1], OFF_COURSE_MARGIN)

    def test_next_course_target_uses_course_order_not_nearest_past_planet(self) -> None:
        app = GravityCourierApp()
        app.planets = [
            make_planet(Vec2(190.0, 0.0), PLANET_TYPE_ROCK),
            make_planet(Vec2(200.0, -400.0), PLANET_TYPE_WIND),
            make_planet(Vec2(360.0, -800.0), PLANET_TYPE_ROCK),
        ]
        app.final_goal = create_final_goal(app.planets)
        app.highest_course_planet_index = 1
        app.rocket.position = Vec2(200.0, -486.0)

        target_type, target_index, target_position = app._off_course_target()

        self.assertEqual(target_type, "planet")
        self.assertEqual(target_index, 2)
        self.assertEqual(target_position, app.planets[2].position)

    def test_next_course_target_skips_planets_that_are_already_behind_rocket(self) -> None:
        app = GravityCourierApp()
        app.planets = [
            make_planet(Vec2(190.0, 0.0), PLANET_TYPE_ROCK),
            make_planet(Vec2(200.0, -400.0), PLANET_TYPE_WIND),
            make_planet(Vec2(220.0, -800.0), PLANET_TYPE_ROCK),
        ]
        app.final_goal = create_final_goal(app.planets)
        app.highest_course_planet_index = 0
        app.rocket.position = Vec2(210.0, -520.0)

        target_type, target_index, target_position = app._off_course_target()

        self.assertEqual(target_type, "planet")
        self.assertEqual(target_index, 2)
        self.assertEqual(target_position, app.planets[2].position)

    def test_off_course_target_becomes_final_goal_after_last_planet(self) -> None:
        app = GravityCourierApp()
        app.highest_course_planet_index = len(app.planets) - 1
        last_planet = app.planets[-1]
        app.rocket.position = last_planet.position + Vec2(0.0, -last_planet.gravity_well_radius - 1.0)

        target_type, target_index, target_position = app._off_course_target()

        self.assertEqual(target_type, "goal")
        self.assertIsNone(target_index)
        self.assertEqual(target_position, app.final_goal.position)

    def test_off_course_helper_activates_when_target_is_offscreen(self) -> None:
        app = GravityCourierApp()
        app.planets = [make_planet(Vec2(WIDTH * 0.5, -2400.0))]
        app.final_goal = create_final_goal(app.planets)
        app.highest_course_planet_index = 0
        app.camera.position = app.rocket.position

        app._update_off_course_helper()

        self.assertTrue(app.off_course_active)
        self.assertEqual(app.off_course_target_type, "planet")
        self.assertEqual(app.off_course_target_index, 0)

    def test_off_course_helper_hides_while_any_planet_gravity_ring_is_visible(self) -> None:
        app = GravityCourierApp()
        app.camera.position = app.rocket.position
        visible_position = app.camera.screen_to_world(Vec2(WIDTH * 0.5, HEIGHT * 0.5))
        app.planets = [
            make_planet(Vec2(WIDTH * 0.5, -2400.0)),
            make_planet(visible_position),
        ]
        app.final_goal = create_final_goal(app.planets)
        app.highest_course_planet_index = 0

        app._update_off_course_helper()

        self.assertFalse(app.off_course_active)

    def test_off_course_helper_counts_stall_when_distance_does_not_improve(self) -> None:
        app = GravityCourierApp()
        app.planets = [make_planet(Vec2(WIDTH * 0.5, -2400.0))]
        app.final_goal = create_final_goal(app.planets)
        app.highest_course_planet_index = 0
        app.camera.position = app.rocket.position

        app._update_off_course_helper()
        app._update_off_course_helper()

        self.assertEqual(app.off_course_stall_frames, 1)

        app.off_course_stall_frames = OFF_COURSE_STALL_FRAMES - 1
        app._update_off_course_helper()

        self.assertTrue(app.off_course_active)

    def test_off_course_indicator_stays_inside_safe_vertical_band(self) -> None:
        app = GravityCourierApp()
        pyxel = IndicatorPyxel()
        app.pyxel = pyxel
        app.planets = [make_planet(Vec2(WIDTH * 0.5, -2400.0))]
        app.final_goal = create_final_goal(app.planets)
        app.off_course_active = True
        app.off_course_distance = 1234.0
        app.camera.position = app.rocket.position

        app._draw_off_course_helper()

        self.assertTrue(pyxel.tris)
        y_values = pyxel.tris[0][1::2]
        self.assertGreaterEqual(min(y_values), OFF_COURSE_SAFE_TOP)
        self.assertLessEqual(max(y_values), HEIGHT - OFF_COURSE_SAFE_BOTTOM)

    def test_off_course_indicator_hides_during_cutin(self) -> None:
        app = GravityCourierApp()
        pyxel = IndicatorPyxel()
        app.pyxel = pyxel
        app.off_course_active = True
        app.cutin.active = True

        app._draw_off_course_helper()

        self.assertFalse(pyxel.tris)
