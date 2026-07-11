import math
import unittest

from dataclasses import replace

import _path  # noqa: F401

from gravity_courier.app import (
    GravityCourierApp,
    choose_demo_pickup_command,
    choose_demo_command,
    choose_demo_supply_command,
    create_initial_planets,
    demo_orbit_minimum_safe_radius,
    demo_orbit_target_radius,
    demo_orbit_target_ratio,
    find_next_demo_planet_index,
    nearest_demo_orbit_planet,
    orbit_track_display_radius,
)
from gravity_courier.constants import (
    DEMO_MIN_SPEED,
    DEMO_ORBIT_MAX_SPEED_MARGIN,
    DEMO_ORBIT_MIN_SPEED,
    DEMO_ORBIT_MIN_RADIUS_RATIO,
    DEMO_ORBIT_RADIUS_RATIO,
    DEMO_ORBIT_SEARCH_RATIO,
    DEMO_ORBIT_SPEED_MARGIN_SCALE,
    DEMO_ORBIT_LONG_TURNS,
    DEMO_ORBIT_TURNS,
    ORBIT_ASSIST_INFLUENCE_RATIO,
)
from gravity_courier.entities import Rocket, Vec2
from gravity_courier.physics import check_planet_collision, nearest_orbit_planet, step_rocket
from gravity_courier.planet_types import PLANET_TYPE_ROCK
from gravity_courier.supply import (
    SUPPLY_STATUS_SPAWNED,
    create_supply_reservation,
    make_supply_ship_from_reservation,
)
from gravity_courier.interplanet_objects import make_supply_item


