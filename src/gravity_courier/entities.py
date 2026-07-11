"""Small data structures for Gravity Courier."""

from __future__ import annotations

from dataclasses import dataclass, field
from math import atan2, cos, hypot, sin


@dataclass(frozen=True)
class Vec2:
    x: float = 0.0
    y: float = 0.0

    def __add__(self, other: "Vec2") -> "Vec2":
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vec2") -> "Vec2":
        return Vec2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> "Vec2":
        return Vec2(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar: float) -> "Vec2":
        return Vec2(self.x / scalar, self.y / scalar)

    def length(self) -> float:
        return hypot(self.x, self.y)

    def distance_to(self, other: "Vec2") -> float:
        return (self - other).length()

    def normalized(self) -> "Vec2":
        length = self.length()
        if length <= 0.0:
            return Vec2()
        return self / length

    def angle(self) -> float:
        return atan2(self.y, self.x)


def from_angle(angle: float) -> Vec2:
    return Vec2(cos(angle), sin(angle))


@dataclass
class Rocket:
    position: Vec2 = field(default_factory=Vec2)
    velocity: Vec2 = field(default_factory=Vec2)
    angle: float = 0.0
    fuel: float = 100.0
    hp: int = 3
    max_hp: int = 3
    shield: int = 0
    max_shield: int = 3
    damage_cooldown: int = 0
    crashed: bool = False
    lost: bool = False
    max_distance: float = 0.0

    def copy(self) -> "Rocket":
        return Rocket(
            position=self.position,
            velocity=self.velocity,
            angle=self.angle,
            fuel=self.fuel,
            hp=self.hp,
            max_hp=self.max_hp,
            shield=self.shield,
            max_shield=self.max_shield,
            damage_cooldown=self.damage_cooldown,
            crashed=self.crashed,
            lost=self.lost,
            max_distance=self.max_distance,
        )


@dataclass(frozen=True)
class Planet:
    position: Vec2
    mass: float
    radius: float
    gravity_well_radius: float
    velocity: Vec2 = field(default_factory=Vec2)
    color: int = 10
    planet_type: str = "rock"
    gravity_multiplier: float = 1.0

    @property
    def gravity_radius(self) -> float:
        return self.gravity_well_radius
