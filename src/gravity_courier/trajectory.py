"""Trajectory preview helpers that avoid mutating live rocket state."""

from __future__ import annotations

from collections.abc import Iterable

from .constants import ORBIT_ASSIST_STRENGTH
from .entities import Planet, Rocket, Vec2
from .physics import nearest_orbit_planet, orbit_assist_velocity, step_rocket


def simulate_preview(
    rocket: Rocket,
    planets: Iterable[Planet] = (),
    steps: int = 30,
    dt: float = 1.0,
) -> list[Vec2]:
    """Return future positions for a copied rocket state."""

    preview_rocket = rocket.copy()
    preview_planets = tuple(planets)
    points: list[Vec2] = []
    for _ in range(max(0, steps)):
        preview_rocket = step_rocket(preview_rocket, preview_planets, dt)
        orbit_planet = nearest_orbit_planet(preview_rocket, preview_planets)
        if orbit_planet is not None:
            preview_rocket.velocity = orbit_assist_velocity(
                preview_rocket,
                orbit_planet,
                ORBIT_ASSIST_STRENGTH,
            )
        points.append(preview_rocket.position)
    return points
