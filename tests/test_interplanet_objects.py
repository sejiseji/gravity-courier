import unittest

import _path  # noqa: F401

from gravity_courier.app import GravityCourierApp
from gravity_courier.constants import (
    CREW_CELEBRATION_FRAMES,
    CROSSING_ROCKET_WARNING_FRAMES,
    ROCKET_DAMAGE_COOLDOWN_FRAMES,
    ROCKET_FUEL_MAX,
    SUPPLY_ITEM_FUEL_RATIO,
    SUPPLY_ITEM_RADIUS,
    SUPPLY_ITEM_SCORE,
    SUPPLY_PICKUP_RADIUS_BONUS,
)
from gravity_courier.entities import Rocket, Vec2
from gravity_courier.interplanet_objects import (
    OBJECT_KIND_CROSSING_ROCKET,
    OBJECT_KIND_FLOATING_ASTEROID,
    OBJECT_KIND_SUPPLY_ITEM,
    InterplanetObject,
    apply_supply_reward,
    collect_supply_item,
    make_crossing_rocket,
    make_floating_asteroid,
    make_supply_item,
    overlaps_circle,
    update_interplanet_object,
)


class InterplanetObjectModelTest(unittest.TestCase):
    def test_floating_asteroid_updates_position_by_velocity(self) -> None:
        asteroid = make_floating_asteroid(1, Vec2(10.0, 20.0), drift_x=0.05)

        updated = update_interplanet_object(asteroid)

        self.assertEqual(updated.kind, OBJECT_KIND_FLOATING_ASTEROID)
        self.assertEqual(updated.pos, Vec2(10.05, 20.0))

    def test_crossing_rocket_warning_counts_down_before_movement(self) -> None:
        rocket = make_crossing_rocket(1, Vec2(-40.0, 120.0), direction=1)

        updated = update_interplanet_object(rocket)

        self.assertEqual(updated.kind, OBJECT_KIND_CROSSING_ROCKET)
        self.assertEqual(updated.warning_timer, CROSSING_ROCKET_WARNING_FRAMES - 1)
        self.assertEqual(updated.pos, rocket.pos)

    def test_crossing_rocket_updates_position_after_warning(self) -> None:
        rocket = make_crossing_rocket(1, Vec2(-40.0, 120.0), direction=1, warning_timer=0)

        updated = update_interplanet_object(rocket)

        self.assertGreater(updated.pos.x, rocket.pos.x)

    def test_inactive_object_does_not_update(self) -> None:
        obj = InterplanetObject(
            object_id=1,
            kind=OBJECT_KIND_FLOATING_ASTEROID,
            pos=Vec2(1.0, 1.0),
            vel=Vec2(2.0, 0.0),
            active=False,
        )

        self.assertEqual(update_interplanet_object(obj), obj)

    def test_crossing_rocket_deactivates_after_leaving_range(self) -> None:
        rocket = make_crossing_rocket(1, Vec2(540.0, 120.0), direction=1, warning_timer=0)

        updated = update_interplanet_object(rocket)

        self.assertFalse(updated.active)


