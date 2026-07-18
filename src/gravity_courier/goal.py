"""Final goal and journey progress helpers."""

from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Sequence

from .constants import (
    FINAL_GOAL_ARRIVAL_RADIUS,
    FINAL_GOAL_RADIUS,
    FINAL_GOAL_SPACING_Y,
    WIDTH,
)
from .entities import Planet, Vec2


@dataclass(frozen=True)
class FinalGoal:
    position: Vec2
    radius: float = FINAL_GOAL_RADIUS
    arrival_radius: float = FINAL_GOAL_ARRIVAL_RADIUS


def create_final_goal(planets: Sequence[Planet]) -> FinalGoal:
    if not planets:
        return FinalGoal(position=Vec2(WIDTH * 0.5, -FINAL_GOAL_SPACING_Y))
    last_planet = planets[-1]
    return FinalGoal(
        position=Vec2(WIDTH * 0.5, last_planet.position.y - FINAL_GOAL_SPACING_Y),
    )


def reached_final_goal(position: Vec2, goal: FinalGoal) -> bool:
    return position.distance_squared_to(goal.position) <= goal.arrival_radius * goal.arrival_radius


def journey_planet_progress(
    rocket_y: float,
    planets: Sequence[Planet],
    previous_highest_index: int = 0,
) -> int:
    if not planets:
        return 0
    highest_index = max(0, min(previous_highest_index, len(planets) - 1))
    for index, planet in enumerate(planets):
        if rocket_y <= planet.position.y + planet.gravity_well_radius:
            highest_index = max(highest_index, index)
    return highest_index
