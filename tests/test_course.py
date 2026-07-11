import unittest
from collections import Counter

import _path  # noqa: F401

from gravity_courier.constants import PLANET_X_MAX, PLANET_X_MIN
from gravity_courier.course import (
    COURSE_MODE_HARD,
    COURSE_MODE_NORMAL,
    HARD_COURSE_PLANET_COUNT,
    HARD_PLANET_APPEARANCES_PER_TYPE,
    NORMAL_COURSE_PLANET_COUNT,
    NORMAL_COURSE_PLANET_TYPES,
    NORMAL_PLANET_APPEARANCES_PER_TYPE,
    course_mode_for_key,
    difficulty_for_gap_index,
    difficulty_for_planet_index,
    first_five_include_recovery,
    future_gap_id_for_supply,
    generate_course,
    generate_planet_type_order,
    has_three_type_streak,
    mark_supply_gap,
    next_course_mode_key,
)


class CourseGenerationTest(unittest.TestCase):
    def test_default_generated_course_is_normal_with_20_planets_and_4_of_each_type(self) -> None:
        course = generate_course()
        counts = Counter(course.planet_type_order)

        self.assertEqual(course.mode.key, COURSE_MODE_NORMAL)
        self.assertEqual(len(course.planets), NORMAL_COURSE_PLANET_COUNT)
        self.assertEqual(len(course.planet_type_order), NORMAL_COURSE_PLANET_COUNT)
        for planet_type in NORMAL_COURSE_PLANET_TYPES:
            self.assertEqual(counts[planet_type], NORMAL_PLANET_APPEARANCES_PER_TYPE)

    def test_hard_course_has_35_planets_and_7_of_each_type(self) -> None:
        course = generate_course(mode_key=COURSE_MODE_HARD)
        counts = Counter(course.planet_type_order)

        self.assertEqual(course.mode.key, COURSE_MODE_HARD)
        self.assertEqual(len(course.planets), HARD_COURSE_PLANET_COUNT)
        self.assertEqual(len(course.planet_type_order), HARD_COURSE_PLANET_COUNT)
        for planet_type in NORMAL_COURSE_PLANET_TYPES:
            self.assertEqual(counts[planet_type], HARD_PLANET_APPEARANCES_PER_TYPE)

    def test_course_mode_helpers(self) -> None:
        self.assertEqual(course_mode_for_key(COURSE_MODE_NORMAL).planet_count, 20)
        self.assertEqual(course_mode_for_key(COURSE_MODE_HARD).planet_count, 35)
        self.assertEqual(next_course_mode_key(COURSE_MODE_NORMAL), COURSE_MODE_HARD)
        self.assertEqual(next_course_mode_key(COURSE_MODE_HARD), COURSE_MODE_NORMAL)

    def test_fairness_constraints(self) -> None:
        order = generate_planet_type_order()

        self.assertFalse(has_three_type_streak(order))
        self.assertTrue(first_five_include_recovery(order))

    def test_generation_is_deterministic_by_seed(self) -> None:
        self.assertEqual(generate_planet_type_order(12345), generate_planet_type_order(12345))
        self.assertNotEqual(generate_planet_type_order(12345), generate_planet_type_order(54321))


class CoursePlacementTest(unittest.TestCase):
    def test_planet_positions_progress_upward_and_stay_in_bounds(self) -> None:
        course = generate_course()
        ys = [planet.position.y for planet in course.planets]

        self.assertEqual(len(set(range(len(course.planets)))), len(course.planets))
        self.assertTrue(all(PLANET_X_MIN <= planet.position.x <= PLANET_X_MAX for planet in course.planets))
        self.assertTrue(all(next_y < current_y for current_y, next_y in zip(ys, ys[1:])))

    def test_gap_metadata_references_valid_planet_ids(self) -> None:
        course = generate_course()
        valid_ids = set(range(len(course.planets)))

        self.assertEqual(len(course.gaps), len(course.planets) - 1)
        for gap in course.gaps:
            self.assertIn(gap.from_planet_id, valid_ids)
            self.assertIn(gap.to_planet_id, valid_ids)
            self.assertEqual(gap.to_planet_id, gap.from_planet_id + 1)

    def test_supply_gap_marking_is_deterministic(self) -> None:
        course = generate_course()
        marked = mark_supply_gap(course.gaps, 3)

        self.assertFalse(course.gaps[3].is_supply_wide_gap)
        self.assertTrue(marked[3].is_supply_wide_gap)
        self.assertEqual(marked[3], mark_supply_gap(course.gaps, 3)[3])

    def test_future_gap_mapping(self) -> None:
        course = generate_course()

        self.assertEqual(future_gap_id_for_supply(0, 2, course.gaps), 2)
        self.assertEqual(future_gap_id_for_supply(4, 3, course.gaps), 7)
        self.assertIsNone(future_gap_id_for_supply(len(course.planets) - 1, 3, course.gaps))


class DifficultyHelperTest(unittest.TestCase):
    def test_difficulty_increases_deterministically(self) -> None:
        start = difficulty_for_planet_index(0, 35)
        end = difficulty_for_planet_index(34, 35)

        self.assertEqual(start, difficulty_for_planet_index(0, 35))
        self.assertLess(start, end)
        self.assertGreaterEqual(difficulty_for_gap_index(0, 34), 1.0)
        self.assertLessEqual(difficulty_for_gap_index(33, 34), 1.75)


if __name__ == "__main__":
    unittest.main()
