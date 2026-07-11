import math
import unittest

import _path  # noqa: F401

from gravity_courier.app import GravityCourierApp, OrbitProgress
from gravity_courier.constants import CREW_CELEBRATION_FRAMES, LAP_COMPLETION_RADIANS
from gravity_courier.entities import Planet, Vec2
from gravity_courier.orbit import OrbitLapTracker, wrap_angle_delta


class OrbitLapTrackingTest(unittest.TestCase):
    def test_wrapped_angle_delta_handles_pi_boundary(self) -> None:
        delta = wrap_angle_delta(-math.pi + 0.10 - (math.pi - 0.10))

        self.assertAlmostEqual(delta, 0.20)

    def test_one_revolution_triggers_lap_event(self) -> None:
        tracker = OrbitLapTracker(prev_angle=0.0)
        steps = 12
        completed = 0
        for step in range(1, steps + 1):
            completed += tracker.update_angle(LAP_COMPLETION_RADIANS * step / steps)

        self.assertEqual(completed, 1)
        self.assertEqual(tracker.completed_laps, 1)
        self.assertTrue(tracker.transfer_ready)

    def test_partial_revolution_does_not_trigger_lap_event(self) -> None:
        tracker = OrbitLapTracker(prev_angle=0.0)

        completed = tracker.update_angle(LAP_COMPLETION_RADIANS * 0.50)

        self.assertEqual(completed, 0)
        self.assertFalse(tracker.transfer_ready)

    def test_back_and_forth_jitter_does_not_trigger_lap_event(self) -> None:
        tracker = OrbitLapTracker(prev_angle=0.0)
        completed = 0
        for angle in (0.20, -0.20) * 20:
            completed += tracker.update_angle(angle)

        self.assertEqual(completed, 0)
        self.assertLess(abs(tracker.accumulated_angle), LAP_COMPLETION_RADIANS)

    def test_accumulation_allows_second_lap_later(self) -> None:
        tracker = OrbitLapTracker(prev_angle=0.0)
        completed = 0
        for lap in range(2):
            for step in range(1, 13):
                completed += tracker.update_angle(LAP_COMPLETION_RADIANS * step / 12 + lap * 0.01)

        self.assertEqual(completed, 2)
        self.assertEqual(tracker.completed_laps, 2)


class OrbitLapEventFlowTest(unittest.TestCase):
    def test_active_orbit_lap_label_starts_at_zero(self) -> None:
        app = GravityCourierApp()
        app.orbit_progress[0] = OrbitProgress(in_orbit=True, visit_laps=0)

        self.assertEqual(app._orbit_lap_label_for_planet(0), "0")

    def test_active_orbit_lap_label_shows_completed_laps(self) -> None:
        app = GravityCourierApp()
        app.orbit_progress[0] = OrbitProgress(in_orbit=True, visit_laps=2)

        self.assertEqual(app._orbit_lap_label_for_planet(0), "2")

    def test_lap_completed_scores_rewards_and_cutin(self) -> None:
        app = GravityCourierApp()
        app.planets = [
            Planet(
                position=Vec2(0.0, 0.0),
                mass=3000.0,
                radius=20.0,
                gravity_well_radius=120.0,
                planet_type="forest",
            )
        ]
        app.planet_lap_counts = [1]

        app._handle_lap_completed(0)

        self.assertEqual(app.planet_lap_counts[0], 2)
        self.assertEqual(app.last_score_gain, 150)
        self.assertEqual(app.cheer_text, "CLAP! CLAP!")
        self.assertEqual(app.reward_feedback_text, "FUEL +25%")
        self.assertTrue(app.cutin.active)
        self.assertEqual(app.crew_celebration_timer, CREW_CELEBRATION_FRAMES)
        assert app.cutin.payload is not None
        self.assertEqual(app.cutin.payload.cheer_stage, 2)

    def test_lap_three_scores_without_retriggering_reward(self) -> None:
        app = GravityCourierApp()
        app.planets = [
            Planet(
                position=Vec2(0.0, 0.0),
                mass=3000.0,
                radius=20.0,
                gravity_well_radius=120.0,
                planet_type="rock",
            )
        ]
        app.planet_lap_counts = [2]
        app.reward_claimed_planet_ids = {0}

        app._handle_lap_completed(0)

        self.assertEqual(app.planet_lap_counts[0], 3)
        self.assertEqual(app.last_score_gain, 200)
        self.assertEqual(app.reward_feedback_text, "")
        self.assertEqual(app.reward_claimed_planet_ids, {0})


if __name__ == "__main__":
    unittest.main()
