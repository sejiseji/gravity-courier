import unittest

import _path  # noqa: F401

from gravity_courier.app import GravityCourierApp
from gravity_courier.constants import CUTIN_MAX_Y_RATIO, HEIGHT
from gravity_courier.entities import Planet, Vec2


class LapScoreTest(unittest.TestCase):
    def test_recorded_assist_increments_planet_lap_count_and_score(self) -> None:
        app = GravityCourierApp()
        app.planets = [
            Planet(
                position=Vec2(0.0, 0.0),
                mass=3000.0,
                radius=20.0,
                gravity_well_radius=50.0,
            )
        ]
        app.planet_lap_counts = [0]
        app.rocket.position = Vec2(80.0, 0.0)
        app.rocket.velocity = Vec2(2.0, 0.0)

        app._handle_lap_completed(0)

        self.assertEqual(app.planet_lap_counts[0], 1)
        self.assertEqual(app.score, 100)
        self.assertEqual(app.last_score_gain, 100)
        self.assertEqual(app.last_lap_count, 1)
        self.assertEqual(app.cheer_text, "WAA!")
        self.assertTrue(app.cutin.active)
        self.assertIsNotNone(app.cutin.payload)
        assert app.cutin.payload is not None
        self.assertLessEqual(app.cutin.payload.target_y, int(HEIGHT * CUTIN_MAX_Y_RATIO))

    def test_repeated_assists_on_same_planet_use_lap_multiplier(self) -> None:
        app = GravityCourierApp()
        app.planets = [
            Planet(
                position=Vec2(0.0, 0.0),
                mass=3000.0,
                radius=20.0,
                gravity_well_radius=50.0,
            )
        ]
        app.planet_lap_counts = [1]
        app.score = 100
        app.rocket.position = Vec2(80.0, 0.0)
        app.rocket.velocity = Vec2(2.0, 0.0)

        app._handle_lap_completed(0)

        self.assertEqual(app.planet_lap_counts[0], 2)
        self.assertEqual(app.score, 250)
        self.assertEqual(app.last_score_gain, 150)
        self.assertEqual(app.cheer_text, "CLAP! CLAP!")
        self.assertTrue(app.cutin.active)
        assert app.cutin.payload is not None
        self.assertEqual(app.cutin.payload.lap_count, 2)
        self.assertEqual(app.cutin.payload.score_gain, 150)


if __name__ == "__main__":
    unittest.main()
