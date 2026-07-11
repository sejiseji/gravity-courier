import math
import unittest

import _path  # noqa: F401

from gravity_courier.app import (
    GravityCourierApp,
    demo_button_rect,
    goal_test_button_rect,
    heading_from_velocity,
    point_in_rect,
    result_retry_hard_button_rect,
    result_retry_button_rect,
    right_of_direction,
)
from gravity_courier.constants import HEIGHT, ROCKET_TURN_RATE_MAX, WIDTH
from gravity_courier.course import COURSE_MODE_HARD
from gravity_courier.entities import Vec2, from_angle


class FakePyxelMouse:
    MOUSE_BUTTON_LEFT = 0
    KEY_ESCAPE = 1
    KEY_R = 2
    KEY_SPACE = 3
    KEY_D = 4
    KEY_M = 5
    KEY_N = 6
    KEY_G = 7

    def __init__(self, mouse_x: int, mouse_y: int, pressed: bool) -> None:
        self.mouse_x = mouse_x
        self.mouse_y = mouse_y
        self.pressed = pressed

    def btnp(self, button: int) -> bool:
        return button == self.MOUSE_BUTTON_LEFT and self.pressed


class FakePyxelKeys:
    KEY_ESCAPE = 1
    KEY_R = 2
    KEY_SPACE = 3
    KEY_D = 4
    KEY_M = 5
    KEY_N = 6
    MOUSE_BUTTON_LEFT = 7
    mouse_x = 0
    mouse_y = 0

    def __init__(self, pressed_key: int | None = None) -> None:
        self.pressed_key = pressed_key

    def btnp(self, key: int) -> bool:
        return key == self.pressed_key

    def btn(self, _key: int) -> bool:
        return False

    def quit(self) -> None:
        pass


