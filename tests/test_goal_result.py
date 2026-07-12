import math
import unittest

import _path  # noqa: F401

from gravity_courier.app import (
    GOAL_TEST_APPROACH_DISTANCE,
    PIXEL_FONT_3X5,
    RESULT_WELCOME_MESSAGE,
    RESULT_TEST_CREW_PRESETS,
    GravityCourierApp,
    STATE_CRASHED,
    STATE_PLAYING,
    STATE_RESULT,
    goal_test_button_rect,
    result_retry_hard_button_rect,
    result_retry_button_rect,
    result_title_button_rect,
)
from gravity_courier.constants import (
    COLOR_ALERT,
    COLOR_GRAVITY_WELL,
    COLOR_HUD,
    COLOR_TRAJECTORY,
    CREW_SCORE_VALUE,
    FINAL_GOAL_RADIUS,
    FINAL_GOAL_SPACING_Y,
    ROCKET_FUEL_MAX,
    WIDTH,
)
from gravity_courier.course import COURSE_MODE_HARD, COURSE_MODE_NORMAL, HARD_RANK_THRESHOLDS, NORMAL_RANK_THRESHOLDS
from gravity_courier.crew import CREW_PLANET_TYPES, initial_crew_count_by_type, total_joined_crew
from gravity_courier.entities import Planet, Vec2
from gravity_courier.goal import create_final_goal, journey_planet_progress, reached_final_goal
from gravity_courier.planet_types import (
    PLANET_TYPE_FOREST,
    PLANET_TYPE_IRON,
    PLANET_TYPE_ROCK,
    PLANET_TYPE_WATER,
    PLANET_TYPE_WIND,
)
from gravity_courier.resources import RESIDENT_RESOURCE_PATH, ResidentResourceState
from gravity_courier.result import (
    RESULT_DENSITY_CROWD,
    RESULT_DENSITY_DENSE,
    RESULT_DENSITY_NORMAL,
    build_result_summary,
    crew_bonus_for_count,
    crew_density_for_count,
    rank_for_score,
)
from gravity_courier.supply import SUPPLY_STATUS_COLLECTED, SupplyShipReservation


class RecordingPyxel:
    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple[int, ...]]] = []

    def line(self, *args: int) -> None:
        self.calls.append(("line", args))

    def rect(self, *args: int) -> None:
        self.calls.append(("rect", args))

    def rectb(self, *args: int) -> None:
        self.calls.append(("rectb", args))

    def circ(self, *args: int) -> None:
        self.calls.append(("circ", args))

    def blt(self, *args: int, **kwargs: int) -> None:
        self.calls.append(("blt", args))

    def pset(self, *args: int) -> None:
        self.calls.append(("pset", args))


class UpdatePyxel:
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
    MOUSE_BUTTON_LEFT = 12
    KEY_RETURN = 13
    KEY_ENTER = 14
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


class FinalGoalTest(unittest.TestCase):
    def test_final_goal_is_created_after_last_planet(self) -> None:
        planets = [
            Planet(position=Vec2(100.0, 0.0), mass=1.0, radius=20.0, gravity_well_radius=100.0),
            Planet(position=Vec2(200.0, -500.0), mass=1.0, radius=20.0, gravity_well_radius=100.0),
        ]

        goal = create_final_goal(planets)

        self.assertLess(goal.position.y, planets[-1].position.y)
        self.assertGreater(goal.arrival_radius, goal.radius)

    def test_final_goal_is_large_and_separated_from_last_planet(self) -> None:
        planets = [
            Planet(position=Vec2(200.0, -500.0), mass=1.0, radius=20.0, gravity_well_radius=100.0),
        ]

        goal = create_final_goal(planets)

        self.assertEqual(goal.radius, FINAL_GOAL_RADIUS)
        self.assertGreaterEqual(goal.radius, 120.0)
        self.assertEqual(planets[-1].position.y - goal.position.y, FINAL_GOAL_SPACING_Y)
        self.assertGreaterEqual(FINAL_GOAL_SPACING_Y, 500.0)

    def test_reached_final_goal_uses_arrival_radius(self) -> None:
        goal = create_final_goal([])

        self.assertTrue(reached_final_goal(goal.position, goal))
        self.assertFalse(reached_final_goal(goal.position + Vec2(goal.arrival_radius + 1.0, 0.0), goal))

    def test_journey_progress_is_monotonic_by_course_order(self) -> None:
        planets = [
            Planet(position=Vec2(100.0, 300.0), mass=1.0, radius=20.0, gravity_well_radius=80.0),
            Planet(position=Vec2(100.0, 0.0), mass=1.0, radius=20.0, gravity_well_radius=80.0),
            Planet(position=Vec2(100.0, -300.0), mass=1.0, radius=20.0, gravity_well_radius=80.0),
        ]

        progress = journey_planet_progress(50.0, planets, 0)
        self.assertEqual(progress, 1)
        self.assertEqual(journey_planet_progress(500.0, planets, progress), 1)
        self.assertEqual(journey_planet_progress(-400.0, planets, progress), 2)


