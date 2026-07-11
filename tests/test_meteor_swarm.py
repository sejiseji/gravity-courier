import unittest

import _path  # noqa: F401

from gravity_courier.constants import METEOR_SWARM_LIFETIME_FRAMES, METEOR_SWARM_WARNING_FRAMES
from gravity_courier.course import generate_course
from gravity_courier.meteor_swarm import (
    OBJECT_KIND_CROSSING_METEOR,
    create_meteor_swarm_for_gap,
    create_meteor_swarms_for_gaps,
    meteor_swarm_out_of_range,
    update_meteor_swarm,
)


class MeteorSwarmTest(unittest.TestCase):
    def test_course_creates_deterministic_meteor_swarms_for_marked_gaps(self) -> None:
        first = create_meteor_swarms_for_gaps(generate_course().gaps)
        second = create_meteor_swarms_for_gaps(generate_course().gaps)

        self.assertGreater(len(first), 0)
        self.assertEqual(first, second)
        self.assertTrue(all(swarm.meteors for swarm in first))

    def test_warning_precedes_meteor_movement(self) -> None:
        gap = next(gap for gap in generate_course().gaps if gap.has_meteor_swarm)
        swarm = create_meteor_swarm_for_gap(gap, swarm_id=1)
        first_pos = swarm.meteors[0].pos

        updated = update_meteor_swarm(swarm)

        self.assertEqual(updated.warning_timer, METEOR_SWARM_WARNING_FRAMES - 1)
        self.assertEqual(updated.meteors[0].pos, first_pos)
        self.assertEqual(updated.meteors[0].kind, OBJECT_KIND_CROSSING_METEOR)

    def test_meteors_move_after_warning(self) -> None:
        gap = next(gap for gap in generate_course().gaps if gap.has_meteor_swarm)
        swarm = create_meteor_swarm_for_gap(gap, swarm_id=1)
        for _ in range(METEOR_SWARM_WARNING_FRAMES):
            swarm = update_meteor_swarm(swarm)
        first_pos = swarm.meteors[0].pos

        moved = update_meteor_swarm(swarm)

        self.assertNotEqual(moved.meteors[0].pos, first_pos)
        self.assertEqual(moved.meteors[0].warning_timer, 0)

    def test_swarm_deactivates_after_lifetime(self) -> None:
        gap = next(gap for gap in generate_course().gaps if gap.has_meteor_swarm)
        swarm = create_meteor_swarm_for_gap(gap, swarm_id=1)
        for _ in range(METEOR_SWARM_WARNING_FRAMES + METEOR_SWARM_LIFETIME_FRAMES):
            swarm = update_meteor_swarm(swarm)

        self.assertFalse(swarm.active)

    def test_out_of_range_detection(self) -> None:
        gap = next(gap for gap in generate_course().gaps if gap.has_meteor_swarm)
        swarm = create_meteor_swarm_for_gap(gap, swarm_id=1)

        self.assertFalse(meteor_swarm_out_of_range(swarm))


if __name__ == "__main__":
    unittest.main()
