import unittest

import _path  # noqa: F401

from gravity_courier.entities import Rocket, Vec2
from gravity_courier.trajectory import simulate_preview


class TrajectoryTest(unittest.TestCase):
    def test_simulate_preview_returns_list(self) -> None:
        rocket = Rocket(position=Vec2(0.0, 0.0), velocity=Vec2(1.0, 0.0))

        preview = simulate_preview(rocket, steps=3, dt=1.0)

        self.assertIsInstance(preview, list)
        self.assertEqual(len(preview), 3)

    def test_simulate_preview_does_not_mutate_rocket(self) -> None:
        rocket = Rocket(position=Vec2(0.0, 0.0), velocity=Vec2(1.0, 0.0), fuel=0.5)

        simulate_preview(rocket, steps=3, dt=1.0)

        self.assertEqual(rocket.position, Vec2(0.0, 0.0))
        self.assertEqual(rocket.velocity, Vec2(1.0, 0.0))
        self.assertEqual(rocket.fuel, 0.5)
