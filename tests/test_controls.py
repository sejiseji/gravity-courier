import math
import unittest

import _path  # noqa: F401

from gravity_courier.app import (
    ControlIntent,
    GravityCourierApp,
    STATE_PLAYING,
    STATE_TITLE,
    TITLE_MENU_DEMO,
    TITLE_MENU_MODE,
    TITLE_MENU_SOUND,
    TITLE_MENU_START,
    TouchControlState,
    demo_button_rect,
    goal_test_button_rect,
    heading_from_velocity,
    point_in_rect,
    result_retry_hard_button_rect,
    result_retry_button_rect,
    result_title_button_rect,
    right_of_direction,
    title_demo_button_rect,
    title_mode_button_rect,
    title_sound_button_rect,
    title_start_button_rect,
)
from gravity_courier.constants import (
    HEIGHT,
    ROCKET_TURN_RATE_MAX,
    TOUCH_BRAKE_PULSE_STRENGTH,
    TOUCH_THRUST_PULSE_STRENGTH,
    WIDTH,
)
from gravity_courier.course import COURSE_MODE_HARD, COURSE_MODE_NORMAL
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
    KEY_LEFT = 8
    KEY_RIGHT = 9
    KEY_UP = 10
    KEY_DOWN = 11
    KEY_Z = 12
    KEY_RETURN = 13
    KEY_ENTER = 14
    KEY_S = 15

    def __init__(self, mouse_x: int, mouse_y: int, pressed: bool) -> None:
        self.mouse_x = mouse_x
        self.mouse_y = mouse_y
        self.pressed = pressed

    def btnp(self, button: int) -> bool:
        return button == self.MOUSE_BUTTON_LEFT and self.pressed

    def btn(self, _button: int) -> bool:
        return False


class FakePyxelKeys:
    KEY_ESCAPE = 1
    KEY_R = 2
    KEY_SPACE = 3
    KEY_D = 4
    KEY_M = 5
    KEY_N = 6
    KEY_G = 7
    KEY_LEFT = 8
    KEY_RIGHT = 9
    KEY_UP = 10
    KEY_DOWN = 11
    KEY_Z = 12
    KEY_RETURN = 13
    KEY_ENTER = 14
    KEY_S = 15
    MOUSE_BUTTON_LEFT = 16
    mouse_x = 0
    mouse_y = 0

    def __init__(self, pressed_key: int | None = None, held_keys: set[int] | None = None) -> None:
        self.pressed_key = pressed_key
        self.held_keys = held_keys or set()

    def btnp(self, key: int) -> bool:
        return key == self.pressed_key

    def btn(self, key: int) -> bool:
        return key in self.held_keys

    def quit(self) -> None:
        pass


class RecordingTitleAudio:
    def __init__(self, enabled: bool = True) -> None:
        self.enabled = enabled
        self.events: list[str] = []

    def start_bgm(self, _pyxel: object) -> None:
        self.events.append("start_bgm")

    def start_title_bgm(self, _pyxel: object) -> None:
        self.events.append("start_title_bgm")

    def start_result_bgm(self, _pyxel: object) -> None:
        self.events.append("start_result_bgm")

    def stop_bgm(self, _pyxel: object) -> None:
        self.events.append("stop_bgm")

    def toggle_enabled(self, _pyxel: object) -> bool:
        self.enabled = not self.enabled
        self.events.append("toggle")
        if self.enabled:
            self.events.append("start_bgm")
        else:
            self.events.append("stop")
        return self.enabled


