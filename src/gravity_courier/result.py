"""Result-screen scoring and display helpers."""

from __future__ import annotations

from dataclasses import dataclass

from .constants import CREW_SCORE_VALUE, RESULT_RANK_THRESHOLDS, ROCKET_FUEL_MAX
from .crew import total_joined_crew


RESULT_DENSITY_NORMAL = "normal"
RESULT_DENSITY_DENSE = "dense"
RESULT_DENSITY_CROWD = "crowd"


@dataclass(frozen=True)
class ResultSummary:
    course_mode_key: str
    course_mode_label: str
    run_score: int
    crew_bonus: int
    final_score: int
    joined_crew_count: int
    display_crew_count: int
    total_laps: int
    supply_cargo_collected: int
    hp_left: int
    shield_left: int
    fuel_left: int
    rank: str
    crew_density: str


def crew_bonus_for_count(joined_crew_count: int, crew_score_value: int = CREW_SCORE_VALUE) -> int:
    return max(0, joined_crew_count) * crew_score_value


def rank_for_score(score: int, thresholds: tuple[int, int, int, int] = RESULT_RANK_THRESHOLDS) -> str:
    s_threshold, a_threshold, b_threshold, c_threshold = thresholds
    if score >= s_threshold:
        return "S"
    if score >= a_threshold:
        return "A"
    if score >= b_threshold:
        return "B"
    if score >= c_threshold:
        return "C"
    return "D"


def crew_density_for_count(joined_crew_count: int) -> str:
    if joined_crew_count <= 50:
        return RESULT_DENSITY_NORMAL
    if joined_crew_count <= 200:
        return RESULT_DENSITY_DENSE
    return RESULT_DENSITY_CROWD


def build_result_summary(
    run_score: int,
    crew_count_by_type: dict[str, int],
    total_laps: int,
    supply_cargo_collected: int,
    hp_left: int,
    shield_left: int,
    fuel: float,
    course_mode_key: str = "normal",
    course_mode_label: str = "Normal",
    rank_thresholds: tuple[int, int, int, int] = RESULT_RANK_THRESHOLDS,
) -> ResultSummary:
    joined_crew_count = total_joined_crew(crew_count_by_type)
    crew_bonus = crew_bonus_for_count(joined_crew_count)
    final_score = run_score + crew_bonus
    return ResultSummary(
        course_mode_key=course_mode_key,
        course_mode_label=course_mode_label,
        run_score=run_score,
        crew_bonus=crew_bonus,
        final_score=final_score,
        joined_crew_count=joined_crew_count,
        display_crew_count=1 + joined_crew_count,
        total_laps=total_laps,
        supply_cargo_collected=supply_cargo_collected,
        hp_left=max(0, hp_left),
        shield_left=max(0, shield_left),
        fuel_left=int(max(0.0, min(ROCKET_FUEL_MAX, fuel))),
        rank=rank_for_score(final_score, rank_thresholds),
        crew_density=crew_density_for_count(joined_crew_count),
    )
