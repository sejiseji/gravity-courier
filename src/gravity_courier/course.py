"""Finite course generation for Gravity Courier."""

from __future__ import annotations

from dataclasses import dataclass, replace
import random
from collections.abc import Iterable, Sequence

from .constants import (
    COURSE_SEED,
    COURSE_START_Y,
    HEIGHT,
    MAX_PLANET_APPEARANCES_PER_TYPE,
    METEOR_SWARM_EVERY_N_GAPS,
    METEOR_SWARM_GAP_START_INDEX,
    PLANET_BASE_SPACING_Y,
    PLANET_SPACING_Y_GROWTH,
    PLANET_X_MAX,
    PLANET_X_MIN,
    RESULT_RANK_THRESHOLDS,
    SUPPLY_GAP_WIDTH_HINT,
    WIDTH,
)
from .entities import Planet, Vec2
from .planet_types import (
    PLANET_TYPE_FOREST,
    PLANET_TYPE_IRON,
    PLANET_TYPE_ROCK,
    PLANET_TYPE_WATER,
    PLANET_TYPE_WIND,
    planet_type_spec,
)

NORMAL_COURSE_PLANET_TYPES = (
    PLANET_TYPE_WIND,
    PLANET_TYPE_IRON,
    PLANET_TYPE_WATER,
    PLANET_TYPE_FOREST,
    PLANET_TYPE_ROCK,
)
COURSE_MODE_NORMAL = "normal"
COURSE_MODE_HARD = "hard"
DEFAULT_COURSE_MODE_KEY = COURSE_MODE_NORMAL
NORMAL_PLANET_APPEARANCES_PER_TYPE = 4
HARD_PLANET_APPEARANCES_PER_TYPE = MAX_PLANET_APPEARANCES_PER_TYPE
NORMAL_COURSE_PLANET_COUNT = len(NORMAL_COURSE_PLANET_TYPES) * NORMAL_PLANET_APPEARANCES_PER_TYPE
HARD_COURSE_PLANET_COUNT = len(NORMAL_COURSE_PLANET_TYPES) * HARD_PLANET_APPEARANCES_PER_TYPE
COURSE_PLANET_COUNT = HARD_COURSE_PLANET_COUNT
NORMAL_RANK_THRESHOLDS = (52000, 34000, 17000, 6000)
HARD_RANK_THRESHOLDS = RESULT_RANK_THRESHOLDS


@dataclass(frozen=True)
class CourseModeSpec:
    key: str
    label: str
    appearances_per_type: int
    rank_thresholds: tuple[int, int, int, int]

    @property
    def planet_count(self) -> int:
        return len(NORMAL_COURSE_PLANET_TYPES) * self.appearances_per_type


COURSE_MODES: dict[str, CourseModeSpec] = {
    COURSE_MODE_NORMAL: CourseModeSpec(
        key=COURSE_MODE_NORMAL,
        label="Normal",
        appearances_per_type=NORMAL_PLANET_APPEARANCES_PER_TYPE,
        rank_thresholds=NORMAL_RANK_THRESHOLDS,
    ),
    COURSE_MODE_HARD: CourseModeSpec(
        key=COURSE_MODE_HARD,
        label="Hard",
        appearances_per_type=HARD_PLANET_APPEARANCES_PER_TYPE,
        rank_thresholds=HARD_RANK_THRESHOLDS,
    ),
}


@dataclass(frozen=True)
class CourseGap:
    gap_id: int
    from_planet_id: int
    to_planet_id: int
    center_pos: Vec2
    width_hint: float = 1.0
    is_supply_wide_gap: bool = False
    has_meteor_swarm: bool = False


@dataclass(frozen=True)
class GeneratedCourse:
    planets: list[Planet]
    gaps: list[CourseGap]
    planet_type_order: tuple[str, ...]
    seed: int
    mode: CourseModeSpec


def course_mode_for_key(mode_key: str | None) -> CourseModeSpec:
    if mode_key is None:
        return COURSE_MODES[DEFAULT_COURSE_MODE_KEY]
    return COURSE_MODES.get(mode_key, COURSE_MODES[DEFAULT_COURSE_MODE_KEY])


def next_course_mode_key(mode_key: str) -> str:
    return COURSE_MODE_HARD if course_mode_for_key(mode_key).key == COURSE_MODE_NORMAL else COURSE_MODE_NORMAL


def generate_planet_type_bag(appearances_per_type: int = HARD_PLANET_APPEARANCES_PER_TYPE) -> list[str]:
    return [
        planet_type
        for planet_type in NORMAL_COURSE_PLANET_TYPES
        for _ in range(appearances_per_type)
    ]


def has_three_type_streak(planet_types: Sequence[str]) -> bool:
    return any(
        planet_types[index] == planet_types[index - 1] == planet_types[index - 2]
        for index in range(2, len(planet_types))
    )


def first_five_include_recovery(planet_types: Sequence[str]) -> bool:
    return any(planet_type in (PLANET_TYPE_FOREST, PLANET_TYPE_ROCK) for planet_type in planet_types[:5])


