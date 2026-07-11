"""Pure physics helpers for Gravity Courier."""

from __future__ import annotations

from collections.abc import Iterable

from .constants import (
    GRAVITY_G,
    GRAVITY_SOFTENING,
    ORBIT_ASSIST_INFLUENCE_RATIO,
    ORBIT_RADIAL_CORRECTION,
    ORBIT_TARGET_RADIUS_RATIO,
    ORBIT_TARGET_SPEED,
    SUB_STEPS,
)
from .entities import Planet, Rocket, Vec2


def gravity_acceleration(
    position: Vec2,
    planet: Planet,
    gravity_strength: float = GRAVITY_G,
    softening: float = GRAVITY_SOFTENING,
) -> Vec2:
    """Return acceleration from one planet toward ``position``."""

    offset = planet.position - position
    raw_distance_sq = offset.x * offset.x + offset.y * offset.y
    if raw_distance_sq <= 0.0:
        return Vec2()

    softened_distance_sq = raw_distance_sq + softening
    scale = gravity_strength * planet.mass * planet.gravity_multiplier / (softened_distance_sq**1.5)
    return offset * scale


def total_gravity_acceleration(position: Vec2, planets: Iterable[Planet]) -> Vec2:
    acceleration = Vec2()
    for planet in planets:
        acceleration = acceleration + gravity_acceleration(position, planet)
    return acceleration


def integrate_rocket(rocket: Rocket, acceleration: Vec2, dt: float) -> Rocket:
    """Advance rocket state with semi-implicit Euler integration."""

    velocity = rocket.velocity + acceleration * dt
    position = rocket.position + velocity * dt
    result = rocket.copy()
    result.velocity = velocity
    result.position = position
    return result


def step_rocket(rocket: Rocket, planets: Iterable[Planet], dt: float = 1.0) -> Rocket:
    """Advance a rocket with substeps for stable readable gravity."""

    next_rocket = rocket.copy()
    sub_dt = dt / max(1, SUB_STEPS)
    for _ in range(max(1, SUB_STEPS)):
        acceleration = total_gravity_acceleration(next_rocket.position, planets)
        next_rocket = integrate_rocket(next_rocket, acceleration, sub_dt)
    return next_rocket


def orbit_assist_velocity(
    rocket: Rocket,
    planet: Planet,
    strength: float,
    target_radius: float | None = None,
) -> Vec2:
    radial = rocket.position - planet.position
    distance = radial.length()
    if distance <= planet.radius + 4.0:
        return rocket.velocity

    influence_radius = planet.gravity_well_radius * ORBIT_ASSIST_INFLUENCE_RATIO
    if distance >= influence_radius:
        return rocket.velocity

    radial_dir = radial.normalized()
    relative_velocity = rocket.velocity - planet.velocity
    angular_motion = radial_dir.x * relative_velocity.y - radial_dir.y * relative_velocity.x
    orbit_sign = 1.0 if angular_motion >= 0.0 else -1.0
    tangent = Vec2(-radial_dir.y * orbit_sign, radial_dir.x * orbit_sign)
    orbit_radius = (
        max(planet.radius + 42.0, planet.gravity_well_radius * ORBIT_TARGET_RADIUS_RATIO)
        if target_radius is None
        else target_radius
    )
    radial_correction = radial_dir * ((orbit_radius - distance) * ORBIT_RADIAL_CORRECTION)
    target_speed = max(ORBIT_TARGET_SPEED, relative_velocity.length())
    desired_velocity = planet.velocity + tangent * target_speed + radial_correction
    closeness = max(0.0, min(1.0, 1.0 - distance / influence_radius))
    blend = strength * (0.35 + closeness * 0.65)
    return rocket.velocity * (1.0 - blend) + desired_velocity * blend


def nearest_orbit_planet(rocket: Rocket, planets: Iterable[Planet]) -> Planet | None:
    candidates = [
        planet
        for planet in planets
        if rocket.position.distance_to(planet.position)
        < planet.gravity_well_radius * ORBIT_ASSIST_INFLUENCE_RATIO
    ]
    if not candidates:
        return None
    return min(candidates, key=lambda planet: rocket.position.distance_to(planet.position))


def check_planet_collision(position: Vec2, planets: Iterable[Planet]) -> bool:
    return any(position.distance_to(planet.position) <= planet.radius for planet in planets)
