"""Pure cut-in state for Gravity Courier."""

from __future__ import annotations

from dataclasses import dataclass

from .constants import CUTIN_DURATION_FRAMES, WIDTH
from .residents import resident_for_planet_type, stage_for_lap

CUTIN_SIDE_LEFT = "left"
CUTIN_SIDE_RIGHT = "right"


@dataclass(frozen=True)
class CutInPayload:
    planet_type: str
    resident_id: str
    resident_name: str
    cheer_stage: int
    lap_count: int
    score_gain: int
    reward_text: str
    main_message: str
    sub_message: str
    cheer_line: str
    side: str
    target_y: int | None = None


def cutin_side_for_planet_x(planet_screen_x: float, screen_width: int = WIDTH) -> str:
    """Choose the side opposite the planet's screen x position."""
    return CUTIN_SIDE_RIGHT if planet_screen_x < screen_width / 2 else CUTIN_SIDE_LEFT


@dataclass
class CutInState:
    active: bool = False
    timer: int = 0
    duration: int = CUTIN_DURATION_FRAMES
    payload: CutInPayload | None = None

    def start(
        self,
        planet_type: str,
        lap_count: int,
        score_gain: int,
        reward_text: str = "",
        main_message: str = "GRAVITY ASSIST!",
        side: str = CUTIN_SIDE_RIGHT,
        target_y: int | None = None,
    ) -> None:
        resident = resident_for_planet_type(planet_type)
        stage = stage_for_lap(lap_count)
        cheer_lines = resident.cheer_lines[stage]
        cheer_line = cheer_lines[0] if cheer_lines else "YEAH!"
        self.active = True
        self.timer = self.duration
        self.payload = CutInPayload(
            planet_type=planet_type,
            resident_id=resident.resident_id,
            resident_name=resident.display_name,
            cheer_stage=stage,
            lap_count=lap_count,
            score_gain=score_gain,
            reward_text=reward_text,
            main_message=main_message,
            sub_message=f"LAP {lap_count if lap_count < 3 else '3+'}  +{score_gain}",
            cheer_line=cheer_line,
            side=side,
            target_y=target_y,
        )

    def tick(self) -> None:
        if not self.active:
            return
        self.timer = max(0, self.timer - 1)
        if self.timer <= 0:
            self.active = False

    def reset(self) -> None:
        self.active = False
        self.timer = 0
        self.payload = None
