"""Planet type definitions for Gravity Courier."""

from __future__ import annotations

from dataclasses import dataclass


PLANET_TYPE_WIND = "wind"
PLANET_TYPE_IRON = "iron"
PLANET_TYPE_WATER = "water"
PLANET_TYPE_FOREST = "forest"
PLANET_TYPE_ROCK = "rock"
PLANET_TYPE_BLACK_HOLE = "black_hole"


@dataclass(frozen=True)
class PlanetTypeSpec:
    key: str
    display_name: str
    color: int
    reward_description: str
    reward_feedback_text: str
    debug_label: str


PLANET_TYPE_SPECS: dict[str, PlanetTypeSpec] = {
    PLANET_TYPE_WIND: PlanetTypeSpec(
        key=PLANET_TYPE_WIND,
        display_name="Wind Planet",
        color=12,
        reward_description="Stronger gravity acceleration on this planet",
        reward_feedback_text="WIND BOOST!",
        debug_label="WIND",
    ),
    PLANET_TYPE_IRON: PlanetTypeSpec(
        key=PLANET_TYPE_IRON,
        display_name="Iron Planet",
        color=5,
        reward_description="Shield/defensive capacity gain",
        reward_feedback_text="SHIELD +1",
        debug_label="IRON",
    ),
    PLANET_TYPE_WATER: PlanetTypeSpec(
        key=PLANET_TYPE_WATER,
        display_name="Water Planet",
        color=6,
        reward_description="Temporary score multiplier for future assists",
        reward_feedback_text="SCORE BONUS x1.25",
        debug_label="WATER",
    ),
    PLANET_TYPE_FOREST: PlanetTypeSpec(
        key=PLANET_TYPE_FOREST,
        display_name="Forest Planet",
        color=11,
        reward_description="Propulsion gauge recovery",
        reward_feedback_text="FUEL +25%",
        debug_label="FOREST",
    ),
    PLANET_TYPE_ROCK: PlanetTypeSpec(
        key=PLANET_TYPE_ROCK,
        display_name="Rock Planet",
        color=13,
        reward_description="HP recovery",
        reward_feedback_text="HP +1",
        debug_label="ROCK",
    ),
    PLANET_TYPE_BLACK_HOLE: PlanetTypeSpec(
        key=PLANET_TYPE_BLACK_HOLE,
        display_name="Black Hole",
        color=0,
        reward_description="Future high-risk gravity route",
        reward_feedback_text="GRAVITY SPIKE!",
        debug_label="BLACK",
    ),
}


INITIAL_PLANET_TYPE_SEQUENCE = [
    PLANET_TYPE_WIND,
    PLANET_TYPE_IRON,
    PLANET_TYPE_WATER,
    PLANET_TYPE_FOREST,
    PLANET_TYPE_ROCK,
]


def planet_type_spec(planet_type: str) -> PlanetTypeSpec:
    return PLANET_TYPE_SPECS.get(planet_type, PLANET_TYPE_SPECS[PLANET_TYPE_ROCK])
