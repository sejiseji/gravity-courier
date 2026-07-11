import unittest

import _path  # noqa: F401

from gravity_courier.entities import Planet, Vec2
from gravity_courier.entities import Rocket
from gravity_courier.physics import gravity_acceleration, nearest_orbit_planet, orbit_assist_velocity


class PhysicsTest(unittest.TestCase):
    def test_gravity_acceleration_points_toward_planet(self) -> None:
        planet = Planet(
            position=Vec2(10.0, 0.0),
            mass=100.0,
            radius=8.0,
            gravity_well_radius=80.0,
        )
        acceleration = gravity_acceleration(Vec2(0.0, 0.0), planet, softening=1.0)

        self.assertGreater(acceleration.x, 0.0)
        self.assertLess(abs(acceleration.y), 1e-9)

    def test_gravity_acceleration_handles_same_position(self) -> None:
        planet = Planet(
            position=Vec2(0.0, 0.0),
            mass=100.0,
            radius=8.0,
            gravity_well_radius=80.0,
        )
        acceleration = gravity_acceleration(Vec2(0.0, 0.0), planet)

        self.assertEqual(acceleration.x, 0.0)
        self.assertEqual(acceleration.y, 0.0)

    def test_gravity_acceleration_is_stronger_when_closer(self) -> None:
        planet = Planet(
            position=Vec2(0.0, 0.0),
            mass=1000.0,
            radius=8.0,
            gravity_well_radius=80.0,
        )

        close = gravity_acceleration(Vec2(20.0, 0.0), planet)
        far = gravity_acceleration(Vec2(100.0, 0.0), planet)

        self.assertGreater(close.length(), far.length())

    def test_gravity_multiplier_increases_acceleration_magnitude(self) -> None:
        base_planet = Planet(
            position=Vec2(0.0, 0.0),
            mass=1000.0,
            radius=8.0,
            gravity_well_radius=80.0,
        )
        boosted_planet = Planet(
            position=Vec2(0.0, 0.0),
            mass=1000.0,
            radius=8.0,
            gravity_well_radius=80.0,
            gravity_multiplier=1.25,
        )

        base = gravity_acceleration(Vec2(20.0, 0.0), base_planet)
        boosted = gravity_acceleration(Vec2(20.0, 0.0), boosted_planet)

        self.assertAlmostEqual(boosted.length(), base.length() * 1.25)

    def test_nearest_orbit_planet_finds_planet_inside_assist_band(self) -> None:
        near = Planet(
            position=Vec2(0.0, 0.0),
            mass=1000.0,
            radius=20.0,
            gravity_well_radius=120.0,
        )
        far = Planet(
            position=Vec2(300.0, 0.0),
            mass=1000.0,
            radius=20.0,
            gravity_well_radius=120.0,
        )
        rocket = Rocket(position=Vec2(60.0, 0.0), velocity=Vec2())

        self.assertEqual(nearest_orbit_planet(rocket, [far, near]), near)

    def test_orbit_assist_adds_tangential_velocity(self) -> None:
        planet = Planet(
            position=Vec2(0.0, 0.0),
            mass=1000.0,
            radius=20.0,
            gravity_well_radius=120.0,
        )
        rocket = Rocket(position=Vec2(60.0, 0.0), velocity=Vec2())

        assisted = orbit_assist_velocity(rocket, planet, strength=0.5)

        self.assertGreater(assisted.y, 0.0)
        self.assertNotEqual(assisted, rocket.velocity)

    def test_orbit_assist_does_not_force_fast_entry_down_to_target_speed(self) -> None:
        planet = Planet(
            position=Vec2(0.0, 0.0),
            mass=1000.0,
            radius=20.0,
            gravity_well_radius=120.0,
        )
        rocket = Rocket(position=Vec2(60.0, 0.0), velocity=Vec2(0.0, 5.0))

        assisted = orbit_assist_velocity(rocket, planet, strength=0.5)

        self.assertGreaterEqual(assisted.length(), rocket.velocity.length())
