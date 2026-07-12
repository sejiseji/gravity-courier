"""Resident registry shared by cut-ins and future crew UI."""

from __future__ import annotations

from dataclasses import dataclass

from .constants import RESIDENT_SPRITE_SIZE, SPRITE_TRANSPARENT_COLKEY
from .planet_types import (
    PLANET_TYPE_BLACK_HOLE,
    PLANET_TYPE_FOREST,
    PLANET_TYPE_IRON,
    PLANET_TYPE_ROCK,
    PLANET_TYPE_WATER,
    PLANET_TYPE_WIND,
)


STAGE_IDLE = 0
STAGE_1 = 1
STAGE_2 = 2
STAGE_3 = 3
CHEER_STAGES = (STAGE_1, STAGE_2, STAGE_3)
SPRITE_STAGES = (STAGE_IDLE, STAGE_1, STAGE_2, STAGE_3)
STAGE_LABELS = {
    STAGE_IDLE: "idle",
    STAGE_1: "cheer1",
    STAGE_2: "cheer2",
    STAGE_3: "cheer3",
}


@dataclass(frozen=True)
class ResidentSprite:
    image_bank: int
    u: int
    v: int
    w: int = RESIDENT_SPRITE_SIZE
    h: int = RESIDENT_SPRITE_SIZE
    colkey: int = SPRITE_TRANSPARENT_COLKEY


@dataclass(frozen=True)
class ResidentDef:
    resident_id: str
    display_name: str
    planet_type: str
    short_label: str
    stage_sprites: dict[int, ResidentSprite]
    cheer_lines: dict[int, tuple[str, ...]]
    fallback_style_id: str


def stage_for_lap(lap: int) -> int:
    if lap <= 1:
        return STAGE_1
    if lap == 2:
        return STAGE_2
    return STAGE_3


def _stage_sprites(row: int) -> dict[int, ResidentSprite]:
    v = row * RESIDENT_SPRITE_SIZE
    sprite = ResidentSprite(0, 0, v)
    return {
        STAGE_IDLE: sprite,
        STAGE_1: sprite,
        STAGE_2: sprite,
        STAGE_3: sprite,
    }


RESIDENTS_BY_PLANET_TYPE: dict[str, ResidentDef] = {
    PLANET_TYPE_WIND: ResidentDef(
        resident_id="wind_gale",
        display_name="Gale",
        planet_type=PLANET_TYPE_WIND,
        short_label="WIND",
        stage_sprites=_stage_sprites(1),
        cheer_lines={
            STAGE_1: ("WAA!", "YEAH!"),
            STAGE_2: ("CLAP! CLAP!", "NICE!"),
            STAGE_3: ("WOOO! WHISTLE!", "WOOO!"),
        },
        fallback_style_id="wind",
    ),
    PLANET_TYPE_IRON: ResidentDef(
        resident_id="iron_bolt",
        display_name="Bolt",
        planet_type=PLANET_TYPE_IRON,
        short_label="IRON",
        stage_sprites=_stage_sprites(2),
        cheer_lines={
            STAGE_1: ("WAA!", "YEAH!"),
            STAGE_2: ("CLAP! CLAP!",),
            STAGE_3: ("WOOO! WHISTLE!", "WOOO!"),
        },
        fallback_style_id="iron",
    ),
    PLANET_TYPE_WATER: ResidentDef(
        resident_id="water_jelly",
        display_name="Jelly",
        planet_type=PLANET_TYPE_WATER,
        short_label="WATER",
        stage_sprites=_stage_sprites(3),
        cheer_lines={
            STAGE_1: ("WAA!", "OOH!"),
            STAGE_2: ("CLAP! CLAP!", "SPLASH!"),
            STAGE_3: ("WOOO! WHISTLE!", "WOOO!"),
        },
        fallback_style_id="water",
    ),
    PLANET_TYPE_FOREST: ResidentDef(
        resident_id="forest_leaf",
        display_name="Leaf",
        planet_type=PLANET_TYPE_FOREST,
        short_label="FOREST",
        stage_sprites=_stage_sprites(4),
        cheer_lines={
            STAGE_1: ("WAA!", "YEAH!"),
            STAGE_2: ("CLAP! CLAP!", "GROW!"),
            STAGE_3: ("WOOO! WHISTLE!", "BLOOM!"),
        },
        fallback_style_id="forest",
    ),
    PLANET_TYPE_ROCK: ResidentDef(
        resident_id="rock_rokka",
        display_name="Rokka",
        planet_type=PLANET_TYPE_ROCK,
        short_label="ROCK",
        stage_sprites=_stage_sprites(5),
        cheer_lines={
            STAGE_1: ("WAA!", "YEAH!"),
            STAGE_2: ("CLAP! CLAP!",),
            STAGE_3: ("WOOO! WHISTLE!", "WOOO!"),
        },
        fallback_style_id="rock",
    ),
    PLANET_TYPE_BLACK_HOLE: ResidentDef(
        resident_id="gravity_unknown",
        display_name="Void",
        planet_type=PLANET_TYPE_BLACK_HOLE,
        short_label="BLACK",
        stage_sprites=_stage_sprites(6),
        cheer_lines={
            STAGE_1: ("...",),
            STAGE_2: ("GRAVITY!",),
            STAGE_3: ("BEYOND!",),
        },
        fallback_style_id="black_hole",
    ),
}

RESIDENTS_BY_ID: dict[str, ResidentDef] = {
    resident.resident_id: resident for resident in RESIDENTS_BY_PLANET_TYPE.values()
}


def resident_for_planet_type(planet_type: str) -> ResidentDef:
    return RESIDENTS_BY_PLANET_TYPE.get(planet_type, RESIDENTS_BY_PLANET_TYPE[PLANET_TYPE_ROCK])


def resident_by_id(resident_id: str) -> ResidentDef | None:
    return RESIDENTS_BY_ID.get(resident_id)
