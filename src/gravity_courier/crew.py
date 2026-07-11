"""Crew growth helpers for Gravity Courier."""

from __future__ import annotations

from .constants import CREW_JOIN_SEQUENCE, MAX_SUPPLY_TIERS_PER_TYPE
from .planet_types import (
    PLANET_TYPE_FOREST,
    PLANET_TYPE_IRON,
    PLANET_TYPE_ROCK,
    PLANET_TYPE_WATER,
    PLANET_TYPE_WIND,
)
from .residents import resident_for_planet_type

CREW_PLANET_TYPES = (
    PLANET_TYPE_WIND,
    PLANET_TYPE_IRON,
    PLANET_TYPE_WATER,
    PLANET_TYPE_FOREST,
    PLANET_TYPE_ROCK,
)


def initial_crew_count_by_type() -> dict[str, int]:
    return {planet_type: 0 for planet_type in CREW_PLANET_TYPES}


def initial_supply_success_tier_by_type() -> dict[str, int]:
    return {planet_type: 0 for planet_type in CREW_PLANET_TYPES}


def crew_join_count_for_tier(tier: int) -> int:
    if tier < 0 or tier >= MAX_SUPPLY_TIERS_PER_TYPE:
        return 0
    return CREW_JOIN_SEQUENCE[tier]


def apply_crew_join(
    crew_count_by_type: dict[str, int],
    supply_success_tier_by_type: dict[str, int],
    planet_type: str,
) -> int:
    if planet_type not in crew_count_by_type:
        return 0
    tier = supply_success_tier_by_type.get(planet_type, 0)
    join_count = crew_join_count_for_tier(tier)
    if join_count <= 0:
        supply_success_tier_by_type[planet_type] = MAX_SUPPLY_TIERS_PER_TYPE
        return 0
    crew_count_by_type[planet_type] += join_count
    supply_success_tier_by_type[planet_type] = min(MAX_SUPPLY_TIERS_PER_TYPE, tier + 1)
    return join_count


def total_joined_crew(crew_count_by_type: dict[str, int]) -> int:
    return sum(crew_count_by_type.get(planet_type, 0) for planet_type in CREW_PLANET_TYPES)


def compact_crew_counts(crew_count_by_type: dict[str, int]) -> tuple[tuple[str, int], ...]:
    return tuple(
        (resident_for_planet_type(planet_type).short_label, crew_count_by_type.get(planet_type, 0))
        for planet_type in CREW_PLANET_TYPES
    )


def representative_crew_types(crew_count_by_type: dict[str, int], max_types: int = 5) -> tuple[str, ...]:
    return tuple(
        planet_type
        for planet_type in CREW_PLANET_TYPES
        if crew_count_by_type.get(planet_type, 0) > 0
    )[:max_types]
