"""Resource loading helpers for optional Pyxel assets."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .constants import HERO_SPRITE_COLKEY, RESIDENT_RESOURCE_PATH, RESIDENT_SPRITE_SIZE


@dataclass(frozen=True)
class SpriteRef:
    image_bank: int
    u: int
    v: int
    w: int = RESIDENT_SPRITE_SIZE
    h: int = RESIDENT_SPRITE_SIZE
    colkey: int = HERO_SPRITE_COLKEY


@dataclass(frozen=True)
class ResidentResourceState:
    path: Path
    resource_loaded: bool = False
    hero_sprite_available: bool = False
    resident_sprite_available: bool = False
    rocket_sprite_available: bool = False
    warning: str = ""

    @property
    def sprite_available(self) -> bool:
        return self.resident_sprite_available


HERO_SPRITE = SpriteRef(image_bank=0, u=0, v=0)
ROCKET_SPRITE = SpriteRef(image_bank=0, u=0, v=192, w=16, h=32)


def resident_resource_exists(path: Path = RESIDENT_RESOURCE_PATH) -> bool:
    return path.exists() and path.is_file()


def load_resident_resources(
    pyxel_module: Any,
    path: Path = RESIDENT_RESOURCE_PATH,
) -> ResidentResourceState:
    """Load optional sprite resources if present, otherwise stay fallback-safe."""

    if not resident_resource_exists(path):
        return ResidentResourceState(path=path)

    try:
        pyxel_module.load(str(path))
    except Exception as exc:  # pragma: no cover - Pyxel errors vary by platform/version.
        return ResidentResourceState(
            path=path,
            resource_loaded=False,
            hero_sprite_available=False,
            resident_sprite_available=False,
            rocket_sprite_available=False,
            warning=f"Could not load resident resource: {exc}",
        )

    return ResidentResourceState(
        path=path,
        resource_loaded=True,
        hero_sprite_available=True,
        resident_sprite_available=True,
        rocket_sprite_available=True,
    )
