"""Resource loading helpers for optional Pyxel assets."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .constants import HERO_SPRITE_COLKEY, RESIDENT_RESOURCE_PATH, RESIDENT_SPRITE_SIZE
from .planet_types import (
    PLANET_TYPE_FOREST,
    PLANET_TYPE_IRON,
    PLANET_TYPE_ROCK,
    PLANET_TYPE_WATER,
    PLANET_TYPE_WIND,
)
from .residents import RESIDENTS_BY_PLANET_TYPE, STAGE_IDLE, STAGE_LABELS, SPRITE_STAGES


HERO_STATE_IDLE = "idle"
HERO_STATE_CHEER = "cheer"
HERO_STATE_RESULT = "result"
HERO_STATES = (HERO_STATE_IDLE, HERO_STATE_CHEER, HERO_STATE_RESULT)
READY_HERO_STATES = (HERO_STATE_IDLE,)
READY_RESIDENT_STAGES = {
    PLANET_TYPE_WIND: (STAGE_IDLE,),
    PLANET_TYPE_IRON: (STAGE_IDLE,),
    PLANET_TYPE_WATER: (STAGE_IDLE,),
    PLANET_TYPE_FOREST: (STAGE_IDLE,),
    PLANET_TYPE_ROCK: (STAGE_IDLE,),
}


@dataclass(frozen=True)
class SpriteRef:
    image_bank: int
    u: int
    v: int
    w: int = RESIDENT_SPRITE_SIZE
    h: int = RESIDENT_SPRITE_SIZE
    colkey: int = HERO_SPRITE_COLKEY


@dataclass(frozen=True)
class ResidentAssetStatus:
    planet_type: str
    stage: int
    stage_label: str
    u: int
    v: int
    ready: bool
    note: str


@dataclass(frozen=True)
class HeroAssetStatus:
    state: str
    u: int
    v: int
    ready: bool
    note: str


@dataclass(frozen=True)
class ResidentResourceState:
    path: Path
    resource_loaded: bool = False
    hero_sprite_available: bool = False
    resident_sprite_available: bool = False
    rocket_sprite_available: bool = False
    hero_ready_states: tuple[str, ...] = ()
    resident_ready_stages: dict[str, tuple[int, ...]] | None = None
    warning: str = ""

    @property
    def sprite_available(self) -> bool:
        return self.resident_sprite_available

    def hero_state_available(self, state: str) -> bool:
        if self.hero_ready_states:
            return self.hero_sprite_available and state in self.hero_ready_states
        return self.hero_sprite_available

    def resident_stage_available(self, planet_type: str, stage: int) -> bool:
        if self.resident_ready_stages is not None:
            return self.resident_sprite_available and stage in self.resident_ready_stages.get(planet_type, ())
        return self.resident_sprite_available


HERO_SPRITE = SpriteRef(image_bank=0, u=0, v=0)
ROCKET_SPRITE = SpriteRef(image_bank=0, u=0, v=192, w=16, h=32)


def resident_asset_inventory(
    ready_stages: dict[str, tuple[int, ...]] | None = None,
) -> list[ResidentAssetStatus]:
    ready_map = READY_RESIDENT_STAGES if ready_stages is None else ready_stages
    rows: list[ResidentAssetStatus] = []
    for planet_type, resident in RESIDENTS_BY_PLANET_TYPE.items():
        if planet_type not in READY_RESIDENT_STAGES:
            continue
        for stage in SPRITE_STAGES:
            sprite = resident.stage_sprites[stage]
            ready = stage in ready_map.get(planet_type, ())
            rows.append(
                ResidentAssetStatus(
                    planet_type=planet_type,
                    stage=stage,
                    stage_label=STAGE_LABELS[stage],
                    u=sprite.u,
                    v=sprite.v,
                    ready=ready,
                    note="ready" if ready else "fallback until authored",
                )
            )
    return rows


def hero_asset_inventory(ready_states: tuple[str, ...] = READY_HERO_STATES) -> list[HeroAssetStatus]:
    return [
        HeroAssetStatus(
            state=state,
            u=HERO_SPRITE.u,
            v=HERO_SPRITE.v,
            ready=state in ready_states,
            note="ready" if state in ready_states else "shares idle/fallback until authored",
        )
        for state in HERO_STATES
    ]


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
        hero_ready_states=READY_HERO_STATES,
        resident_ready_stages=READY_RESIDENT_STAGES,
    )
