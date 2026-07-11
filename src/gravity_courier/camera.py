"""Camera state and world/screen transform placeholders."""

from __future__ import annotations

from dataclasses import dataclass

from .constants import CAMERA_ANCHOR_X_RATIO, CAMERA_ANCHOR_Y_RATIO, CAMERA_SMOOTHING, HEIGHT, WIDTH
from .entities import Vec2


@dataclass
class Camera:
    position: Vec2 = Vec2()
    anchor_x_ratio: float = CAMERA_ANCHOR_X_RATIO
    anchor_y_ratio: float = CAMERA_ANCHOR_Y_RATIO
    smoothing: float = CAMERA_SMOOTHING
    zoom: float = 1.0

    @property
    def anchor(self) -> Vec2:
        return Vec2(WIDTH * self.anchor_x_ratio, HEIGHT * self.anchor_y_ratio)

    def follow(self, target: Vec2) -> None:
        delta = target - self.position
        self.position = self.position + delta * self.smoothing

    def world_to_screen(self, world_position: Vec2) -> Vec2:
        return (world_position - self.position) * self.zoom + self.anchor

    def screen_to_world(self, screen_position: Vec2) -> Vec2:
        return (screen_position - self.anchor) / self.zoom + self.position
