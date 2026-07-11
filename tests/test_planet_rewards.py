import unittest

import _path  # noqa: F401

from gravity_courier.app import GravityCourierApp
from gravity_courier.constants import (
    COLLISION_ESCAPE_FRAMES,
    COLLISION_ESCAPE_GRAVITY_SCALE,
    FOREST_REWARD_FUEL_RATIO,
    ROCKET_DAMAGE_COOLDOWN_FRAMES,
    ROCKET_FUEL_MAX,
    WATER_REWARD_SCORE_USES,
    WIND_REWARD_GRAVITY_MULTIPLIER,
)
from gravity_courier.entities import Planet, Vec2
from gravity_courier.planet_types import (
    INITIAL_PLANET_TYPE_SEQUENCE,
    PLANET_TYPE_FOREST,
    PLANET_TYPE_IRON,
    PLANET_TYPE_ROCK,
    PLANET_TYPE_WATER,
    PLANET_TYPE_WIND,
)


def make_planet(planet_type: str, x: float = 0.0) -> Planet:
    return Planet(
        position=Vec2(x, 0.0),
        mass=3000.0,
        radius=20.0,
        gravity_well_radius=50.0,
        planet_type=planet_type,
    )


def trigger_assist(app: GravityCourierApp, planet_index: int, speed: float = 2.0) -> None:
    app.rocket.position = Vec2(500.0, 500.0)
    app.rocket.velocity = Vec2(speed, 0.0)
    app._handle_lap_completed(planet_index)


class PlanetRewardTest(unittest.TestCase):
    def test_initial_planet_type_sequence_defines_all_required_types(self) -> None:
        self.assertEqual(
            set(INITIAL_PLANET_TYPE_SEQUENCE),
            {
                PLANET_TYPE_WIND,
                PLANET_TYPE_IRON,
                PLANET_TYPE_WATER,
                PLANET_TYPE_FOREST,
                PLANET_TYPE_ROCK,
            },
        )

    def test_lap_one_does_not_trigger_reward(self) -> None:
        app = GravityCourierApp()
        app.planets = [make_planet(PLANET_TYPE_FOREST)]
        app.planet_lap_counts = [0]
        app.rocket.fuel = 10.0

        trigger_assist(app, 0)

        self.assertEqual(app.planet_lap_counts[0], 1)
        self.assertEqual(app.reward_claimed_planet_ids, set())
        self.assertEqual(app.reward_feedback_text, "")

    def test_lap_two_triggers_reward_once_and_lap_three_does_not_retrigger(self) -> None:
        app = GravityCourierApp()
        app.planets = [make_planet(PLANET_TYPE_FOREST)]
        app.planet_lap_counts = [1]
        app.rocket.fuel = 10.0

        trigger_assist(app, 0)

        self.assertEqual(app.planet_lap_counts[0], 2)
        self.assertEqual(app.reward_claimed_planet_ids, {0})
        self.assertEqual(app.reward_feedback_text, "FUEL +25%")
        fuel_after_lap_two = app.rocket.fuel

        trigger_assist(app, 0)

        self.assertEqual(app.planet_lap_counts[0], 3)
        self.assertEqual(app.reward_claimed_planet_ids, {0})
        self.assertEqual(app.reward_feedback_text, "")
        self.assertEqual(app.rocket.fuel, fuel_after_lap_two + 8.0)

    def test_different_planets_can_each_trigger_reward(self) -> None:
        app = GravityCourierApp()
        app.planets = [make_planet(PLANET_TYPE_IRON, 0.0), make_planet(PLANET_TYPE_ROCK, 200.0)]
        app.planet_lap_counts = [1, 1]
        app.rocket.hp = 2

        trigger_assist(app, 0)
        trigger_assist(app, 1)

        self.assertEqual(app.reward_claimed_planet_ids, {0, 1})

    def test_forest_reward_recovers_fuel_and_clamps_to_max(self) -> None:
        app = GravityCourierApp()
        app.planets = [make_planet(PLANET_TYPE_FOREST)]
        app.rocket.fuel = 50.0

        app._apply_planet_reward(0)

        self.assertEqual(app.rocket.fuel, 50.0 + ROCKET_FUEL_MAX * FOREST_REWARD_FUEL_RATIO)

        app.rocket.fuel = ROCKET_FUEL_MAX - 1
        app._apply_planet_reward(0)

        self.assertEqual(app.rocket.fuel, ROCKET_FUEL_MAX)

    def test_rock_reward_recovers_hp_and_clamps_to_max(self) -> None:
        app = GravityCourierApp()
        app.planets = [make_planet(PLANET_TYPE_ROCK)]
        app.rocket.hp = 1

        app._apply_planet_reward(0)

        self.assertEqual(app.rocket.hp, 2)

        app.rocket.hp = app.rocket.max_hp
        app._apply_planet_reward(0)

        self.assertEqual(app.rocket.hp, app.rocket.max_hp)

    def test_iron_reward_increases_shield_and_clamps_to_max(self) -> None:
        app = GravityCourierApp()
        app.planets = [make_planet(PLANET_TYPE_IRON)]
        app.rocket.shield = 0

        app._apply_planet_reward(0)

        self.assertEqual(app.rocket.shield, 1)

        app.rocket.shield = app.rocket.max_shield
        app._apply_planet_reward(0)

        self.assertEqual(app.rocket.shield, app.rocket.max_shield)

    def test_water_reward_applies_to_future_assist_scoring_and_decrements_uses(self) -> None:
        app = GravityCourierApp()
        app.planets = [make_planet(PLANET_TYPE_WATER)]
        app.planet_lap_counts = [1]

        trigger_assist(app, 0)

        self.assertEqual(app.last_score_gain, 150)
        self.assertEqual(app.water_score_bonus_uses, WATER_REWARD_SCORE_USES)

        trigger_assist(app, 0)

        self.assertEqual(app.last_score_gain, 250)
        self.assertEqual(app.water_score_bonus_uses, WATER_REWARD_SCORE_USES - 1)

    def test_wind_reward_increases_planet_gravity_multiplier(self) -> None:
        app = GravityCourierApp()
        app.planets = [make_planet(PLANET_TYPE_WIND)]

        app._apply_planet_reward(0)

        self.assertEqual(app.planets[0].gravity_multiplier, WIND_REWARD_GRAVITY_MULTIPLIER)