def generate_planet_type_order(
    seed: int = COURSE_SEED,
    appearances_per_type: int = HARD_PLANET_APPEARANCES_PER_TYPE,
) -> tuple[str, ...]:
    rng = random.Random(seed)
    bag = generate_planet_type_bag(appearances_per_type)
    best_order: list[str] | None = None
    best_score = -1
    for _ in range(300):
        candidate = bag[:]
        rng.shuffle(candidate)
        score = _fairness_score(candidate)
        if score > best_score:
            best_order = candidate
            best_score = score
        if not has_three_type_streak(candidate) and first_five_include_recovery(candidate):
            return tuple(candidate)
    assert best_order is not None
    return tuple(_repair_planet_type_order(best_order))


def _fairness_score(planet_types: Sequence[str]) -> int:
    score = 0
    if first_five_include_recovery(planet_types):
        score += 10
    score -= sum(
        1
        for index in range(2, len(planet_types))
        if planet_types[index] == planet_types[index - 1] == planet_types[index - 2]
    )
    return score


def _repair_planet_type_order(planet_types: Sequence[str]) -> list[str]:
    repaired = list(planet_types)
    if not first_five_include_recovery(repaired):
        recovery_index = next(
            index
            for index, planet_type in enumerate(repaired)
            if planet_type in (PLANET_TYPE_FOREST, PLANET_TYPE_ROCK)
        )
        repaired[4], repaired[recovery_index] = repaired[recovery_index], repaired[4]
    for index in range(2, len(repaired)):
        if repaired[index] != repaired[index - 1] or repaired[index] != repaired[index - 2]:
            continue
        swap_index = next(
            candidate_index
            for candidate_index in range(index + 1, len(repaired))
            if repaired[candidate_index] != repaired[index - 1]
        )
        repaired[index], repaired[swap_index] = repaired[swap_index], repaired[index]
    return repaired


def difficulty_for_index(index: int, total: int) -> float:
    progress = index / max(total - 1, 1)
    return 1.0 + progress * 0.75


def difficulty_for_planet_index(index: int, total: int = COURSE_PLANET_COUNT) -> float:
    return difficulty_for_index(index, total)


def difficulty_for_gap_index(index: int, total: int = COURSE_PLANET_COUNT - 1) -> float:
    return difficulty_for_index(index, total)


def create_course_planets(planet_type_order: Sequence[str]) -> list[Planet]:
    planets: list[Planet] = []
    x_lanes = (0.40, 0.70, 0.30, 0.55, 0.22, 0.78, 0.42, 0.62, 0.26, 0.74)
    radii = (20.0, 18.0, 22.0, 20.0, 24.0, 17.0)
    for index, planet_type in enumerate(planet_type_order):
        radius = radii[index % len(radii)]
        x = WIDTH * x_lanes[index % len(x_lanes)]
        x = max(PLANET_X_MIN, min(PLANET_X_MAX, x))
        y = COURSE_START_Y - index * PLANET_BASE_SPACING_Y - index * index * PLANET_SPACING_Y_GROWTH
        direction = -1.0 if index % 2 else 1.0
        speed = direction * (0.08 + (index % 5) * 0.025)
        spec = planet_type_spec(planet_type)
        planets.append(
            Planet(
                position=Vec2(x, y),
                velocity=Vec2(speed, 0.0),
                radius=radius,
                mass=radius * 135 + (index % 4) * 160,
                color=spec.color,
                gravity_well_radius=radius * 5 + (index % 3) * 8,
                planet_type=planet_type,
            )
        )
    return planets


def create_course_gaps(planets: Sequence[Planet]) -> list[CourseGap]:
    gaps: list[CourseGap] = []
    for index in range(max(0, len(planets) - 1)):
        current_planet = planets[index]
        next_planet = planets[index + 1]
        center_pos = (current_planet.position + next_planet.position) * 0.5
        has_meteor = index >= METEOR_SWARM_GAP_START_INDEX and (
            (index - METEOR_SWARM_GAP_START_INDEX) % METEOR_SWARM_EVERY_N_GAPS == 0
        )
        gaps.append(
            CourseGap(
                gap_id=index,
                from_planet_id=index,
                to_planet_id=index + 1,
                center_pos=center_pos,
                width_hint=difficulty_for_gap_index(index, max(1, len(planets) - 1)),
                has_meteor_swarm=has_meteor,
            )
        )
    return gaps


def generate_course(seed: int = COURSE_SEED, mode_key: str | None = DEFAULT_COURSE_MODE_KEY) -> GeneratedCourse:
    mode = course_mode_for_key(mode_key)
    planet_type_order = generate_planet_type_order(seed, mode.appearances_per_type)
    planets = create_course_planets(planet_type_order)
    gaps = create_course_gaps(planets)
    return GeneratedCourse(planets=planets, gaps=gaps, planet_type_order=planet_type_order, seed=seed, mode=mode)


def mark_supply_gap(gaps: Iterable[CourseGap], gap_id: int) -> list[CourseGap]:
    return [
        replace(gap, is_supply_wide_gap=True, width_hint=max(gap.width_hint, SUPPLY_GAP_WIDTH_HINT))
        if gap.gap_id == gap_id
        else gap
        for gap in gaps
    ]


def future_gap_id_for_supply(source_planet_id: int, delay_gaps: int, gaps: Sequence[CourseGap]) -> int | None:
    if not gaps:
        return None
    target_gap_id = source_planet_id + delay_gaps
    if target_gap_id >= len(gaps):
        return None
    return target_gap_id
