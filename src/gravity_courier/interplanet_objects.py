"""Interplanet obstacles and normal collectibles for Gravity Courier."""

from __future__ import annotations

from dataclasses import dataclass, replace
from collections.abc import Sequence

from .constants import (
    ASTEROID_DAMAGE,
    ASTEROID_DRIFT_SPEED,
    ASTEROID_RADIUS,
    CROSSING_ROCKET_DAMAGE,
    CROSSING_ROCKET_LIFETIME_FRAMES,
    CROSSING_ROCKET_RADIUS,
    CROSSING_ROCKET_SPEED,
    CROSSING_ROCKET_WARNING_FRAMES,
    INTERPLANET_OBJECT_DESPAWN_MARGIN,
    SUPPLY_ITEM_FUEL_RATIO,
    SUPPLY_ITEM_RADIUS,
    SUPPLY_ITEM_SCORE,
    WIDTH,
)
from .entities import Planet, Rocket, Vec2

OBJECT_KIND_FLOATING_ASTEROID = "floating_asteroid"
OBJECT_KIND_CROSSING_ROCKET = "crossing_rocket"
OBJECT_KIND_SUPPLY_ITEM = "supply_item"


@dataclass(frozen=True)
class InterplanetObject:
    object_id: int
    kind: str
    pos: Vec2
    vel: Vec2 = Vec2()
    radius: float = 8.0
    active: bool = True
    collected: bool = False
    color: int = 7
    damage: int = 0
    score_value: int = 0
    fuel_restore_ratio: float = 0.0
    lifetime: int | None = None
    warning_timer: int = 0


@dataclass(frozen=True)
class DamageResult:
    damaged: bool
    shield_used: int = 0
    hp_lost: int = 0
    crashed: bool = False


@dataclass(frozen=True)
class SupplyCollectionResult:
    collected: bool
    score_gain: int = 0
    fuel_gain: float = 0.0


def update_interplanet_object(obj: InterplanetObject) -> InterplanetObject:
    """Advance one object by one frame."""
    if not obj.active or obj.collected:
        return obj
    if obj.warning_timer > 0:
        return replace(obj, warning_timer=obj.warning_timer - 1)

    next_lifetime = None if obj.lifetime is None else obj.lifetime - 1
    next_obj = replace(obj, pos=obj.pos + obj.vel, lifetime=next_lifetime)
    if next_lifetime is not None and next_lifetime <= 0:
        return replace(next_obj, active=False)
    if obj.kind == OBJECT_KIND_CROSSING_ROCKET and crossing_rocket_out_of_range(next_obj):
        return replace(next_obj, active=False)
    return next_obj


def crossing_rocket_out_of_range(obj: InterplanetObject) -> bool:
    margin = INTERPLANET_OBJECT_DESPAWN_MARGIN
    return obj.pos.x < -margin or obj.pos.x > WIDTH + margin


def object_can_collide(obj: InterplanetObject) -> bool:
    return obj.active and not obj.collected and obj.warning_timer <= 0


def overlaps_circle(obj: InterplanetObject, pos: Vec2, radius: float) -> bool:
    if not object_can_collide(obj):
        return False
    collision_radius = obj.radius + radius
    return obj.pos.distance_squared_to(pos) <= collision_radius * collision_radius


def collect_supply_item(obj: InterplanetObject) -> tuple[InterplanetObject, SupplyCollectionResult]:
    if obj.kind != OBJECT_KIND_SUPPLY_ITEM or not object_can_collide(obj):
        return obj, SupplyCollectionResult(collected=False)
    return (
        replace(obj, active=False, collected=True),
        SupplyCollectionResult(
            collected=True,
            score_gain=obj.score_value,
            fuel_gain=obj.fuel_restore_ratio,
        ),
    )


def apply_supply_reward(
    rocket: Rocket,
    current_score: int,
    result: SupplyCollectionResult,
    max_fuel: float,
) -> tuple[int, float]:
    if not result.collected:
        return current_score, rocket.fuel
    next_score = current_score + result.score_gain
    next_fuel = min(max_fuel, rocket.fuel + max_fuel * result.fuel_gain)
    return next_score, next_fuel