class InterplanetCollisionAndSupplyTest(unittest.TestCase):
    def test_overlap_detection_uses_combined_radius(self) -> None:
        asteroid = make_floating_asteroid(1, Vec2(0.0, 0.0))

        self.assertTrue(overlaps_circle(asteroid, Vec2(10.0, 0.0), 4.0))
        self.assertFalse(overlaps_circle(asteroid, Vec2(80.0, 0.0), 4.0))

    def test_warning_crossing_rocket_does_not_collide_yet(self) -> None:
        rocket = make_crossing_rocket(1, Vec2(0.0, 0.0), warning_timer=10)

        self.assertFalse(overlaps_circle(rocket, Vec2(0.0, 0.0), 4.0))

    def test_supply_item_collects_once(self) -> None:
        supply = make_supply_item(1, Vec2(0.0, 0.0))

        collected, result = collect_supply_item(supply)
        collected_again, second_result = collect_supply_item(collected)

        self.assertTrue(result.collected)
        self.assertTrue(collected.collected)
        self.assertFalse(collected.active)
        self.assertFalse(second_result.collected)
        self.assertEqual(collected_again, collected)

    def test_supply_reward_adds_score_and_clamps_fuel(self) -> None:
        rocket = Rocket(fuel=ROCKET_FUEL_MAX - 1)
        supply = make_supply_item(1, Vec2(0.0, 0.0))
        _, result = collect_supply_item(supply)

        score, fuel = apply_supply_reward(rocket, 1000, result, ROCKET_FUEL_MAX)

        self.assertEqual(score, 1000 + SUPPLY_ITEM_SCORE)
        self.assertEqual(fuel, ROCKET_FUEL_MAX)

    def test_supply_item_does_not_add_crew_state(self) -> None:
        app = GravityCourierApp()
        app.rocket.position = Vec2(0.0, 0.0)
        app.rocket.fuel = 10.0
        app.interplanet_objects = [make_supply_item(1, Vec2(0.0, 0.0))]
        crew_before = dict(app.crew_count_by_type)

        app._update_interplanet_objects()

        self.assertEqual(app.crew_count_by_type, crew_before)
        self.assertEqual(app.score, SUPPLY_ITEM_SCORE)
        self.assertEqual(app.rocket.fuel, 10.0 + ROCKET_FUEL_MAX * SUPPLY_ITEM_FUEL_RATIO)
        self.assertEqual(app.last_collected_supply_item_id, 1)
        self.assertEqual(app.crew_celebration_timer, CREW_CELEBRATION_FRAMES)

    def test_supply_item_pickup_has_extra_padding(self) -> None:
        app = GravityCourierApp()
        app.rocket.position = Vec2(SUPPLY_ITEM_RADIUS + 10.0 + SUPPLY_PICKUP_RADIUS_BONUS - 0.1, 0.0)
        app.interplanet_objects = [make_supply_item(1, Vec2(0.0, 0.0))]

        app._update_interplanet_objects()

        self.assertEqual(app.last_collected_supply_item_id, 1)


class InterplanetDamageIntegrationTest(unittest.TestCase):
    def test_shield_absorbs_obstacle_damage_before_hp(self) -> None:
        app = GravityCourierApp()
        app.rocket.shield = 1
        app.rocket.hp = 3

        result = app._apply_rocket_damage(1, OBJECT_KIND_FLOATING_ASTEROID)

        self.assertTrue(result.damaged)
        self.assertEqual(result.shield_used, 1)
        self.assertEqual(app.rocket.shield, 0)
        self.assertEqual(app.rocket.hp, 3)
        self.assertEqual(app.rocket.damage_cooldown, ROCKET_DAMAGE_COOLDOWN_FRAMES)

    def test_hp_damage_occurs_when_no_shield(self) -> None:
        app = GravityCourierApp()
        app.rocket.shield = 0
        app.rocket.hp = 3

        result = app._apply_rocket_damage(1, OBJECT_KIND_CROSSING_ROCKET)

        self.assertEqual(result.hp_lost, 1)
        self.assertEqual(app.rocket.hp, 2)
        self.assertFalse(app.rocket.crashed)

    def test_hp_zero_crashes_rocket(self) -> None:
        app = GravityCourierApp()
        app.rocket.shield = 0
        app.rocket.hp = 1

        result = app._apply_rocket_damage(1, OBJECT_KIND_FLOATING_ASTEROID)

        self.assertTrue(result.crashed)
        self.assertTrue(app.rocket.crashed)

    def test_damage_cooldown_prevents_repeated_damage(self) -> None:
        app = GravityCourierApp()
        app.rocket.hp = 3

        app._apply_rocket_damage(1, OBJECT_KIND_FLOATING_ASTEROID)
        result = app._apply_rocket_damage(1, OBJECT_KIND_FLOATING_ASTEROID)

        self.assertFalse(result.damaged)
        self.assertEqual(app.rocket.hp, 2)


if __name__ == "__main__":
    unittest.main()
