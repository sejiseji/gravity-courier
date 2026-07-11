import unittest

import _path  # noqa: F401

from gravity_courier.app import (
    GravityCourierApp,
    OrbitProgress,
    find_forward_destination_planet_index,
    swingby_exit_velocity,
)
from gravity_courier.constants import ASSIST_EXIT_MIN_SPEED, ASSIST_ORBIT_COOLDOWN_FRAMES
from gravity_courier.entities import Planet, Rocket, Vec2


class SwingbyExitTest(unittest.TestCase):
    def test_swingby_exit_velocity_adds_speed_and_radial_escape(self) -> None:
        planet = Planet(
            position=Vec2(0.0, 0.0),
            mass=3000.0,
            radius=20.0,
            gravity_well_radius=120.0,
        )
        rocket = Rocket(position=Vec2(80.0, 0.0), velocity=Vec2(0.0, -2.5))

        exit_velocity = swingby_exit_velocity(rocket, planet)

        self.assertGreater(exit_velocity.length(), rocket.velocity.length())
        self.assertGreater(exit_velocity.x, rocket.velocity.x)

    def test_swingby_exit_velocity_guarantees_minimum_transfer_speed(self) -> None:
        planet = Planet(
            position=Vec2(0.0, 0.0),
            mass=3000.0,
            radius=20.0,
            gravity_well_radius=120.0,
        )
        rocket = Rocket(position=Vec2(80.0, 0.0), velocity=Vec2(0.0, -0.2))

        exit_velocity = swingby_exit_velocity(rocket, planet)

        self.assertGreaterEqual(exit_velocity.length(), ASSIST_EXIT_MIN_SPEED - 0.0001)

    def test_orbit_assist_skips_planet_during_exit_cooldown(self) -> None:
        app = GravityCourierApp()
        app.rocket.position = Vec2(80.0, 0.0)
        app.rocket.velocity = Vec2(0.0, -2.5)
        app.planets = [
            Planet(
                position=Vec2(0.0, 0.0),
                mass=3000.0,
                radius=20.0,
                gravity_well_radius=120.0,
            )
        ]
        app.assist_orbit_cooldowns = [ASSIST_ORBIT_COOLDOWN_FRAMES]

        app._apply_orbit_assist(strength=1.0)

        self.assertEqual(app.rocket.velocity, Vec2(0.0, -2.5))

    def test_forward_destination_requires_planet_ahead_of_velocity(self) -> None:
        current = Planet(
            position=Vec2(0.0, 0.0),
            mass=3000.0,
            radius=20.0,
            gravity_well_radius=120.0,
        )
        ahead = Planet(
            position=Vec2(190.0, -120.0),
            mass=3000.0,
            radius=20.0,
            gravity_well_radius=120.0,
        )
        behind = Planet(
            position=Vec2(70.0, 120.0),
            mass=3000.0,
            radius=20.0,
            gravity_well_radius=120.0,
        )
        rocket = Rocket(position=Vec2(130.0, 0.0), velocity=Vec2(2.0, 0.0))

        upward_rocket = Rocket(position=Vec2(130.0, 0.0), velocity=Vec2(1.0, -2.0))

        self.assertEqual(find_forward_destination_planet_index(upward_rocket, [current, ahead], 0), 1)
        self.assertIsNone(find_forward_destination_planet_index(rocket, [current, ahead], 0))
        self.assertIsNone(find_forward_destination_planet_index(upward_rocket, [current, behind], 0))

    def test_forward_destination_requires_planet_above_rocket(self) -> None:
        current = Planet(
            position=Vec2(0.0, 0.0),
            mass=3000.0,
            radius=20.0,
            gravity_well_radius=120.0,
        )
        lower_ahead = Planet(
            position=Vec2(130.0, 100.0),
            mass=3000.0,
            radius=20.0,
            gravity_well_radius=120.0,
        )
        same_height_ahead = Planet(
            position=Vec2(130.0, 0.0),
            mass=3000.0,
            radius=20.0,
            gravity_well_radius=120.0,
        )
        rocket = Rocket(position=Vec2(130.0, 0.0), velocity=Vec2(0.0, -2.0))

        self.assertIsNone(find_forward_destination_planet_index(rocket, [current, lower_ahead], 0))
        self.assertIsNone(find_forward_destination_planet_index(rocket, [current, same_height_ahead], 0))

    def test_forward_destination_rejects_sideways_upper_planet(self) -> None:
        current = Planet(
            position=Vec2(0.0, 0.0),
            mass=3000.0,
            radius=20.0,
            gravity_well_radius=120.0,
        )
        mostly_sideways = Planet(
            position=Vec2(180.0, -120.0),
            mass=3000.0,
            radius=20.0,
            gravity_well_radius=120.0,
        )
        rocket = Rocket(position=Vec2(130.0, 0.0), velocity=Vec2(0.0, -2.0))

        self.assertIsNone(find_forward_destination_planet_index(rocket, [current, mostly_sideways], 0))

    def test_forward_destination_prefers_nearest_upper_planet_not_next_next(self) -> None:
        current = Planet(
            position=Vec2(0.0, 0.0),
            mass=3000.0,
            radius=20.0,
            gravity_well_radius=120.0,
        )
        next_planet = Planet(
            position=Vec2(130.0, -120.0),
            mass=3000.0,
            radius=20.0,
            gravity_well_radius=120.0,
        )
        next_next_planet = Planet(
            position=Vec2(130.0, -320.0),
            mass=3000.0,
            radius=20.0,
            gravity_well_radius=120.0,
        )
        rocket = Rocket(position=Vec2(130.0, 0.0), velocity=Vec2(0.0, -2.0))

        self.assertEqual(
            find_forward_destination_planet_index(
                rocket,
                [current, next_next_planet, next_planet],
                0,
            ),
            2,
        )

    def test_orbit_transfer_boosts_when_visit_is_ready(self) -> None:
        app = GravityCourierApp()
        current = Planet(
            position=Vec2(0.0, 0.0),
            mass=3000.0,
            radius=20.0,
            gravity_well_radius=180.0,
        )
        ahead = Planet(
            position=Vec2(0.0, -320.0),
            mass=3000.0,
            radius=20.0,
            gravity_well_radius=120.0,
        )
        app.planets = [current, ahead]
        app.assist_orbit_cooldowns = [0, 0]
        app.orbit_progress[0] = OrbitProgress(turns=1.05, visit_laps=1, in_orbit=True, transfer_ready=True)
        app.active_orbit_planet_index = 0
        app.rocket.position = Vec2(0.0, -190.0)
        app.rocket.velocity = Vec2(0.0, -2.0)

        app._try_orbit_transfer()

        self.assertGreater(app.rocket.velocity.length(), Vec2(0.0, -2.0).length())
        self.assertEqual(app.assist_orbit_cooldowns[0], ASSIST_ORBIT_COOLDOWN_FRAMES)
        self.assertEqual(app.transfer_boost_target_index, 1)
        self.assertGreater(app.transfer_boost_timer, 0)

    def test_orbit_transfer_does_not_boost_before_one_orbit(self) -> None:
        app = GravityCourierApp()
        current = Planet(
            position=Vec2(0.0, 0.0),
            mass=3000.0,
            radius=20.0,
            gravity_well_radius=180.0,
        )
        ahead = Planet(
            position=Vec2(0.0, -260.0),
            mass=3000.0,
            radius=20.0,
            gravity_well_radius=120.0,
        )
        app.planets = [current, ahead]
        app.assist_orbit_cooldowns = [0, 0]
        app.orbit_progress[0] = OrbitProgress(turns=0.95, in_orbit=True, transfer_ready=False)
        app.active_orbit_planet_index = 0
        app.rocket.position = Vec2(0.0, -190.0)
        app.rocket.velocity = Vec2(0.0, -2.0)

        app._try_orbit_transfer()

        self.assertEqual(app.rocket.velocity, Vec2(0.0, -2.0))
        self.assertEqual(app.assist_orbit_cooldowns[0], 0)
        self.assertIsNone(app.transfer_boost_target_index)
        self.assertEqual(app.transfer_boost_timer, 0)

    def test_orbit_transfer_does_not_boost_until_gravity_well_exit(self) -> None:
        app = GravityCourierApp()
        current = Planet(
            position=Vec2(0.0, 0.0),
            mass=3000.0,
            radius=20.0,
            gravity_well_radius=180.0,
        )
        app.planets = [current]
        app.assist_orbit_cooldowns = [0]
        app.orbit_progress[0] = OrbitProgress(turns=1.05, visit_laps=1, in_orbit=True, transfer_ready=True)
        app.active_orbit_planet_index = 0
        app.rocket.position = Vec2(0.0, -100.0)
        app.rocket.velocity = Vec2(0.0, -2.0)

        app._try_orbit_transfer()

        self.assertEqual(app.rocket.velocity, Vec2(0.0, -2.0))
        self.assertEqual(app.transfer_boost_timer, 0)

    def test_orbit_transfer_still_boosts_when_no_aligned_destination(self) -> None:
        app = GravityCourierApp()
        current = Planet(
            position=Vec2(0.0, 0.0),
            mass=3000.0,
            radius=20.0,
            gravity_well_radius=180.0,
        )
        angled_destination = Planet(
            position=Vec2(40.0, -320.0),
            mass=3000.0,
            radius=20.0,
            gravity_well_radius=120.0,
        )
        app.planets = [current, angled_destination]
        app.assist_orbit_cooldowns = [0, 0]
        app.orbit_progress[0] = OrbitProgress(turns=1.05, visit_laps=1, in_orbit=True, transfer_ready=True)
        app.active_orbit_planet_index = 0
        app.rocket.position = Vec2(0.0, -190.0)
        app.rocket.velocity = Vec2(0.0, -2.0)

        app._try_orbit_transfer()

        self.assertGreater(app.rocket.velocity.length(), Vec2(0.0, -2.0).length())
        self.assertEqual(app.assist_orbit_cooldowns[0], ASSIST_ORBIT_COOLDOWN_FRAMES)
        self.assertIsNone(app.transfer_boost_target_index)
        self.assertGreater(app.transfer_boost_timer, 0)

    def test_orbit_transfer_still_boosts_when_destination_is_not_above(self) -> None:
        app = GravityCourierApp()
        current = Planet(
            position=Vec2(0.0, 0.0),
            mass=3000.0,
            radius=20.0,
            gravity_well_radius=180.0,
        )
        lower_ahead = Planet(
            position=Vec2(0.0, 100.0),
            mass=3000.0,
            radius=20.0,
            gravity_well_radius=120.0,
        )
        app.planets = [current, lower_ahead]
        app.assist_orbit_cooldowns = [0, 0]
        app.orbit_progress[0] = OrbitProgress(turns=1.05, visit_laps=1, in_orbit=True, transfer_ready=True)
        app.active_orbit_planet_index = 0
        app.rocket.position = Vec2(0.0, -190.0)
        app.rocket.velocity = Vec2(0.0, -2.0)

        app._try_orbit_transfer()

        self.assertGreater(app.rocket.velocity.length(), Vec2(0.0, -2.0).length())
        self.assertEqual(app.assist_orbit_cooldowns[0], ASSIST_ORBIT_COOLDOWN_FRAMES)
        self.assertIsNone(app.transfer_boost_target_index)

    def test_orbit_transfer_does_not_boost_after_leaving_orbit_path(self) -> None:
        app = GravityCourierApp()
        current = Planet(
            position=Vec2(0.0, 0.0),
            mass=3000.0,
            radius=20.0,
            gravity_well_radius=180.0,
        )
        ahead = Planet(
            position=Vec2(0.0, -260.0),
            mass=3000.0,
            radius=20.0,
            gravity_well_radius=120.0,
        )
        app.planets = [current, ahead]
        app.assist_orbit_cooldowns = [0, 0]
        app.orbit_progress[0] = OrbitProgress(turns=1.05, visit_laps=1, in_orbit=False, transfer_ready=True)
        app.active_orbit_planet_index = None
        app.rocket.position = Vec2(0.0, -100.0)
        app.rocket.velocity = Vec2(0.0, -2.0)

        app._try_orbit_transfer()

        self.assertEqual(app.rocket.velocity, Vec2(0.0, -2.0))
        self.assertEqual(app.assist_orbit_cooldowns[0], 0)
        self.assertIsNone(app.transfer_boost_target_index)

    def test_exiting_gravity_well_after_lap_triggers_transfer_once(self) -> None:
        app = GravityCourierApp()
        current = Planet(
            position=Vec2(0.0, 0.0),
            mass=3000.0,
            radius=20.0,
            gravity_well_radius=120.0,
        )
        app.planets = [current]
        app.assist_orbit_cooldowns = [0]
        app.orbit_progress = [OrbitProgress(turns=1.0, visit_laps=1, in_orbit=True, transfer_ready=True)]
        app.active_orbit_planet_index = 0
        app.rocket.position = Vec2(200.0, 0.0)
        app.rocket.velocity = Vec2(2.0, 0.0)

        app._update_orbit_progress()
        first_velocity = app.rocket.velocity
        first_timer = app.transfer_boost_timer
        app._update_orbit_progress()

        self.assertGreater(first_velocity.length(), Vec2(2.0, 0.0).length())
        self.assertEqual(app.last_transfer_boost_planet_index, 0)
        self.assertGreater(first_timer, 0)
        self.assertEqual(app.rocket.velocity, first_velocity)

    def test_exiting_gravity_well_without_lap_does_not_trigger_transfer(self) -> None:
        app = GravityCourierApp()
        current = Planet(
            position=Vec2(0.0, 0.0),
            mass=3000.0,
            radius=20.0,
            gravity_well_radius=120.0,
        )
        app.planets = [current]
        app.assist_orbit_cooldowns = [0]
        app.orbit_progress = [OrbitProgress(turns=0.4, in_orbit=True, transfer_ready=False)]
        app.active_orbit_planet_index = 0
        app.rocket.position = Vec2(200.0, 0.0)
        app.rocket.velocity = Vec2(2.0, 0.0)

        app._update_orbit_progress()

        self.assertEqual(app.rocket.velocity, Vec2(2.0, 0.0))
        self.assertEqual(app.transfer_boost_timer, 0)
        self.assertIsNone(app.last_transfer_boost_planet_index)

    def test_orbit_speed_bonus_accelerates_without_spending_fuel(self) -> None:
        app = GravityCourierApp()
        planet = Planet(
            position=Vec2(0.0, 0.0),
            mass=3000.0,
            radius=20.0,
            gravity_well_radius=180.0,
        )
        app.planets = [planet]
        app.orbit_progress[0] = OrbitProgress(turns=1.25, in_orbit=True)
        app.rocket.position = Vec2(0.0, -100.0)
        app.rocket.velocity = Vec2(0.0, -2.0)
        starting_fuel = app.rocket.fuel

        app._apply_orbit_speed_bonus()

        self.assertGreater(app.rocket.velocity.length(), Vec2(0.0, -2.0).length())
        self.assertEqual(app.rocket.fuel, starting_fuel)
        self.assertGreater(app.orbit_speed_boost_timer, 0)

    def test_orbit_speed_bonus_accelerates_before_first_completed_lap(self) -> None:
        app = GravityCourierApp()
        planet = Planet(
            position=Vec2(0.0, 0.0),
            mass=3000.0,
            radius=20.0,
            gravity_well_radius=180.0,
        )
        app.planets = [planet]
        app.orbit_progress[0] = OrbitProgress(turns=0.0, in_orbit=True)
        app.rocket.position = Vec2(0.0, -100.0)
        app.rocket.velocity = Vec2(0.0, -2.0)

        app._apply_orbit_speed_bonus()

        self.assertGreater(app.rocket.velocity.length(), Vec2(0.0, -2.0).length())
        self.assertGreater(app.orbit_speed_boost_timer, 0)

    def test_orbit_speed_bonus_grows_with_orbit_turns(self) -> None:
        app = GravityCourierApp()

        self.assertGreater(
            app._orbit_speed_bonus_amount(2.0),
            app._orbit_speed_bonus_amount(0.0),
        )

    def test_orbit_speed_bonus_does_not_apply_after_leaving_orbit(self) -> None:
        app = GravityCourierApp()
        planet = Planet(
            position=Vec2(0.0, 0.0),
            mass=3000.0,
            radius=20.0,
            gravity_well_radius=180.0,
        )
        app.planets = [planet]
        app.orbit_progress[0] = OrbitProgress(turns=2.0, in_orbit=False)
        app.rocket.position = Vec2(0.0, -100.0)
        app.rocket.velocity = Vec2(0.0, -2.0)

        app._apply_orbit_speed_bonus()

        self.assertEqual(app.rocket.velocity, Vec2(0.0, -2.0))
        self.assertEqual(app.orbit_speed_boost_timer, 0)

    def test_orbit_track_guidance_bends_velocity_toward_orbit_tangent(self) -> None:
        app = GravityCourierApp()
        planet = Planet(
            position=Vec2(0.0, 0.0),
            mass=3000.0,
            radius=20.0,
            gravity_well_radius=180.0,
        )
        app.planets = [planet]
        app.active_orbit_planet_index = 0
        app.orbit_progress[0] = OrbitProgress(in_orbit=True)
        app.rocket.position = Vec2(100.0, 0.0)
        app.rocket.velocity = Vec2(2.0, 0.0)

        app._apply_orbit_track_guidance()

        self.assertLess(app.rocket.velocity.x, 2.0)
        self.assertGreater(app.rocket.velocity.y, 0.0)

    def test_orbit_track_guidance_weakens_after_more_laps(self) -> None:
        app = GravityCourierApp()

        self.assertLess(
            app._orbit_track_guidance_strength(3),
            app._orbit_track_guidance_strength(0),
        )

    def test_active_orbit_track_prefers_current_manual_orbit_planet(self) -> None:
        app = GravityCourierApp()
        nearer = Planet(
            position=Vec2(0.0, 0.0),
            mass=3000.0,
            radius=20.0,
            gravity_well_radius=180.0,
        )
        farther = Planet(
            position=Vec2(80.0, -80.0),
            mass=3000.0,
            radius=20.0,
            gravity_well_radius=180.0,
        )
        app.planets = [farther, nearer]
        app.orbit_progress[0] = OrbitProgress(in_orbit=True)
        app.orbit_progress[1] = OrbitProgress(in_orbit=True)
        app.rocket.position = Vec2(32.0, 0.0)

        self.assertEqual(app._active_orbit_planet_index(), 1)

    def test_active_orbit_track_prefers_demo_orbit_planet_in_demo_mode(self) -> None:
        app = GravityCourierApp()
        app.demo_mode = True
        app.demo_orbit_index = 2
        app.orbit_progress[0] = OrbitProgress(in_orbit=True)
        app.rocket.position = app.planets[2].position + Vec2(app.planets[2].radius + 24.0, 0.0)

        self.assertEqual(app._active_orbit_planet_index(), 2)

    def test_active_orbit_track_ignores_stale_past_orbit_planet(self) -> None:
        app = GravityCourierApp()
        past_planet = Planet(
            position=Vec2(120.0, 200.0),
            mass=3000.0,
            radius=20.0,
            gravity_well_radius=120.0,
        )
        current_planet = Planet(
            position=Vec2(120.0, -100.0),
            mass=3000.0,
            radius=20.0,
            gravity_well_radius=160.0,
        )
        app.planets = [past_planet, current_planet]
        app.orbit_progress[0] = OrbitProgress(in_orbit=True)
        app.orbit_progress[1] = OrbitProgress(in_orbit=True)
        app.rocket.position = current_planet.position + Vec2(72.0, 0.0)

        self.assertEqual(app._active_orbit_planet_index(), 1)