class ResultSummaryTest(unittest.TestCase):
    def test_crew_bonus_uses_joined_crew_only(self) -> None:
        self.assertEqual(crew_bonus_for_count(7), 7 * CREW_SCORE_VALUE)

    def test_rank_thresholds(self) -> None:
        self.assertEqual(rank_for_score(90000), "S")
        self.assertEqual(rank_for_score(60000), "A")
        self.assertEqual(rank_for_score(30000), "B")
        self.assertEqual(rank_for_score(10000), "C")
        self.assertEqual(rank_for_score(9999), "D")

    def test_crew_density_boundaries(self) -> None:
        self.assertEqual(crew_density_for_count(50), RESULT_DENSITY_NORMAL)
        self.assertEqual(crew_density_for_count(51), RESULT_DENSITY_DENSE)
        self.assertEqual(crew_density_for_count(200), RESULT_DENSITY_DENSE)
        self.assertEqual(crew_density_for_count(201), RESULT_DENSITY_CROWD)

    def test_result_summary_uses_mode_specific_rank_thresholds(self) -> None:
        normal_summary = build_result_summary(
            run_score=60000,
            crew_count_by_type=initial_crew_count_by_type(),
            total_laps=0,
            supply_cargo_collected=0,
            hp_left=3,
            shield_left=0,
            fuel=50.0,
            rank_thresholds=NORMAL_RANK_THRESHOLDS,
        )
        hard_summary = build_result_summary(
            run_score=60000,
            crew_count_by_type=initial_crew_count_by_type(),
            total_laps=0,
            supply_cargo_collected=0,
            hp_left=3,
            shield_left=0,
            fuel=50.0,
            course_mode_key=COURSE_MODE_HARD,
            course_mode_label="Hard",
            rank_thresholds=HARD_RANK_THRESHOLDS,
        )

        self.assertEqual(normal_summary.rank, "S")
        self.assertEqual(hard_summary.rank, "A")
        self.assertEqual(hard_summary.course_mode_label, "Hard")

    def test_result_summary_includes_score_crew_and_resources(self) -> None:
        crew = initial_crew_count_by_type()
        crew[PLANET_TYPE_ROCK] = 3
        crew[PLANET_TYPE_WIND] = 2

        summary = build_result_summary(
            run_score=1200,
            crew_count_by_type=crew,
            total_laps=9,
            supply_cargo_collected=2,
            hp_left=2,
            shield_left=1,
            fuel=ROCKET_FUEL_MAX + 10,
        )

        self.assertEqual(summary.joined_crew_count, 5)
        self.assertEqual(summary.display_crew_count, 6)
        self.assertEqual(summary.crew_bonus, 5 * CREW_SCORE_VALUE)
        self.assertEqual(summary.final_score, 1200 + 5 * CREW_SCORE_VALUE)
        self.assertEqual(summary.total_laps, 9)
        self.assertEqual(summary.supply_cargo_collected, 2)
        self.assertEqual(summary.hp_left, 2)
        self.assertEqual(summary.shield_left, 1)
        self.assertEqual(summary.fuel_left, int(ROCKET_FUEL_MAX))
        self.assertEqual(summary.course_mode_key, COURSE_MODE_NORMAL)
        self.assertEqual(summary.course_mode_label, "Normal")