class DemoModeTest(unittest.TestCase):
    def test_find_next_demo_planet_selects_nearest_planet_above_rocket(self) -> None:
        planets = create_initial_planets()
        rocket = Rocket(position=Vec2(196.5, 700.0), velocity=Vec2(0.0, -2.0))

        index = find_next_demo_planet_index(rocket, planets)

        self.assertEqual(index, 0)

    def test_choose_demo_command_points_toward_a_pass_offset(self) -> None:
        planets = create_initial_planets()
        rocket = Rocket(position=Vec2(196.5, 700.0), velocity=Vec2(0.0, -2.0))

        command = choose_demo_command(rocket, planets)

        self.assertIsNotNone(command.target_index)
        self.assertGreater(command.lateral_input, 0.0)
        self.assertTrue(command.boost)

    def test_choose_demo_command_brakes_when_too_fast(self) -> None:
        planets = create_initial_planets()
        rocket = Rocket(position=Vec2(196.5, 700.0), velocity=Vec2(0.0, -8.0))

        command = choose_demo_command(rocket, planets)

        self.assertTrue(command.brake)

    def test_choose_demo_command_boosts_when_below_min_speed(self) -> None:
        planets = create_initial_planets()
        rocket = Rocket(position=Vec2(196.5, 700.0), velocity=Vec2(0.0, -0.8))

        command = choose_demo_command(rocket, planets)

        self.assertTrue(command.boost)

    def test_demo_min_speed_floor_keeps_demo_moving(self) -> None:
        self.assertGreaterEqual(DEMO_MIN_SPEED, 3.0)

    def test_choose_demo_supply_command_targets_waiting_supply_ship(self) -> None:
        reservation = create_supply_reservation(1, PLANET_TYPE_ROCK, 0, 3)
        ship = replace(
            make_supply_ship_from_reservation(reservation, y=420.0, direction=1),
            pos=Vec2(260.0, 420.0),
            vel=Vec2(),
            warning_timer=0,
            stationary=True,
        )
        rocket = Rocket(position=Vec2(190.0, 520.0), velocity=Vec2(0.0, -2.0))

        command = choose_demo_supply_command(rocket, [ship])

        self.assertIsNotNone(command)
        assert command is not None
        self.assertTrue(command.supply_target)
        self.assertEqual(command.target_x, ship.cargo_pos.x)
        self.assertEqual(command.target_y, ship.cargo_pos.y)
        self.assertGreater(command.lateral_input, 0.0)

    def test_choose_demo_pickup_command_targets_supply_ship(self) -> None:
        far_ship = replace(
            make_supply_ship_from_reservation(create_supply_reservation(1, PLANET_TYPE_ROCK, 0, 3), y=240.0, direction=1),
            pos=Vec2(320.0, 240.0),
            warning_timer=0,
            stationary=True,
        )
        rocket = Rocket(position=Vec2(130.0, 520.0), velocity=Vec2(0.0, -2.0))

        command = choose_demo_pickup_command(rocket, [far_ship])

        self.assertIsNotNone(command)
        assert command is not None
        self.assertEqual(command.target_x, far_ship.cargo_pos.x)
        self.assertEqual(command.target_y, far_ship.cargo_pos.y)

    def test_choose_demo_pickup_command_returns_none_without_supply_ship(self) -> None:
        rocket = Rocket(position=Vec2(130.0, 520.0), velocity=Vec2(0.0, -2.0))

        command = choose_demo_pickup_command(rocket, [])

        self.assertIsNone(command)

    def test_demo_supply_command_steers_toward_supply_ship(self) -> None:
        app = GravityCourierApp()
        app.rocket.position = Vec2(120.0, 520.0)
        app.rocket.velocity = Vec2(0.0, -2.0)
        ship = replace(
            make_supply_ship_from_reservation(create_supply_reservation(1, PLANET_TYPE_ROCK, 0, 3), 420.0, 1),
            pos=Vec2(280.0, 420.0),
            warning_timer=0,
            stationary=True,
        )
        command = choose_demo_supply_command(app.rocket, [ship])

        assert command is not None
        app._apply_demo_command(command)

        self.assertGreater(app.rocket.velocity.x, 0.0)

    def test_demo_command_applies_min_speed_assist(self) -> None:
        app = GravityCourierApp()
        app.rocket.velocity = Vec2(0.0, -0.7)
        before_speed = app.rocket.velocity.length()

        app._apply_demo_command(choose_demo_command(app.rocket, app.planets))

        self.assertGreater(app.rocket.velocity.length(), before_speed)
        self.assertLess(app.rocket.velocity.length(), DEMO_MIN_SPEED)
        self.assertTrue(app.thrusting)

    def test_demo_update_continues_orbit_with_recovery_item_present(self) -> None:
        class FakePyxel:
            KEY_ESCAPE = 1
            KEY_R = 2
            KEY_SPACE = 3
            KEY_D = 4
            KEY_M = 5
            MOUSE_BUTTON_LEFT = 6
            mouse_x = 0
            mouse_y = 0

            def btnp(self, _key: int) -> bool:
                return False

            def btn(self, _key: int) -> bool:
                return False

            def quit(self) -> None:
                pass

        app = GravityCourierApp()
        app.pyxel = FakePyxel()
        app.demo_mode = True
        planet = app.planets[0]
        radius = demo_orbit_target_radius(planet, app.rocket)
        app.rocket.position = planet.position + Vec2(0.0, -radius)
        app.rocket.velocity = Vec2(0.0, -2.0)
        app.interplanet_objects = [
            make_supply_item(1, Vec2(app.rocket.position.x + 160.0, app.rocket.position.y - 80.0))
        ]

        app.update()

        self.assertEqual(app.demo_orbit_index, 0)

    def test_demo_orbit_search_extends_to_gravity_well_edge(self) -> None:
        app = GravityCourierApp()
        planet = app.planets[0]
        distance = planet.gravity_well_radius * ((ORBIT_ASSIST_INFLUENCE_RATIO + DEMO_ORBIT_SEARCH_RATIO) * 0.5)
        app.rocket.position = planet.position + Vec2(0.0, -distance)

        self.assertIs(nearest_orbit_planet(app.rocket, app.planets), None)
        self.assertIs(nearest_demo_orbit_planet(app.rocket, app.planets), planet)

    def test_demo_update_uses_wide_orbit_search_with_recovery_item_present(self) -> None:
        class FakePyxel:
            KEY_ESCAPE = 1
            KEY_R = 2
            KEY_SPACE = 3
            KEY_D = 4
            KEY_M = 5
            MOUSE_BUTTON_LEFT = 6
            mouse_x = 0
            mouse_y = 0

            def btnp(self, _key: int) -> bool:
                return False

            def btn(self, _key: int) -> bool:
                return False

            def quit(self) -> None:
                pass

        app = GravityCourierApp()
        app.pyxel = FakePyxel()
        app.demo_mode = True
        planet = app.planets[0]
        distance = planet.gravity_well_radius * ((ORBIT_ASSIST_INFLUENCE_RATIO + DEMO_ORBIT_SEARCH_RATIO) * 0.5)
        app.rocket.position = planet.position + Vec2(0.0, -distance)
        app.rocket.velocity = Vec2(0.0, -2.0)
        app.interplanet_objects = [
            make_supply_item(1, Vec2(app.rocket.position.x + 160.0, app.rocket.position.y - 80.0))
        ]

        app.update()

        self.assertEqual(app.demo_orbit_index, 0)

    def test_demo_route_avoids_early_planet_collisions(self) -> None:
        app = GravityCourierApp()

        for _ in range(600):
            app._update_planets()
            command = choose_demo_command(app.rocket, app.planets)
            app._apply_demo_command(command)
            app.rocket = step_rocket(app.rocket, app.planets)

            self.assertFalse(check_planet_collision(app.rocket.position, app.planets))

    def test_demo_orbit_can_complete_several_planet_loops(self) -> None:
        app = GravityCourierApp()
        orbit_planet = app.planets[0]
        app.rocket.position = orbit_planet.position + Vec2(0.0, -demo_orbit_target_radius(orbit_planet, app.rocket))
        app.rocket.velocity = orbit_planet.velocity + Vec2(2.7, 0.0)

        for _ in range(820):
            app._update_planets()
            orbit_planet = app.planets[0]
            app._apply_demo_orbit(orbit_planet, 0)
            app.rocket = step_rocket(app.rocket, app.planets)
            app._apply_orbit_assist(strength=0.07)
            app._repel_demo_from_completed_planets()
            app._sync_angle_to_velocity()
            app._update_demo_orbit_progress()
            if app.demo_orbit_done_indices:
                break

        self.assertIn(0, app.demo_orbit_done_indices)

    def test_demo_orbit_uses_higher_minimum_speed(self) -> None:
        app = GravityCourierApp()
        orbit_planet = app.planets[0]
        app.rocket.position = orbit_planet.position + Vec2(0.0, -demo_orbit_target_radius(orbit_planet, app.rocket))
        app.rocket.velocity = orbit_planet.velocity + Vec2(0.8, 0.0)

        app._apply_demo_orbit(orbit_planet, 0)

        relative_speed = (app.rocket.velocity - orbit_planet.velocity).length()
        self.assertGreater(relative_speed, 1.2)
        self.assertGreaterEqual(DEMO_ORBIT_MIN_SPEED, 3.0)

    def test_demo_orbit_targets_three_or_four_turns(self) -> None:
        app = GravityCourierApp()

        self.assertEqual(app._demo_orbit_turn_target(0), DEMO_ORBIT_TURNS)
        self.assertEqual(app._demo_orbit_turn_target(1), DEMO_ORBIT_TURNS)
        self.assertEqual(app._demo_orbit_turn_target(2), DEMO_ORBIT_LONG_TURNS)
        self.assertGreaterEqual(DEMO_ORBIT_TURNS, 3.0)
        self.assertEqual(DEMO_ORBIT_LONG_TURNS, 4.0)

    def test_demo_orbit_lap_label_shows_third_lap(self) -> None:
        app = GravityCourierApp()
        app.demo_mode = True
        app.demo_orbit_index = 0
        app.demo_orbit_turns = 3.1

        self.assertEqual(app._orbit_lap_label_for_planet(0), "3+")

    def test_demo_orbit_lap_label_starts_at_zero(self) -> None:
        app = GravityCourierApp()
        app.demo_mode = True
        app.demo_orbit_index = 0
        app.demo_orbit_turns = 0.4

        self.assertEqual(app._orbit_lap_label_for_planet(0), "0")

    def test_demo_orbit_lap_label_shows_completed_laps(self) -> None:
        app = GravityCourierApp()
        app.demo_mode = True
        app.demo_orbit_index = 0
        app.demo_orbit_turns = 2.1

        self.assertEqual(app._orbit_lap_label_for_planet(0), "2")

    def test_demo_orbit_lap_completion_triggers_cutin(self) -> None:
        app = GravityCourierApp()
        planet = app.planets[0]
        radius = demo_orbit_target_radius(planet, app.rocket)
        app.demo_mode = True
        app.demo_orbit_index = 0
        app.demo_orbit_prev_angle = 0.0
        app.demo_orbit_turns = 0.95
        app.rocket.position = planet.position + Vec2(math.cos(0.4) * radius, math.sin(0.4) * radius)

        app._update_demo_orbit_progress()

        self.assertEqual(app.planet_lap_counts[0], 1)
        self.assertEqual(app.last_lap_event_planet_index, 0)
        self.assertTrue(app.cutin.active)

    def test_demo_transfer_advances_supply_reservations(self) -> None:
        app = GravityCourierApp()
        planet = app.planets[0]
        radius = demo_orbit_target_radius(planet, app.rocket)
        reservation = create_supply_reservation(1, planet.planet_type, 0, 3)
        app.supply_reservations = [replace(reservation, remaining_gap_count=1)]
        app.demo_mode = True
        app.demo_orbit_index = 0
        app.demo_orbit_prev_angle = 0.0
        app.demo_orbit_turns = app._demo_orbit_turn_target(0) - 0.01
        app.rocket.position = planet.position + Vec2(math.cos(0.4) * radius, math.sin(0.4) * radius)

        app._update_demo_orbit_progress()
        app._update_supply_ships()

        self.assertEqual(app.supply_reservations[0].status, SUPPLY_STATUS_SPAWNED)
        self.assertEqual(len(app.supply_ships), 1)
        self.assertTrue(app.supply_ships[0].stationary)

    def test_demo_orbit_target_radius_stays_inside_orbit_limit(self) -> None:
        planets = create_initial_planets()
        rocket = Rocket(position=Vec2(196.5, 700.0), velocity=Vec2(0.0, -3.0))

        for planet in planets[:10]:
            self.assertLess(demo_orbit_target_radius(planet, rocket), planet.gravity_well_radius)

    def test_orbit_track_display_radius_stays_on_visual_track_radius(self) -> None:
        planet = create_initial_planets()[0]

        self.assertEqual(
            orbit_track_display_radius(planet),
            max(planet.radius + 42.0, planet.gravity_well_radius * 0.58),
        )

    def test_demo_orbit_target_radius_is_inside_visual_orbit_track_radius(self) -> None:
        planets = create_initial_planets()
        rocket = Rocket(position=Vec2(196.5, 700.0), velocity=Vec2(0.0, -3.0))

        for planet in planets[:10]:
            self.assertLess(demo_orbit_target_radius(planet, rocket), orbit_track_display_radius(planet))
            self.assertLessEqual(demo_orbit_target_radius(planet, rocket), planet.radius + 24.0)

    def test_demo_orbit_target_radius_respects_collision_safe_minimum(self) -> None:
        planet = create_initial_planets()[0]
        rocket = Rocket(position=Vec2(196.5, 700.0), velocity=Vec2(0.0, -40.0))

        self.assertGreaterEqual(demo_orbit_target_radius(planet, rocket), demo_orbit_minimum_safe_radius(planet))

    def test_demo_orbit_target_radius_does_not_expand_at_higher_speed(self) -> None:
        planet = create_initial_planets()[0]
        slow_rocket = Rocket(position=Vec2(), velocity=Vec2(0.0, -1.0))
        fast_rocket = Rocket(position=Vec2(), velocity=Vec2(0.0, -8.0))

        self.assertLessEqual(demo_orbit_target_radius(planet, fast_rocket), demo_orbit_target_radius(planet, slow_rocket))

    def test_demo_orbit_assist_uses_inner_demo_target_radius(self) -> None:
        app = GravityCourierApp()
        planet = app.planets[0]
        visual_track_radius = orbit_track_display_radius(planet)
        app.planets = [planet]
        app.demo_mode = True
        app.demo_orbit_index = 0
        app.rocket.position = planet.position + Vec2(visual_track_radius, 0.0)
        app.rocket.velocity = planet.velocity + Vec2(0.0, 2.75)

        app._apply_orbit_assist(strength=1.0)

        self.assertLess((app.rocket.velocity - planet.velocity).x, 0.0)

    def test_demo_orbit_guidance_pulls_strongly_toward_inner_orbit(self) -> None:
        app = GravityCourierApp()
        planet = app.planets[0]
        visual_track_radius = orbit_track_display_radius(planet)
        app.rocket.position = planet.position + Vec2(visual_track_radius, 0.0)
        app.rocket.velocity = planet.velocity + Vec2(0.0, 3.1)

        app._apply_demo_orbit(planet, 0)

        self.assertLess((app.rocket.velocity - planet.velocity).x, -0.35)

    def test_demo_transfer_ready_hint_uses_current_demo_orbit_planet(self) -> None:
        app = GravityCourierApp()
        app.demo_mode = True
        app.demo_orbit_index = 1
        app.active_orbit_planet_index = 0
        app.planet_lap_counts[0] = 3
        app.planet_lap_counts[1] = 1

        self.assertEqual(app._transfer_ready_hint_planet_index(), 1)

    def test_demo_orbit_target_ratio_clamps_within_configured_bounds(self) -> None:
        self.assertEqual(demo_orbit_target_ratio(0.0), DEMO_ORBIT_RADIUS_RATIO)
        self.assertEqual(demo_orbit_target_ratio(1000.0), DEMO_ORBIT_MIN_RADIUS_RATIO)

        medium_speed = 5.0
        expected_ratio = DEMO_ORBIT_RADIUS_RATIO - min(
            DEMO_ORBIT_MAX_SPEED_MARGIN,
            medium_speed * DEMO_ORBIT_SPEED_MARGIN_SCALE,
        )
        self.assertEqual(demo_orbit_target_ratio(medium_speed), expected_ratio)

    def test_scaled_text_width_uses_visible_pixel_font_width(self) -> None:
        app = GravityCourierApp()

        self.assertEqual(app._scaled_text_width("1", 4), 12)
        self.assertEqual(app._scaled_text_width("3+", 4), 28)

    def test_demo_boost_consumes_fuel(self) -> None:
        app = GravityCourierApp()
        starting_fuel = app.rocket.fuel
        command = choose_demo_command(app.rocket, app.planets)

        app._apply_demo_command(command)

        self.assertLess(app.rocket.fuel, starting_fuel)