class DamageModelTest(unittest.TestCase):
    def test_shield_absorbs_damage_before_hp(self) -> None:
        app = GravityCourierApp()
        planet = make_planet(PLANET_TYPE_ROCK)
        app.rocket.position = Vec2(1.0, 0.0)
        app.rocket.velocity = Vec2(3.0, 0.0)
        app.rocket.hp = 3
        app.rocket.shield = 1

        app._handle_planet_collision(planet)

        self.assertEqual(app.rocket.shield, 0)
        self.assertEqual(app.rocket.hp, 3)
        self.assertEqual(app.rocket.damage_cooldown, ROCKET_DAMAGE_COOLDOWN_FRAMES)
        self.assertFalse(app.rocket.crashed)

    def test_hp_damage_occurs_when_no_shield(self) -> None:
        app = GravityCourierApp()
        planet = make_planet(PLANET_TYPE_ROCK)
        app.rocket.position = Vec2(1.0, 0.0)
        app.rocket.velocity = Vec2(3.0, 0.0)
        app.rocket.hp = 3
        app.rocket.shield = 0

        app._handle_planet_collision(planet)

        self.assertEqual(app.rocket.hp, 2)
        self.assertFalse(app.rocket.crashed)

    def test_hp_zero_causes_crash(self) -> None:
        app = GravityCourierApp()
        planet = make_planet(PLANET_TYPE_ROCK)
        app.rocket.position = Vec2(1.0, 0.0)
        app.rocket.velocity = Vec2(3.0, 0.0)
        app.rocket.hp = 1
        app.rocket.shield = 0

        app._handle_planet_collision(planet)

        self.assertEqual(app.rocket.hp, 0)
        self.assertTrue(app.rocket.crashed)

    def test_damage_cooldown_prevents_repeated_immediate_damage(self) -> None:
        app = GravityCourierApp()
        planet = make_planet(PLANET_TYPE_ROCK)
        app.rocket.position = Vec2(1.0, 0.0)
        app.rocket.velocity = Vec2(3.0, 0.0)
        app.rocket.hp = 3

        app._handle_planet_collision(planet)
        app._handle_planet_collision(planet)

        self.assertEqual(app.rocket.hp, 2)

    def test_planet_collision_starts_temporary_escape_gravity_window(self) -> None:
        app = GravityCourierApp()
        planet = make_planet(PLANET_TYPE_ROCK)
        app.planets = [planet]
        app.rocket.position = Vec2(1.0, 0.0)
        app.rocket.velocity = Vec2(3.0, 0.0)

        app._handle_planet_collision(planet)

        self.assertEqual(app.collision_escape_timer, COLLISION_ESCAPE_FRAMES)
        gravity_planets = app._gravity_planets_for_step()
        self.assertAlmostEqual(
            gravity_planets[0].gravity_multiplier,
            planet.gravity_multiplier * COLLISION_ESCAPE_GRAVITY_SCALE,
        )

    def test_planet_collision_refreshes_escape_window_during_damage_cooldown(self) -> None:
        app = GravityCourierApp()
        planet = make_planet(PLANET_TYPE_ROCK)
        app.rocket.position = Vec2(1.0, 0.0)
        app.rocket.velocity = Vec2(3.0, 0.0)
        app.rocket.damage_cooldown = 10
        app.collision_escape_timer = 1

        app._handle_planet_collision(planet)

        self.assertEqual(app.collision_escape_timer, COLLISION_ESCAPE_FRAMES)


if __name__ == "__main__":
    unittest.main()