class FakePyxelTouch:
    MOUSE_BUTTON_LEFT = 0

    def __init__(self, mouse_x: int, mouse_y: int, held: bool = True) -> None:
        self.mouse_x = mouse_x
        self.mouse_y = mouse_y
        self.held = held

    def btn(self, button: int) -> bool:
        return button == self.MOUSE_BUTTON_LEFT and self.held


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

    def test_keyboard_input_builds_control_intent(self) -> None:
        app = GravityCourierApp()
        pyxel = FakePyxelKeys(
            held_keys={FakePyxelKeys.KEY_RIGHT, FakePyxelKeys.KEY_UP},
        )

        intent = app._keyboard_control_intent(pyxel)

        self.assertEqual(intent.rotate_axis, 1.0)
        self.assertEqual(intent.thrust_axis, 1.0)
        self.assertEqual(intent.brake_axis, 0.0)

    def test_touch_drag_builds_screen_space_rotate_intent(self) -> None:
        app = GravityCourierApp()
        app.touch_controls = TouchControlState(active=True, last_x=100.0, last_y=300.0)
        app.camera.zoom = 1.12

        intent = app._touch_control_intent(FakePyxelTouch(126, 300))

        self.assertGreater(intent.rotate_axis, 0.0)
        self.assertEqual(app.touch_controls.last_x, 126.0)

    def test_touch_high_speed_turn_assist_raises_drag_response(self) -> None:
        app = GravityCourierApp()
        app.touch_controls = TouchControlState(active=True, last_x=100.0, last_y=300.0)
        app.rocket.velocity = Vec2(0.0, -1.0)
        low_speed = app._touch_control_intent(FakePyxelTouch(110, 300)).rotate_axis

        app.touch_controls = TouchControlState(active=True, last_x=100.0, last_y=300.0)
        app.rocket.velocity = Vec2(0.0, -6.0)
        high_speed = app._touch_control_intent(FakePyxelTouch(110, 300)).rotate_axis

        self.assertGreater(high_speed, low_speed)

    def test_touch_up_swipe_creates_gentle_thrust_pulse(self) -> None:
        app = GravityCourierApp()
        app.touch_controls = TouchControlState(active=True, last_x=100.0, last_y=300.0)

        intent = app._touch_control_intent(FakePyxelTouch(100, 260))

        self.assertEqual(intent.thrust_pulse, TOUCH_THRUST_PULSE_STRENGTH)
        self.assertGreater(app.touch_thrust_pulse_frames, 0)

    def test_touch_down_swipe_creates_gentle_brake_pulse(self) -> None:
        app = GravityCourierApp()
        app.touch_controls = TouchControlState(active=True, last_x=100.0, last_y=300.0)

        intent = app._touch_control_intent(FakePyxelTouch(100, 340))

        self.assertEqual(intent.brake_pulse, TOUCH_BRAKE_PULSE_STRENGTH)
        self.assertGreater(app.touch_brake_pulse_frames, 0)

    def test_touch_on_screen_button_does_not_become_flight_drag(self) -> None:
        app = GravityCourierApp()
        app.touch_controls = TouchControlState(active=True, last_x=100.0, last_y=300.0)
        x, y, width, height = demo_button_rect()

        intent = app._touch_control_intent(FakePyxelTouch(x + width // 2, y + height // 2))

        self.assertEqual(intent.rotate_axis, 0.0)
        self.assertFalse(app.touch_controls.active)

    def test_control_intent_applies_gentle_pulse_without_full_keyboard_boost(self) -> None:
        app = GravityCourierApp()
        app.rocket.velocity = Vec2(0.0, -2.0)
        starting_speed = app.rocket.velocity.length()

        app._apply_control_intent(ControlIntent(thrust_pulse=TOUCH_THRUST_PULSE_STRENGTH), spend_fuel=True)

        self.assertGreater(app.rocket.velocity.length(), starting_speed)
        self.assertLess(app.rocket.velocity.length(), starting_speed + 0.03)

    def test_trajectory_preview_is_always_enabled_for_mobile_readiness(self) -> None:
        app = GravityCourierApp()
        app.show_preview = False

        self.assertTrue(app._trajectory_preview_enabled())

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

    def test_title_button_rects_are_centered_and_touch_sized(self) -> None:
        for rect in (
            title_start_button_rect(),
            title_mode_button_rect(),
            title_demo_button_rect(),
            title_sound_button_rect(),
        ):
            x, _y, width, height = rect
            self.assertEqual(x + width // 2, WIDTH // 2)
            self.assertGreaterEqual(width, 200)
            self.assertGreaterEqual(height, 34)

    def test_enter_title_stops_bgm_without_resetting_course_selection(self) -> None:
        app = GravityCourierApp()
        app._toggle_course_mode()
        app.pyxel = object()
        app.audio = RecordingTitleAudio()  # type: ignore[assignment]

        app.enter_title()

        self.assertEqual(app.game_state, STATE_TITLE)
        self.assertFalse(app.demo_mode)
        self.assertEqual(app.course_mode_key, COURSE_MODE_HARD)
        self.assertIn("stop_bgm", app.audio.events)  # type: ignore[attr-defined]
        self.assertIn("start_title_bgm", app.audio.events)  # type: ignore[attr-defined]

    def test_title_start_button_starts_selected_course_and_bgm(self) -> None:
        app = GravityCourierApp()
        app.enter_title()
        app.score = 999
        app.title_demo_enabled = True
        app.pyxel = object()
        app.audio = RecordingTitleAudio()  # type: ignore[assignment]
        x, y, width, height = title_start_button_rect()
        app.pyxel = FakePyxelMouse(x + width // 2, y + height // 2, pressed=True)

        app.update()

        self.assertEqual(app.game_state, STATE_PLAYING)
        self.assertTrue(app.demo_mode)
        self.assertEqual(app.score, 0)
        self.assertIn("start_bgm", app.audio.events)  # type: ignore[attr-defined]

    def test_title_demo_button_toggles_demo_setting_without_starting_run(self) -> None:
        app = GravityCourierApp()
        app.enter_title()
        app.audio = RecordingTitleAudio()  # type: ignore[assignment]
        x, y, width, height = title_demo_button_rect()
        app.pyxel = FakePyxelMouse(x + width // 2, y + height // 2, pressed=True)

        app.update()

        self.assertEqual(app.game_state, STATE_TITLE)
        self.assertTrue(app.title_demo_enabled)
        self.assertFalse(app.demo_mode)

    def test_title_mode_button_changes_selection_without_starting_run(self) -> None:
        app = GravityCourierApp()
        app.enter_title()
        x, y, width, height = title_mode_button_rect()
        app.pyxel = FakePyxelMouse(x + width // 2, y + height // 2, pressed=True)

        app.update()

        self.assertEqual(app.game_state, STATE_TITLE)
        self.assertEqual(app.course_mode_key, COURSE_MODE_HARD)
        self.assertEqual(app.course.mode.key, COURSE_MODE_NORMAL)

    def test_title_sound_button_reenables_title_bgm_without_starting_gameplay_bgm(self) -> None:
        app = GravityCourierApp()
        app.enter_title()
        app.audio = RecordingTitleAudio(enabled=False)  # type: ignore[assignment]
        x, y, width, height = title_sound_button_rect()
        app.pyxel = FakePyxelMouse(x + width // 2, y + height // 2, pressed=True)

        app.update()

        self.assertTrue(app.audio.enabled)  # type: ignore[attr-defined]
        self.assertIn("start_title_bgm", app.audio.events)  # type: ignore[attr-defined]
        self.assertNotIn("start_bgm", app.audio.events)  # type: ignore[attr-defined]

    def test_title_up_down_keys_move_menu_selection(self) -> None:
        app = GravityCourierApp()
        app.enter_title()
        app.pyxel = FakePyxelKeys(pressed_key=FakePyxelKeys.KEY_DOWN)

        app.update()

        self.assertEqual(app.title_menu_index, TITLE_MENU_MODE)

        app.pyxel = FakePyxelKeys(pressed_key=FakePyxelKeys.KEY_UP)
        app.update()

        self.assertEqual(app.title_menu_index, TITLE_MENU_START)

        app.pyxel = FakePyxelKeys(pressed_key=FakePyxelKeys.KEY_UP)
        app.update()

        self.assertEqual(app.title_menu_index, TITLE_MENU_SOUND)

    def test_title_left_right_activates_selected_mode_menu_item(self) -> None:
        app = GravityCourierApp()
        app.enter_title()
        app.title_menu_index = TITLE_MENU_MODE
        app.pyxel = FakePyxelKeys(pressed_key=FakePyxelKeys.KEY_RIGHT)

        app.update()

        self.assertEqual(app.game_state, STATE_TITLE)
        self.assertEqual(app.course_mode_key, COURSE_MODE_HARD)

    def test_title_left_right_toggles_selected_demo_menu_item(self) -> None:
        app = GravityCourierApp()
        app.enter_title()
        app.title_menu_index = TITLE_MENU_DEMO
        app.pyxel = FakePyxelKeys(pressed_key=FakePyxelKeys.KEY_RIGHT)

        app.update()

        self.assertEqual(app.game_state, STATE_TITLE)
        self.assertTrue(app.title_demo_enabled)
        self.assertFalse(app.demo_mode)

    def test_title_left_right_toggles_selected_sound_menu_item(self) -> None:
        app = GravityCourierApp()
        app.enter_title()
        app.title_menu_index = TITLE_MENU_SOUND
        app.audio = RecordingTitleAudio()  # type: ignore[assignment]
        app.pyxel = FakePyxelKeys(pressed_key=FakePyxelKeys.KEY_RIGHT)

        app.update()

        self.assertFalse(app.audio.enabled)  # type: ignore[attr-defined]
        self.assertIn("toggle", app.audio.events)  # type: ignore[attr-defined]

    def test_title_enter_only_works_on_start_menu_item(self) -> None:
        app = GravityCourierApp()
        app.enter_title()
        app.title_menu_index = TITLE_MENU_MODE
        app.pyxel = FakePyxelKeys(pressed_key=FakePyxelKeys.KEY_ENTER)

        app.update()

        self.assertEqual(app.game_state, STATE_TITLE)
        self.assertEqual(app.course_mode_key, COURSE_MODE_NORMAL)

        app.title_menu_index = TITLE_MENU_DEMO
        app.pyxel = FakePyxelKeys(pressed_key=FakePyxelKeys.KEY_ENTER)
        app.update()

        self.assertEqual(app.game_state, STATE_TITLE)
        self.assertFalse(app.title_demo_enabled)

        app.title_menu_index = TITLE_MENU_START
        app.pyxel = FakePyxelKeys(pressed_key=FakePyxelKeys.KEY_ENTER)
        app.update()

        self.assertEqual(app.game_state, STATE_PLAYING)

    def test_title_z_still_starts_from_any_menu_selection(self) -> None:
        app = GravityCourierApp()
        app.enter_title()
        app.title_menu_index = TITLE_MENU_SOUND
        app.pyxel = FakePyxelKeys(pressed_key=FakePyxelKeys.KEY_Z)

        app.update()

        self.assertEqual(app.game_state, STATE_PLAYING)
        self.assertFalse(app.demo_mode)

    def test_result_retry_button_rect_is_bottom_centered(self) -> None:
        x, y, width, height = result_retry_button_rect()
        hard_x, hard_y, hard_width, hard_height = result_retry_hard_button_rect()
        title_x, title_y, title_width, title_height = result_title_button_rect()

        self.assertLess(x, hard_x)
        self.assertGreater(hard_x + hard_width, WIDTH // 2)
        self.assertEqual(y, hard_y)
        self.assertEqual(height, hard_height)
        self.assertLess(height, 34)
        self.assertGreater(y, HEIGHT - 150)
        self.assertLessEqual(y + height, HEIGHT - 40)
        self.assertLessEqual(hard_x + hard_width, WIDTH)
        self.assertGreater(title_y, y + height)
        self.assertLessEqual(title_y - (y + height), 6)
        self.assertEqual(title_height, height)
        self.assertGreater(title_width, hard_width)
        self.assertEqual(title_x + title_width // 2, WIDTH // 2)
        self.assertGreater(title_y, y)
        self.assertLessEqual(title_y + title_height, HEIGHT - 40)

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

    def test_result_title_button_pressed_requires_click_inside_button(self) -> None:
        app = GravityCourierApp()
        x, y, width, height = result_title_button_rect()

        inside = FakePyxelMouse(x + width // 2, y + height // 2, pressed=True)
        outside = FakePyxelMouse(x - 1, y + height // 2, pressed=True)
        not_pressed = FakePyxelMouse(x + width // 2, y + height // 2, pressed=False)

        self.assertTrue(app._result_title_button_pressed(inside))
        self.assertFalse(app._result_title_button_pressed(outside))
        self.assertFalse(app._result_title_button_pressed(not_pressed))

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

    def test_result_title_button_returns_to_title_screen(self) -> None:
        app = GravityCourierApp()
        app.game_state = "result"
        app.demo_mode = True
        app.audio = RecordingTitleAudio()  # type: ignore[assignment]
        x, y, width, height = result_title_button_rect()
        app.pyxel = FakePyxelMouse(x + width // 2, y + height // 2, pressed=True)

        app.update()

        self.assertEqual(app.game_state, STATE_TITLE)
        self.assertFalse(app.demo_mode)
        self.assertIn("stop_bgm", app.audio.events)  # type: ignore[attr-defined]
        self.assertIn("start_title_bgm", app.audio.events)  # type: ignore[attr-defined]
