"""Crossing meteor swarm hazards for Gravity Courier."""

from __future__ import annotations

from dataclasses import dataclass, replace
from collections.abc import Sequence

from .constants import (
    HEIGHT,
    INTERPLANET_OBJECT_DESPAWN_MARGIN,
    METEOR_SWARM_DAMAGE,
    METEOR_SWARM_LIFETIME_FRAMES,
    METEOR_SWARM_METEOR_COUNT,
    METEOR_SWARM_RADIUS,
    METEOR_SWARM_SPEED,
    METEOR_SWARM_WARNING_FRAMES,
    WIDTH,
)
from .course import CourseGap
from .entities import Vec2
from .interplanet_objects import InterplanetObject

OBJECT_KIND_CROSSING_METEOR = "crossing_meteor"


@dataclass(frozen=True)
class MeteorSwarm:
    swarm_id: int
    gap_id: int
    meteors: tuple[InterplanetObject, ...]
    warning_timer: int = METEOR_SWARM_WARNING_FRAMES
    lifetime: int = METEOR_SWARM_LIFETIME_FRAMES
    active: bool = True


def create_meteor_swarm_for_gap(gap: CourseGap, swarm_id: int) -> MeteorSwarm:
    direction = 1 if gap.gap_id % 2 == 0 else -1
    start_x = -48.0 if direction > 0 else WIDTH + 48.0
    speed = METEOR_SWARM_SPEED if direction > 0 else -METEOR_SWARM_SPEED
    meteors: list[InterplanetObject] = []
    for index in range(METEOR_SWARM_METEOR_COUNT):
        y_offset = (index - (METEOR_SWARM_METEOR_COUNT - 1) / 2.0) * 22.0
        x_offset = -index * 18.0 * direction
        meteors.append(
            InterplanetObject(
                object_id=swarm_id * 100 + index,
                kind=OBJECT_KIND_CROSSING_METEOR,
                pos=Vec2(start_x + x_offset, gap.center_pos.y + y_offset),
                vel=Vec2(speed, 0.0),
                radius=METEOR_SWARM_RADIUS,
                color=9,
                damage=METEOR_SWARM_DAMAGE,
                lifetime=METEOR_SWARM_LIFETIME_FRAMES,
                warning_timer=METEOR_SWARM_WARNING_FRAMES,
            )
        )
    return MeteorSwarm(swarm_id=swarm_id, gap_id=gap.gap_id, meteors=tuple(meteors))


def create_meteor_swarms_for_gaps(gaps: Sequence[CourseGap]) -> list[MeteorSwarm]:
    return [
        create_meteor_swarm_for_gap(gap, swarm_id=index + 1)
        for index, gap in enumerate(gaps)
        if gap.has_meteor_swarm
    ]


def update_meteor_swarm(swarm: MeteorSwarm) -> MeteorSwarm:
    if not swarm.active:
        return swarm
    if swarm.warning_timer > 0:
        next_warning = swarm.warning_timer - 1
        meteors = tuple(replace(meteor, warning_timer=next_warning) for meteor in swarm.meteors)
        return replace(swarm, warning_timer=next_warning, meteors=meteors)

    next_lifetime = swarm.lifetime - 1
    meteors = tuple(
        replace(meteor, pos=meteor.pos + meteor.vel, lifetime=next_lifetime, warning_timer=0)
        for meteor in swarm.meteors
    )
    next_swarm = replace(swarm, meteors=meteors, lifetime=next_lifetime)
    if next_lifetime <= 0 or meteor_swarm_out_of_range(next_swarm):
        return replace(next_swarm, active=False)
    return next_swarm


def meteor_swarm_out_of_range(swarm: MeteorSwarm) -> bool:
    margin = INTERPLANET_OBJECT_DESPAWN_MARGIN
    if not swarm.meteors:
        return True
    return all(meteor.pos.x < -margin or meteor.pos.x > WIDTH + margin for meteor in swarm.meteors)


def meteor_warning_y(swarm: MeteorSwarm) -> float:
    if not swarm.meteors:
        return HEIGHT * 0.5
    return sum(meteor.pos.y for meteor in swarm.meteors) / len(swarm.meteors)