def make_floating_asteroid(object_id: int, pos: Vec2, drift_x: float = 0.0) -> InterplanetObject:
    return InterplanetObject(
        object_id=object_id,
        kind=OBJECT_KIND_FLOATING_ASTEROID,
        pos=pos,
        vel=Vec2(drift_x, 0.0),
        radius=ASTEROID_RADIUS,
        color=13,
        damage=ASTEROID_DAMAGE,
    )


def make_crossing_rocket(
    object_id: int,
    pos: Vec2,
    direction: int = 1,
    warning_timer: int = CROSSING_ROCKET_WARNING_FRAMES,
) -> InterplanetObject:
    speed = CROSSING_ROCKET_SPEED if direction >= 0 else -CROSSING_ROCKET_SPEED
    return InterplanetObject(
        object_id=object_id,
        kind=OBJECT_KIND_CROSSING_ROCKET,
        pos=pos,
        vel=Vec2(speed, 0.0),
        radius=CROSSING_ROCKET_RADIUS,
        color=8,
        damage=CROSSING_ROCKET_DAMAGE,
        lifetime=CROSSING_ROCKET_LIFETIME_FRAMES,
        warning_timer=warning_timer,
    )


def make_supply_item(object_id: int, pos: Vec2) -> InterplanetObject:
    return InterplanetObject(
        object_id=object_id,
        kind=OBJECT_KIND_SUPPLY_ITEM,
        pos=pos,
        radius=SUPPLY_ITEM_RADIUS,
        color=11,
        score_value=SUPPLY_ITEM_SCORE,
        fuel_restore_ratio=SUPPLY_ITEM_FUEL_RATIO,
    )


def create_initial_interplanet_objects(planets: list[Planet], gaps: Sequence[object] | None = None) -> list[InterplanetObject]:
    """Create deterministic interplanet objects for the current course."""
    if len(planets) < 2:
        return []

    def gap_y(index: int) -> float:
        if gaps is not None and index < len(gaps):
            center_pos = getattr(gaps[index], "center_pos", None)
            if center_pos is not None:
                return center_pos.y
        upper_index = min(index + 1, len(planets) - 1)
        return (planets[index].position.y + planets[upper_index].position.y) * 0.5

    objects = [
        make_supply_item(1, Vec2(WIDTH * 0.34, gap_y(0) + 28.0)),
        make_floating_asteroid(2, Vec2(WIDTH * 0.66, gap_y(0) - 12.0), ASTEROID_DRIFT_SPEED),
    ]
    if len(planets) >= 3:
        objects.extend(
            [
                make_crossing_rocket(3, Vec2(-72.0, gap_y(1)), direction=1),
                make_floating_asteroid(4, Vec2(WIDTH * 0.26, gap_y(1) - 34.0), -ASTEROID_DRIFT_SPEED),
            ]
        )
    if len(planets) >= 4:
        objects.append(make_supply_item(5, Vec2(WIDTH * 0.72, gap_y(2) + 16.0)))
    if len(planets) >= 5:
        objects.append(make_floating_asteroid(6, Vec2(WIDTH * 0.52, gap_y(3)), 0.0))
    if gaps is None:
        return objects

    next_id = 7
    for gap_index, gap in enumerate(gaps[4:14], start=4):
        if getattr(gap, "is_supply_wide_gap", False):
            continue
        difficulty = max(1.0, float(getattr(gap, "width_hint", 1.0)))
        if gap_index % 3 == 0:
            objects.append(
                make_crossing_rocket(
                    next_id,
                    Vec2(-72.0 if gap_index % 2 == 0 else WIDTH + 72.0, gap_y(gap_index)),
                    direction=1 if gap_index % 2 == 0 else -1,
                )
            )
            next_id += 1
        if gap_index % 4 == 0:
            drift = ASTEROID_DRIFT_SPEED * difficulty * (1 if gap_index % 2 == 0 else -1)
            objects.append(make_floating_asteroid(next_id, Vec2(WIDTH * 0.50, gap_y(gap_index) - 24.0), drift))
            next_id += 1
        if gap_index % 5 == 0:
            objects.append(make_supply_item(next_id, Vec2(WIDTH * 0.28 + (gap_index % 2) * WIDTH * 0.42, gap_y(gap_index) + 18.0)))
            next_id += 1
    return objects