class AppGoalResultTest(unittest.TestCase):
    def test_final_goal_is_not_added_to_planets(self) -> None:
        app = GravityCourierApp()

        self.assertEqual(len(app.planets), 20)
        self.assertNotIn(app.final_goal.position, [planet.position for planet in app.planets])

    def test_app_can_toggle_to_hard_course_mode(self) -> None:
        app = GravityCourierApp()

        app._toggle_course_mode()

        self.assertEqual(app.course_mode_key, COURSE_MODE_HARD)
        self.assertEqual(app.course.mode.key, COURSE_MODE_HARD)
        self.assertEqual(len(app.planets), 35)

    def test_restart_preserves_selected_course_mode(self) -> None:
        app = GravityCourierApp()
        app._toggle_course_mode()

        app.restart()

        self.assertEqual(app.course_mode_key, COURSE_MODE_HARD)
        self.assertEqual(app.course.mode.key, COURSE_MODE_HARD)
        self.assertEqual(len(app.planets), 35)

    def test_reaching_final_goal_enters_result_state(self) -> None:
        app = GravityCourierApp()
        app.score = 500
        app.planet_lap_counts[0] = 2
        app.crew_count_by_type[PLANET_TYPE_ROCK] = 4
        app.supply_reservations = [
            SupplyShipReservation(
                reservation_id=1,
                planet_type=PLANET_TYPE_ROCK,
                source_planet_id=0,
                source_lap_count=3,
                remaining_gap_count=0,
                status=SUPPLY_STATUS_COLLECTED,
            )
        ]
        app.rocket.position = app.final_goal.position

        self.assertTrue(app._try_complete_final_goal())

        self.assertEqual(app.game_state, STATE_RESULT)
        self.assertFalse(app.rocket.crashed)
        self.assertIsNotNone(app.result_summary)
        assert app.result_summary is not None
        self.assertEqual(app.result_summary.run_score, 500)
        self.assertEqual(app.result_summary.joined_crew_count, 4)
        self.assertEqual(app.result_summary.supply_cargo_collected, 1)
        self.assertEqual(app.result_summary.course_mode_key, COURSE_MODE_NORMAL)

    def test_goal_test_assigns_deterministic_crew_boundaries(self) -> None:
        app = GravityCourierApp()
        observed: list[tuple[int, tuple[int, ...]]] = []

        for _ in RESULT_TEST_CREW_PRESETS:
            app._activate_goal_test()
            counts = tuple(app.crew_count_by_type[planet_type] for planet_type in CREW_PLANET_TYPES)
            observed.append((app.last_result_test_crew_count, counts))
            app._cycle_goal_test_preset()

        self.assertEqual([item[0] for item in observed], list(RESULT_TEST_CREW_PRESETS))
        self.assertEqual(sum(observed[0][1]), 12)
        self.assertEqual(observed[0][1], (3, 3, 2, 2, 2))
        self.assertEqual(observed[-1][1], (127, 127, 127, 127, 127))

    def test_goal_test_places_rocket_before_goal_without_immediate_result(self) -> None:
        app = GravityCourierApp()
        app._activate_goal_test()

        self.assertEqual(app.game_state, STATE_PLAYING)
        self.assertFalse(reached_final_goal(app.rocket.position, app.final_goal))
        self.assertLess(app.rocket.velocity.y, 0.0)
        self.assertGreater(
            app.rocket.position.distance_to(app.final_goal.position),
            app.final_goal.arrival_radius + GOAL_TEST_APPROACH_DISTANCE * 0.5,
        )
        self.assertTrue(math.isclose(app.rocket.position.x, app.final_goal.position.x))

        app.pyxel = UpdatePyxel()
        app.update()

        self.assertEqual(app.game_state, STATE_PLAYING)
        self.assertIsNone(app.result_summary)

        app.rocket.position = app.final_goal.position
        app.update()

        self.assertEqual(app.game_state, STATE_RESULT)
        self.assertIsNotNone(app.result_summary)
        assert app.result_summary is not None
        self.assertEqual(app.result_summary.joined_crew_count, RESULT_TEST_CREW_PRESETS[0])
        self.assertEqual(app.result_summary.course_mode_key, COURSE_MODE_NORMAL)
        self.assertGreater(app.result_summary.run_score, 0)

    def test_goal_test_uses_selected_hard_course_for_result(self) -> None:
        app = GravityCourierApp()
        app._toggle_course_mode()
        app._cycle_goal_test_preset()
        app._activate_goal_test()
        app.pyxel = UpdatePyxel()
        app.rocket.position = app.final_goal.position

        app.update()

        self.assertEqual(app.game_state, STATE_RESULT)
        self.assertIsNotNone(app.result_summary)
        assert app.result_summary is not None
        self.assertEqual(len(app.planets), 35)
        self.assertEqual(app.result_summary.course_mode_key, COURSE_MODE_HARD)
        self.assertEqual(app.result_summary.joined_crew_count, RESULT_TEST_CREW_PRESETS[1])

    def test_goal_test_keyboard_shortcut_only_cycles_preset_when_available(self) -> None:
        app = GravityCourierApp()
        app.pyxel = UpdatePyxel(pressed_key=UpdatePyxel.KEY_G)

        app.update()

        self.assertEqual(app.game_state, STATE_PLAYING)
        self.assertEqual(total_joined_crew(app.crew_count_by_type), 0)
        self.assertEqual(app.result_test_preset_index, 0)

        app.show_debug = True
        app.update()

        self.assertEqual(app.result_test_preset_index, 1)
        self.assertEqual(app.last_result_test_crew_count, 0)
        self.assertEqual(total_joined_crew(app.crew_count_by_type), 0)
        self.assertEqual(app.game_state, STATE_PLAYING)

    def test_goal_test_button_click_executes_selected_preset(self) -> None:
        app = GravityCourierApp()
        app.show_debug = True
        app._cycle_goal_test_preset()
        x, y, width, height = goal_test_button_rect()
        pyxel = UpdatePyxel(pressed_key=UpdatePyxel.MOUSE_BUTTON_LEFT)
        pyxel.mouse_x = x + width // 2
        pyxel.mouse_y = y + height // 2
        app.pyxel = pyxel

        app.update()

        self.assertEqual(app.last_result_test_crew_count, RESULT_TEST_CREW_PRESETS[1])
        self.assertEqual(total_joined_crew(app.crew_count_by_type), RESULT_TEST_CREW_PRESETS[1])
        self.assertEqual(app.game_state, STATE_PLAYING)
        self.assertFalse(reached_final_goal(app.rocket.position, app.final_goal))

    def test_goal_test_enter_executes_selected_preset_in_debug(self) -> None:
        app = GravityCourierApp()
        app.show_debug = True
        app._cycle_goal_test_preset()
        app.pyxel = UpdatePyxel(pressed_key=UpdatePyxel.KEY_ENTER)

        app.update()

        self.assertEqual(app.last_result_test_crew_count, RESULT_TEST_CREW_PRESETS[1])
        self.assertEqual(total_joined_crew(app.crew_count_by_type), RESULT_TEST_CREW_PRESETS[1])

    def test_demo_goal_test_button_click_cycles_without_executing(self) -> None:
        app = GravityCourierApp()
        app.demo_mode = True
        x, y, width, height = goal_test_button_rect()
        pyxel = UpdatePyxel(pressed_key=UpdatePyxel.MOUSE_BUTTON_LEFT)
        pyxel.mouse_x = x + width // 2
        pyxel.mouse_y = y + height // 2
        app.pyxel = pyxel

        app.update()

        self.assertEqual(app.result_test_preset_index, 1)
        self.assertEqual(app.last_result_test_crew_count, 0)
        self.assertEqual(total_joined_crew(app.crew_count_by_type), 0)
        self.assertEqual(app.game_state, STATE_PLAYING)

    def test_demo_goal_test_enter_cycles_without_executing(self) -> None:
        app = GravityCourierApp()
        app.demo_mode = True
        app.pyxel = UpdatePyxel(pressed_key=UpdatePyxel.KEY_ENTER)

        app.update()

        self.assertEqual(app.result_test_preset_index, 1)
        self.assertEqual(app.last_result_test_crew_count, 0)
        self.assertEqual(total_joined_crew(app.crew_count_by_type), 0)

    def test_demo_goal_test_button_horizontal_flick_cycles_preset(self) -> None:
        app = GravityCourierApp()
        app.demo_mode = True
        x, y, width, height = goal_test_button_rect()
        pyxel = UpdatePyxel(held_keys={UpdatePyxel.MOUSE_BUTTON_LEFT})
        pyxel.mouse_x = x + width // 2
        pyxel.mouse_y = y + height // 2

        self.assertFalse(app._goal_test_button_flicked(pyxel))
        pyxel.mouse_x += 30

        self.assertTrue(app._goal_test_button_flicked(pyxel))

    def test_journey_progress_display_starts_at_zero(self) -> None:
        app = GravityCourierApp()
        pyxel = RecordingPyxel()
        app.pyxel = pyxel
        records: list[tuple[int, int, str, int, int]] = []
        app._draw_text_scaled = (  # type: ignore[method-assign]
            lambda x, y, text, color, scale=2: records.append((x, y, text, color, scale))
        )
        app.highest_course_planet_index = 0

        app._draw_journey_progress()

        self.assertIn(("GOAL", COLOR_ALERT, 2), [(record[2], record[3], record[4]) for record in records])
        self.assertIn(("P 00/20", COLOR_HUD, 2), [(record[2], record[3], record[4]) for record in records])

    def test_journey_progress_bar_fills_at_last_zero_based_planet(self) -> None:
        app = GravityCourierApp()
        pyxel = RecordingPyxel()
        app.pyxel = pyxel
        app.highest_course_planet_index = len(app.planets) - 1

        app._draw_journey_progress()

        filled_bars = [
            args
            for name, args in pyxel.calls
            if name == "rect" and len(args) == 5 and args[0] == 152 and args[1] == 28
        ]
        self.assertEqual(filled_bars[-1][2], 108)

    def test_restart_resets_result_state(self) -> None:
        app = GravityCourierApp()
        app.rocket.position = app.final_goal.position
        app._try_complete_final_goal()

        app.restart()

        self.assertEqual(app.game_state, STATE_PLAYING)
        self.assertIsNone(app.result_summary)

    def test_crash_state_is_separate_from_result_state(self) -> None:
        app = GravityCourierApp()
        app.rocket.hp = 1

        app._apply_rocket_damage(1, "test")

        self.assertEqual(app.game_state, STATE_CRASHED)
        self.assertTrue(app.rocket.crashed)
        self.assertIsNone(app.result_summary)

    def test_result_confetti_draws_even_without_joined_crew(self) -> None:
        app = GravityCourierApp()
        pyxel = RecordingPyxel()
        app.pyxel = pyxel
        summary = build_result_summary(
            run_score=100,
            crew_count_by_type=initial_crew_count_by_type(),
            total_laps=3,
            supply_cargo_collected=0,
            hp_left=3,
            shield_left=0,
            fuel=50.0,
        )

        app._draw_result_confetti(summary)

        self.assertGreaterEqual(len(pyxel.calls), 36)
        self.assertIn("pset", {name for name, _args in pyxel.calls})
        self.assertIn("line", {name for name, _args in pyxel.calls})

    def test_result_title_draws_with_multiple_shimmer_colors(self) -> None:
        app = GravityCourierApp()
        pyxel = RecordingPyxel()
        app.pyxel = pyxel
        app.frame = 12
        app.result_summary = build_result_summary(
            run_score=100,
            crew_count_by_type=initial_crew_count_by_type(),
            total_laps=3,
            supply_cargo_collected=0,
            hp_left=3,
            shield_left=0,
            fuel=50.0,
        )

        app._draw_result_screen()

        title_colors = {
            args[4]
            for name, args in pyxel.calls
            if name == "rect" and len(args) == 5 and 48 <= args[1] <= 62 and args[2] == 3 and args[3] == 3
        }
        self.assertGreater(len(title_colors), 1)

    def test_result_title_shimmer_runs_in_reverse_character_order(self) -> None:
        app = GravityCourierApp()
        pyxel = RecordingPyxel()
        app.pyxel = pyxel
        app.frame = 12

        app._draw_text_scaled_shimmer(20, 40, "RE", scale=3)

        first_pixel_by_x: dict[int, int] = {}
        for name, args in pyxel.calls:
            if name == "rect" and len(args) == 5:
                first_pixel_by_x.setdefault(args[0], args[4])
        self.assertEqual(first_pixel_by_x[20], COLOR_TRAJECTORY)
        self.assertEqual(first_pixel_by_x[32], COLOR_HUD)

    def test_result_screen_draws_large_glittering_s_rank(self) -> None:
        app = GravityCourierApp()
        pyxel = RecordingPyxel()
        app.pyxel = pyxel
        app.frame = 12
        app.result_summary = build_result_summary(
            run_score=90000,
            crew_count_by_type=initial_crew_count_by_type(),
            total_laps=3,
            supply_cargo_collected=0,
            hp_left=3,
            shield_left=0,
            fuel=50.0,
        )

        app._draw_result_screen()

        large_s_pixels = [
            args
            for name, args in pyxel.calls
            if name == "rect" and len(args) == 5 and args[2] == 7 and args[3] == 7 and 68 <= args[1] <= 108
        ]
        glitter_lines = [
            args
            for name, args in pyxel.calls
            if name == "line" and len(args) == 5 and 72 <= args[1] <= 118 and 72 <= args[3] <= 118
        ]
        self.assertGreater(len(large_s_pixels), 0)
        self.assertGreater(len({args[4] for args in large_s_pixels}), 1)
        self.assertGreaterEqual(len(glitter_lines), 6)
        s_left = min(args[0] for args in large_s_pixels)
        s_right = max(args[0] + args[2] for args in large_s_pixels)
        s_top = min(args[1] for args in large_s_pixels)
        s_bottom = max(args[1] + args[3] for args in large_s_pixels)
        for x1, y1, x2, y2, _color in glitter_lines:
            self.assertTrue(x2 < s_left or x1 > s_right or y2 < s_top or y1 > s_bottom)

    def test_result_screen_draws_retry_button(self) -> None:
        app = GravityCourierApp()
        pyxel = RecordingPyxel()
        app.pyxel = pyxel
        app.result_summary = build_result_summary(
            run_score=100,
            crew_count_by_type=initial_crew_count_by_type(),
            total_laps=3,
            supply_cargo_collected=0,
            hp_left=3,
            shield_left=0,
            fuel=50.0,
        )

        app._draw_result_screen()

        x, y, width, height = result_retry_button_rect()
        hard_x, hard_y, hard_width, hard_height = result_retry_hard_button_rect()
        title_x, title_y, title_width, title_height = result_title_button_rect()
        self.assertIn(("rect", (x, y, width, height, 10)), pyxel.calls)
        self.assertIn(("rectb", (x, y, width, height, 7)), pyxel.calls)
        self.assertIn(("rect", (hard_x, hard_y, hard_width, hard_height, 10)), pyxel.calls)
        self.assertIn(("rectb", (hard_x, hard_y, hard_width, hard_height, 7)), pyxel.calls)
        self.assertIn(("rect", (title_x, title_y, title_width, title_height, 10)), pyxel.calls)
        self.assertIn(("rectb", (title_x, title_y, title_width, title_height, 7)), pyxel.calls)

    def test_result_screen_draws_selected_course_mode(self) -> None:
        app = GravityCourierApp()
        app.pyxel = RecordingPyxel()
        labels: list[str] = []
        values: list[str] = []
        app.result_summary = build_result_summary(
            run_score=100,
            crew_count_by_type=initial_crew_count_by_type(),
            total_laps=3,
            supply_cargo_collected=0,
            hp_left=3,
            shield_left=0,
            fuel=50.0,
            course_mode_key=COURSE_MODE_HARD,
            course_mode_label="Hard",
            rank_thresholds=HARD_RANK_THRESHOLDS,
        )
        app._draw_text_scaled = (  # type: ignore[method-assign]
            lambda x, y, text, color, scale=2: labels.append(text)
        )
        app._draw_text_right_aligned = (  # type: ignore[method-assign]
            lambda right_x, y, text, color, scale=2: values.append(text)
        )

        app._draw_result_screen()

        self.assertIn("MODE", labels)
        self.assertIn("HARD", values)

    def test_result_screen_underlines_summary_rows(self) -> None:
        app = GravityCourierApp()
        pyxel = RecordingPyxel()
        app.pyxel = pyxel
        app.result_summary = build_result_summary(
            run_score=100,
            crew_count_by_type=initial_crew_count_by_type(),
            total_laps=3,
            supply_cargo_collected=0,
            hp_left=3,
            shield_left=0,
            fuel=50.0,
        )

        app._draw_result_screen()

        underlines = [
            args
            for name, args in pyxel.calls
            if name == "line"
            and args[0] == 42
            and args[2] == WIDTH - 42
            and args[4] == COLOR_GRAVITY_WELL
        ]
        self.assertEqual(len(underlines), 9)
        self.assertEqual(len({args[1] for args in underlines}), 9)

    def test_result_screen_draws_earth_welcome_message(self) -> None:
        app = GravityCourierApp()
        app.pyxel = RecordingPyxel()
        jumping_texts: list[str] = []
        app.result_summary = build_result_summary(
            run_score=100,
            crew_count_by_type=initial_crew_count_by_type(),
            total_laps=3,
            supply_cargo_collected=0,
            hp_left=3,
            shield_left=0,
            fuel=50.0,
        )
        app._draw_text_centered_jumping = (  # type: ignore[method-assign]
            lambda center_x, y, text, color, scale=2: jumping_texts.append(text)
        )

        app._draw_result_screen()

        self.assertIn(RESULT_WELCOME_MESSAGE, jumping_texts)

    def test_result_welcome_message_characters_have_font_glyphs(self) -> None:
        missing_glyphs = {character for character in RESULT_WELCOME_MESSAGE if character not in PIXEL_FONT_3X5}

        self.assertEqual(missing_glyphs, set())

    def test_result_welcome_message_jumps_left_to_right(self) -> None:
        app = GravityCourierApp()
        app.frame = 9

        first_jump = app._result_welcome_jump_offset(0)
        fourth_jump = app._result_welcome_jump_offset(3)
        later_jump = app._result_welcome_jump_offset(10)

        self.assertEqual(first_jump, 7)
        self.assertEqual(fourth_jump, 0)
        self.assertEqual(later_jump, 0)

        app.frame = 18

        self.assertEqual(app._result_welcome_jump_offset(0), 0)
        self.assertEqual(app._result_welcome_jump_offset(3), 7)

    def test_result_hero_message_is_below_large_hero_sprite(self) -> None:
        app = GravityCourierApp()
        records: list[tuple[str, int, int, str | int]] = []
        app._draw_hero = lambda x, y, scale=1: records.append(("hero", x, y, scale))  # type: ignore[method-assign]
        app._draw_text_centered = (  # type: ignore[method-assign]
            lambda center_x, y, text, color, scale=2: records.append(("text", center_x, y, text))
        )
        summary = build_result_summary(
            run_score=100,
            crew_count_by_type=initial_crew_count_by_type(),
            total_laps=3,
            supply_cargo_collected=0,
            hp_left=3,
            shield_left=0,
            fuel=50.0,
        )

        app._draw_result_crew_crowd(summary)

        hero = next(record for record in records if record[0] == "hero")
        message = next(record for record in records if record[0] == "text" and record[3] == "HERO MADE IT HOME")
        self.assertGreaterEqual(message[2], hero[2] + 80)

    def test_result_character_jump_is_deterministic_and_staggered(self) -> None:
        app = GravityCourierApp()
        app.frame = 12

        first = app._result_character_jump(seed=0, amplitude=8)
        self.assertEqual(first, app._result_character_jump(seed=0, amplitude=8))
        self.assertNotEqual(first, app._result_character_jump(seed=3, amplitude=8))

    def test_result_crew_crowd_draws_resident_sprites_in_lower_area(self) -> None:
        app = GravityCourierApp()
        pyxel = RecordingPyxel()
        app.pyxel = pyxel
        app.resident_resources = ResidentResourceState(
            path=RESIDENT_RESOURCE_PATH,
            resource_loaded=True,
            hero_sprite_available=True,
            resident_sprite_available=True,
        )
        app.crew_count_by_type[PLANET_TYPE_WIND] = 8
        app.crew_count_by_type[PLANET_TYPE_ROCK] = 6
        summary = build_result_summary(
            run_score=100,
            crew_count_by_type=app.crew_count_by_type,
            total_laps=3,
            supply_cargo_collected=2,
            hp_left=3,
            shield_left=0,
            fuel=50.0,
        )

        app._draw_result_crew_crowd(summary)

        blt_calls = [args for name, args in pyxel.calls if name == "blt"]
        self.assertGreaterEqual(len(blt_calls), 10)
        crew_calls = [args for args in blt_calls if args[1] >= 360]
        self.assertGreaterEqual(len(crew_calls), 10)
        self.assertTrue(all(20 <= args[0] <= 341 for args in crew_calls))
        self.assertGreater(len({args[1] for args in crew_calls}), 8)

    def test_result_crowd_visible_counts_preserve_species_ratio_at_max_crew(self) -> None:
        app = GravityCourierApp()
        for planet_type in CREW_PLANET_TYPES:
            app.crew_count_by_type[planet_type] = 127
        summary = build_result_summary(
            run_score=100,
            crew_count_by_type=app.crew_count_by_type,
            total_laps=3,
            supply_cargo_collected=2,
            hp_left=3,
            shield_left=0,
            fuel=50.0,
        )

        visible_counts = app._result_crowd_visible_counts(summary)

        self.assertEqual(sum(visible_counts.values()), 44)
        self.assertLessEqual(max(visible_counts.values()) - min(visible_counts.values()), 1)

    def test_result_crowd_visible_counts_keep_dominant_species_dominant(self) -> None:
        app = GravityCourierApp()
        app.crew_count_by_type[PLANET_TYPE_WIND] = 100
        app.crew_count_by_type[PLANET_TYPE_IRON] = 10
        app.crew_count_by_type[PLANET_TYPE_WATER] = 10
        app.crew_count_by_type[PLANET_TYPE_FOREST] = 10
        app.crew_count_by_type[PLANET_TYPE_ROCK] = 10
        summary = build_result_summary(
            run_score=100,
            crew_count_by_type=app.crew_count_by_type,
            total_laps=3,
            supply_cargo_collected=2,
            hp_left=3,
            shield_left=0,
            fuel=50.0,
        )

        visible_counts = app._result_crowd_visible_counts(summary)

        self.assertGreater(visible_counts[PLANET_TYPE_WIND], visible_counts[PLANET_TYPE_ROCK])
        self.assertEqual(sum(visible_counts.values()), app._result_crowd_visible_limit(summary))

    def test_result_crowd_positions_spread_max_crew_across_lower_area(self) -> None:
        app = GravityCourierApp()
        for planet_type in CREW_PLANET_TYPES:
            app.crew_count_by_type[planet_type] = 127
        summary = build_result_summary(
            run_score=100,
            crew_count_by_type=app.crew_count_by_type,
            total_laps=3,
            supply_cargo_collected=2,
            hp_left=3,
            shield_left=0,
            fuel=50.0,
        )
        members = app._result_crowd_members(summary)

        positions = [
            app._result_crowd_position(index, planet_type, crew_index, len(members))
            for index, (planet_type, crew_index) in enumerate(members)
        ]

        self.assertEqual(len(positions), 44)
        self.assertTrue(all(24 <= x <= 337 and 392 <= y <= 734 for x, y in positions))
        self.assertGreater(max(x for x, _y in positions) - min(x for x, _y in positions), 250)
        self.assertGreater(max(y for _x, y in positions) - min(y for _x, y in positions), 260)
        self.assertGreaterEqual(len({x // 40 for x, _y in positions}), 7)
        self.assertGreaterEqual(len({y // 44 for _x, y in positions}), 7)

    def test_result_crew_sprites_draw_without_flip_animation(self) -> None:
        app = GravityCourierApp()
        pyxel = RecordingPyxel()
        app.pyxel = pyxel
        app.frame = 16
        app.resident_resources = ResidentResourceState(
            path=RESIDENT_RESOURCE_PATH,
            resource_loaded=True,
            hero_sprite_available=True,
            resident_sprite_available=True,
        )
        app.crew_count_by_type[PLANET_TYPE_WIND] = 10
        summary = build_result_summary(
            run_score=100,
            crew_count_by_type=app.crew_count_by_type,
            total_laps=3,
            supply_cargo_collected=2,
            hp_left=3,
            shield_left=0,
            fuel=50.0,
        )

        app._draw_result_crew_crowd(summary)

        crew_calls = [args for name, args in pyxel.calls if name == "blt" and args[1] >= 360]
        widths = [args[5] for args in crew_calls]
        self.assertGreaterEqual(len(crew_calls), 10)
        self.assertTrue(all(width == 32 for width in widths))
        self.assertTrue(all(args[3] == 0 for args in crew_calls))

    def test_result_rock_crew_sometimes_emits_floating_hearts(self) -> None:
        app = GravityCourierApp()
        pyxel = RecordingPyxel()
        app.pyxel = pyxel
        app.frame = 0

        app._draw_result_crew_member(PLANET_TYPE_ROCK, 50, 420, seed=0)

        heart_pixels = [
            args
            for name, args in pyxel.calls
            if name == "rect" and len(args) == 5 and args[2:4] == (2, 2) and args[4] == 8
        ]
        self.assertGreater(len(heart_pixels), 0)

    def test_result_hearts_are_rock_only(self) -> None:
        app = GravityCourierApp()
        pyxel = RecordingPyxel()
        app.pyxel = pyxel
        app.frame = 0

        app._draw_result_crew_member(PLANET_TYPE_WIND, 50, 420, seed=0)

        heart_pixels = [
            args
            for name, args in pyxel.calls
            if name == "rect" and len(args) == 5 and args[2:4] == (2, 2) and args[4] == 8
        ]
        self.assertEqual(heart_pixels, [])
