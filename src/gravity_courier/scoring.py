"""Score-related pure helpers for Gravity Courier."""

from __future__ import annotations

from dataclasses import dataclass

from .constants import ASSIST_SPEED_GAIN_THRESHOLD


BASE_ASSIST_SCORE = 100


def is_gravity_assist(
    speed_before: float,
    speed_after: float,
    min_gain: float = ASSIST_SPEED_GAIN_THRESHOLD,
) -> bool:
    """Return whether a speed gain is large enough to count as an assist."""

    return speed_after - speed_before >= min_gain


@dataclass
class GravityAssistState:
    active_planet_id: int | None = None
    entry_speed: float = 0.0


def update_gravity_assist(
    state: GravityAssistState,
    planet_id: int,
    in_gravity_well: bool,
    speed: float,
    min_gain: float = ASSIST_SPEED_GAIN_THRESHOLD,
) -> bool:
    """Update one planet assist state and return True once on successful exit."""

    if in_gravity_well:
        if state.active_planet_id != planet_id:
            state.active_planet_id = planet_id
            state.entry_speed = speed
        return False

    if state.active_planet_id != planet_id:
        return False

    entry_speed = state.entry_speed
    state.active_planet_id = None
    state.entry_speed = 0.0
    return is_gravity_assist(entry_speed, speed, min_gain)


def lap_multiplier(lap: int) -> float:
    """Return the provisional score multiplier for a successful planet lap."""

    if lap <= 1:
        return 1.0
    if lap == 2:
        return 1.5
    if lap == 3:
        return 2.0
    return 2.0 + 0.25 * (lap - 3)


def score_gain_for_assist(
    lap: int,
    planet_bonus_multiplier: float = 1.0,
    base_assist_score: int = BASE_ASSIST_SCORE,
) -> int:
    """Return provisional score gain for one successful swing-by assist."""

    score = base_assist_score * lap_multiplier(lap) * planet_bonus_multiplier
    return int(round(score))


def lap_display_text(lap: int) -> str:
    """Return the compact planet lap label used in the portrait playfield."""

    if lap <= 0:
        return ""
    if lap >= 3:
        return "3+"
    return str(lap)


def cheer_stage_for_lap(lap: int) -> int:
    """Map lap count to the 3-stage cheer presentation."""

    if lap <= 1:
        return 1
    if lap == 2:
        return 2
    return 3


def cheer_text_for_stage(stage: int) -> str:
    """Return ASCII-only first-pass cheer text for Pyxel compatibility."""

    if stage <= 1:
        return "WAA!"
    if stage == 2:
        return "CLAP! CLAP!"
    return "WOOO! WHISTLE!"