class RelativeControlTest(unittest.TestCase):
    def test_heading_follows_velocity_direction(self) -> None:
        self.assertAlmostEqual(heading_from_velocity(Vec2(0.0, -2.0)), -math.pi / 2)
        self.assertAlmostEqual(heading_from_velocity(Vec2(2.0, 0.0)), 0.0)

    def test_right_direction_is_relative_to_forward_motion(self) -> None:
        upward_right = right_of_direction(from_angle(-math.pi / 2))
        rightward_right = right_of_direction(from_angle(0.0))

        self.assertAlmostEqual(upward_right.x, 1.0)
        self.assertAlmostEqual(upward_right.y, 0.0)
        self.assertAlmostEqual(rightward_right.x, 0.0)
        self.assertAlmostEqual(rightward_right.y, 1.0)

    def test_right_input_changes_velocity_right_of_current_motion(self) -> None:
        app = GravityCourierApp()
        app.rocket.velocity = Vec2(0.0, -2.0)

        app._apply_controls(lateral_input=1.0, boost=False, brake=False, spend_fuel=True)

        self.assertGreater(app.rocket.velocity.x, 0.0)
        self.assertLess(app.rocket.velocity.y, 0.0)

    def test_left_input_on_rightward_motion_moves_screen_up(self) -> None:
        app = GravityCourierApp()
        app.rocket.velocity = Vec2(2.0, 0.0)

        app._apply_controls(lateral_input=-1.0, boost=False, brake=False, spend_fuel=True)

        self.assertLess(app.rocket.velocity.y, 0.0)

    def test_high_speed_right_input_turns_without_losing_speed(self) -> None:
        app = GravityCourierApp()
        app.rocket.velocity = Vec2(0.0, -4.4)
        starting_speed = app.rocket.velocity.length()

        app._apply_controls(lateral_input=1.0, boost=False, brake=False, spend_fuel=True)

        self.assertGreater(app.rocket.velocity.angle(), -math.pi / 2 + 0.04)
        self.assertAlmostEqual(app.rocket.velocity.length(), starting_speed)

    def test_very_high_speed_right_input_gets_extra_steer_response(self) -> None:
        app = GravityCourierApp()
        app.rocket.velocity = Vec2(0.0, -6.0)
        starting_speed = app.rocket.velocity.length()

        app._apply_controls(lateral_input=1.0, boost=False, brake=False, spend_fuel=True)

        self.assertGreater(app.rocket.velocity.angle(), -math.pi / 2 + ROCKET_TURN_RATE_MAX)
        self.assertAlmostEqual(app.rocket.velocity.length(), starting_speed)

    def test_demo_button_rect_is_in_top_right_corner(self) -> None:
        x, y, width, height = demo_button_rect()

        self.assertGreater(x, WIDTH // 2)
        self.assertLess(y, 16)
        self.assertGreater(width, 0)
        self.assertGreater(height, 0)
        self.assertLessEqual(x + width, WIDTH)

    def test_demo_button_hit_testing_uses_screen_coordinates(self) -> None:
        x, y, width, height = demo_button_rect()

        self.assertTrue(point_in_rect(x + width // 2, y + height // 2, demo_button_rect()))
        self.assertFalse(point_in_rect(x - 1, y + height // 2, demo_button_rect()))
        self.assertFalse(point_in_rect(x + width, y + height // 2, demo_button_rect()))

    def test_demo_button_pressed_requires_click_inside_button(self) -> None:
        app = GravityCourierApp()
        x, y, width, height = demo_button_rect()

        inside = FakePyxelMouse(x + width // 2, y + height // 2, pressed=True)
        outside = FakePyxelMouse(x - 1, y + height // 2, pressed=True)
        not_pressed = FakePyxelMouse(x + width // 2, y + height // 2, pressed=False)

        self.assertTrue(app._demo_button_pressed(inside))
        self.assertFalse(app._demo_button_pressed(outside))
        self.assertFalse(app._demo_button_pressed(not_pressed))

    def test_result_retry_button_rect_is_bottom_centered(self) -> None:
        x, y, width, height = result_retry_button_rect()
        hard_x, hard_y, hard_width, hard_height = result_retry_hard_button_rect()

        self.assertLess(x, hard_x)
        self.assertGreater(hard_x + hard_width, WIDTH // 2)
        self.assertEqual(y, hard_y)
        self.assertEqual(height, hard_height)
        self.assertGreater(y, HEIGHT - 120)
        self.assertLessEqual(y + height, HEIGHT - 40)
        self.assertLessEqual(hard_x + hard_width, WIDTH)

    def test_result_retry_button_pressed_requires_click_inside_button(self) -> None:
        app = GravityCourierApp()
        x, y, width, height = result_retry_button_rect()

        inside = FakePyxelMouse(x + width // 2, y + height // 2, pressed=True)
        outside = FakePyxelMouse(x - 1, y + height // 2, pressed=True)
        not_pressed = FakePyxelMouse(x + width // 2, y + height // 2, pressed=False)

        self.assertTrue(app._result_retry_button_pressed(inside))
        self.assertFalse(app._result_retry_button_pressed(outside))
        self.assertFalse(app._result_retry_button_pressed(not_pressed))

    def test_result_retry_hard_button_pressed_requires_click_inside_button(self) -> None:
        app = GravityCourierApp()
        x, y, width, height = result_retry_hard_button_rect()

        inside = FakePyxelMouse(x + width // 2, y + height // 2, pressed=True)
        outside = FakePyxelMouse(x - 1, y + height // 2, pressed=True)
        not_pressed = FakePyxelMouse(x + width // 2, y + height // 2, pressed=False)

        self.assertTrue(app._result_retry_hard_button_pressed(inside))
        self.assertFalse(app._result_retry_hard_button_pressed(outside))
        self.assertFalse(app._result_retry_hard_button_pressed(not_pressed))

    def test_goal_test_button_rect_is_bottom_right_development_button(self) -> None:
        x, y, width, height = goal_test_button_rect()

        self.assertGreater(x, WIDTH // 2)
        self.assertGreater(y, HEIGHT // 2)
        self.assertGreater(width, 0)
        self.assertGreater(height, 0)
        self.assertLessEqual(x + width, WIDTH)
        self.assertLessEqual(y + height, HEIGHT)

    def test_goal_test_button_requires_debug_or_demo_availability(self) -> None:
        app = GravityCourierApp()
        x, y, width, height = goal_test_button_rect()
        click = FakePyxelMouse(x + width // 2, y + height // 2, pressed=True)

        self.assertFalse(app._goal_test_available())
        self.assertTrue(app._goal_test_button_pressed(click))

        app.show_debug = True

        self.assertTrue(app._goal_test_available())

    def test_n_key_toggles_course_mode_and_restarts_course(self) -> None:
        app = GravityCourierApp()
        app.score = 999
        app.rocket.position = Vec2(40.0, 40.0)
        app.pyxel = FakePyxelKeys(pressed_key=FakePyxelKeys.KEY_N)

        app.update()

        self.assertEqual(app.course_mode_key, COURSE_MODE_HARD)
        self.assertEqual(app.course.mode.key, COURSE_MODE_HARD)
        self.assertEqual(len(app.planets), 35)
        self.assertEqual(app.score, 0)
        self.assertNotEqual(app.rocket.position, Vec2(40.0, 40.0))

    def test_result_retry_hard_button_switches_to_hard_and_restarts(self) -> None:
        app = GravityCourierApp()
        app.game_state = "result"
        app.score = 999
        app.rocket.position = Vec2(40.0, 40.0)
        x, y, width, height = result_retry_hard_button_rect()
        app.pyxel = FakePyxelMouse(x + width // 2, y + height // 2, pressed=True)

        app.update()

        self.assertEqual(app.course_mode_key, COURSE_MODE_HARD)
        self.assertEqual(app.course.mode.key, COURSE_MODE_HARD)
        self.assertEqual(len(app.planets), 35)
        self.assertEqual(app.score, 0)
        self.assertNotEqual(app.rocket.position, Vec2(40.0, 40.0))
