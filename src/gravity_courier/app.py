"""Pyxel app loop for Gravity Courier."""

from __future__ import annotations

from dataclasses import dataclass, replace
import math
from typing import Any

from .audio import AudioManager
from .camera import Camera
from .constants import (
    ASSIST_FUEL_REWARD,
    ASSIST_MESSAGE_FRAMES,
    ASSIST_EXIT_BOOST,
    ASSIST_EXIT_MIN_SPEED,
    ASSIST_EXIT_RADIAL_WEIGHT,
    ASSIST_MIN_UPWARD_DESTINATION_GAP,
    ASSIST_ORBIT_COOLDOWN_FRAMES,
    ASSIST_SPEED_GAIN_THRESHOLD,
    ASSIST_TRANSFER_ALIGNMENT_DEGREES,
    CUTIN_DURATION_FRAMES,
    CUTIN_MAX_Y_RATIO,
    CUTIN_MIN_Y_RATIO,
    CUTIN_PANEL_HEIGHT,
    CUTIN_PANEL_WIDTH,
    CUTIN_RESIDENT_DRAW_SIZE,
    CUTIN_RESIDENT_SCALE,
    CUTIN_SIDE_MARGIN,
    CUTIN_SLIDE_IN_FRAMES,
    CUTIN_SLIDE_OUT_FRAMES,
    COLLISION_ESCAPE_FRAMES,
    COLLISION_ESCAPE_GRAVITY_SCALE,
    COLLISION_ESCAPE_ORBIT_ASSIST_SCALE,
    COLOR_ALERT,
    COLOR_BACKGROUND,
    COLOR_FLAME,
    COLOR_GRAVITY_WELL,
    COLOR_HUD,
    COLOR_ROCKET,
    COLOR_STAR,
    COLOR_STAR_DIM,
    COLOR_TRAJECTORY,
    CREW_CELEBRATION_FRAMES,
    DEMO_BUTTON_HEIGHT,
    DEMO_BUTTON_WIDTH,
    DEMO_BUTTON_X,
    DEMO_BUTTON_Y,
    DEMO_MAX_SPEED,
    DEMO_ORBIT_MAX_SPEED_MARGIN,
    DEMO_ORBIT_MIN_CLEARANCE,
    DEMO_ORBIT_MIN_RADIUS_RATIO,
    DEMO_ORBIT_RADIUS_RATIO,
    DEMO_ORBIT_SEARCH_RATIO,
    DEMO_ORBIT_SPEED_MARGIN_SCALE,
    DEMO_PASS_OFFSET_RATIO,
    DEMO_RESTART_FRAMES,
    DEMO_STEER_DAMPING,
    DEMO_STEER_GAIN,
    DEMO_TARGET_UPWARD_SPEED,
    DEMO_FUEL_COST,
    DEMO_MIN_SPEED,
    DEMO_ORBIT_LONG_INTERVAL,
    DEMO_ORBIT_LONG_TURNS,
    DEMO_ORBIT_FUEL_COST,
    DEMO_ORBIT_MIN_SPEED,
    DEMO_ORBIT_TURNS,
    FOREST_REWARD_FUEL_RATIO,
    HEIGHT,
    HUD_TEXT_SCALE,
    INTERPLANET_FEEDBACK_FRAMES,
    IRON_REWARD_SHIELD_GAIN,
    ORBIT_ASSIST_INFLUENCE_RATIO,
    ORBIT_ASSIST_STRENGTH,
    ORBIT_DEMO_ASSIST_STRENGTH,
    ORBIT_SPEED_BONUS_BASE,
    ORBIT_SPEED_BONUS_MAX,
    ORBIT_SPEED_BONUS_MAX_SPEED,
    ORBIT_SPEED_BONUS_PER_TURN,
    ORBIT_FOCUS_CUTIN_SCALE,
    ORBIT_FOCUS_LINE_ORBIT_MARGIN,
    ORBIT_FOCUS_LINE_JITTER,
    ORBIT_FOCUS_MAX_LINES,
    ORBIT_FOCUS_MAX_ZOOM,
    ORBIT_FOCUS_MIN_LINES,
    ORBIT_FOCUS_PLANET_SWITCH_RELEASE_FRAMES,
    ORBIT_FOCUS_POSITION_BLEND,
    ORBIT_FOCUS_RELEASE_LERP,
    ORBIT_FOCUS_START_PROGRESS,
    ORBIT_FOCUS_ZOOM_LERP,
    ORBIT_TARGET_SPEED,
    ORBIT_COUNT_LABEL_SCALE,
    ORBIT_TRACK_GUIDE_DECAY_PER_LAP,
    ORBIT_TRACK_GUIDE_MIN_STRENGTH,
    ORBIT_TRACK_GUIDE_RADIAL_CORRECTION,
    ORBIT_TRACK_GUIDE_STRENGTH,
    OFF_COURSE_AWAY_SPEED_THRESHOLD,
    OFF_COURSE_DISTANCE_THRESHOLD,
    OFF_COURSE_MARGIN,
    OFF_COURSE_SAFE_BOTTOM,
    OFF_COURSE_SAFE_TOP,
    OFF_COURSE_STALL_FRAMES,
    LAP_COMPLETION_RADIANS,
    ORBIT_TARGET_RADIUS_RATIO,
    PROFILE_NAME,
    ROCK_REWARD_HP_GAIN,
    ROCKET_DAMAGE_COOLDOWN_FRAMES,
    ROCKET_FUEL_COST,
    ROCKET_FUEL_MAX,
    ROCKET_BRAKE_DAMPING,
    ROCKET_HIGH_SPEED_STEER_BONUS_MAX,
    ROCKET_HIGH_SPEED_STEER_RESPONSE,
    ROCKET_HIGH_SPEED_STEER_THRESHOLD,
    ROCKET_MAX_HP,
    ROCKET_MAX_HORIZONTAL_SPEED,
    ROCKET_MAX_SHIELD,
    ROCKET_STRAFE_POWER,
    ROCKET_THRUST_POWER,
    ROCKET_TURN_RATE,
    ROCKET_TURN_RATE_MAX,
    ROCKET_TURN_SPEED_RESPONSE,
    RESIDENT_RESOURCE_PATH,
    STAR_COUNT,
    SUPPLY_PICKUP_RADIUS_BONUS,
    TOUCH_BRAKE_PULSE_FRAMES,
    TOUCH_BRAKE_PULSE_STRENGTH,
    TOUCH_DRAG_FULL_RESPONSE_PIXELS,
    TOUCH_HIGH_SPEED_REFERENCE,
    TOUCH_HIGH_SPEED_TURN_ASSIST,
    TOUCH_THRUST_PULSE_FRAMES,
    TOUCH_THRUST_PULSE_STRENGTH,
    TOUCH_VERTICAL_SWIPE_THRESHOLD,
    TRAJECTORY_DOT_INTERVAL,
    TRAJECTORY_PREVIEW_ALWAYS_ON,
    TRAJECTORY_STEPS,
    WATER_REWARD_SCORE_MULTIPLIER,
    WATER_REWARD_SCORE_USES,
    WIDTH,
    WIND_REWARD_GRAVITY_MULTIPLIER,
    WORLD_LABEL_SCALE,
)
from .course import (
    COURSE_MODE_HARD,
    COURSE_MODES,
    CourseGap,
    DEFAULT_COURSE_MODE_KEY,
    future_gap_id_for_supply,
    generate_course,
    next_course_mode_key,
    mark_supply_gap,
)
from .crew import (
    CREW_PLANET_TYPES,
    initial_crew_count_by_type,
    initial_supply_success_tier_by_type,
    total_joined_crew,
    apply_crew_join,
)
from .cutin import CUTIN_SIDE_LEFT, CutInState, cutin_side_for_planet_x
from .entities import Planet, Rocket, Vec2, from_angle
from .goal import FinalGoal, create_final_goal, journey_planet_progress, reached_final_goal
from .interplanet_objects import (
    DamageResult,
    InterplanetObject,
    OBJECT_KIND_CROSSING_ROCKET,
    OBJECT_KIND_FLOATING_ASTEROID,
    OBJECT_KIND_SUPPLY_ITEM,
    apply_supply_reward,
    collect_supply_item,
    create_initial_interplanet_objects,
    overlaps_circle,
    update_interplanet_object,
)
from .meteor_swarm import (
    MeteorSwarm,
    create_meteor_swarms_for_gaps,
    meteor_warning_y,
    update_meteor_swarm,
)
from .orbit import consume_completed_laps, wrap_angle_delta
from .physics import nearest_orbit_planet, orbit_assist_velocity, step_rocket
from .planet_types import (
    PLANET_TYPE_BLACK_HOLE,
    PLANET_TYPE_FOREST,
    PLANET_TYPE_IRON,
    PLANET_TYPE_ROCK,
    PLANET_TYPE_WATER,
    PLANET_TYPE_WIND,
    planet_type_spec,
)
from .residents import STAGE_IDLE, resident_by_id, resident_for_planet_type
from .resources import HERO_SPRITE, HERO_STATE_IDLE, ROCKET_SPRITE, ResidentResourceState, load_resident_resources
from .result import (
    RESULT_DENSITY_CROWD,
    RESULT_DENSITY_DENSE,
    RESULT_DENSITY_NORMAL,
    ResultSummary,
    build_result_summary,
)
from .scoring import (
    GravityAssistState,
    cheer_stage_for_lap,
    cheer_text_for_stage,
    lap_display_text,
    score_gain_for_assist,
    update_gravity_assist,
)
from .supply import (
    SUPPLY_STATUS_SPAWNED,
    SupplyShip,
    SupplyShipReservation,
    advance_reserved_gap,
    apply_supply_cargo_reward,
    collect_supply_cargo,
    create_supply_reservation,
    is_reservation_ready_to_spawn,
    make_supply_ship_from_reservation,
    mark_reservation_collected,
    mark_reservation_missed,
    mark_reservation_spawned,
    should_reserve_supply_ship,
    supply_cargo_overlaps,
    update_supply_ship,
)
from .trajectory import simulate_preview


START_POSITION = Vec2(WIDTH * 0.5, HEIGHT * 0.82)
STATE_TITLE = "title"
STATE_PLAYING = "playing"
STATE_CRASHED = "crashed"
STATE_RESULT = "result"
RESULT_TEST_CREW_PRESETS = (12, 50, 51, 200, 201, 635)
GOAL_TEST_APPROACH_DISTANCE = 120.0
GOAL_TEST_APPROACH_SPEED = -1.25
GOAL_TEST_FLICK_THRESHOLD = 24.0


@dataclass(frozen=True)
class ControlIntent:
    rotate_axis: float = 0.0
    thrust_axis: float = 0.0
    brake_axis: float = 0.0
    thrust_pulse: float = 0.0
    brake_pulse: float = 0.0


@dataclass
class TouchControlState:
    active: bool = False
    last_x: float = 0.0
    last_y: float = 0.0
    accumulated_horizontal: float = 0.0
    accumulated_vertical: float = 0.0


PLANET_RENDERERS = {
    PLANET_TYPE_WIND: "_draw_wind_planet",
    PLANET_TYPE_IRON: "_draw_iron_planet",
    PLANET_TYPE_WATER: "_draw_water_planet",
    PLANET_TYPE_FOREST: "_draw_forest_planet",
    PLANET_TYPE_ROCK: "_draw_rock_planet",
    PLANET_TYPE_BLACK_HOLE: "_draw_black_hole_planet",
}
GOAL_TEST_BUTTON_WIDTH = 106
GOAL_TEST_BUTTON_HEIGHT = 32
GOAL_TEST_ARROW_WIDTH = 24
TITLE_BUTTON_WIDTH = 236
TITLE_BUTTON_HEIGHT = 42
TITLE_BUTTON_GAP = 16
TITLE_START_Y = 294
TITLE_MODE_Y = TITLE_START_Y + TITLE_BUTTON_HEIGHT + TITLE_BUTTON_GAP
TITLE_DEMO_Y = TITLE_MODE_Y + TITLE_BUTTON_HEIGHT + TITLE_BUTTON_GAP
TITLE_SOUND_Y = TITLE_DEMO_Y + TITLE_BUTTON_HEIGHT + TITLE_BUTTON_GAP
TITLE_SHOOTING_STAR_INTERVAL_FRAMES = 600
TITLE_SHOOTING_STAR_DURATION_FRAMES = 44
TITLE_SHOOTING_STAR_FIRST_FRAME = 120
TITLE_MENU_START = 0
TITLE_MENU_MODE = 1
TITLE_MENU_DEMO = 2
TITLE_MENU_SOUND = 3
TITLE_MENU_COUNT = 4
RESULT_RETRY_BUTTON_WIDTH = 112
RESULT_RETRY_HARD_BUTTON_WIDTH = 156
RESULT_RETRY_BUTTON_HEIGHT = 28
RESULT_RETRY_BUTTON_GAP = 10
RESULT_TITLE_BUTTON_WIDTH = 250
RESULT_TITLE_BUTTON_HEIGHT = 28
RESULT_TITLE_BUTTON_Y = HEIGHT - 74
RESULT_WELCOME_MESSAGE = "WELCOME TO EARTH, FRIENDS!"


def goal_test_button_rect() -> tuple[int, int, int, int]:
    return (
        WIDTH - GOAL_TEST_BUTTON_WIDTH - 16,
        HEIGHT - 222,
        GOAL_TEST_BUTTON_WIDTH,
        GOAL_TEST_BUTTON_HEIGHT,
    )


def goal_test_left_arrow_rect() -> tuple[int, int, int, int]:
    x, y, _width, height = goal_test_button_rect()
    return (x, y, GOAL_TEST_ARROW_WIDTH, height)


def goal_test_right_arrow_rect() -> tuple[int, int, int, int]:
    x, y, width, height = goal_test_button_rect()
    return (x + width - GOAL_TEST_ARROW_WIDTH, y, GOAL_TEST_ARROW_WIDTH, height)


def goal_test_action_rect() -> tuple[int, int, int, int]:
    x, y, width, height = goal_test_button_rect()
    return (x + GOAL_TEST_ARROW_WIDTH, y, width - GOAL_TEST_ARROW_WIDTH * 2, height)


@dataclass(frozen=True)
class DemoCommand:
    lateral_input: float = 0.0
    boost: bool = False
    brake: bool = False
    target_index: int | None = None
    target_x: float = WIDTH * 0.5
    target_y: float | None = None
    supply_target: bool = False


@dataclass
class OrbitProgress:
    prev_angle: float | None = None
    accumulated_angle: float = 0.0
    turns: float = 0.0
    visit_laps: int = 0
    in_orbit: bool = False
    transfer_ready: bool = False
    transfer_triggered: bool = False


def demo_button_rect() -> tuple[int, int, int, int]:
    return (DEMO_BUTTON_X, DEMO_BUTTON_Y, DEMO_BUTTON_WIDTH, DEMO_BUTTON_HEIGHT)


def title_start_button_rect() -> tuple[int, int, int, int]:
    return ((WIDTH - TITLE_BUTTON_WIDTH) // 2, TITLE_START_Y, TITLE_BUTTON_WIDTH, TITLE_BUTTON_HEIGHT)


def title_mode_button_rect() -> tuple[int, int, int, int]:
    return ((WIDTH - TITLE_BUTTON_WIDTH) // 2, TITLE_MODE_Y, TITLE_BUTTON_WIDTH, TITLE_BUTTON_HEIGHT)


def title_demo_button_rect() -> tuple[int, int, int, int]:
    return ((WIDTH - TITLE_BUTTON_WIDTH) // 2, TITLE_DEMO_Y, TITLE_BUTTON_WIDTH, TITLE_BUTTON_HEIGHT)


def title_sound_button_rect() -> tuple[int, int, int, int]:
    return ((WIDTH - TITLE_BUTTON_WIDTH) // 2, TITLE_SOUND_Y, TITLE_BUTTON_WIDTH, TITLE_BUTTON_HEIGHT)


def title_shooting_star_phase(frame: int) -> int | None:
    cycle_frame = (frame - TITLE_SHOOTING_STAR_FIRST_FRAME) % TITLE_SHOOTING_STAR_INTERVAL_FRAMES
    if 0 <= cycle_frame < TITLE_SHOOTING_STAR_DURATION_FRAMES:
        return cycle_frame
    return None


def result_retry_button_rect() -> tuple[int, int, int, int]:
    total_width = RESULT_RETRY_BUTTON_WIDTH + RESULT_RETRY_BUTTON_GAP + RESULT_RETRY_HARD_BUTTON_WIDTH
    x = (WIDTH - total_width) // 2
    return (x, RESULT_TITLE_BUTTON_Y - RESULT_RETRY_BUTTON_HEIGHT - 6, RESULT_RETRY_BUTTON_WIDTH, RESULT_RETRY_BUTTON_HEIGHT)


def result_retry_hard_button_rect() -> tuple[int, int, int, int]:
    retry_x, y, retry_width, _height = result_retry_button_rect()
    return (
        retry_x + retry_width + RESULT_RETRY_BUTTON_GAP,
        y,
        RESULT_RETRY_HARD_BUTTON_WIDTH,
        RESULT_RETRY_BUTTON_HEIGHT,
    )


def result_title_button_rect() -> tuple[int, int, int, int]:
    return ((WIDTH - RESULT_TITLE_BUTTON_WIDTH) // 2, RESULT_TITLE_BUTTON_Y, RESULT_TITLE_BUTTON_WIDTH, RESULT_TITLE_BUTTON_HEIGHT)


def point_in_rect(x: int, y: int, rect: tuple[int, int, int, int]) -> bool:
    rect_x, rect_y, rect_width, rect_height = rect
    return rect_x <= x < rect_x + rect_width and rect_y <= y < rect_y + rect_height


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def edge_indicator_position(
    target_screen_x: float,
    target_screen_y: float,
    width: int,
    height: int,
    margin: int,
) -> tuple[int, int]:
    center_x = width * 0.5
    center_y = height * 0.5
    dx = target_screen_x - center_x
    dy = target_screen_y - center_y
    if abs(dx) < 0.001 and abs(dy) < 0.001:
        return (int(center_x), int(center_y))

    candidates: list[float] = []
    if dx > 0:
        candidates.append((width - margin - center_x) / dx)
    elif dx < 0:
        candidates.append((margin - center_x) / dx)
    if dy > 0:
        candidates.append((height - margin - center_y) / dy)
    elif dy < 0:
        candidates.append((margin - center_y) / dy)
    scale = min(candidate for candidate in candidates if candidate >= 0.0)
    return (int(round(center_x + dx * scale)), int(round(center_y + dy * scale)))


PIXEL_FONT_3X5: dict[str, tuple[str, ...]] = {
    " ": ("000", "000", "000", "000", "000"),
    "!": ("010", "010", "010", "000", "010"),
    ",": ("000", "000", "000", "010", "100"),
    "+": ("000", "010", "111", "010", "000"),
    "-": ("000", "000", "111", "000", "000"),
    ".": ("000", "000", "000", "000", "010"),
    "/": ("001", "001", "010", "100", "100"),
    "%": ("101", "001", "010", "100", "101"),
    ":": ("000", "010", "000", "010", "000"),
    "?": ("111", "001", "010", "000", "010"),
    "0": ("111", "101", "101", "101", "111"),
    "1": ("010", "110", "010", "010", "111"),
    "2": ("111", "001", "111", "100", "111"),
    "3": ("111", "001", "111", "001", "111"),
    "4": ("101", "101", "111", "001", "001"),
    "5": ("111", "100", "111", "001", "111"),
    "6": ("111", "100", "111", "101", "111"),
    "7": ("111", "001", "010", "010", "010"),
    "8": ("111", "101", "111", "101", "111"),
    "9": ("111", "101", "111", "001", "111"),
    "A": ("010", "101", "111", "101", "101"),
    "B": ("110", "101", "110", "101", "110"),
    "C": ("011", "100", "100", "100", "011"),
    "D": ("110", "101", "101", "101", "110"),
    "E": ("111", "100", "110", "100", "111"),
    "F": ("111", "100", "110", "100", "100"),
    "G": ("011", "100", "101", "101", "011"),
    "H": ("101", "101", "111", "101", "101"),
    "I": ("111", "010", "010", "010", "111"),
    "J": ("001", "001", "001", "101", "010"),
    "K": ("101", "101", "110", "101", "101"),
    "L": ("100", "100", "100", "100", "111"),
    "M": ("101", "111", "111", "101", "101"),
    "N": ("101", "111", "111", "111", "101"),
    "O": ("111", "101", "101", "101", "111"),
    "P": ("110", "101", "110", "100", "100"),
    "Q": ("111", "101", "101", "111", "001"),
    "R": ("110", "101", "110", "101", "101"),
    "S": ("011", "100", "010", "001", "110"),
    "T": ("111", "010", "010", "010", "010"),
    "U": ("101", "101", "101", "101", "111"),
    "V": ("101", "101", "101", "101", "010"),
    "W": ("101", "101", "111", "111", "101"),
    "X": ("101", "101", "010", "101", "101"),
    "Y": ("101", "101", "010", "010", "010"),
    "Z": ("111", "001", "010", "100", "111"),
}


def heading_from_velocity(velocity: Vec2, fallback_angle: float = -math.pi / 2) -> float:
    if velocity.length() <= 0.001:
        return fallback_angle
    return velocity.angle()


def right_of_direction(direction: Vec2) -> Vec2:
    return Vec2(-direction.y, direction.x)


def swingby_exit_velocity(rocket: Rocket, planet: Planet) -> Vec2:
    forward = rocket.velocity.normalized()
    away = (rocket.position - planet.position).normalized()
    if forward.length() <= 0.0:
        forward = away
    if away.length() <= 0.0:
        away = forward
    exit_direction = (forward + away * ASSIST_EXIT_RADIAL_WEIGHT).normalized()
    if exit_direction.length() <= 0.0:
        exit_direction = forward
    boosted = rocket.velocity + exit_direction * ASSIST_EXIT_BOOST
    if boosted.length() < ASSIST_EXIT_MIN_SPEED:
        return exit_direction * ASSIST_EXIT_MIN_SPEED
    return boosted


def find_forward_destination_planet_index(
    rocket: Rocket,
    planets: list[Planet],
    current_index: int,
) -> int | None:
    forward = from_angle(heading_from_velocity(rocket.velocity, rocket.angle))
    if forward.length() <= 0.0:
        return None
    min_alignment = math.cos(math.radians(ASSIST_TRANSFER_ALIGNMENT_DEGREES))

    best_index: int | None = None
    best_vertical_gap = float("inf")
    for index, planet in enumerate(planets):
        if index == current_index:
            continue
        vertical_gap = rocket.position.y - planet.position.y
        if vertical_gap < ASSIST_MIN_UPWARD_DESTINATION_GAP:
            continue
        offset = planet.position - rocket.position
        distance = offset.length()
        if distance <= 0.0:
            continue
        offset_dir = offset / distance
        alignment = forward.x * offset_dir.x + forward.y * offset_dir.y
        if alignment < min_alignment:
            continue
        if vertical_gap < best_vertical_gap:
            best_index = index
            best_vertical_gap = vertical_gap
    return best_index


def demo_orbit_target_ratio(speed: float) -> float:
    speed_margin = min(DEMO_ORBIT_MAX_SPEED_MARGIN, max(0.0, speed) * DEMO_ORBIT_SPEED_MARGIN_SCALE)
    return max(DEMO_ORBIT_MIN_RADIUS_RATIO, DEMO_ORBIT_RADIUS_RATIO - speed_margin)


def demo_orbit_minimum_safe_radius(planet: Planet, rocket_collision_radius: float = 0.0) -> float:
    return planet.radius + rocket_collision_radius + DEMO_ORBIT_MIN_CLEARANCE


def demo_orbit_target_radius(planet: Planet, rocket: Rocket) -> float:
    target_radius = planet.gravity_well_radius * demo_orbit_target_ratio(rocket.velocity.length())
    return max(demo_orbit_minimum_safe_radius(planet), target_radius)


def orbit_track_display_radius(planet: Planet) -> float:
    return max(planet.radius + 42.0, planet.gravity_well_radius * ORBIT_TARGET_RADIUS_RATIO)


def nearest_demo_orbit_planet(
    rocket: Rocket,
    planets: list[Planet],
    skip_indices: set[int] | None = None,
) -> Planet | None:
    skipped = skip_indices or set()
    candidates = [
        planet
        for index, planet in enumerate(planets)
        if index not in skipped
        and rocket.position.distance_to(planet.position) < planet.gravity_well_radius * DEMO_ORBIT_SEARCH_RATIO
    ]
    if not candidates:
        return None
    return min(candidates, key=lambda planet: rocket.position.distance_to(planet.position))


def create_initial_planets() -> list[Planet]:
    return generate_course(mode_key=DEFAULT_COURSE_MODE_KEY).planets


def choose_demo_command(
    rocket: Rocket,
    planets: list[Planet],
    skip_indices: set[int] | None = None,
) -> DemoCommand:
    target_index = find_next_demo_planet_index(rocket, planets, skip_indices)
    if target_index is None:
        return DemoCommand(boost=rocket.velocity.y > DEMO_TARGET_UPWARD_SPEED)

    planet = planets[target_index]
    side = 1.0 if target_index % 2 == 0 else -1.0
    target_x = planet.position.x + side * planet.gravity_well_radius * DEMO_PASS_OFFSET_RATIO
    target_x = max(48.0, min(WIDTH - 48.0, target_x))
    dx = target_x - rocket.position.x
    lateral_input = dx * DEMO_STEER_GAIN - rocket.velocity.x * DEMO_STEER_DAMPING
    close_brake = False
    for planet in planets:
        distance = rocket.position.distance_to(planet.position)
        avoid_radius = planet.gravity_well_radius * 0.72
        if distance <= 0.0 or distance >= avoid_radius:
            continue
        away = 1.0 if rocket.position.x >= planet.position.x else -1.0
        lateral_input += away * (1.0 - distance / avoid_radius) * 1.4
        if distance < planet.radius + 48.0:
            target_x = planet.position.x + away * (planet.radius + 70.0)
            target_x = max(48.0, min(WIDTH - 48.0, target_x))
            lateral_input = away
            close_brake = True
    lateral_input = max(-1.0, min(1.0, lateral_input))
    speed = rocket.velocity.length()
    boost = (rocket.velocity.y > DEMO_TARGET_UPWARD_SPEED or speed < DEMO_MIN_SPEED) and speed < DEMO_MAX_SPEED
    brake = speed > DEMO_MAX_SPEED or close_brake
    return DemoCommand(
        lateral_input=lateral_input,
        boost=boost,
        brake=brake,
        target_index=target_index,
        target_x=target_x,
    )


def choose_demo_supply_command(rocket: Rocket, supply_ships: list[SupplyShip]) -> DemoCommand | None:
    targets = [
        ship.cargo_pos
        for ship in supply_ships
        if ship.active and ship.cargo_active and not ship.cargo_collected and ship.warning_timer <= 0
    ]
    if not targets:
        return None
    return demo_pickup_command_for_target(rocket, min(targets, key=rocket.position.distance_to))


def choose_demo_pickup_command(
    rocket: Rocket,
    supply_ships: list[SupplyShip],
) -> DemoCommand | None:
    return choose_demo_supply_command(rocket, supply_ships)


def demo_pickup_command_for_target(rocket: Rocket, target: Vec2) -> DemoCommand:
    dx = target.x - rocket.position.x
    dy = target.y - rocket.position.y
    lateral_input = dx * DEMO_STEER_GAIN * 1.45 - rocket.velocity.x * DEMO_STEER_DAMPING * 1.25
    lateral_input = max(-1.0, min(1.0, lateral_input))
    speed = rocket.velocity.length()
    boost = (dy < -36.0 or speed < DEMO_MIN_SPEED) and speed < DEMO_MAX_SPEED * 0.82
    brake = abs(dx) > 34.0 or speed > DEMO_MAX_SPEED * 0.72 or dy > 24.0
    return DemoCommand(
        lateral_input=lateral_input,
        boost=boost,
        brake=brake,
        target_x=target.x,
        target_y=target.y,
        supply_target=True,
    )


def find_next_demo_planet_index(
    rocket: Rocket,
    planets: list[Planet],
    skip_indices: set[int] | None = None,
) -> int | None:
    skip_indices = skip_indices or set()
    candidates = [
        (index, planet)
        for index, planet in enumerate(planets)
        if index not in skip_indices and planet.position.y < rocket.position.y - 48.0
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda item: item[1].position.y)[0]


class GravityCourierApp:
    """First playable Pyxel prototype for Gravity Courier."""

    def scaffold_message(self) -> str:
        return (
            "Gravity Courier playable prototype ready: "
            f"{PROFILE_NAME} {WIDTH}x{HEIGHT}. "
            "Run with Pyxel installed to launch."
        )

    def __init__(self) -> None:
        self.pyxel: Any | None = None
        self.show_preview = True
        self.show_debug = False
        self.demo_mode = False
        self.title_demo_enabled = False
        self.course_mode_key = DEFAULT_COURSE_MODE_KEY
        self.game_state = STATE_PLAYING
        self.result_summary: ResultSummary | None = None
        self.message_timer = 0
        self.transfer_boost_timer = 0
        self.transfer_boost_target_index: int | None = None
        self.last_score_gain = 0
        self.last_lap_count = 0
        self.cheer_text = ""
        self.reward_feedback_text = ""
        self.water_score_bonus_uses = 0
        self.cutin = CutInState(duration=CUTIN_DURATION_FRAMES)
        self.active_orbit_planet_index: int | None = None
        self.last_lap_event_planet_index: int | None = None
        self.last_transfer_boost_planet_index: int | None = None
        self.last_cutin_side = "-"
        self.course_gaps: list[CourseGap] = []
        self.final_goal = FinalGoal(position=Vec2(WIDTH * 0.5, -HEIGHT))
        self.highest_course_planet_index = 0
        self.interplanet_objects: list[InterplanetObject] = []
        self.meteor_swarms: list[MeteorSwarm] = []
        self.interplanet_feedback_timer = 0
        self.interplanet_feedback_lines: tuple[str, ...] = ()
        self.last_collected_supply_item_id: int | None = None
        self.last_damage_source = "-"
        self.collision_escape_timer = 0
        self.supply_reservations: list[SupplyShipReservation] = []
        self.supply_ships: list[SupplyShip] = []
        self.next_supply_reservation_id = 1
        self.crew_count_by_type = initial_crew_count_by_type()
        self.supply_success_tier_by_type = initial_supply_success_tier_by_type()
        self.supply_ship_chance_count_by_type = initial_supply_success_tier_by_type()
        self.last_supply_reservation_id: int | None = None
        self.last_supply_ship_status = "-"
        self.last_crew_join_count = 0
        self.resident_resources = ResidentResourceState(path=RESIDENT_RESOURCE_PATH)
        self.crew_celebration_timer = 0
        self.crew_type_celebration_timers = initial_supply_success_tier_by_type()
        self.demo_restart_timer = 0
        self.result_test_preset_index = 0
        self.last_result_test_crew_count = 0
        self.thrusting = False
        self.audio = AudioManager()
        self.demo_orbit_index: int | None = None
        self.demo_orbit_prev_angle: float | None = None
        self.demo_orbit_turns = 0.0
        self.demo_orbit_done_indices: set[int] = set()
        self.orbit_speed_boost_timer = 0
        self.orbit_focus_strength = 0.0
        self.orbit_focus_planet_index: int | None = None
        self.orbit_focus_switch_release_timer = 0
        self.off_course_active = False
        self.off_course_target_type = "-"
        self.off_course_target_index: int | None = None
        self.off_course_distance = 0.0
        self.off_course_stall_frames = 0
        self.off_course_previous_distance: float | None = None
        self.off_course_previous_target_key: tuple[str, int | None] | None = None
        self.touch_controls = TouchControlState()
        self.touch_thrust_pulse_frames = 0
        self.touch_brake_pulse_frames = 0
        self.goal_test_flick_active = False
        self.goal_test_flick_last_x = 0.0
        self.title_audio_started_in_update = False
        self.title_menu_index = TITLE_MENU_START
        self.frame = 0
        self.restart()

    def restart(self) -> None:
        self.rocket = Rocket(
            position=START_POSITION,
            velocity=Vec2(0.4, -2.4),
            angle=-math.pi / 2,
            fuel=ROCKET_FUEL_MAX,
            hp=ROCKET_MAX_HP,
            max_hp=ROCKET_MAX_HP,
            shield=0,
            max_shield=ROCKET_MAX_SHIELD,
        )
        self.course = generate_course(mode_key=self.course_mode_key)
        self.planets = self.course.planets
        self.course_gaps = self.course.gaps
        self.final_goal = create_final_goal(self.planets)
        self.highest_course_planet_index = 0
        self.interplanet_objects = create_initial_interplanet_objects(self.planets, self.course_gaps)
        self.meteor_swarms = create_meteor_swarms_for_gaps(self.course_gaps)
        self.camera = Camera(position=self.rocket.position)
        self.assist_states = [GravityAssistState() for _ in self.planets]
        self.planet_lap_counts = [0 for _ in self.planets]
        self.reward_claimed_planet_ids: set[int] = set()
        self.assist_orbit_cooldowns = [0 for _ in self.planets]
        self.orbit_progress = [OrbitProgress() for _ in self.planets]
        self.active_orbit_planet_index = None
        self.assist_count = 0
        self.score = 0
        self.game_state = STATE_PLAYING
        self.result_summary = None
        self.last_score_gain = 0
        self.last_lap_count = 0
        self.cheer_text = ""
        self.reward_feedback_text = ""
        self.water_score_bonus_uses = 0
        self.last_lap_event_planet_index = None
        self.last_transfer_boost_planet_index = None
        self.last_cutin_side = "-"
        self.interplanet_feedback_timer = 0
        self.interplanet_feedback_lines = ()
        self.last_collected_supply_item_id = None
        self.last_damage_source = "-"
        self.collision_escape_timer = 0
        self.supply_reservations = []
        self.supply_ships = []
        self.next_supply_reservation_id = 1
        self.crew_count_by_type = initial_crew_count_by_type()
        self.supply_success_tier_by_type = initial_supply_success_tier_by_type()
        self.supply_ship_chance_count_by_type = initial_supply_success_tier_by_type()
        self.last_supply_reservation_id = None
        self.last_supply_ship_status = "-"
        self.last_crew_join_count = 0
        self.crew_celebration_timer = 0
        self.crew_type_celebration_timers = initial_supply_success_tier_by_type()
        self.cutin.reset()
        self.message_timer = 0
        self.transfer_boost_timer = 0
        self.transfer_boost_target_index = None
        self.demo_restart_timer = 0
        self.thrusting = False
        self.demo_orbit_index = None
        self.demo_orbit_prev_angle = None
        self.demo_orbit_turns = 0.0
        self.demo_orbit_done_indices = set()
        self.orbit_speed_boost_timer = 0
        self.orbit_focus_strength = 0.0
        self.orbit_focus_planet_index = None
        self.orbit_focus_switch_release_timer = 0
        self.off_course_active = False
        self.off_course_target_type = "-"
        self.off_course_target_index = None
        self.off_course_distance = 0.0
        self.off_course_stall_frames = 0
        self.off_course_previous_distance = None
        self.off_course_previous_target_key = None
        self.touch_controls = TouchControlState()
        self.touch_thrust_pulse_frames = 0
        self.touch_brake_pulse_frames = 0
        self.goal_test_flick_active = False
        self.goal_test_flick_last_x = 0.0
        self.camera.zoom = 1.0
        self.frame = 0
        if self.pyxel is not None:
            self.audio.start_bgm(self.pyxel)

    def enter_title(self) -> None:
        self.game_state = STATE_TITLE
        self.demo_mode = False
        self.result_summary = None
        self.thrusting = False
        self.touch_controls = TouchControlState()
        self.touch_thrust_pulse_frames = 0
        self.touch_brake_pulse_frames = 0
        self.title_audio_started_in_update = False
        self.title_menu_index = TITLE_MENU_START
        if self.pyxel is not None:
            self.audio.stop_bgm(self.pyxel)
            self.audio.start_title_bgm(self.pyxel)

    def _start_run(self, demo_mode: bool = False) -> None:
        self.demo_mode = demo_mode
        self.restart()
        self.game_state = STATE_PLAYING

    def _start_title_selected_run(self) -> None:
        self._start_run(demo_mode=self.title_demo_enabled)

    def _toggle_sound(self) -> bool:
        if self.pyxel is None:
            self.audio.enabled = not self.audio.enabled
            return self.audio.enabled
        if self.game_state == STATE_TITLE and not self.audio.enabled:
            self.audio.enabled = True
            self.audio.start_title_bgm(self.pyxel)
            return True
        if self.game_state == STATE_RESULT and not self.audio.enabled:
            self.audio.enabled = True
            self.audio.start_result_bgm(self.pyxel)
            return True
        return self.audio.toggle_enabled(self.pyxel)

    def run(self) -> None:
        try:
            import pyxel
        except ImportError as exc:
            raise RuntimeError("Pyxel is required to launch Gravity Courier.") from exc

        self.pyxel = pyxel
        pyxel.init(WIDTH, HEIGHT, title="Gravity Courier", fps=60)
        if hasattr(pyxel, "mouse"):
            pyxel.mouse(True)
        self.resident_resources = load_resident_resources(pyxel)
        self.audio.configure(pyxel)
        self.enter_title()
        pyxel.run(self.update, self.draw)

    def update(self) -> None:
        pyxel = self.pyxel
        if pyxel is None:
            return

        if pyxel.btnp(pyxel.KEY_ESCAPE):
            pyxel.quit()
        if pyxel.btnp(pyxel.KEY_R) and self.game_state != STATE_TITLE:
            self.restart()
            return
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.show_preview = not self.show_preview
        if pyxel.btnp(pyxel.KEY_D):
            self.show_debug = not self.show_debug
        key_s = getattr(pyxel, "KEY_S", None)
        if key_s is not None and pyxel.btnp(key_s):
            self._toggle_sound()
        if self.game_state == STATE_TITLE:
            self._update_title(pyxel)
            self.frame += 1
            return
        if pyxel.btnp(pyxel.KEY_M) or self._demo_button_pressed(pyxel):
            self.demo_mode = not self.demo_mode
        key_n = getattr(pyxel, "KEY_N", None)
        if key_n is not None and pyxel.btnp(key_n):
            self._toggle_course_mode()
            return
        key_g = getattr(pyxel, "KEY_G", None)
        goal_test_key_pressed = key_g is not None and pyxel.btnp(key_g)
        key_return = getattr(pyxel, "KEY_RETURN", None)
        key_enter = getattr(pyxel, "KEY_ENTER", None)
        goal_test_enter_pressed = (key_return is not None and pyxel.btnp(key_return)) or (
            key_enter is not None and pyxel.btnp(key_enter)
        )
        if self._goal_test_available():
            if goal_test_key_pressed:
                self._cycle_goal_test_preset()
                return
            if self._goal_test_left_arrow_pressed(pyxel):
                self._change_goal_test_preset(-1)
                return
            if self._goal_test_right_arrow_pressed(pyxel) or self._goal_test_button_flicked(pyxel):
                self._change_goal_test_preset(1)
                return
            if goal_test_enter_pressed or self._goal_test_button_pressed(pyxel):
                self._activate_goal_test()
                return
        else:
            self._reset_goal_test_flick()

        if self.game_state == STATE_RESULT:
            if self._result_title_button_pressed(pyxel):
                self.enter_title()
                return
            if self._result_retry_hard_button_pressed(pyxel):
                self._restart_hard_course()
                return
            if self._result_retry_button_pressed(pyxel):
                self.restart()
                return
            self.cutin.tick()
            self.frame += 1
            return

        self.cutin.tick()
        if self.rocket.crashed or self.rocket.lost:
            if self.game_state != STATE_CRASHED:
                self.audio.play_crash(pyxel)
                self.audio.stop_bgm(pyxel)
            self.game_state = STATE_CRASHED
            self.thrusting = False
            self._update_orbit_focus()
            self.camera.follow(self._camera_follow_target())
            if self.demo_mode:
                self.demo_restart_timer += 1
                if self.demo_restart_timer >= DEMO_RESTART_FRAMES:
                    self.restart()
            return

        self.demo_restart_timer = 0
        self._tick_damage_cooldown()
        self._tick_collision_escape_timer()
        self._tick_assist_orbit_cooldowns()
        if self.demo_mode:
            self._sync_supply_zone_waiting_ships()
            orbit_planet = nearest_demo_orbit_planet(
                self.rocket,
                self.planets,
                self.demo_orbit_done_indices,
            )
            orbit_index = self.planets.index(orbit_planet) if orbit_planet in self.planets else None
            if orbit_planet is not None:
                self._apply_demo_orbit(orbit_planet, orbit_index)
            else:
                command = choose_demo_pickup_command(self.rocket, self.supply_ships)
                if command is None:
                    command = choose_demo_command(self.rocket, self.planets, self.demo_orbit_done_indices)
                self._apply_demo_command(command)
        else:
            self._apply_control_intent(self._control_intent(pyxel), spend_fuel=True)

        self._update_planets()
        self.rocket = step_rocket(self.rocket, self._gravity_planets_for_step())
        orbit_assist_strength = ORBIT_DEMO_ASSIST_STRENGTH if self.demo_mode else ORBIT_ASSIST_STRENGTH
        if self.collision_escape_timer > 0:
            orbit_assist_strength *= COLLISION_ESCAPE_ORBIT_ASSIST_SCALE
        self._apply_orbit_assist(orbit_assist_strength)
        if self.demo_mode:
            self._repel_demo_from_completed_planets()
        self._sync_angle_to_velocity()
        if self.demo_mode:
            self._update_demo_orbit_progress()
            self._apply_orbit_speed_bonus()
        else:
            self._update_orbit_progress()
            self._apply_orbit_track_guidance()
            self._apply_orbit_speed_bonus()
        self.rocket.max_distance = max(self.rocket.max_distance, START_POSITION.y - self.rocket.position.y)
        collision_planet = self._colliding_planet()
        if collision_planet is not None:
            self._handle_planet_collision(collision_planet)
        self._update_interplanet_objects()
        self._update_meteor_swarms()
        self._update_supply_ships()
        if self.rocket.position.y > START_POSITION.y + HEIGHT * 0.65:
            self.rocket.lost = True
            self.game_state = STATE_CRASHED

        self._update_journey_progress()
        if self._try_complete_final_goal():
            self._update_orbit_focus()
            self.camera.follow(self._camera_follow_target())
            self.frame += 1
            return

        self._update_off_course_helper()
        self._update_orbit_focus()
        self.camera.follow(self._camera_follow_target())
        self.message_timer = max(0, self.message_timer - 1)
        self.transfer_boost_timer = max(0, self.transfer_boost_timer - 1)
        if self.transfer_boost_timer == 0:
            self.transfer_boost_target_index = None
        self.orbit_speed_boost_timer = max(0, self.orbit_speed_boost_timer - 1)
        self.crew_celebration_timer = max(0, self.crew_celebration_timer - 1)
        self.crew_type_celebration_timers = {
            planet_type: max(0, timer - 1)
            for planet_type, timer in self.crew_type_celebration_timers.items()
        }
        self.interplanet_feedback_timer = max(0, self.interplanet_feedback_timer - 1)
        self.frame += 1

    def _update_title(self, pyxel: Any) -> None:
        self._update_title_ambient(pyxel)
        key_left = getattr(pyxel, "KEY_LEFT", None)
        key_right = getattr(pyxel, "KEY_RIGHT", None)
        key_up = getattr(pyxel, "KEY_UP", None)
        key_down = getattr(pyxel, "KEY_DOWN", None)
        key_z = getattr(pyxel, "KEY_Z", None)
        key_return = getattr(pyxel, "KEY_RETURN", None)
        key_enter = getattr(pyxel, "KEY_ENTER", None)
        if key_up is not None and pyxel.btnp(key_up):
            self._move_title_menu_selection(-1)
            return
        if key_down is not None and pyxel.btnp(key_down):
            self._move_title_menu_selection(1)
            return
        if (
            (key_left is not None and pyxel.btnp(key_left))
            or (key_right is not None and pyxel.btnp(key_right))
        ):
            self._adjust_title_menu_selection()
            return
        if self._title_mode_button_pressed(pyxel):
            self.title_menu_index = TITLE_MENU_MODE
            self._select_next_course_mode()
            return
        if pyxel.btnp(pyxel.KEY_M) or self._title_demo_button_pressed(pyxel):
            self.title_menu_index = TITLE_MENU_DEMO
            self._toggle_title_demo()
            return
        if self._title_sound_button_pressed(pyxel):
            self.title_menu_index = TITLE_MENU_SOUND
            self._toggle_sound()
            return
        start_pressed = self._title_start_button_pressed(pyxel)
        if key_z is not None:
            start_pressed = start_pressed or pyxel.btnp(key_z)
        if start_pressed:
            self._start_title_selected_run()
            return
        if (key_return is not None and pyxel.btnp(key_return)) or (key_enter is not None and pyxel.btnp(key_enter)):
            self._activate_title_menu_selection()

    def _move_title_menu_selection(self, direction: int) -> None:
        self.title_menu_index = (self.title_menu_index + direction) % TITLE_MENU_COUNT

    def _adjust_title_menu_selection(self) -> None:
        if self.title_menu_index == TITLE_MENU_MODE:
            self._select_next_course_mode()
        elif self.title_menu_index == TITLE_MENU_DEMO:
            self._toggle_title_demo()
        elif self.title_menu_index == TITLE_MENU_SOUND:
            self._toggle_sound()

    def _activate_title_menu_selection(self) -> None:
        if self.title_menu_index == TITLE_MENU_START:
            self._start_title_selected_run()

    def _toggle_title_demo(self) -> None:
        self.title_demo_enabled = not self.title_demo_enabled

    def _update_title_ambient(self, pyxel: Any) -> None:
        if not self.title_audio_started_in_update:
            self.audio.stop_bgm(pyxel)
            self.audio.start_title_bgm(pyxel)
            self.title_audio_started_in_update = True
        if title_shooting_star_phase(self.frame) == 0:
            self.audio.play_title_shooting_star(pyxel)

    def _update_journey_progress(self) -> None:
        self.highest_course_planet_index = journey_planet_progress(
            self.rocket.position.y,
            self.planets,
            self.highest_course_planet_index,
        )

    def _next_course_planet_index(self) -> int | None:
        if not self.planets:
            return None
        current = max(0, min(len(self.planets) - 1, self.highest_course_planet_index))
        for index in range(current, len(self.planets)):
            planet = self.planets[index]
            if self.rocket.position.y > planet.position.y - planet.gravity_well_radius:
                return index
        return None

    def _off_course_target(self) -> tuple[str, int | None, Vec2]:
        planet_index = self._next_course_planet_index()
        if planet_index is None:
            return ("goal", None, self.final_goal.position)
        return ("planet", planet_index, self.planets[planet_index].position)

    def _update_off_course_helper(self) -> None:
        if self.game_state != STATE_PLAYING or self.rocket.crashed or self.rocket.lost:
            self._reset_off_course_helper()
            return

        target_type, target_index, target_position = self._off_course_target()
        target_key = (target_type, target_index)
        distance = self.rocket.position.distance_to(target_position)
        if target_key != self.off_course_previous_target_key:
            self.off_course_stall_frames = 0
            self.off_course_previous_distance = distance
            self.off_course_previous_target_key = target_key
        elif self.off_course_previous_distance is not None:
            if distance < self.off_course_previous_distance - 5.0:
                self.off_course_stall_frames = 0
            else:
                self.off_course_stall_frames += 1
            self.off_course_previous_distance = distance

        target_screen = self.camera.world_to_screen(target_position)
        target_visible = self._off_course_target_is_visible(target_screen)
        moving_away = self._rocket_moving_away_from_target(target_position)
        no_planets_visible = not self._has_visible_course_planet()
        needs_recovery_hint = (
            not target_visible
            or distance >= OFF_COURSE_DISTANCE_THRESHOLD
            or self.off_course_stall_frames >= OFF_COURSE_STALL_FRAMES
            or moving_away
        )
        self.off_course_active = no_planets_visible and needs_recovery_hint
        self.off_course_target_type = target_type
        self.off_course_target_index = target_index
        self.off_course_distance = distance

    def _reset_off_course_helper(self) -> None:
        self.off_course_active = False
        self.off_course_target_type = "-"
        self.off_course_target_index = None
        self.off_course_distance = 0.0
        self.off_course_stall_frames = 0
        self.off_course_previous_distance = None
        self.off_course_previous_target_key = None

    def _off_course_target_is_visible(self, target_screen: Vec2) -> bool:
        return (
            OFF_COURSE_MARGIN <= target_screen.x <= WIDTH - OFF_COURSE_MARGIN
            and OFF_COURSE_SAFE_TOP <= target_screen.y <= HEIGHT - OFF_COURSE_SAFE_BOTTOM
        )

    def _has_visible_course_planet(self) -> bool:
        for planet in self.planets:
            screen = self.camera.world_to_screen(planet.position)
            margin = self._world_screen_radius(planet.gravity_well_radius) + 4
            if -margin <= screen.x <= WIDTH + margin and -margin <= screen.y <= HEIGHT + margin:
                return True
        return False

    def _rocket_moving_away_from_target(self, target_position: Vec2) -> bool:
        target_vector = target_position - self.rocket.position
        distance = target_vector.length()
        if distance <= 1.0:
            return False
        direction = target_vector / distance
        away_speed = -(self.rocket.velocity.x * direction.x + self.rocket.velocity.y * direction.y)
        return away_speed >= OFF_COURSE_AWAY_SPEED_THRESHOLD

    def _try_complete_final_goal(self) -> bool:
        if self.game_state != STATE_PLAYING:
            return False
        if self.rocket.crashed or self.rocket.lost:
            return False
        if not reached_final_goal(self.rocket.position, self.final_goal):
            return False
        if self.pyxel is not None:
            self.audio.stop_bgm(self.pyxel)
            self.audio.start_result_bgm(self.pyxel)
            self.audio.play_result(self.pyxel)
        self.game_state = STATE_RESULT
        self.thrusting = False
        self.highest_course_planet_index = max(0, len(self.planets) - 1)
        self.result_summary = build_result_summary(
            self.score,
            self.crew_count_by_type,
            sum(self.planet_lap_counts),
            self._supply_cargo_collected_count(),
            self.rocket.hp,
            self.rocket.shield,
            self.rocket.fuel,
            self.course.mode.key,
            self.course.mode.label,
            self.course.mode.rank_thresholds,
        )
        return True

    def _supply_cargo_collected_count(self) -> int:
        return sum(1 for reservation in self.supply_reservations if reservation.status == "collected")

    def _demo_button_pressed(self, pyxel: Any) -> bool:
        mouse_button = getattr(pyxel, "MOUSE_BUTTON_LEFT", None)
        if mouse_button is None:
            return False
        if not pyxel.btnp(mouse_button):
            return False
        return point_in_rect(int(pyxel.mouse_x), int(pyxel.mouse_y), demo_button_rect())

    def _title_start_button_pressed(self, pyxel: Any) -> bool:
        return self._screen_button_pressed(pyxel, title_start_button_rect())

    def _title_mode_button_pressed(self, pyxel: Any) -> bool:
        return self._screen_button_pressed(pyxel, title_mode_button_rect())

    def _title_demo_button_pressed(self, pyxel: Any) -> bool:
        return self._screen_button_pressed(pyxel, title_demo_button_rect())

    def _title_sound_button_pressed(self, pyxel: Any) -> bool:
        return self._screen_button_pressed(pyxel, title_sound_button_rect())

    def _screen_button_pressed(self, pyxel: Any, rect: tuple[int, int, int, int]) -> bool:
        mouse_button = getattr(pyxel, "MOUSE_BUTTON_LEFT", None)
        if mouse_button is None:
            return False
        if not pyxel.btnp(mouse_button):
            return False
        return point_in_rect(int(pyxel.mouse_x), int(pyxel.mouse_y), rect)

    def _result_retry_button_pressed(self, pyxel: Any) -> bool:
        mouse_button = getattr(pyxel, "MOUSE_BUTTON_LEFT", None)
        if mouse_button is None:
            return False
        if not pyxel.btnp(mouse_button):
            return False
        return point_in_rect(int(pyxel.mouse_x), int(pyxel.mouse_y), result_retry_button_rect())

    def _result_retry_hard_button_pressed(self, pyxel: Any) -> bool:
        mouse_button = getattr(pyxel, "MOUSE_BUTTON_LEFT", None)
        if mouse_button is None:
            return False
        if not pyxel.btnp(mouse_button):
            return False
        return point_in_rect(int(pyxel.mouse_x), int(pyxel.mouse_y), result_retry_hard_button_rect())

    def _result_title_button_pressed(self, pyxel: Any) -> bool:
        mouse_button = getattr(pyxel, "MOUSE_BUTTON_LEFT", None)
        if mouse_button is None:
            return False
        if not pyxel.btnp(mouse_button):
            return False
        return point_in_rect(int(pyxel.mouse_x), int(pyxel.mouse_y), result_title_button_rect())

    def _goal_test_available(self) -> bool:
        return self.game_state == STATE_PLAYING

    def _goal_test_button_pressed(self, pyxel: Any) -> bool:
        return self._goal_test_rect_pressed(pyxel, goal_test_action_rect())

    def _goal_test_left_arrow_pressed(self, pyxel: Any) -> bool:
        return self._goal_test_rect_pressed(pyxel, goal_test_left_arrow_rect())

    def _goal_test_right_arrow_pressed(self, pyxel: Any) -> bool:
        return self._goal_test_rect_pressed(pyxel, goal_test_right_arrow_rect())

    def _goal_test_rect_pressed(self, pyxel: Any, rect: tuple[int, int, int, int]) -> bool:
        mouse_button = getattr(pyxel, "MOUSE_BUTTON_LEFT", None)
        if mouse_button is None:
            return False
        if not pyxel.btnp(mouse_button):
            return False
        return point_in_rect(int(pyxel.mouse_x), int(pyxel.mouse_y), rect)

    def _goal_test_button_flicked(self, pyxel: Any) -> bool:
        mouse_button = getattr(pyxel, "MOUSE_BUTTON_LEFT", None)
        if mouse_button is None or not hasattr(pyxel, "btn"):
            self._reset_goal_test_flick()
            return False
        if not pyxel.btn(mouse_button):
            self._reset_goal_test_flick()
            return False
        x = float(getattr(pyxel, "mouse_x", 0.0))
        y = float(getattr(pyxel, "mouse_y", 0.0))
        if not point_in_rect(int(x), int(y), goal_test_button_rect()):
            self._reset_goal_test_flick()
            return False
        if not self.goal_test_flick_active:
            self.goal_test_flick_active = True
            self.goal_test_flick_last_x = x
            return False
        dx = x - self.goal_test_flick_last_x
        if abs(dx) < GOAL_TEST_FLICK_THRESHOLD:
            return False
        self.goal_test_flick_last_x = x
        return True

    def _reset_goal_test_flick(self) -> None:
        self.goal_test_flick_active = False
        self.goal_test_flick_last_x = 0.0

    def _cycle_goal_test_preset(self) -> None:
        self._change_goal_test_preset(1)

    def _change_goal_test_preset(self, delta: int) -> None:
        self.result_test_preset_index = (self.result_test_preset_index + delta) % len(RESULT_TEST_CREW_PRESETS)
        self.cheer_text = "GOAL TEST"
        self.last_score_gain = RESULT_TEST_CREW_PRESETS[self.result_test_preset_index]
        self.message_timer = ASSIST_MESSAGE_FRAMES

    def _activate_goal_test(self) -> None:
        crew_count = RESULT_TEST_CREW_PRESETS[self.result_test_preset_index]
        self.last_result_test_crew_count = crew_count
        self._assign_result_test_crew(crew_count)

        self.game_state = STATE_PLAYING
        self.rocket.crashed = False
        self.rocket.lost = False
        self.rocket.hp = self.rocket.max_hp
        self.rocket.shield = self.rocket.max_shield
        self.rocket.fuel = ROCKET_FUEL_MAX
        goal_test_offset = self.final_goal.arrival_radius + GOAL_TEST_APPROACH_DISTANCE
        self.rocket.position = self.final_goal.position + Vec2(0.0, goal_test_offset)
        self.rocket.velocity = Vec2(0.0, GOAL_TEST_APPROACH_SPEED)
        self.rocket.angle = -math.pi / 2
        self.rocket.max_distance = max(self.rocket.max_distance, START_POSITION.y - self.rocket.position.y)
        self.score = 10000 + crew_count * 75
        self.planet_lap_counts = [index % 4 for index in range(len(self.planets))]
        self.highest_course_planet_index = max(0, len(self.planets) - 1)
        self.demo_mode = False
        self.thrusting = False
        self.collision_escape_timer = 0
        self.result_summary = None
        self.message_timer = ASSIST_MESSAGE_FRAMES
        self.cheer_text = "GOAL TEST"
        self.last_score_gain = crew_count
        self.last_lap_count = 0
        self.camera.follow(self.rocket.position)

    def _world_screen_radius(self, radius: float) -> int:
        return max(1, int(radius * self.camera.zoom))

    def _orbit_focus_context(self) -> tuple[int, float, int] | None:
        planet_index = self._active_orbit_planet_index()
        if planet_index is None or planet_index >= len(self.planets):
            return None
        if self.demo_mode and planet_index == self.demo_orbit_index:
            turns = self.demo_orbit_turns
            completed_laps = int(turns)
            return planet_index, turns - completed_laps, completed_laps
        if planet_index >= len(self.orbit_progress):
            return None
        progress = self.orbit_progress[planet_index]
        if not progress.in_orbit:
            return None
        current_lap_progress = abs(progress.accumulated_angle) / math.tau
        return planet_index, current_lap_progress, progress.visit_laps

    def _target_orbit_focus_strength(self) -> float:
        context = self._orbit_focus_context()
        if context is None or self.transfer_boost_timer > 0:
            return 0.0
        if self.orbit_focus_switch_release_timer > 0:
            return 0.0
        _planet_index, current_lap_progress, completed_laps = context
        if completed_laps <= 0 and current_lap_progress < ORBIT_FOCUS_START_PROGRESS:
            return 0.0
        lap_progress_component = current_lap_progress * 0.70
        lap_count_component = min(completed_laps * 0.15, 0.45)
        strength = max(0.0, min(1.0, lap_progress_component + lap_count_component))
        if self.cutin.active:
            strength *= ORBIT_FOCUS_CUTIN_SCALE
        return strength

    def _update_orbit_focus(self) -> None:
        self._sync_orbit_focus_planet()
        target_strength = self._target_orbit_focus_strength()
        lerp = ORBIT_FOCUS_ZOOM_LERP if target_strength > self.orbit_focus_strength else ORBIT_FOCUS_RELEASE_LERP
        self.orbit_focus_strength += (target_strength - self.orbit_focus_strength) * lerp
        if self.orbit_focus_strength < 0.001:
            self.orbit_focus_strength = 0.0
        target_zoom = 1.0 + self.orbit_focus_strength * (ORBIT_FOCUS_MAX_ZOOM - 1.0)
        self.camera.zoom += (target_zoom - self.camera.zoom) * lerp
        if abs(self.camera.zoom - 1.0) < 0.001 and self.orbit_focus_strength <= 0.0:
            self.camera.zoom = 1.0
        self.orbit_focus_switch_release_timer = max(0, self.orbit_focus_switch_release_timer - 1)

    def _sync_orbit_focus_planet(self) -> None:
        context = self._orbit_focus_context()
        next_planet_index = context[0] if context is not None else None
        if next_planet_index == self.orbit_focus_planet_index:
            return
        was_focused = self.orbit_focus_planet_index is not None
        self.orbit_focus_planet_index = next_planet_index
        if was_focused or self.camera.zoom > 1.01 or self.orbit_focus_strength > 0.05:
            self.orbit_focus_strength = 0.0
            self.orbit_focus_switch_release_timer = ORBIT_FOCUS_PLANET_SWITCH_RELEASE_FRAMES

    def _camera_follow_target(self) -> Vec2:
        context = self._orbit_focus_context()
        if context is None or self.orbit_focus_strength <= 0.0:
            return self.rocket.position
        planet_index, _current_lap_progress, _completed_laps = context
        planet = self.planets[planet_index]
        midpoint = (self.rocket.position + planet.position) * 0.5
        blend = min(ORBIT_FOCUS_POSITION_BLEND, ORBIT_FOCUS_POSITION_BLEND * self.orbit_focus_strength)
        return self.rocket.position * (1.0 - blend) + midpoint * blend

    def _assign_result_test_crew(self, crew_count: int) -> None:
        base_count = crew_count // len(CREW_PLANET_TYPES)
        remainder = crew_count % len(CREW_PLANET_TYPES)
        self.crew_count_by_type = {
            planet_type: base_count + (1 if index < remainder else 0)
            for index, planet_type in enumerate(CREW_PLANET_TYPES)
        }

    def _toggle_course_mode(self) -> None:
        self._select_next_course_mode()
        self.restart()

    def _select_next_course_mode(self) -> None:
        self.course_mode_key = next_course_mode_key(self.course_mode_key)

    def _restart_hard_course(self) -> None:
        self.course_mode_key = COURSE_MODE_HARD
        self.restart()

    def _control_intent(self, pyxel: Any) -> ControlIntent:
        keyboard = self._keyboard_control_intent(pyxel)
        touch = self._touch_control_intent(pyxel)
        return ControlIntent(
            rotate_axis=clamp(keyboard.rotate_axis + touch.rotate_axis, -1.0, 1.0),
            thrust_axis=clamp(max(keyboard.thrust_axis, touch.thrust_axis), 0.0, 1.0),
            brake_axis=clamp(max(keyboard.brake_axis, touch.brake_axis), 0.0, 1.0),
            thrust_pulse=clamp(max(keyboard.thrust_pulse, touch.thrust_pulse), 0.0, 1.0),
            brake_pulse=clamp(max(keyboard.brake_pulse, touch.brake_pulse), 0.0, 1.0),
        )

    def _keyboard_control_intent(self, pyxel: Any) -> ControlIntent:
        rotate = 0.0
        key_left = getattr(pyxel, "KEY_LEFT", None)
        key_right = getattr(pyxel, "KEY_RIGHT", None)
        key_up = getattr(pyxel, "KEY_UP", None)
        key_down = getattr(pyxel, "KEY_DOWN", None)
        if key_left is not None and pyxel.btn(key_left):
            rotate -= 1.0
        if key_right is not None and pyxel.btn(key_right):
            rotate += 1.0
        return ControlIntent(
            rotate_axis=rotate,
            thrust_axis=1.0 if key_up is not None and pyxel.btn(key_up) else 0.0,
            brake_axis=1.0 if key_down is not None and pyxel.btn(key_down) else 0.0,
        )

    def _touch_control_intent(self, pyxel: Any) -> ControlIntent:
        mouse_button = getattr(pyxel, "MOUSE_BUTTON_LEFT", None)
        if mouse_button is None or not hasattr(pyxel, "btn"):
            self._release_touch_control()
            return self._active_touch_pulse_intent()
        pressed = pyxel.btn(mouse_button)
        x = float(getattr(pyxel, "mouse_x", 0.0))
        y = float(getattr(pyxel, "mouse_y", 0.0))
        if not pressed:
            self._release_touch_control()
            return self._active_touch_pulse_intent()
        if self._touch_on_screen_button(int(x), int(y)):
            self._release_touch_control()
            return self._active_touch_pulse_intent()

        if not self.touch_controls.active:
            self.touch_controls = TouchControlState(active=True, last_x=x, last_y=y)
            return self._active_touch_pulse_intent()

        dx = x - self.touch_controls.last_x
        dy = y - self.touch_controls.last_y
        self.touch_controls.last_x = x
        self.touch_controls.last_y = y
        self.touch_controls.accumulated_horizontal = clamp(
            self.touch_controls.accumulated_horizontal + dx,
            -TOUCH_DRAG_FULL_RESPONSE_PIXELS,
            TOUCH_DRAG_FULL_RESPONSE_PIXELS,
        )
        self.touch_controls.accumulated_vertical += dy
        if self.touch_controls.accumulated_vertical <= -TOUCH_VERTICAL_SWIPE_THRESHOLD:
            self.touch_thrust_pulse_frames = TOUCH_THRUST_PULSE_FRAMES
            self.touch_controls.accumulated_vertical = 0.0
        elif self.touch_controls.accumulated_vertical >= TOUCH_VERTICAL_SWIPE_THRESHOLD:
            self.touch_brake_pulse_frames = TOUCH_BRAKE_PULSE_FRAMES
            self.touch_controls.accumulated_vertical = 0.0

        speed_ratio = clamp(self.rocket.velocity.length() / TOUCH_HIGH_SPEED_REFERENCE, 0.0, 1.0)
        assist = 1.0 + speed_ratio * TOUCH_HIGH_SPEED_TURN_ASSIST
        rotate = clamp(
            self.touch_controls.accumulated_horizontal / TOUCH_DRAG_FULL_RESPONSE_PIXELS * assist,
            -1.0,
            1.0,
        )
        pulse_intent = self._active_touch_pulse_intent()
        return ControlIntent(
            rotate_axis=rotate,
            thrust_pulse=pulse_intent.thrust_pulse,
            brake_pulse=pulse_intent.brake_pulse,
        )

    def _release_touch_control(self) -> None:
        if self.touch_controls.active:
            self.touch_controls = TouchControlState()

    def _touch_on_screen_button(self, x: int, y: int) -> bool:
        if self.game_state == STATE_TITLE:
            return any(
                point_in_rect(x, y, rect)
                for rect in (
                    title_start_button_rect(),
                    title_mode_button_rect(),
                    title_demo_button_rect(),
                    title_sound_button_rect(),
                )
            )
        if self.game_state == STATE_RESULT:
            return any(
                point_in_rect(x, y, rect)
                for rect in (
                    result_title_button_rect(),
                    result_retry_button_rect(),
                    result_retry_hard_button_rect(),
                )
            )
        if point_in_rect(x, y, demo_button_rect()):
            return True
        return self._goal_test_available() and point_in_rect(x, y, goal_test_button_rect())

    def _active_touch_pulse_intent(self) -> ControlIntent:
        thrust = TOUCH_THRUST_PULSE_STRENGTH if self.touch_thrust_pulse_frames > 0 else 0.0
        brake = TOUCH_BRAKE_PULSE_STRENGTH if self.touch_brake_pulse_frames > 0 else 0.0
        self.touch_thrust_pulse_frames = max(0, self.touch_thrust_pulse_frames - 1)
        self.touch_brake_pulse_frames = max(0, self.touch_brake_pulse_frames - 1)
        return ControlIntent(thrust_pulse=thrust, brake_pulse=brake)

    def _apply_control_intent(self, intent: ControlIntent, spend_fuel: bool) -> None:
        thrust_strength = max(intent.thrust_axis, intent.thrust_pulse)
        brake_strength = max(intent.brake_axis, intent.brake_pulse)
        self._apply_controls(
            intent.rotate_axis,
            thrust_strength > 0.0,
            brake_strength > 0.0,
            spend_fuel=spend_fuel,
            boost_strength=thrust_strength,
            brake_strength=brake_strength,
        )

    def _apply_controls(
        self,
        lateral_input: float,
        boost: bool,
        brake: bool,
        spend_fuel: bool,
        boost_strength: float = 1.0,
        brake_strength: float = 1.0,
    ) -> None:
        self.thrusting = False
        lateral_input = clamp(lateral_input, -1.0, 1.0)
        boost_strength = clamp(boost_strength, 0.0, 1.0)
        brake_strength = clamp(brake_strength, 0.0, 1.0)
        forward = from_angle(heading_from_velocity(self.rocket.velocity, self.rocket.angle))
        if lateral_input:
            speed = self.rocket.velocity.length()
            if speed > 0.001:
                high_speed_steer_bonus = min(
                    ROCKET_HIGH_SPEED_STEER_BONUS_MAX,
                    max(0.0, speed - ROCKET_HIGH_SPEED_STEER_THRESHOLD) * ROCKET_HIGH_SPEED_STEER_RESPONSE,
                )
                turn_rate = min(
                    ROCKET_TURN_RATE_MAX + high_speed_steer_bonus,
                    ROCKET_TURN_RATE + speed * ROCKET_TURN_SPEED_RESPONSE + high_speed_steer_bonus,
                )
                self.rocket.velocity = from_angle(
                    self.rocket.velocity.angle() + lateral_input * turn_rate
                ) * speed
            else:
                right = right_of_direction(forward)
                lateral_speed = self.rocket.velocity.x * right.x + self.rocket.velocity.y * right.y
                next_lateral_speed = lateral_speed + lateral_input * ROCKET_STRAFE_POWER
                next_lateral_speed = max(
                    -ROCKET_MAX_HORIZONTAL_SPEED,
                    min(ROCKET_MAX_HORIZONTAL_SPEED, next_lateral_speed),
                )
                self.rocket.velocity = self.rocket.velocity + right * (next_lateral_speed - lateral_speed)
        if boost and self.rocket.fuel > 0.0:
            forward = from_angle(heading_from_velocity(self.rocket.velocity, self.rocket.angle))
            thrust = forward * (ROCKET_THRUST_POWER * boost_strength)
            self.rocket.velocity = self.rocket.velocity + thrust
            if spend_fuel:
                self.rocket.fuel = max(0.0, self.rocket.fuel - ROCKET_FUEL_COST * boost_strength)
            self.thrusting = True
        if brake:
            damping = 1.0 - (1.0 - ROCKET_BRAKE_DAMPING) * brake_strength
            self.rocket.velocity = self.rocket.velocity * damping
        self._sync_angle_to_velocity()

    def _apply_demo_command(self, command: DemoCommand) -> None:
        can_boost = command.boost and self.rocket.fuel > 0.0
        desired_vx = max(-2.2, min(2.2, (command.target_x - self.rocket.position.x) * 0.035))
        if command.supply_target and command.target_y is not None:
            desired_vy = max(-3.2, min(1.2, (command.target_y - self.rocket.position.y) * 0.030))
        else:
            desired_vy = DEMO_TARGET_UPWARD_SPEED if can_boost else -2.25
        if command.brake:
            desired_vx *= 0.65 if not command.supply_target else 0.78
            desired_vy = desired_vy * 0.65 if command.supply_target else -1.85
        self.rocket.velocity = Vec2(
            self.rocket.velocity.x * 0.78 + desired_vx * 0.22,
            self.rocket.velocity.y * 0.82 + desired_vy * 0.18,
        )
        if can_boost:
            self.rocket.fuel = max(0.0, self.rocket.fuel - DEMO_FUEL_COST)
        min_speed_assisted = self._apply_demo_min_speed_assist()
        self._sync_angle_to_velocity()
        self.thrusting = can_boost or min_speed_assisted

    def _apply_demo_min_speed_assist(self) -> bool:
        speed = self.rocket.velocity.length()
        if speed >= DEMO_MIN_SPEED:
            return False
        direction = self.rocket.velocity.normalized()
        if direction.length() <= 0.0:
            direction = Vec2(0.0, -1.0)
        assist = min(0.16, (DEMO_MIN_SPEED - speed) * 0.20)
        self.rocket.velocity = self.rocket.velocity + direction * assist
        return True

    def _apply_demo_orbit(self, planet: Planet, orbit_index: int | None) -> None:
        if orbit_index is not None and self.demo_orbit_index != orbit_index:
            self.demo_orbit_index = orbit_index
            self.demo_orbit_prev_angle = None
            self.demo_orbit_turns = 0.0
            if self.pyxel is not None:
                self.audio.play_orbit_enter(self.pyxel)
        radial = self.rocket.position - planet.position
        if radial.length() <= 0.0:
            return
        radial_dir = radial.normalized()
        relative_velocity = self.rocket.velocity - planet.velocity
        angular_motion = radial_dir.x * relative_velocity.y - radial_dir.y * relative_velocity.x
        orbit_sign = 1.0 if angular_motion >= 0.0 else -1.0
        tangent = Vec2(-radial_dir.y * orbit_sign, radial_dir.x * orbit_sign)
        target_radius = demo_orbit_target_radius(planet, self.rocket)
        radial_correction = radial_dir * ((target_radius - radial.length()) * 0.050)
        orbit_speed = max(DEMO_ORBIT_MIN_SPEED, min(4.2, relative_velocity.length()))
        desired_velocity = planet.velocity + tangent * orbit_speed + radial_correction
        self.rocket.velocity = self.rocket.velocity * 0.76 + desired_velocity * 0.24
        if self.rocket.fuel > 0.0:
            self.rocket.fuel = max(0.0, self.rocket.fuel - DEMO_ORBIT_FUEL_COST)
        self.thrusting = self.rocket.fuel > 0.0
        self._sync_angle_to_velocity()

    def _update_demo_orbit_progress(self) -> None:
        if self.demo_orbit_index is None:
            return
        planet = self.planets[self.demo_orbit_index]
        if self.rocket.position.distance_to(planet.position) >= planet.gravity_well_radius:
            self.demo_orbit_index = None
            self.demo_orbit_prev_angle = None
            self.demo_orbit_turns = 0.0
            return
        radial = self.rocket.position - planet.position
        angle = math.atan2(radial.y, radial.x)
        if self.demo_orbit_prev_angle is None:
            self.demo_orbit_prev_angle = angle
            return
        delta = angle - self.demo_orbit_prev_angle
        while delta > math.pi:
            delta -= math.pi * 2.0
        while delta < -math.pi:
            delta += math.pi * 2.0
        previous_completed_laps = int(self.demo_orbit_turns)
        self.demo_orbit_turns += abs(delta) / (math.pi * 2.0)
        self.demo_orbit_prev_angle = angle
        completed_laps = int(self.demo_orbit_turns) - previous_completed_laps
        for _ in range(max(0, completed_laps)):
            self._handle_lap_completed(self.demo_orbit_index)
        if self.demo_orbit_turns >= self._demo_orbit_turn_target(self.demo_orbit_index):
            completed_index = self.demo_orbit_index
            target_index = find_forward_destination_planet_index(
                self.rocket,
                self.planets,
                completed_index,
            )
            self.demo_orbit_done_indices.add(completed_index)
            self._push_demo_toward_next_planet(completed_index, target_index)
            self.transfer_boost_timer = ASSIST_MESSAGE_FRAMES
            self.transfer_boost_target_index = target_index
            self._trigger_crew_celebration()
            self._advance_supply_reservations_after_transfer()
            self.demo_orbit_index = None
            self.demo_orbit_prev_angle = None
            self.demo_orbit_turns = 0.0

    def _demo_orbit_turn_target(self, planet_index: int) -> float:
        if DEMO_ORBIT_LONG_INTERVAL > 0 and (planet_index + 1) % DEMO_ORBIT_LONG_INTERVAL == 0:
            return DEMO_ORBIT_LONG_TURNS
        return DEMO_ORBIT_TURNS

    def _push_demo_toward_next_planet(self, completed_index: int, next_index: int | None = None) -> None:
        if next_index is None:
            skip_indices = set(self.demo_orbit_done_indices)
            next_index = find_next_demo_planet_index(self.rocket, self.planets, skip_indices)
        if next_index is None:
            transfer_direction = Vec2(0.0, -1.0)
        else:
            transfer_direction = (self.planets[next_index].position - self.rocket.position).normalized()
        completed_planet = self.planets[completed_index]
        away = (self.rocket.position - completed_planet.position).normalized()
        self.rocket.velocity = self.rocket.velocity * 0.30 + transfer_direction * 3.15 + away * 1.20

    def _ensure_orbit_progress_length(self) -> None:
        if len(self.orbit_progress) < len(self.planets):
            self.orbit_progress.extend(
                OrbitProgress() for _ in range(len(self.planets) - len(self.orbit_progress))
            )

    def _ensure_lap_count_length(self) -> None:
        if len(self.planet_lap_counts) < len(self.planets):
            self.planet_lap_counts.extend(0 for _ in range(len(self.planets) - len(self.planet_lap_counts)))

    def _update_orbit_progress(self) -> None:
        self._ensure_orbit_progress_length()
        planet_index = self._current_gravity_well_planet_index()
        if planet_index != self.active_orbit_planet_index:
            if self.active_orbit_planet_index is not None:
                self._finish_orbit_visit(self.active_orbit_planet_index)
            if planet_index is None:
                return
            self._start_orbit_visit(planet_index)
            return

        if planet_index is None:
            return

        progress = self.orbit_progress[planet_index]
        planet = self.planets[planet_index]
        radial = self.rocket.position - planet.position
        angle = math.atan2(radial.y, radial.x)
        completed_laps = self._advance_orbit_progress(progress, angle)
        for _ in range(completed_laps):
            self._handle_lap_completed(planet_index)

    def _current_gravity_well_planet_index(self) -> int | None:
        candidates: list[tuple[float, int]] = []
        for index, planet in enumerate(self.planets):
            if index >= len(self.assist_orbit_cooldowns) or self.assist_orbit_cooldowns[index] > 0:
                continue
            distance = self.rocket.position.distance_to(planet.position)
            if planet.radius + 4.0 < distance <= planet.gravity_well_radius:
                candidates.append((distance, index))
        if not candidates:
            return None
        return min(candidates)[1]

    def _start_orbit_visit(self, planet_index: int) -> None:
        for progress in self.orbit_progress:
            progress.in_orbit = False
        planet = self.planets[planet_index]
        radial = self.rocket.position - planet.position
        self.orbit_progress[planet_index] = OrbitProgress(
            prev_angle=math.atan2(radial.y, radial.x),
            in_orbit=True,
        )
        self.active_orbit_planet_index = planet_index
        if self.pyxel is not None:
            self.audio.play_orbit_enter(self.pyxel)

    def _finish_orbit_visit(self, planet_index: int) -> None:
        if planet_index >= len(self.orbit_progress):
            self.active_orbit_planet_index = None
            return
        progress = self.orbit_progress[planet_index]
        if progress.transfer_ready and not progress.transfer_triggered:
            self._trigger_transfer_boost(planet_index)
        self.orbit_progress[planet_index] = OrbitProgress()
        self.active_orbit_planet_index = None

    def _advance_orbit_progress(self, progress: OrbitProgress, angle: float) -> int:
        if progress.prev_angle is None:
            progress.prev_angle = angle
            progress.in_orbit = True
            return 0

        progress.accumulated_angle += wrap_angle_delta(angle - progress.prev_angle)
        progress.prev_angle = angle
        completed_laps, progress.accumulated_angle = consume_completed_laps(progress.accumulated_angle)
        if completed_laps:
            progress.visit_laps += completed_laps
            progress.transfer_ready = True
        progress.turns = progress.visit_laps + abs(progress.accumulated_angle) / math.tau
        progress.in_orbit = True
        return completed_laps

    def _is_transfer_orbit_ready(self, planet_index: int) -> bool:
        if planet_index >= len(self.orbit_progress) or planet_index >= len(self.assist_orbit_cooldowns):
            return False
        progress = self.orbit_progress[planet_index]
        return (
            progress.transfer_ready
            and progress.in_orbit
            and not progress.transfer_triggered
            and self.assist_orbit_cooldowns[planet_index] <= 0
        )

    def _find_ready_transfer(self) -> tuple[int, int] | None:
        self._ensure_orbit_progress_length()
        for planet_index in range(len(self.planets)):
            if not self._is_transfer_orbit_ready(planet_index):
                continue
            target_index = find_forward_destination_planet_index(
                self.rocket,
                self.planets,
                planet_index,
            )
            if target_index is not None:
                return planet_index, target_index
        return None

    def _try_orbit_transfer(self) -> None:
        planet_index = self.active_orbit_planet_index
        if planet_index is None or not self._is_transfer_orbit_ready(planet_index):
            return
        if self._current_gravity_well_planet_index() == planet_index:
            return
        self._finish_orbit_visit(planet_index)

    def _trigger_transfer_boost(self, planet_index: int) -> None:
        if planet_index >= len(self.planets):
            return
        progress = self.orbit_progress[planet_index]
        if progress.transfer_triggered:
            return
        planet = self.planets[planet_index]
        self.rocket.velocity = swingby_exit_velocity(self.rocket, planet)
        self.assist_orbit_cooldowns[planet_index] = ASSIST_ORBIT_COOLDOWN_FRAMES
        progress.transfer_triggered = True
        self.transfer_boost_timer = ASSIST_MESSAGE_FRAMES
        self.transfer_boost_target_index = find_forward_destination_planet_index(
            self.rocket,
            self.planets,
            planet_index,
        )
        self.last_transfer_boost_planet_index = planet_index
        if self.pyxel is not None:
            self.audio.play_transfer(self.pyxel)
        self._trigger_crew_celebration()
        self._advance_supply_reservations_after_transfer()

    def _advance_supply_reservations_after_transfer(self) -> None:
        updated: list[SupplyShipReservation] = []
        for reservation in self.supply_reservations:
            next_reservation = advance_reserved_gap(reservation)
            if is_reservation_ready_to_spawn(next_reservation):
                next_reservation = mark_reservation_spawned(next_reservation)
                self.last_supply_ship_status = "spawned"
            updated.append(next_reservation)
        self.supply_reservations = updated

    def _create_supply_ship(self, reservation: SupplyShipReservation) -> SupplyShip:
        direction = 1 if reservation.reservation_id % 2 == 1 else -1
        gap = self._course_gap_by_id(reservation.target_gap_id)
        y = gap.center_pos.y if gap is not None else self.rocket.position.y - HEIGHT * 0.22
        return make_supply_ship_from_reservation(reservation, y, direction)

    def _ready_supply_reservations(self) -> list[SupplyShipReservation]:
        return [
            reservation
            for reservation in self.supply_reservations
            if reservation.status == SUPPLY_STATUS_SPAWNED
        ]

    def _supply_zone_waiting_gap(self) -> CourseGap | None:
        if not self.course_gaps:
            return None

        visible_gaps: list[tuple[float, CourseGap]] = []
        target_screen_y = HEIGHT * 0.48
        for gap in self.course_gaps:
            screen = self.camera.world_to_screen(gap.center_pos)
            if 70 <= screen.y <= HEIGHT - 118:
                visible_gaps.append((abs(screen.y - target_screen_y), gap))
        if visible_gaps:
            return min(visible_gaps, key=lambda item: item[0])[1]

        upcoming_gaps = [
            gap
            for gap in self.course_gaps
            if gap.center_pos.y <= self.rocket.position.y + HEIGHT * 0.18
        ]
        if upcoming_gaps:
            return max(upcoming_gaps, key=lambda gap: gap.center_pos.y)
        return min(self.course_gaps, key=lambda gap: abs(gap.center_pos.y - self.rocket.position.y))

    def _sync_supply_zone_waiting_ships(self) -> None:
        waiting_reservations = self._ready_supply_reservations()
        waiting_ids = {reservation.reservation_id for reservation in waiting_reservations}
        existing_by_id = {
            ship.reservation_id: ship
            for ship in self.supply_ships
            if ship.reservation_id in waiting_ids and ship.active and not ship.cargo_collected
        }
        self.supply_ships = [
            ship
            for ship in self.supply_ships
            if not ship.stationary and ship.reservation_id not in waiting_ids
        ]
        if not waiting_reservations:
            return

        gap = self._supply_zone_waiting_gap()
        gap_y = gap.center_pos.y if gap is not None else self.rocket.position.y - HEIGHT * 0.22
        if gap is not None and not gap.is_supply_wide_gap:
            self.course_gaps = mark_supply_gap(self.course_gaps, gap.gap_id)

        type_stack_counts: dict[str, int] = {}
        type_order = {planet_type: index for index, planet_type in enumerate(CREW_PLANET_TYPES)}
        sorted_reservations = sorted(
            waiting_reservations,
            key=lambda reservation: (
                type_order.get(reservation.planet_type, len(CREW_PLANET_TYPES)),
                reservation.reservation_id,
            ),
        )
        lane_count = max(1, len(CREW_PLANET_TYPES) - 1)
        for reservation in sorted_reservations:
            type_index = type_order.get(reservation.planet_type, len(CREW_PLANET_TYPES) - 1)
            stack_index = type_stack_counts.get(reservation.planet_type, 0)
            type_stack_counts[reservation.planet_type] = stack_index + 1
            base_ship = existing_by_id.get(reservation.reservation_id)
            if base_ship is not None and base_ship.stationary:
                self.supply_ships.append(base_ship)
                continue

            world_x = 54.0 + type_index * ((WIDTH - 108.0) / lane_count)
            ship_y = gap_y - 48.0 - stack_index * 34.0
            if base_ship is None:
                base_ship = make_supply_ship_from_reservation(reservation, ship_y, 1)
            self.supply_ships.append(
                replace(
                    base_ship,
                    pos=Vec2(world_x, ship_y),
                    vel=Vec2(0.0, 0.0),
                    warning_timer=0,
                    active=True,
                    cargo_active=True,
                    cargo_collected=False,
                    stationary=True,
                )
            )

    def _course_gap_by_id(self, gap_id: int | None) -> CourseGap | None:
        if gap_id is None:
            return None
        for gap in self.course_gaps:
            if gap.gap_id == gap_id:
                return gap
        return None

    def _orbit_track_guidance_strength(self, visit_laps: int) -> float:
        return max(
            ORBIT_TRACK_GUIDE_MIN_STRENGTH,
            ORBIT_TRACK_GUIDE_STRENGTH - visit_laps * ORBIT_TRACK_GUIDE_DECAY_PER_LAP,
        )

    def _apply_orbit_track_guidance(self) -> None:
        planet_index = self.active_orbit_planet_index
        if planet_index is None or planet_index >= len(self.planets) or planet_index >= len(self.orbit_progress):
            return
        progress = self.orbit_progress[planet_index]
        if not progress.in_orbit:
            return

        planet = self.planets[planet_index]
        radial = self.rocket.position - planet.position
        distance = radial.length()
        if distance <= planet.radius + 4.0:
            return
        radial_dir = radial.normalized()
        relative_velocity = self.rocket.velocity - planet.velocity
        relative_speed = max(relative_velocity.length(), ORBIT_TARGET_SPEED)
        angular_motion = radial_dir.x * relative_velocity.y - radial_dir.y * relative_velocity.x
        orbit_sign = 1.0 if angular_motion >= 0.0 else -1.0
        tangent = Vec2(-radial_dir.y * orbit_sign, radial_dir.x * orbit_sign)
        target_radius = orbit_track_display_radius(planet)
        radial_correction = radial_dir * ((target_radius - distance) * ORBIT_TRACK_GUIDE_RADIAL_CORRECTION)
        desired_relative = tangent * relative_speed + radial_correction
        if desired_relative.length() <= 0.0:
            return
        desired_relative = desired_relative.normalized() * relative_speed
        desired_velocity = planet.velocity + desired_relative
        strength = self._orbit_track_guidance_strength(progress.visit_laps)
        self.rocket.velocity = self.rocket.velocity * (1.0 - strength) + desired_velocity * strength

    def _orbit_speed_bonus_amount(self, turns: float) -> float:
        scaled_turns = max(0.0, min(4.0, turns))
        return min(
            ORBIT_SPEED_BONUS_MAX,
            ORBIT_SPEED_BONUS_BASE + scaled_turns * ORBIT_SPEED_BONUS_PER_TURN,
        )

    def _active_orbit_boost_context(self) -> tuple[int, float] | None:
        planet_index = self._active_orbit_planet_index()
        if planet_index is None:
            return None
        if self.demo_mode and planet_index == self.demo_orbit_index:
            return planet_index, self.demo_orbit_turns
        if planet_index >= len(self.orbit_progress):
            return None
        return planet_index, self.orbit_progress[planet_index].turns

    def _apply_orbit_speed_bonus(self) -> None:
        context = self._active_orbit_boost_context()
        if context is None:
            return
        planet_index, turns = context
        speed = self.rocket.velocity.length()
        if speed >= ORBIT_SPEED_BONUS_MAX_SPEED:
            return
        forward = self.rocket.velocity.normalized()
        if forward.length() <= 0.0:
            planet = self.planets[planet_index]
            radial = (self.rocket.position - planet.position).normalized()
            if radial.length() <= 0.0:
                return
            forward = Vec2(-radial.y, radial.x)
        bonus = min(
            self._orbit_speed_bonus_amount(turns),
            ORBIT_SPEED_BONUS_MAX_SPEED - speed,
        )
        if bonus <= 0.0:
            return
        self.rocket.velocity = self.rocket.velocity + forward * bonus
        self.orbit_speed_boost_timer = 8

    def _repel_demo_from_completed_planets(self) -> None:
        for index in self.demo_orbit_done_indices:
            planet = self.planets[index]
            offset = self.rocket.position - planet.position
            distance = offset.length()
            safe_radius = planet.radius + 34.0
            if distance >= safe_radius:
                continue
            direction = offset.normalized() if distance > 0.0 else Vec2(0.0, -1.0)
            self.rocket.position = planet.position + direction * safe_radius
            self.rocket.velocity = self.rocket.velocity + direction * 1.8

    def _tick_assist_orbit_cooldowns(self) -> None:
        self.assist_orbit_cooldowns = [
            max(0, cooldown - 1) for cooldown in self.assist_orbit_cooldowns
        ]

    def _tick_damage_cooldown(self) -> None:
        self.rocket.damage_cooldown = max(0, self.rocket.damage_cooldown - 1)

    def _tick_collision_escape_timer(self) -> None:
        self.collision_escape_timer = max(0, self.collision_escape_timer - 1)

    def _gravity_planets_for_step(self) -> list[Planet]:
        if self.collision_escape_timer <= 0:
            return self.planets
        return [
            replace(
                planet,
                gravity_multiplier=planet.gravity_multiplier * COLLISION_ESCAPE_GRAVITY_SCALE,
            )
            for planet in self.planets
        ]

    def _sync_angle_to_velocity(self) -> None:
        self.rocket.angle = heading_from_velocity(self.rocket.velocity, self.rocket.angle)

    def _apply_orbit_assist(self, strength: float) -> None:
        planets = self.planets
        if self.demo_mode:
            planets = [
                planet
                for index, planet in enumerate(self.planets)
                if index not in self.demo_orbit_done_indices
                and self.assist_orbit_cooldowns[index] <= 0
            ]
        else:
            planets = [
                planet
                for index, planet in enumerate(self.planets)
                if self.assist_orbit_cooldowns[index] <= 0
            ]
        planet = nearest_orbit_planet(self.rocket, planets)
        if planet is None:
            return
        target_radius = demo_orbit_target_radius(planet, self.rocket) if self.demo_mode else None
        self.rocket.velocity = orbit_assist_velocity(self.rocket, planet, strength, target_radius=target_radius)

    def draw(self) -> None:
        pyxel = self.pyxel
        if pyxel is None:
            return

        pyxel.cls(COLOR_BACKGROUND)
        self._draw_starfield()
        if self.game_state == STATE_TITLE:
            self._draw_title_screen()
            return
        if self.game_state == STATE_RESULT:
            self._draw_result_screen()
            return
        if self._trajectory_preview_enabled() and not (self.rocket.crashed or self.rocket.lost):
            self._draw_trajectory()
        self._draw_planets()
        self._draw_final_goal()
        self._draw_active_orbit_track()
        self._draw_orbit_focus_lines()
        self._draw_transfer_ready_hint()
        self._draw_transfer_boost_effect()
        self._draw_course_gap_markers()
        self._draw_interplanet_objects()
        self._draw_meteor_swarms()
        self._draw_supply_ships()
        self._draw_rocket()
        self._draw_orbit_speed_sparkles()
        self._draw_cutin_panel()
        self._draw_hud()

    def _update_planets(self) -> None:
        updated: list[Planet] = []
        for planet in self.planets:
            next_position = planet.position + planet.velocity
            next_velocity = planet.velocity
            if next_position.x < planet.radius or next_position.x > WIDTH - planet.radius:
                next_velocity = Vec2(-planet.velocity.x, planet.velocity.y)
                next_position = planet.position + next_velocity
            updated.append(replace(planet, position=next_position, velocity=next_velocity))
        self.planets = updated

    def _update_interplanet_objects(self) -> None:
        updated: list[InterplanetObject] = []
        for obj in self.interplanet_objects:
            next_obj = update_interplanet_object(obj)
            if next_obj.kind == OBJECT_KIND_SUPPLY_ITEM:
                next_obj = self._try_collect_supply_item(next_obj)
            elif next_obj.damage > 0 and overlaps_circle(next_obj, self.rocket.position, 10.0):
                self._handle_interplanet_object_collision(next_obj)
            updated.append(next_obj)
        self.interplanet_objects = updated

    def _update_meteor_swarms(self) -> None:
        updated: list[MeteorSwarm] = []
        for swarm in self.meteor_swarms:
            next_swarm = update_meteor_swarm(swarm)
            if next_swarm.active and next_swarm.warning_timer <= 0:
                for meteor in next_swarm.meteors:
                    if meteor.damage > 0 and overlaps_circle(meteor, self.rocket.position, 10.0):
                        self._handle_interplanet_object_collision(meteor)
                        break
            updated.append(next_swarm)
        self.meteor_swarms = updated

    def _update_supply_ships(self) -> None:
        self._sync_supply_zone_waiting_ships()
        updated: list[SupplyShip] = []
        for ship in self.supply_ships:
            next_ship = update_supply_ship(ship)
            if supply_cargo_overlaps(next_ship, self.rocket.position, 10.0):
                next_ship = self._collect_supply_ship_cargo(next_ship)
            elif not ship.stationary and ship.active and not next_ship.active and not next_ship.cargo_collected:
                self._mark_supply_reservation_missed(next_ship.reservation_id)
            updated.append(next_ship)
        self.supply_ships = updated

    def _collect_supply_ship_cargo(self, ship: SupplyShip) -> SupplyShip:
        if not ship.active or not ship.cargo_active or ship.cargo_collected:
            return ship
        join_count = apply_crew_join(
            self.crew_count_by_type,
            self.supply_success_tier_by_type,
            ship.planet_type,
        )
        collected_ship, collection = collect_supply_cargo(ship, join_count)
        if not collection.collected:
            return ship
        self.score, self.rocket.fuel = apply_supply_cargo_reward(
            self.rocket,
            self.score,
            collection,
            ROCKET_FUEL_MAX,
        )
        self._mark_supply_reservation_collected(ship.reservation_id)
        self.last_crew_join_count = join_count
        self.last_supply_ship_status = "collected"
        if self.pyxel is not None:
            self.audio.play_supply(self.pyxel)
        self._trigger_crew_celebration()
        self._trigger_crew_type_celebration(ship.planet_type)
        self.interplanet_feedback_lines = (
            "SUPPLY SHIP!",
            f"CREW +{join_count}",
            f"FUEL +{int(collection.fuel_gain_ratio * 100)}%",
        )
        self.interplanet_feedback_timer = INTERPLANET_FEEDBACK_FRAMES
        return collected_ship

    def _mark_supply_reservation_collected(self, reservation_id: int) -> None:
        self.supply_reservations = [
            mark_reservation_collected(reservation)
            if reservation.reservation_id == reservation_id
            else reservation
            for reservation in self.supply_reservations
        ]

    def _mark_supply_reservation_missed(self, reservation_id: int) -> None:
        self.supply_reservations = [
            mark_reservation_missed(reservation)
            if reservation.reservation_id == reservation_id
            else reservation
            for reservation in self.supply_reservations
        ]
        self.last_supply_ship_status = "missed"

    def _try_collect_supply_item(self, obj: InterplanetObject) -> InterplanetObject:
        if not overlaps_circle(obj, self.rocket.position, 10.0 + SUPPLY_PICKUP_RADIUS_BONUS):
            return obj
        collected_obj, result = collect_supply_item(obj)
        if not result.collected:
            return obj
        self.score, self.rocket.fuel = apply_supply_reward(
            self.rocket,
            self.score,
            result,
            ROCKET_FUEL_MAX,
        )
        self.last_collected_supply_item_id = obj.object_id
        if self.pyxel is not None:
            self.audio.play_supply(self.pyxel)
        self._trigger_crew_celebration()
        self.interplanet_feedback_lines = (
            f"SUPPLY +{result.score_gain}",
            f"FUEL +{int(result.fuel_gain * 100)}%",
        )
        self.interplanet_feedback_timer = INTERPLANET_FEEDBACK_FRAMES
        return collected_obj

    def _handle_interplanet_object_collision(self, obj: InterplanetObject) -> None:
        if self.rocket.damage_cooldown > 0:
            return
        normal = (self.rocket.position - obj.pos).normalized()
        if normal.length() <= 0.0:
            normal = Vec2(0.0, -1.0)
        result = self._apply_rocket_damage(obj.damage, obj.kind)
        if not result.damaged:
            return
        safe_radius = obj.radius + 12.0
        self.rocket.position = obj.pos + normal * safe_radius
        bounce_speed = max(self.rocket.velocity.length() * 0.35, 1.6)
        self.rocket.velocity = normal * bounce_speed
        self._sync_angle_to_velocity()
        self.interplanet_feedback_lines = self._damage_feedback_lines(result)
        self.interplanet_feedback_timer = INTERPLANET_FEEDBACK_FRAMES

    def _update_assists(self) -> None:
        """Legacy exit-speed assist detector kept for isolated tests only.

        The runtime loop now awards score from lap completion events while the
        rocket remains inside a planet gravity well.
        """
        speed = self.rocket.velocity.length()
        self._ensure_lap_count_length()
        for index, planet in enumerate(self.planets):
            in_well = self.rocket.position.distance_to(planet.position) <= planet.gravity_well_radius
            if update_gravity_assist(
                self.assist_states[index],
                index,
                in_well,
                speed,
                ASSIST_SPEED_GAIN_THRESHOLD,
            ):
                self._handle_lap_completed(index)

    def _handle_lap_completed(self, planet_index: int) -> None:
        self._ensure_lap_count_length()
        if planet_index >= len(self.planets):
            return

        planet = self.planets[planet_index]
        self.assist_count += 1
        planet_bonus_multiplier = self._consume_score_bonus_multiplier()
        self.planet_lap_counts[planet_index] += 1
        lap = self.planet_lap_counts[planet_index]
        score_gain = score_gain_for_assist(lap, planet_bonus_multiplier)
        self.score += score_gain
        self.last_score_gain = score_gain
        self.last_lap_count = lap
        self.last_lap_event_planet_index = planet_index
        self.cheer_text = cheer_text_for_stage(cheer_stage_for_lap(lap))
        self.reward_feedback_text = ""
        if self.pyxel is not None:
            self.audio.play_lap(self.pyxel, lap)
        self.rocket.fuel = min(ROCKET_FUEL_MAX, self.rocket.fuel + ASSIST_FUEL_REWARD)
        self._trigger_crew_celebration()
        self._trigger_crew_type_celebration(planet.planet_type)
        if lap == 2 and planet_index not in self.reward_claimed_planet_ids:
            self._apply_planet_reward(planet_index)
        self._try_reserve_supply_ship(planet_index, lap)

        if planet_index < len(self.orbit_progress):
            self.orbit_progress[planet_index].transfer_ready = True

        planet_screen = self.camera.world_to_screen(planet.position)
        cutin_side = cutin_side_for_planet_x(planet_screen.x)
        target_y = int(
            max(
                HEIGHT * CUTIN_MIN_Y_RATIO,
                min(HEIGHT * CUTIN_MAX_Y_RATIO, planet_screen.y - CUTIN_PANEL_HEIGHT / 2),
            )
        )
        self.last_cutin_side = cutin_side
        self.cutin.start(
            planet.planet_type,
            lap,
            score_gain,
            self.reward_feedback_text,
            side=cutin_side,
            target_y=target_y,
        )
        self.message_timer = ASSIST_MESSAGE_FRAMES

    def _try_reserve_supply_ship(self, planet_index: int, lap: int) -> None:
        if planet_index >= len(self.planets):
            return
        planet_type = self.planets[planet_index].planet_type
        if not should_reserve_supply_ship(
            lap,
            planet_type,
            self.supply_ship_chance_count_by_type,
            self.supply_success_tier_by_type,
        ):
            return
        delay = 2 if self.next_supply_reservation_id % 2 == 1 else 3
        target_gap_id = future_gap_id_for_supply(planet_index, delay, self.course_gaps)
        reservation = create_supply_reservation(
            self.next_supply_reservation_id,
            planet_type,
            planet_index,
            lap,
            target_gap_id=target_gap_id,
        )
        self.next_supply_reservation_id += 1
        self.supply_ship_chance_count_by_type[planet_type] += 1
        self.supply_reservations.append(reservation)
        if target_gap_id is not None:
            self.course_gaps = mark_supply_gap(self.course_gaps, target_gap_id)
        self.last_supply_reservation_id = reservation.reservation_id
        self.last_supply_ship_status = "reserved"

    def _consume_score_bonus_multiplier(self) -> float:
        if self.water_score_bonus_uses <= 0:
            return 1.0
        self.water_score_bonus_uses -= 1
        return WATER_REWARD_SCORE_MULTIPLIER

    def _apply_planet_reward(self, planet_index: int) -> None:
        planet = self.planets[planet_index]
        self.reward_claimed_planet_ids.add(planet_index)
        spec = planet_type_spec(planet.planet_type)
        self.reward_feedback_text = spec.reward_feedback_text

        if planet.planet_type == PLANET_TYPE_WIND:
            self.planets[planet_index] = replace(
                planet,
                gravity_multiplier=WIND_REWARD_GRAVITY_MULTIPLIER,
            )
        elif planet.planet_type == PLANET_TYPE_IRON:
            self.rocket.shield = min(
                self.rocket.max_shield,
                self.rocket.shield + IRON_REWARD_SHIELD_GAIN,
            )
        elif planet.planet_type == PLANET_TYPE_WATER:
            self.water_score_bonus_uses += WATER_REWARD_SCORE_USES
        elif planet.planet_type == PLANET_TYPE_FOREST:
            fuel_gain = ROCKET_FUEL_MAX * FOREST_REWARD_FUEL_RATIO
            self.rocket.fuel = min(ROCKET_FUEL_MAX, self.rocket.fuel + fuel_gain)
        elif planet.planet_type == PLANET_TYPE_ROCK:
            self.rocket.hp = min(self.rocket.max_hp, self.rocket.hp + ROCK_REWARD_HP_GAIN)

    def _colliding_planet(self) -> Planet | None:
        for planet in self.planets:
            if self.rocket.position.distance_to(planet.position) <= planet.radius:
                return planet
        return None

    def _handle_planet_collision(self, planet: Planet) -> None:
        self.collision_escape_timer = COLLISION_ESCAPE_FRAMES
        if self.rocket.damage_cooldown > 0:
            return

        result = self._apply_rocket_damage(1, "planet")
        if not result.damaged:
            return
        self._bounce_rocket_from_planet(planet)
        self.interplanet_feedback_lines = self._damage_feedback_lines(result)
        self.interplanet_feedback_timer = INTERPLANET_FEEDBACK_FRAMES

    def _apply_rocket_damage(self, damage: int, source: str) -> DamageResult:
        if damage <= 0 or self.rocket.damage_cooldown > 0:
            return DamageResult(damaged=False)

        remaining = damage
        shield_used = 0
        hp_lost = 0
        if self.rocket.shield > 0:
            shield_used = min(self.rocket.shield, remaining)
            self.rocket.shield -= shield_used
            remaining -= shield_used
        if remaining > 0:
            hp_lost = min(self.rocket.hp, remaining)
            self.rocket.hp = max(0, self.rocket.hp - remaining)

        self.rocket.damage_cooldown = ROCKET_DAMAGE_COOLDOWN_FRAMES
        if self.rocket.hp <= 0:
            self.rocket.crashed = True
            self.game_state = STATE_CRASHED
        if self.pyxel is not None:
            if self.rocket.crashed:
                self.audio.play_crash(self.pyxel)
                self.audio.stop_bgm(self.pyxel)
            else:
                self.audio.play_damage(self.pyxel)
        self.last_damage_source = source
        return DamageResult(
            damaged=True,
            shield_used=shield_used,
            hp_lost=hp_lost,
            crashed=self.rocket.crashed,
        )

    def _damage_feedback_lines(self, result: DamageResult) -> tuple[str, ...]:
        if result.shield_used > 0:
            return ("SHIELD HIT!",)
        if result.hp_lost > 0:
            return (f"HP -{result.hp_lost}",)
        return ()

    def _bounce_rocket_from_planet(self, planet: Planet) -> None:
        normal = (self.rocket.position - planet.position).normalized()
        if normal.length() <= 0.0:
            normal = Vec2(0.0, -1.0)
        safe_radius = planet.radius + 4.0
        self.rocket.position = planet.position + normal * safe_radius
        bounce_speed = max(self.rocket.velocity.length() * 0.35, 1.5)
        self.rocket.velocity = normal * bounce_speed
        self._sync_angle_to_velocity()

    def _draw_starfield(self) -> None:
        pyxel = self.pyxel
        assert pyxel is not None
        for index in range(STAR_COUNT):
            x = (index * 47 + index * index * 3 + int(self.camera.position.x * 0.12)) % WIDTH
            y = (index * 83 + index * index * 5 + int(self.camera.position.y * 0.18)) % HEIGHT
            color = self._starfield_color(index)
            pyxel.pset(x, y, color)
            if self.game_state == STATE_TITLE and color == COLOR_STAR and (index + self.frame // 5) % 67 == 0:
                if 0 < x < WIDTH - 1:
                    pyxel.pset(x - 1, y, COLOR_STAR_DIM)
                    pyxel.pset(x + 1, y, COLOR_STAR_DIM)
                if 0 < y < HEIGHT - 1:
                    pyxel.pset(x, y - 1, COLOR_STAR_DIM)
                    pyxel.pset(x, y + 1, COLOR_STAR_DIM)

    def _starfield_color(self, index: int) -> int:
        if self.game_state != STATE_TITLE:
            return COLOR_STAR if index % 23 == 0 else COLOR_STAR_DIM
        if index % 4 != 0:
            return COLOR_STAR if index % 37 == 0 else COLOR_STAR_DIM
        phase = (self.frame // 8 + index * 7 + (index * index) // 11) % 48
        if phase in (0, 1):
            return COLOR_STAR
        if phase == 24:
            return COLOR_BACKGROUND
        return COLOR_STAR_DIM

    def _trajectory_preview_enabled(self) -> bool:
        return TRAJECTORY_PREVIEW_ALWAYS_ON or self.show_preview

    def _draw_trajectory(self) -> None:
        pyxel = self.pyxel
        assert pyxel is not None
        for index, point in enumerate(simulate_preview(self.rocket, self.planets, TRAJECTORY_STEPS)):
            if index % TRAJECTORY_DOT_INTERVAL != 0:
                continue
            screen = self.camera.world_to_screen(point)
            if -2 <= screen.x <= WIDTH + 2 and -2 <= screen.y <= HEIGHT + 2:
                pyxel.pset(int(screen.x), int(screen.y), COLOR_TRAJECTORY)

    def _draw_planets(self) -> None:
        pyxel = self.pyxel
        assert pyxel is not None
        self._ensure_lap_count_length()
        self._ensure_orbit_progress_length()
        for index, planet in enumerate(self.planets):
            screen = self.camera.world_to_screen(planet.position)
            margin = planet.gravity_well_radius + 4
            if screen.x < -margin or screen.x > WIDTH + margin:
                continue
            if screen.y < -margin or screen.y > HEIGHT + margin:
                continue
            gravity_radius = self._world_screen_radius(planet.gravity_well_radius)
            pyxel.circb(int(screen.x), int(screen.y), gravity_radius, COLOR_GRAVITY_WELL)
            x = int(screen.x)
            y = int(screen.y)
            radius = self._world_screen_radius(planet.radius)
            self._draw_planet_base(x, y, radius, planet.color)
            self._draw_planet_surface(x, y, radius, planet.planet_type, index)
            self._draw_planet_atmosphere(x, y, radius, planet.planet_type, index)
            self._draw_planet_particles(x, y, radius, planet.planet_type, index)
            spec = planet_type_spec(planet.planet_type)
            type_label_width = len(spec.debug_label) * 4 * WORLD_LABEL_SCALE
            type_label_x = int(max(4, min(WIDTH - type_label_width - 4, screen.x - type_label_width / 2)))
            type_label_y = int(max(44, min(HEIGHT - 24, screen.y + radius + 8)))
            self._draw_text_scaled(type_label_x, type_label_y, spec.debug_label, COLOR_HUD, scale=WORLD_LABEL_SCALE)
            lap_label = self._orbit_lap_label_for_planet(index)
            if lap_label:
                label_scale = ORBIT_COUNT_LABEL_SCALE
                label_height = self._scaled_text_height(label_scale)
                self._draw_text_centered(
                    int(screen.x),
                    int(screen.y - label_height / 2),
                    lap_label,
                    COLOR_HUD,
                    scale=label_scale,
                )

    def _draw_planet_base(self, x: int, y: int, radius: int, color: int) -> None:
        pyxel = self.pyxel
        assert pyxel is not None
        pyxel.circ(x, y, radius, color)
        pyxel.circb(x, y, radius, 7)

    def _draw_planet_surface(self, x: int, y: int, radius: int, planet_type: str, index: int) -> None:
        renderer_name = PLANET_RENDERERS.get(planet_type, "_draw_rock_planet")
        renderer = getattr(self, renderer_name)
        renderer(x, y, radius, index)

    def _draw_planet_atmosphere(self, x: int, y: int, radius: int, planet_type: str, index: int) -> None:
        pyxel = self.pyxel
        assert pyxel is not None
        pulse = (self.frame // 18 + index) % 3
        if planet_type == PLANET_TYPE_WIND:
            pyxel.circb(x, y, radius + 2 + pulse, COLOR_TRAJECTORY)
            pyxel.circb(x, y, max(1, radius - 2), 7)
        elif planet_type == PLANET_TYPE_WATER:
            pyxel.circb(x, y, radius + 2, 12)
            if self.frame % 40 < 20:
                pyxel.circb(x, y, max(1, radius - 3), 7)
        elif planet_type == PLANET_TYPE_FOREST:
            pyxel.circb(x, y, radius + 1, 3)
            pyxel.circb(x, y, radius + 3, 11)
        elif planet_type == PLANET_TYPE_ROCK:
            pyxel.circb(x, y, radius, 5)
            pyxel.circb(x, y, radius + 1, 7)
        elif planet_type == PLANET_TYPE_IRON:
            pyxel.circb(x, y, radius, 13)
            pyxel.circb(x, y, max(1, radius - 4), 1)
        elif planet_type == PLANET_TYPE_BLACK_HOLE:
            pyxel.circb(x, y, radius + 2 + pulse, 5)
            pyxel.circb(x, y, max(3, radius - 3), COLOR_ALERT)

    def _draw_planet_particles(self, x: int, y: int, radius: int, planet_type: str, index: int) -> None:
        pyxel = self.pyxel
        assert pyxel is not None
        if radius < 10:
            return
        phase = self.frame // 8 + index * 5
        if planet_type == PLANET_TYPE_WIND:
            for slot in range(3):
                angle = (phase + slot * 7) * 0.32
                px = x + int(math.cos(angle) * (radius + 5))
                py = y + int(math.sin(angle) * (radius + 3))
                pyxel.pset(px, py, 7 if slot % 2 else COLOR_TRAJECTORY)
        elif planet_type == PLANET_TYPE_FOREST:
            for slot in range(3):
                angle = (phase + slot * 9) * 0.27
                px = x + int(math.cos(angle) * (radius + 4))
                py = y + int(math.sin(angle) * (radius + 2))
                pyxel.pset(px, py, 11)
        elif planet_type == PLANET_TYPE_ROCK:
            for slot in range(2):
                angle = (phase + slot * 11) * 0.22
                px = x + int(math.cos(angle) * (radius + 4))
                py = y + int(math.sin(angle) * (radius + 4))
                pyxel.pset(px, py, 13)

    def _draw_wind_planet(self, x: int, y: int, radius: int, index: int) -> None:
        pyxel = self.pyxel
        assert pyxel is not None
        inner = max(4, radius - 4)
        phase = (index * 3 + self.frame // 16) % 8
        for band_index, offset in enumerate((-9, -2, 6, 12)):
            yy = y + self._scaled_planet_offset(offset, radius) + (phase + band_index) % 3 - 1
            pyxel.line(x - inner + 4, yy, x - 1, yy - 4, 7)
            pyxel.line(x + 3, yy - 3, x + inner - 5, yy - 7, COLOR_TRAJECTORY)
        for slot in range(3):
            px = x - radius // 2 + slot * max(4, radius // 2)
            py = y + ((slot * 5 + phase) % max(3, radius // 2)) - radius // 4
            pyxel.line(px, py, px + max(4, radius // 4), py - 2, 7)

    def _draw_iron_planet(self, x: int, y: int, radius: int, index: int) -> None:
        pyxel = self.pyxel
        assert pyxel is not None
        inner = max(4, radius - 4)
        pyxel.line(x - inner + 3, y - radius // 3, x + inner - 4, y - radius // 5, 13)
        pyxel.line(x - inner + 2, y, x + inner - 2, y - 2, 7)
        pyxel.line(x - inner + 6, y + radius // 3, x + inner - 6, y + radius // 5, 13)
        pyxel.rect(x - 3, y - inner + 5, 6, inner * 2 - 10, 1)
        pyxel.line(x - 6, y - inner + 6, x + 6, y - inner + 6, 7)
        for slot in range(5):
            dx, dy = self._planet_pattern_point(index, slot, radius - 5)
            pyxel.pset(x + dx, y + dy, COLOR_ALERT if slot == (self.frame // 20 + index) % 5 else 7)

    def _draw_water_planet(self, x: int, y: int, radius: int, index: int) -> None:
        pyxel = self.pyxel
        assert pyxel is not None
        inner = max(4, radius - 4)
        phase = (index * 5 + self.frame // 14) % 9
        for band_index, offset in enumerate((-8, -1, 6, 12)):
            yy = y + self._scaled_planet_offset(offset, radius)
            wave = ((offset + phase + band_index) % 5) - 2
            pyxel.line(x - inner + 4, yy, x - 4, yy + wave, 12)
            pyxel.line(x, yy + 1, x + inner - 5, yy - wave, 7)
        bubbles = (
            (-radius // 3, -radius // 4, max(2, radius // 7)),
            (radius // 3, radius // 5, max(2, radius // 8)),
            (radius // 6, -radius // 3, max(1, radius // 10)),
        )
        for dx, dy, bubble_radius in bubbles:
            pyxel.circb(x + dx, y + dy, bubble_radius, 12)

    def _draw_forest_planet(self, x: int, y: int, radius: int, index: int) -> None:
        pyxel = self.pyxel
        assert pyxel is not None
        inner = max(4, radius - 4)
        clusters = (
            (-radius // 4, -radius // 5, max(3, radius // 3), 3),
            (radius // 4, radius // 6, max(3, radius // 4), 11),
            (0, radius // 5, max(2, radius // 5), 3),
        )
        for dx, dy, cluster_radius, color in clusters:
            pyxel.circ(x + dx, y + dy, cluster_radius, color)
        pyxel.tri(x, y - inner + 4, x - 7, y - 2, x + 7, y - 2, 3)
        pyxel.line(x - inner + 5, y + radius // 3, x + inner - 6, y + radius // 4, 7)
        for slot in range(4):
            dx, dy = self._planet_pattern_point(index + 3, slot, radius - 6)
            pyxel.pset(x + dx, y + dy, 11)

    def _draw_rock_planet(self, x: int, y: int, radius: int, index: int) -> None:
        pyxel = self.pyxel
        assert pyxel is not None
        craters = (
            (-radius // 3, -radius // 5, max(2, radius // 5)),
            (radius // 4, radius // 4, max(2, radius // 6)),
            (radius // 5, -radius // 3, max(1, radius // 8)),
        )
        for dx, dy, crater_radius in craters:
            pyxel.circ(x + dx, y + dy, crater_radius, 5)
            pyxel.circb(x + dx, y + dy, crater_radius, 7)
        pyxel.line(x - radius // 4, y + radius // 3, x + radius // 6, y + radius // 8, 5)
        pyxel.line(x + radius // 6, y + radius // 8, x + radius // 3, y + radius // 4, 7)

    def _draw_black_hole_planet(self, x: int, y: int, radius: int, index: int) -> None:
        pyxel = self.pyxel
        assert pyxel is not None
        inner = max(4, radius - 4)
        pyxel.circ(x, y, max(3, radius - 5), 0)
        pyxel.circb(x, y, max(4, radius - 3), 5)
        pyxel.line(x - inner + 4, y + 2, x + inner - 4, y - 2, COLOR_ALERT)
        pyxel.line(x - inner + 8, y - 4, x + inner - 8, y + 4, 7)

    def _scaled_planet_offset(self, offset: int, radius: int) -> int:
        return int(round(offset * max(0.65, radius / 20.0)))

    def _planet_pattern_point(self, planet_index: int, slot: int, radius: int) -> tuple[int, int]:
        seed = planet_index * 31 + slot * 17 + 11
        angle = (seed % 36) * math.tau / 36.0
        distance = max(2, radius) * (0.35 + (seed % 5) * 0.10)
        return int(round(math.cos(angle) * distance)), int(round(math.sin(angle) * distance))

    def _draw_final_goal(self) -> None:
        pyxel = self.pyxel
        assert pyxel is not None
        screen = self.camera.world_to_screen(self.final_goal.position)
        margin = self.final_goal.arrival_radius + 12
        if screen.x < -margin or screen.x > WIDTH + margin:
            return
        if screen.y < -margin or screen.y > HEIGHT + margin:
            return

        x = int(screen.x)
        y = int(screen.y)
        radius = self._world_screen_radius(self.final_goal.radius)
        pulse = 2 if self.frame % 40 < 20 else 0
        pyxel.circb(x, y, self._world_screen_radius(self.final_goal.arrival_radius) + pulse, COLOR_TRAJECTORY)
        pyxel.circ(x, y, radius, 6)
        pyxel.circb(x, y, radius, COLOR_HUD)
        pyxel.circ(x - radius // 3, y - radius // 5, max(5, radius // 4), 11)
        pyxel.circ(x + radius // 4, y + radius // 6, max(4, radius // 5), 3)
        pyxel.circ(x + radius // 5, y - radius // 3, max(3, radius // 6), 11)
        self._draw_text_centered(x, y - radius - 22, "GOAL", COLOR_ALERT, scale=2)

    def _orbit_lap_label_for_planet(self, planet_index: int) -> str:
        if self.demo_mode and planet_index == self.demo_orbit_index:
            return self._active_orbit_count_label(int(self.demo_orbit_turns))
        orbit_progress = self.orbit_progress[planet_index] if planet_index < len(self.orbit_progress) else None
        if orbit_progress is not None and orbit_progress.in_orbit:
            return self._active_orbit_count_label(orbit_progress.visit_laps)
        return lap_display_text(self.planet_lap_counts[planet_index])

    def _active_orbit_count_label(self, completed_laps: int) -> str:
        if completed_laps >= 3:
            return "3+"
        return str(max(0, completed_laps))

    def _active_orbit_planet_index(self) -> int | None:
        if self.demo_mode and self.demo_orbit_index is not None:
            if (
                0 <= self.demo_orbit_index < len(self.planets)
                and self.demo_orbit_index not in self.demo_orbit_done_indices
                and self._rocket_is_inside_orbit_focus_range(self.demo_orbit_index)
            ):
                return self.demo_orbit_index
        self._ensure_orbit_progress_length()
        candidates = [
            (self.rocket.position.distance_to(planet.position), index)
            for index, planet in enumerate(self.planets)
            if self.orbit_progress[index].in_orbit and self._rocket_is_inside_orbit_focus_range(index)
        ]
        if not candidates:
            return None
        return min(candidates)[1]

    def _rocket_is_inside_orbit_focus_range(self, planet_index: int) -> bool:
        if planet_index < 0 or planet_index >= len(self.planets):
            return False
        planet = self.planets[planet_index]
        distance = self.rocket.position.distance_to(planet.position)
        return planet.radius + 4.0 < distance <= planet.gravity_well_radius

    def _draw_active_orbit_track(self) -> None:
        pyxel = self.pyxel
        assert pyxel is not None
        planet_index = self._active_orbit_planet_index()
        if planet_index is None:
            return

        planet = self.planets[planet_index]
        orbit_radius = orbit_track_display_radius(planet)
        screen = self.camera.world_to_screen(planet.position)
        margin = orbit_radius + 6
        if screen.x < -margin or screen.x > WIDTH + margin:
            return
        if screen.y < -margin or screen.y > HEIGHT + margin:
            return

        color = COLOR_ALERT if self._is_transfer_orbit_ready(planet_index) else COLOR_TRAJECTORY
        radius = self._world_screen_radius(orbit_radius)
        for offset in (-2, -1, 0, 1, 2):
            pyxel.circb(int(screen.x), int(screen.y), max(1, radius + offset), color)

    def _draw_orbit_focus_lines(self) -> None:
        pyxel = self.pyxel
        assert pyxel is not None
        if self.orbit_focus_strength <= 0.05:
            return
        context = self._orbit_focus_context()
        if context is None:
            return
        planet_index, _current_lap_progress, _completed_laps = context
        planet = self.planets[planet_index]
        focus_screen = self.camera.world_to_screen(planet.position)
        center_x = int(focus_screen.x)
        center_y = int(focus_screen.y)
        line_count = int(
            ORBIT_FOCUS_MIN_LINES
            + (ORBIT_FOCUS_MAX_LINES - ORBIT_FOCUS_MIN_LINES) * self.orbit_focus_strength
        )
        line_count = max(ORBIT_FOCUS_MIN_LINES, min(ORBIT_FOCUS_MAX_LINES, line_count))
        stop_distance = int(orbit_track_display_radius(planet) * ORBIT_FOCUS_MAX_ZOOM) + ORBIT_FOCUS_LINE_ORBIT_MARGIN
        for index in range(line_count):
            start_x, start_y = self._orbit_focus_line_anchor(index)
            direction = Vec2(center_x - start_x, center_y - start_y)
            distance = direction.length()
            jitter = ((index * 11 + 7) % (ORBIT_FOCUS_LINE_JITTER * 2 + 1)) - ORBIT_FOCUS_LINE_JITTER
            line_stop_distance = max(24, stop_distance + jitter)
            if distance <= line_stop_distance + 4:
                continue
            end_ratio = max(0.12, (distance - line_stop_distance) / distance)
            end_x = int(start_x + direction.x * end_ratio)
            end_y = int(start_y + direction.y * end_ratio)
            color = COLOR_HUD if index % 3 == 0 else COLOR_TRAJECTORY
            pyxel.line(start_x, start_y, end_x, end_y, color)

    def _orbit_focus_line_anchor(self, index: int) -> tuple[int, int]:
        edge = index % 4
        seed = (index * 37 + 19) % 100
        if edge == 0:
            return int(WIDTH * seed / 100), 58
        if edge == 1:
            return WIDTH - 12, int(72 + (HEIGHT - 190) * seed / 100)
        if edge == 2:
            return int(WIDTH * (100 - seed) / 100), HEIGHT - 96
        return 12, int(72 + (HEIGHT - 190) * seed / 100)

    def _draw_transfer_boost_effect(self) -> None:
        pyxel = self.pyxel
        assert pyxel is not None
        if self.transfer_boost_timer <= 0:
            return
        rocket_screen = self.camera.world_to_screen(self.rocket.position)
        color = COLOR_ALERT if self.transfer_boost_timer % 12 < 6 else COLOR_TRAJECTORY
        text_x = max(8, min(WIDTH - 150, int(rocket_screen.x) - 54))
        text_y = max(64, min(HEIGHT - 104, int(rocket_screen.y) - 36))
        if self.transfer_boost_target_index is not None and self.transfer_boost_target_index < len(self.planets):
            target = self.planets[self.transfer_boost_target_index]
            target_screen = self.camera.world_to_screen(target.position)
            if -target.gravity_well_radius <= target_screen.y <= HEIGHT + target.gravity_well_radius:
                pyxel.line(
                    int(rocket_screen.x),
                    int(rocket_screen.y),
                    int(target_screen.x),
                    int(target_screen.y),
                    color,
                )
                pyxel.circb(
                    int(target_screen.x),
                    int(target_screen.y),
                    int(target.radius + 8),
                    color,
                )
                text_x = max(8, min(WIDTH - 150, int(target_screen.x) - 54))
                text_y = max(64, min(HEIGHT - 104, int(target_screen.y) - 28))
        self._draw_text_scaled_clamped(
            text_x,
            text_y,
            "TRANSFER BOOST!",
            color,
            scale=2,
        )

    def _draw_transfer_ready_hint(self) -> None:
        pyxel = self.pyxel
        assert pyxel is not None
        planet_index = self._transfer_ready_hint_planet_index()
        if planet_index is None:
            return

        rocket_screen = self.camera.world_to_screen(self.rocket.position)
        planet = self.planets[planet_index]
        planet_screen = self.camera.world_to_screen(planet.position)
        color = COLOR_TRAJECTORY if self.frame % 16 < 8 else COLOR_HUD
        pyxel.line(int(rocket_screen.x), int(rocket_screen.y), int(planet_screen.x), int(planet_screen.y), color)
        self._draw_text_scaled_clamped(
            int(planet_screen.x) - self._scaled_text_width("TRANSFER READY", 2) // 2,
            max(64, min(HEIGHT - 104, int(planet_screen.y) - 34)),
            "TRANSFER READY",
            color,
            scale=2,
        )

    def _transfer_ready_hint_planet_index(self) -> int | None:
        if self.transfer_boost_timer > 0:
            return None
        if self.demo_mode:
            planet_index = self.demo_orbit_index
            if planet_index is None or planet_index >= len(self.planets):
                return None
            if planet_index in self.demo_orbit_done_indices:
                return None
            if planet_index < len(self.planet_lap_counts) and self.planet_lap_counts[planet_index] > 0:
                return planet_index
            if planet_index < len(self.orbit_progress) and self.orbit_progress[planet_index].transfer_ready:
                return planet_index
            return None

        planet_index = self.active_orbit_planet_index
        if planet_index is None or planet_index >= len(self.planets):
            return None
        if not self._is_transfer_orbit_ready(planet_index):
            return None
        return planet_index

    def _draw_course_gap_markers(self) -> None:
        pyxel = self.pyxel
        assert pyxel is not None
        for gap in self.course_gaps:
            if not gap.is_supply_wide_gap:
                continue
            screen = self.camera.world_to_screen(gap.center_pos)
            if screen.y < 54 or screen.y > HEIGHT - 110:
                continue
            color = COLOR_TRAJECTORY if self.frame % 24 < 12 else COLOR_HUD
            pyxel.line(24, int(screen.y), WIDTH - 24, int(screen.y), color)
            self._draw_text_centered(WIDTH // 2, int(screen.y) - 16, "SUPPLY ZONE", color, scale=2)

    def _draw_interplanet_objects(self) -> None:
        pyxel = self.pyxel
        assert pyxel is not None
        for obj in self.interplanet_objects:
            if not obj.active or obj.collected:
                continue
            if obj.kind == OBJECT_KIND_CROSSING_ROCKET and obj.warning_timer > 0:
                self._draw_crossing_rocket_warning(obj)
                continue

            screen = self.camera.world_to_screen(obj.pos)
            margin = obj.radius + 12
            if screen.x < -margin or screen.x > WIDTH + margin:
                continue
            if screen.y < -margin or screen.y > HEIGHT + margin:
                continue

            if obj.kind == OBJECT_KIND_FLOATING_ASTEROID:
                self._draw_floating_asteroid(int(screen.x), int(screen.y), int(obj.radius))
            elif obj.kind == OBJECT_KIND_CROSSING_ROCKET:
                self._draw_crossing_rocket(obj, int(screen.x), int(screen.y))
            elif obj.kind == OBJECT_KIND_SUPPLY_ITEM:
                self._draw_supply_item(int(screen.x), int(screen.y), int(obj.radius))

    def _draw_meteor_swarms(self) -> None:
        pyxel = self.pyxel
        assert pyxel is not None
        for swarm in self.meteor_swarms:
            if not swarm.active:
                continue
            if swarm.warning_timer > 0:
                self._draw_meteor_swarm_warning(swarm)
                continue
            for meteor in swarm.meteors:
                screen = self.camera.world_to_screen(meteor.pos)
                margin = meteor.radius + 8
                if screen.x < -margin or screen.x > WIDTH + margin:
                    continue
                if screen.y < -margin or screen.y > HEIGHT + margin:
                    continue
                pyxel.circ(int(screen.x), int(screen.y), int(meteor.radius), 9)
                pyxel.circb(int(screen.x), int(screen.y), int(meteor.radius + 1), COLOR_HUD)
                tail_x = int(screen.x - (10 if meteor.vel.x > 0 else -10))
                pyxel.line(int(screen.x), int(screen.y), tail_x, int(screen.y), COLOR_FLAME)

    def _draw_meteor_swarm_warning(self, swarm: MeteorSwarm) -> None:
        pyxel = self.pyxel
        assert pyxel is not None
        y = meteor_warning_y(swarm)
        screen = self.camera.world_to_screen(Vec2(WIDTH * 0.5, y))
        if screen.y < 42 or screen.y > HEIGHT - 96:
            return
        color = COLOR_ALERT if swarm.warning_timer % 14 < 7 else COLOR_HUD
        self._draw_text_centered(WIDTH // 2, int(screen.y) - 10, "METEOR WARNING", color, scale=2)
        pyxel.line(20, int(screen.y) + 8, WIDTH - 20, int(screen.y) + 8, color)

    def _draw_crossing_rocket_warning(self, obj: InterplanetObject) -> None:
        pyxel = self.pyxel
        assert pyxel is not None
        warning_pos = Vec2(8.0 if obj.vel.x > 0 else WIDTH - 8.0, obj.pos.y)
        screen = self.camera.world_to_screen(warning_pos)
        if screen.y < 42 or screen.y > HEIGHT - 90:
            return
        color = COLOR_ALERT if obj.warning_timer % 12 < 6 else COLOR_HUD
        x = 6 if obj.vel.x > 0 else WIDTH - 18
        pyxel.tri(x, int(screen.y), x + (10 if obj.vel.x > 0 else -10), int(screen.y) - 6, x + (10 if obj.vel.x > 0 else -10), int(screen.y) + 6, color)
        if obj.vel.x > 0:
            self._draw_text_scaled_clamped(20, int(screen.y) - 9, "WARNING", color, scale=2)
        else:
            self._draw_text_right_aligned(WIDTH - 20, int(screen.y) - 9, "WARNING", color, scale=2)

    def _draw_floating_asteroid(self, x: int, y: int, radius: int) -> None:
        pyxel = self.pyxel
        assert pyxel is not None
        pyxel.circ(x, y, radius, 13)
        pyxel.circ(x - radius // 2, y + 2, max(3, radius // 3), 5)
        pyxel.circ(x + radius // 3, y - radius // 3, max(2, radius // 4), 6)
        pyxel.circb(x, y, radius, 7)

    def _draw_crossing_rocket(self, obj: InterplanetObject, x: int, y: int) -> None:
        pyxel = self.pyxel
        assert pyxel is not None
        direction = 1 if obj.vel.x >= 0 else -1
        nose_x = x + direction * 10
        tail_x = x - direction * 8
        pyxel.tri(nose_x, y, tail_x, y - 5, tail_x, y + 5, 8)
        pyxel.line(tail_x - direction * 2, y, tail_x - direction * 10, y, COLOR_FLAME)

    def _draw_supply_item(self, x: int, y: int, radius: int) -> None:
        pyxel = self.pyxel
        assert pyxel is not None
        pulse = 1 if self.frame % 24 < 12 else 0
        pyxel.circ(x, y, radius + pulse, 11)
        pyxel.circb(x, y, radius + 2, COLOR_HUD)
        pyxel.rect(x - 4, y - 2, 8, 4, COLOR_ALERT)

    def _draw_supply_ships(self) -> None:
        pyxel = self.pyxel
        assert pyxel is not None
        for ship in self.supply_ships:
            if not ship.active:
                continue
            if ship.warning_timer > 0:
                self._draw_supply_ship_warning(ship)
                continue

            screen = self.camera.world_to_screen(ship.pos)
            margin = ship.radius + 32
            if screen.x < -margin or screen.x > WIDTH + margin:
                continue
            if screen.y < -margin or screen.y > HEIGHT + margin:
                continue
            self._draw_supply_ship(ship, int(screen.x), int(screen.y))
            if ship.cargo_active and not ship.cargo_collected:
                cargo_screen = self.camera.world_to_screen(ship.cargo_pos)
                self._draw_supply_cargo(int(cargo_screen.x), int(cargo_screen.y), ship.planet_type)

    def _draw_supply_ship_warning(self, ship: SupplyShip) -> None:
        pyxel = self.pyxel
        assert pyxel is not None
        warning_pos = Vec2(10.0 if ship.vel.x > 0 else WIDTH - 10.0, ship.pos.y)
        screen = self.camera.world_to_screen(warning_pos)
        if screen.y < 42 or screen.y > HEIGHT - 96:
            return
        color = COLOR_ALERT if ship.warning_timer % 14 < 7 else COLOR_HUD
        label = f"{planet_type_spec(ship.planet_type).debug_label} SHIP"
        if ship.vel.x > 0:
            self._draw_text_scaled_clamped(8, int(screen.y) - 10, label, color, scale=2)
        else:
            self._draw_text_right_aligned(WIDTH - 8, int(screen.y) - 10, label, color, scale=2)
        pyxel.circb(6 if ship.vel.x > 0 else WIDTH - 7, int(screen.y), 5, color)

    def _draw_supply_ship(self, ship: SupplyShip, x: int, y: int) -> None:
        pyxel = self.pyxel
        assert pyxel is not None
        spec = planet_type_spec(ship.planet_type)
        direction = 1 if ship.vel.x >= 0 else -1
        pyxel.rect(x - 18, y - 8, 36, 16, 5)
        pyxel.rectb(x - 18, y - 8, 36, 16, COLOR_HUD)
        pyxel.tri(x + direction * 22, y, x + direction * 8, y - 10, x + direction * 8, y + 10, spec.color)
        pyxel.line(x - direction * 20, y, x - direction * 30, y, COLOR_TRAJECTORY)
        self._draw_text_centered(x, y - 28, spec.debug_label, spec.color, scale=2)

    def _draw_supply_cargo(self, x: int, y: int, planet_type: str) -> None:
        pyxel = self.pyxel
        assert pyxel is not None
        color = planet_type_spec(planet_type).color
        pulse = 1 if self.frame % 20 < 10 else 0
        pyxel.rect(x - 7 - pulse, y - 5 - pulse, 14 + pulse * 2, 10 + pulse * 2, color)
        pyxel.rectb(x - 8, y - 6, 16, 12, COLOR_HUD)

    def _draw_rocket(self) -> None:
        pyxel = self.pyxel
        assert pyxel is not None
        screen = self.camera.world_to_screen(self.rocket.position)
        if self.resident_resources.rocket_sprite_available:
            if self._try_draw_rotated_sprite_centered(screen, ROCKET_SPRITE, self.rocket.angle):
                if self.thrusting and not self.rocket.crashed:
                    forward = from_angle(self.rocket.angle)
                    tail = screen - forward * (ROCKET_SPRITE.h * 0.42)
                    flame = screen - forward * (ROCKET_SPRITE.h * 0.72)
                    pyxel.line(int(tail.x), int(tail.y), int(flame.x), int(flame.y), COLOR_FLAME)
                return

        forward = from_angle(self.rocket.angle)
        right = from_angle(self.rocket.angle + math.pi / 2)
        nose = screen + forward * 11
        left = screen - forward * 8 - right * 5
        right_point = screen - forward * 8 + right * 5
        pyxel.tri(
            int(nose.x),
            int(nose.y),
            int(left.x),
            int(left.y),
            int(right_point.x),
            int(right_point.y),
            COLOR_ROCKET,
        )
        if self.thrusting and not self.rocket.crashed:
            flame = screen - forward * 14
            pyxel.line(int(screen.x), int(screen.y), int(flame.x), int(flame.y), COLOR_FLAME)

    def _try_draw_rotated_sprite_centered(self, center: Vec2, sprite: Any, angle: float) -> bool:
        pyxel = self.pyxel
        assert pyxel is not None
        if not hasattr(pyxel, "images") or not hasattr(pyxel, "pset"):
            return False
        try:
            image = pyxel.images[sprite.image_bank]
        except (Exception, TypeError, IndexError):
            return False
        if not hasattr(image, "pget"):
            return False

        center_x = int(center.x)
        center_y = int(center.y)
        source_center_x = (sprite.w - 1) / 2
        source_center_y = (sprite.h - 1) / 2
        radius = int(math.ceil(math.sqrt(sprite.w * sprite.w + sprite.h * sprite.h) / 2)) + 1
        rotation = angle + math.pi / 2
        cos_r = math.cos(rotation)
        sin_r = math.sin(rotation)
        drew_pixel = False
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                source_x = int(round(cos_r * dx + sin_r * dy + source_center_x))
                source_y = int(round(-sin_r * dx + cos_r * dy + source_center_y))
                if source_x < 0 or source_x >= sprite.w or source_y < 0 or source_y >= sprite.h:
                    continue
                try:
                    color = image.pget(sprite.u + source_x, sprite.v + source_y)
                except (Exception, TypeError):
                    return False
                if color == sprite.colkey:
                    continue
                pyxel.pset(center_x + dx, center_y + dy, color)
                drew_pixel = True
        return drew_pixel

    def _draw_orbit_speed_sparkles(self) -> None:
        pyxel = self.pyxel
        assert pyxel is not None
        if self.orbit_speed_boost_timer <= 0 or self.rocket.crashed:
            return

        screen = self.camera.world_to_screen(self.rocket.position)
        colors = [COLOR_TRAJECTORY, COLOR_HUD, COLOR_ALERT]
        for index in range(6):
            phase = self.frame * 0.33 + index * 1.19
            radius = 13.0 + ((self.frame + index * 7) % 9)
            x = int(screen.x + math.cos(phase) * radius)
            y = int(screen.y + math.sin(phase * 0.83) * radius)
            color = colors[(self.frame // 3 + index) % len(colors)]
            if index % 2 == 0:
                pyxel.pset(x, y, color)
                pyxel.pset(x - 1, y, color)
                pyxel.pset(x + 1, y, color)
                pyxel.pset(x, y - 1, color)
                pyxel.pset(x, y + 1, color)
            else:
                pyxel.circ(x, y, 1, color)

    def _draw_cutin_panel(self) -> None:
        pyxel = self.pyxel
        assert pyxel is not None
        if not self.cutin.active or self.cutin.payload is None:
            return

        payload = self.cutin.payload
        panel_width = CUTIN_PANEL_WIDTH
        panel_height = CUTIN_PANEL_HEIGHT
        target_x = (
            CUTIN_SIDE_MARGIN
            if payload.side == CUTIN_SIDE_LEFT
            else WIDTH - panel_width - CUTIN_SIDE_MARGIN
        )
        offscreen_x = -panel_width if payload.side == CUTIN_SIDE_LEFT else WIDTH
        elapsed = self.cutin.duration - self.cutin.timer
        if elapsed < CUTIN_SLIDE_IN_FRAMES:
            t = elapsed / max(1, CUTIN_SLIDE_IN_FRAMES)
            t = 1.0 - (1.0 - t) * (1.0 - t)
            panel_x = int(offscreen_x + (target_x - offscreen_x) * t)
        elif self.cutin.timer < CUTIN_SLIDE_OUT_FRAMES:
            t = 1.0 - self.cutin.timer / max(1, CUTIN_SLIDE_OUT_FRAMES)
            panel_x = int(target_x + (offscreen_x - target_x) * t)
        else:
            panel_x = target_x
        panel_y = payload.target_y if payload.target_y is not None else int(HEIGHT * CUTIN_MAX_Y_RATIO)

        pyxel.rect(panel_x, panel_y, panel_width, panel_height, 1)
        pyxel.rectb(panel_x, panel_y, panel_width, panel_height, COLOR_HUD)
        pyxel.line(panel_x + 104, panel_y + 8, panel_x + 104, panel_y + panel_height - 8, COLOR_GRAVITY_WELL)

        portrait_slot_x = panel_x + 36
        portrait_slot_y = panel_y + 30
        portrait_slot_width = 96
        portrait_slot_height = panel_height
        portrait_draw_size = CUTIN_RESIDENT_DRAW_SIZE
        self._draw_resident_portrait(
            portrait_slot_x + (portrait_slot_width - portrait_draw_size) // 2,
            portrait_slot_y + (portrait_slot_height - portrait_draw_size) // 2,
            payload.resident_id,
            payload.cheer_stage,
        )

        text_x = panel_x + 126
        text_y = panel_y + 12
        self._draw_text_scaled_clamped(text_x, text_y, payload.resident_name, COLOR_ALERT, scale=2)
        self._draw_text_scaled_clamped(text_x, text_y + 20, payload.main_message, COLOR_HUD, scale=2)
        self._draw_text_scaled_clamped(text_x, text_y + 40, payload.sub_message, COLOR_HUD, scale=2)
        self._draw_text_scaled_clamped(text_x, text_y + 64, payload.cheer_line, COLOR_ALERT, scale=2)
        if payload.reward_text:
            self._draw_text_scaled_clamped(text_x, text_y + 88, payload.reward_text, COLOR_ALERT, scale=2)

    def _draw_resident_portrait(self, x: int, y: int, resident_id: str, stage: int) -> None:
        resident = resident_by_id(resident_id)
        if resident is None:
            return

        sprite_stage = stage
        if not self.resident_resources.resident_stage_available(resident.planet_type, sprite_stage):
            sprite_stage = STAGE_IDLE
        sprite = resident.stage_sprites.get(sprite_stage) or resident.stage_sprites[STAGE_IDLE]
        if (
            self.resident_resources.resident_stage_available(resident.planet_type, sprite_stage)
            and self._try_draw_resident_sprite(x, y, sprite)
        ):
            return
        self._draw_fallback_portrait(x, y, resident.fallback_style_id)

    def _try_draw_resident_sprite(self, x: int, y: int, sprite: Any) -> bool:
        return self._try_draw_sprite(x, y, sprite, scale=CUTIN_RESIDENT_SCALE)

    def _try_draw_sprite(self, x: int, y: int, sprite: Any, scale: int = 1) -> bool:
        pyxel = self.pyxel
        assert pyxel is not None
        try:
            pyxel.blt(
                x,
                y,
                sprite.image_bank,
                sprite.u,
                sprite.v,
                sprite.w,
                sprite.h,
                sprite.colkey,
                scale=scale,
            )
        except (Exception, TypeError):
            return False
        return True

    def _draw_hero(self, x: int, y: int, scale: int = 1, state: str = HERO_STATE_IDLE) -> None:
        if self.resident_resources.hero_state_available(state) and self._try_draw_sprite(x, y, HERO_SPRITE, scale=scale):
            return
        self._draw_fallback_hero(x, y, scale=scale)

    def _draw_fallback_hero(self, x: int, y: int, scale: int = 1) -> None:
        pyxel = self.pyxel
        assert pyxel is not None
        size = 32 * scale
        cx = x + size // 2
        cy = y + size // 2
        pyxel.circ(cx, cy - 3 * scale, 10 * scale, 7)
        pyxel.circ(cx + 7 * scale, cy - 1 * scale, 9 * scale, 7)
        pyxel.rect(cx - 8 * scale, cy + 5 * scale, 16 * scale, 8 * scale, 7)
        pyxel.rectb(cx - 9 * scale, cy + 4 * scale, 18 * scale, 10 * scale, COLOR_HUD)
        pyxel.circ(cx - 6 * scale, cy - 2 * scale, max(1, 2 * scale), 0)
        pyxel.line(x + 5 * scale, y + 26 * scale, x + 27 * scale, y + 23 * scale, COLOR_TRAJECTORY)

    def _draw_fallback_portrait(self, x: int, y: int, style_id: str) -> None:
        pyxel = self.pyxel
        assert pyxel is not None
        size = CUTIN_RESIDENT_DRAW_SIZE
        pyxel.rect(x, y, size, size, 0)
        pyxel.rectb(x, y, size, size, COLOR_HUD)
        cx = x + size // 2
        cy = y + size // 2

        if style_id == "wind":
            pyxel.circ(cx - 14, cy, 18, 7)
            pyxel.circ(cx + 8, cy - 4, 22, 7)
            pyxel.circ(cx + 24, cy + 4, 14, 6)
            pyxel.line(x + 12, y + 70, x + 84, y + 58, COLOR_TRAJECTORY)
            pyxel.line(x + 18, y + 78, x + 78, y + 72, COLOR_TRAJECTORY)
        elif style_id == "iron":
            pyxel.rect(cx - 28, cy - 28, 56, 56, 5)
            pyxel.rectb(cx - 28, cy - 28, 56, 56, 7)
            pyxel.line(cx, cy - 28, cx, cy - 42, 7)
            pyxel.pset(cx - 18, cy - 34, COLOR_ALERT)
            pyxel.rect(cx - 18, cy - 4, 8, 8, 7)
            pyxel.rect(cx + 10, cy - 4, 8, 8, 7)
        elif style_id == "water":
            pyxel.circ(cx, cy - 14, 28, 6)
            pyxel.circb(cx, cy - 14, 28, 7)
            for offset in (-24, -12, 0, 12, 24):
                pyxel.line(cx + offset, cy + 14, cx + offset - 6, cy + 34, 6)
            pyxel.circ(cx + 30, cy - 34, 3, 7)
        elif style_id == "forest":
            pyxel.circ(cx, cy + 4, 24, 11)
            pyxel.tri(cx - 10, cy - 18, cx, cy - 44, cx + 10, cy - 18, 3)
            pyxel.tri(cx - 32, cy - 4, cx - 50, cy - 22, cx - 20, cy - 18, 11)
            pyxel.tri(cx + 32, cy - 4, cx + 50, cy - 22, cx + 20, cy - 18, 11)
        else:
            points = (
                (cx - 34, cy - 18),
                (cx - 12, cy - 36),
                (cx + 22, cy - 30),
                (cx + 36, cy - 4),
                (cx + 18, cy + 28),
                (cx - 24, cy + 30),
                (cx - 40, cy + 6),
            )
            for px, py in points:
                pyxel.circ(px, py, 12, 13)
            pyxel.line(cx - 8, cy + 16, cx + 8, cy + 16, 7)

        pyxel.rect(cx - 18, cy - 8, 6, 6, 0)
        pyxel.rect(cx + 12, cy - 8, 6, 6, 0)

    def _draw_hud(self) -> None:
        pyxel = self.pyxel
        assert pyxel is not None
        distance = int(max(0.0, self.rocket.max_distance))
        speed = self.rocket.velocity.length()
        hud_gap = 24
        left_edge = 24
        right_edge = WIDTH - 24
        self._draw_text_scaled_clamped(left_edge, 10, f"SCORE {self.score:06d}", COLOR_HUD, scale=HUD_TEXT_SCALE)
        self._draw_text_scaled_clamped(left_edge, 10 + hud_gap, f"DIST {distance:05d}", COLOR_HUD, scale=HUD_TEXT_SCALE)
        self._draw_text_scaled_clamped(left_edge, 10 + hud_gap * 2, f"SPEED {speed:04.1f}", COLOR_HUD, scale=HUD_TEXT_SCALE)
        self._draw_journey_progress()
        self._draw_demo_button()
        if self._goal_test_available():
            self._draw_goal_test_button()
        self._draw_text_right_aligned(
            right_edge,
            10 + hud_gap,
            f"HP {self.rocket.hp}/{self.rocket.max_hp}",
            COLOR_HUD,
            scale=HUD_TEXT_SCALE,
        )
        self._draw_text_right_aligned(
            right_edge,
            10 + hud_gap * 2,
            f"SHIELD {self.rocket.shield}",
            COLOR_HUD,
            scale=HUD_TEXT_SCALE,
        )
        self._draw_text_right_aligned(
            right_edge,
            10 + hud_gap * 3,
            f"ASSIST {self.assist_count}",
            COLOR_HUD,
            scale=HUD_TEXT_SCALE,
        )

        self._draw_crew_ui()

        fuel_width = int((WIDTH - 32) * max(0.0, min(1.0, self.rocket.fuel / ROCKET_FUEL_MAX)))
        pyxel.rectb(16, HEIGHT - 74, WIDTH - 32, 12, COLOR_HUD)
        pyxel.rect(16, HEIGHT - 74, fuel_width, 12, 11 if self.rocket.fuel > 20 else 8)
        self._draw_text_scaled_clamped(24, HEIGHT - 56, "DRAG/LR STEER  UP BOOST", 5, scale=2)
        self._draw_text_scaled_clamped(24, HEIGHT - 40, "SWIPE/DOWN BRAKE  PREVIEW ON", 5, scale=2)
        mode_hint = f"{self.course.mode.label.upper()}  N MODE"
        sound_hint = "SOUND ON" if self.audio.enabled else "SOUND OFF"
        self._draw_text_scaled_clamped(24, HEIGHT - 24, f"{mode_hint}  DEMO M  S {sound_hint}", 5, scale=2)

        self._draw_off_course_helper()

        if self.message_timer > 0:
            message_scale = 2
            self._draw_text_centered(WIDTH // 2, 82, "GRAVITY!", COLOR_ALERT, scale=message_scale)
            summary = f"LAP {lap_display_text(self.last_lap_count)}  +{self.last_score_gain}"
            if self.cheer_text:
                summary = f"{summary}  {self.cheer_text}"
            self._draw_text_centered(WIDTH // 2, 100, summary, COLOR_HUD, scale=message_scale)
            if self.reward_feedback_text:
                self._draw_text_centered(
                    WIDTH // 2,
                    118,
                    self.reward_feedback_text,
                    COLOR_ALERT,
                    scale=message_scale,
                )
        if self.interplanet_feedback_timer > 0 and self.interplanet_feedback_lines:
            base_y = 136 if self.message_timer > 0 else 108
            for index, line in enumerate(self.interplanet_feedback_lines):
                self._draw_text_right_aligned(
                    WIDTH - 16,
                    base_y + index * 18,
                    line,
                    COLOR_ALERT if index == 0 else COLOR_HUD,
                    scale=2,
                )
        if self.rocket.crashed:
            self._draw_center_message("CRASH", "Press R to restart")
        if self.rocket.lost:
            self._draw_center_message("LOST IN SPACE", "Press R to restart")
        if self.show_debug:
            pyxel.text(8, 108, f"POS {self.rocket.position.x:.1f},{self.rocket.position.y:.1f}", 13)
            pyxel.text(8, 118, f"VEL {self.rocket.velocity.x:.2f},{self.rocket.velocity.y:.2f}", 13)
            pyxel.text(8, 128, f"HP {self.rocket.hp}/{self.rocket.max_hp} SH {self.rocket.shield}", 13)
            pyxel.text(8, 138, f"WATER USES {self.water_score_bonus_uses}", 13)
            pyxel.text(8, 148, f"REWARDS {len(self.reward_claimed_planet_ids)}", 13)
            pyxel.text(8, 158, f"LAST REWARD {self.reward_feedback_text or '-'}", 13)
            planet_index = self._active_orbit_planet_index()
            if planet_index is not None:
                planet = self.planets[planet_index]
                spec = planet_type_spec(planet.planet_type)
                progress = self.orbit_progress[planet_index]
                lap_percent = abs(progress.accumulated_angle) / LAP_COMPLETION_RADIANS * 100.0
                pyxel.text(8, 168, f"ORBIT ID {planet_index} {spec.debug_label} GM {planet.gravity_multiplier:.2f}", 13)
                pyxel.text(8, 178, f"LAP ANG {progress.accumulated_angle:.2f} {lap_percent:03.0f}%", 13)
                pyxel.text(
                    8,
                    188,
                    f"VISIT {progress.visit_laps} TOTAL {self.planet_lap_counts[planet_index]} READY {progress.transfer_ready}",
                    13,
                )
                if self.demo_mode and planet_index == self.demo_orbit_index:
                    actual_radius = self.rocket.position.distance_to(planet.position)
                    target_radius = demo_orbit_target_radius(planet, self.rocket)
                    pyxel.text(8, 198, f"DEMO TARGET R {target_radius:.1f}", 13)
                    pyxel.text(8, 208, f"ACTUAL R {actual_radius:.1f}", 13)
                    pyxel.text(8, 218, f"ORBIT LIMIT R {planet.gravity_well_radius:.1f}", 13)
            pyxel.text(
                8,
                228,
                f"LAST LAP {self.last_lap_event_planet_index} TRANS {self.last_transfer_boost_planet_index}",
                13,
            )
            pyxel.text(8, 238, f"CUTIN SIDE {self.last_cutin_side}", 13)
            active_objects = sum(1 for obj in self.interplanet_objects if obj.active and not obj.collected)
            active_warnings = sum(
                1
                for obj in self.interplanet_objects
                if obj.kind == OBJECT_KIND_CROSSING_ROCKET and obj.active and obj.warning_timer > 0
            )
            pyxel.text(8, 248, f"OBJECTS {active_objects} WARN {active_warnings}", 13)
            pyxel.text(8, 258, f"LAST SUPPLY {self.last_collected_supply_item_id}", 13)
            pyxel.text(8, 268, f"LAST DAMAGE {self.last_damage_source}", 13)
            active_ships = sum(1 for ship in self.supply_ships if ship.active)
            pyxel.text(8, 278, f"SUPPLY RES {len(self.supply_reservations)} SHIPS {active_ships}", 13)
            pyxel.text(8, 288, f"LAST SHIP {self.last_supply_ship_status} CREW +{self.last_crew_join_count}", 13)
            active_swarms = sum(1 for swarm in self.meteor_swarms if swarm.active)
            supply_gaps = sum(1 for gap in self.course_gaps if gap.is_supply_wide_gap)
            pyxel.text(8, 298, f"COURSE GAPS {len(self.course_gaps)} SUPPLY {supply_gaps}", 13)
            pyxel.text(8, 308, f"METEOR SWARMS {active_swarms}", 13)
            pyxel.text(
                8,
                318,
                f"OFF {self.off_course_active} {self.off_course_target_type} {self.off_course_target_index}",
                13,
            )
            pyxel.text(8, 328, f"OFF DIST {self.off_course_distance:.0f} STALL {self.off_course_stall_frames}", 13)

    def _draw_off_course_helper(self) -> None:
        pyxel = self.pyxel
        assert pyxel is not None
        if not self.off_course_active:
            return
        if self.game_state != STATE_PLAYING or self.rocket.crashed or self.rocket.lost:
            return
        if self.cutin.active:
            return

        target_type, _target_index, target_position = self._off_course_target()
        target_screen = self.camera.world_to_screen(target_position)
        arrow_extent = 18
        center_x, center_y = edge_indicator_position(
            target_screen.x,
            target_screen.y,
            WIDTH,
            HEIGHT,
            OFF_COURSE_MARGIN + arrow_extent,
        )
        center_x = int(
            max(
                OFF_COURSE_MARGIN + arrow_extent,
                min(WIDTH - OFF_COURSE_MARGIN - arrow_extent, center_x),
            )
        )
        center_y = int(
            max(
                OFF_COURSE_SAFE_TOP + arrow_extent,
                min(HEIGHT - OFF_COURSE_SAFE_BOTTOM - arrow_extent, center_y),
            )
        )

        direction = Vec2(target_screen.x - WIDTH * 0.5, target_screen.y - HEIGHT * 0.5)
        if direction.length() <= 0.001:
            direction = Vec2(0.0, -1.0)
        else:
            direction = direction.normalized()
        perpendicular = Vec2(-direction.y, direction.x)
        origin = Vec2(float(center_x), float(center_y))
        tip = origin + direction * 13.0
        base = origin - direction * 9.0
        left = base + perpendicular * 7.0
        right = base - perpendicular * 7.0

        color = COLOR_ALERT if self.frame % 24 < 12 else COLOR_HUD
        pyxel.tri(
            int(round(tip.x)),
            int(round(tip.y)),
            int(round(left.x)),
            int(round(left.y)),
            int(round(right.x)),
            int(round(right.y)),
            color,
        )
        pyxel.line(
            int(round(base.x)),
            int(round(base.y)),
            int(round(tip.x)),
            int(round(tip.y)),
            COLOR_HUD,
        )

        label = "GOAL" if target_type == "goal" else "NEXT"
        if center_y <= OFF_COURSE_SAFE_TOP + 34:
            label_y = center_y + 18
            distance_y = center_y + 36
        else:
            label_y = center_y - 38
            distance_y = center_y - 20
        self._draw_text_centered(center_x, label_y, label, COLOR_ALERT, scale=2)
        self._draw_text_centered(
            center_x,
            distance_y,
            f"{int(self.off_course_distance):04d}",
            COLOR_HUD,
            scale=1,
        )

    def _draw_journey_progress(self) -> None:
        pyxel = self.pyxel
        assert pyxel is not None
        total = max(1, len(self.planets))
        current = max(0, min(total - 1, self.highest_course_planet_index))
        x = 150
        y = 9
        width = 148
        height = 50
        bar_width = 108
        filled_width = int(bar_width * current / max(1, total - 1))
        pyxel.rect(x - 4, y - 3, width, height, 0)
        pyxel.rectb(x - 4, y - 3, width, height, COLOR_GRAVITY_WELL)
        self._draw_text_scaled(x, y, "GOAL", COLOR_ALERT, scale=2)
        pyxel.rectb(x + 2, y + 19, bar_width, 8, COLOR_HUD)
        if filled_width > 0:
            pyxel.rect(x + 2, y + 19, filled_width, 8, COLOR_TRAJECTORY)
        self._draw_text_scaled(x, y + 33, f"P {current:02d}/{total:02d}", COLOR_HUD, scale=2)
        if self._has_pending_supply_gap_hint():
            self._draw_text_scaled(x + 72, y + 33, "SUPPLY", COLOR_ALERT, scale=2)

    def _has_pending_supply_gap_hint(self) -> bool:
        return any(gap.is_supply_wide_gap for gap in self.course_gaps)

    def _draw_demo_button(self) -> None:
        pyxel = self.pyxel
        assert pyxel is not None
        x, y, width, height = demo_button_rect()
        fill_color = 5 if self.demo_mode else 1
        border_color = COLOR_ALERT if self.demo_mode else COLOR_HUD
        label = "DEMO ON" if self.demo_mode else "DEMO"
        pyxel.rect(x, y, width, height, fill_color)
        pyxel.rectb(x, y, width, height, border_color)
        text_x = x + (width - self._scaled_text_width(label, 2)) // 2
        text_y = y + (height - self._scaled_text_height(2)) // 2
        self._draw_text_scaled(text_x, text_y, label, border_color, scale=2)

    def _draw_goal_test_button(self) -> None:
        pyxel = self.pyxel
        assert pyxel is not None
        x, y, width, height = goal_test_button_rect()
        crew_count = RESULT_TEST_CREW_PRESETS[self.result_test_preset_index]
        pyxel.rect(x, y, width, height, 1)
        pyxel.rectb(x, y, width, height, COLOR_ALERT)
        left_x, _left_y, left_width, _left_height = goal_test_left_arrow_rect()
        right_x, _right_y, right_width, _right_height = goal_test_right_arrow_rect()
        pyxel.line(x + left_width, y + 3, x + left_width, y + height - 4, COLOR_GRAVITY_WELL)
        pyxel.line(right_x, y + 3, right_x, y + height - 4, COLOR_GRAVITY_WELL)
        arrow_y = y + 12
        pyxel.tri(left_x + 7, arrow_y, left_x + 16, arrow_y - 6, left_x + 16, arrow_y + 6, COLOR_ALERT)
        pyxel.tri(
            right_x + right_width - 7,
            arrow_y,
            right_x + right_width - 16,
            arrow_y - 6,
            right_x + right_width - 16,
            arrow_y + 6,
            COLOR_ALERT,
        )
        goal_label = "GOAL"
        goal_x = x + (width - self._scaled_text_width(goal_label, 2)) // 2
        self._draw_text_scaled(goal_x, y + 4, goal_label, COLOR_ALERT, scale=2)
        test_label = "TEST"
        test_x = x + (width - self._scaled_text_width(test_label, 1)) // 2
        self._draw_text_scaled(test_x, y + 18, test_label, COLOR_HUD, scale=1)
        crew_label = f"CREW {crew_count}"
        crew_x = x + (width - self._scaled_text_width(crew_label, 1)) // 2
        self._draw_text_scaled(crew_x, y + 25, crew_label, COLOR_HUD, scale=1)

    def _draw_title_screen(self) -> None:
        pyxel = self.pyxel
        assert pyxel is not None
        self._draw_title_shooting_star()
        self._draw_text_centered_shimmer(WIDTH // 2, 92, "GRAVITY", scale=5)
        self._draw_text_centered(WIDTH // 2, 132, "COURIER", COLOR_HUD, scale=5)
        self._draw_text_centered(WIDTH // 2, 184, "ORBIT. GATHER. RETURN.", COLOR_ALERT, scale=2)
        self._draw_title_mode_summary()
        self._draw_title_button(
            title_start_button_rect(),
            "START",
            primary=True,
            selected=self.title_menu_index == TITLE_MENU_START,
        )
        mode_spec = COURSE_MODES[self.course_mode_key]
        self._draw_title_button(
            title_mode_button_rect(),
            f"MODE {mode_spec.label.upper()}",
            subtitle=f"{mode_spec.planet_count} PLANETS",
            selected=self.title_menu_index == TITLE_MENU_MODE,
        )
        demo_label = "DEMO ON" if self.title_demo_enabled else "DEMO OFF"
        self._draw_title_button(
            title_demo_button_rect(),
            demo_label,
            subtitle="LR / TAP",
            selected=self.title_menu_index == TITLE_MENU_DEMO,
        )
        sound_label = "SOUND ON" if self.audio.enabled else "SOUND OFF"
        self._draw_title_button(
            title_sound_button_rect(),
            sound_label,
            subtitle="S KEY",
            selected=self.title_menu_index == TITLE_MENU_SOUND,
        )
        self._draw_text_centered(WIDTH // 2, HEIGHT - 124, "DRAG TURN  SWIPE SPEED", COLOR_HUD, scale=2)
        self._draw_text_centered(WIDTH // 2, HEIGHT - 100, "UD SELECT  ENTER START  LR CHANGE", 5, scale=2)

    def _draw_title_shooting_star(self) -> None:
        pyxel = self.pyxel
        assert pyxel is not None
        phase = title_shooting_star_phase(self.frame)
        if phase is None:
            return
        progress = phase / max(1, TITLE_SHOOTING_STAR_DURATION_FRAMES - 1)
        start_x = WIDTH + 26
        start_y = 86
        end_x = -48
        end_y = 204
        head_x = int(start_x + (end_x - start_x) * progress)
        head_y = int(start_y + (end_y - start_y) * progress)
        tail_dx = 30
        tail_dy = -11
        pyxel.line(head_x, head_y, head_x + tail_dx, head_y + tail_dy, 7)
        pyxel.line(head_x + 5, head_y - 1, head_x + tail_dx + 12, head_y + tail_dy - 3, COLOR_TRAJECTORY)
        pyxel.pset(head_x, head_y, COLOR_ALERT)
        pyxel.pset(head_x - 1, head_y, 7)
        pyxel.pset(head_x, head_y - 1, 7)

    def _draw_title_mode_summary(self) -> None:
        mode_spec = COURSE_MODES[self.course_mode_key]
        label = f"{mode_spec.label.upper()} - {mode_spec.planet_count} PLANETS"
        self._draw_text_centered(WIDTH // 2, 228, label, COLOR_HUD, scale=2)

    def _draw_title_button(
        self,
        rect: tuple[int, int, int, int],
        label: str,
        subtitle: str = "",
        primary: bool = False,
        selected: bool = False,
    ) -> None:
        pyxel = self.pyxel
        assert pyxel is not None
        x, y, width, height = rect
        fill_color = COLOR_ALERT if primary else 1
        border_color = COLOR_HUD if primary else COLOR_GRAVITY_WELL
        text_color = 1 if primary else COLOR_ALERT
        pyxel.rect(x, y, width, height, fill_color)
        pyxel.rectb(x, y, width, height, border_color)
        pyxel.rectb(x + 2, y + 2, width - 4, height - 4, 5 if primary else COLOR_HUD)
        if selected:
            pyxel.rectb(x - 4, y - 4, width + 8, height + 8, COLOR_ALERT)
            pyxel.tri(x - 16, y + height // 2, x - 8, y + height // 2 - 6, x - 8, y + height // 2 + 6, COLOR_ALERT)
            pyxel.tri(
                x + width + 16,
                y + height // 2,
                x + width + 8,
                y + height // 2 - 6,
                x + width + 8,
                y + height // 2 + 6,
                COLOR_ALERT,
            )
        text_y = y + 8 if subtitle else y + (height - self._scaled_text_height(2)) // 2
        self._draw_text_centered(x + width // 2, text_y, label, text_color, scale=2)
        if subtitle:
            self._draw_text_centered(x + width // 2, y + 27, subtitle, COLOR_HUD, scale=1)

    def _draw_result_screen(self) -> None:
        pyxel = self.pyxel
        assert pyxel is not None
        summary = self.result_summary
        if summary is None:
            return

        pyxel.rect(18, 26, WIDTH - 36, HEIGHT - 52, 1)
        pyxel.rectb(18, 26, WIDTH - 36, HEIGHT - 52, COLOR_HUD)
        self._draw_text_centered_shimmer(WIDTH // 2, 48, "RETURN COMPLETE", scale=3)
        self._draw_result_rank(summary.rank)

        left_x = 42
        right_x = WIDTH - 42
        y = 112
        gap = 20
        rows = (
            ("MODE", summary.course_mode_label.upper()),
            ("FINAL", f"{summary.final_score:06d}"),
            ("RUN", f"{summary.run_score:06d}"),
            ("CREW BONUS", f"+{summary.crew_bonus:05d}"),
            ("CREW", f"{summary.display_crew_count}"),
            ("LAPS", f"{summary.total_laps}"),
            ("SUPPLY", f"{summary.supply_cargo_collected}"),
            ("HP", f"{summary.hp_left}/{self.rocket.max_hp}"),
            ("FUEL", f"{summary.fuel_left}"),
        )
        for index, (label, value) in enumerate(rows):
            row_y = y + index * gap
            underline_y = row_y + self._scaled_text_height(2) + 4
            self._draw_text_scaled(left_x, row_y, label, COLOR_HUD, scale=2)
            self._draw_text_right_aligned(right_x, row_y, value, COLOR_ALERT if index == 0 else COLOR_HUD, scale=2)
            pyxel.line(left_x, underline_y, right_x, underline_y, COLOR_GRAVITY_WELL)

        self._draw_text_centered_jumping(WIDTH // 2, 306, RESULT_WELCOME_MESSAGE, COLOR_ALERT, scale=3)
        self._draw_result_confetti(summary)
        self._draw_result_crew_crowd(summary)
        self._draw_result_retry_button()

    def _draw_result_rank(self, rank: str) -> None:
        if rank != "S":
            self._draw_text_centered(WIDTH // 2, 80, f"RANK {rank}", COLOR_HUD, scale=3)
            return

        pyxel = self.pyxel
        assert pyxel is not None
        self._draw_text_centered(WIDTH // 2 - 34, 82, "RANK", COLOR_HUD, scale=2)
        self._draw_result_s_rank_glyph(WIDTH // 2 + 31, 70, scale=7)
        sparkle_color = (COLOR_ALERT, COLOR_HUD, COLOR_TRAJECTORY, 10)[(self.frame // 4) % 4]
        center_x = WIDTH // 2 + 31
        center_y = 88
        for index, (dx, dy) in enumerate(((-31, -11), (-31, 13), (30, -11), (30, 13), (-8, 25), (12, 25))):
            color = sparkle_color if (self.frame // 5 + index) % 2 == 0 else COLOR_HUD
            pyxel.line(center_x + dx - 4, center_y + dy, center_x + dx + 4, center_y + dy, color)
            pyxel.line(center_x + dx, center_y + dy - 4, center_x + dx, center_y + dy + 4, color)

    def _draw_result_s_rank_glyph(self, center_x: int, y: int, scale: int) -> None:
        pyxel = self.pyxel
        assert pyxel is not None
        glyph = PIXEL_FONT_3X5["S"]
        colors = (COLOR_ALERT, COLOR_HUD, COLOR_TRAJECTORY, 10, 11, 12, 13)
        x = int(center_x - self._scaled_text_width("S", scale) / 2)
        color_phase = self.frame // 3
        for row, pixels in enumerate(glyph):
            for column, pixel in enumerate(pixels):
                if pixel == "1":
                    color = colors[(color_phase + row * 2 + column) % len(colors)]
                    pyxel.rect(x + column * scale, y + row * scale, scale, scale, color)

    def _draw_result_retry_button(self) -> None:
        self._draw_result_button(result_retry_button_rect(), "RETRY")
        self._draw_result_button(result_retry_hard_button_rect(), "RETRY HARD")
        self._draw_result_button(result_title_button_rect(), "BACK TO TITLE", scale=2)

    def _draw_result_button(self, rect: tuple[int, int, int, int], label: str, scale: int = 2) -> None:
        pyxel = self.pyxel
        assert pyxel is not None
        x, y, width, height = rect
        pyxel.rect(x, y, width, height, COLOR_ALERT)
        pyxel.rectb(x, y, width, height, COLOR_HUD)
        pyxel.rectb(x + 2, y + 2, width - 4, height - 4, 1)
        text_x = x + (width - self._scaled_text_width(label, scale)) // 2
        text_y = y + (height - self._scaled_text_height(scale)) // 2
        self._draw_text_scaled(text_x, text_y, label, 1, scale=scale)

    def _draw_result_confetti(self, summary: ResultSummary) -> None:
        pyxel = self.pyxel
        assert pyxel is not None
        colors = (COLOR_ALERT, COLOR_HUD, COLOR_TRAJECTORY, 11, 12, 13)
        particle_count = min(96, 36 + summary.display_crew_count * 3)
        top = 338
        bottom = HEIGHT - 82
        height = bottom - top
        base_seed = summary.total_laps * 101 + summary.display_crew_count * 59 + summary.final_score
        for index in range(particle_count):
            seed = self._confetti_noise(base_seed + index * 131)
            speed = 1 + seed % 4
            fall_offset = (seed >> 4) % height
            y = top + (fall_offset + self.frame * speed) % height
            sway_rate = 16 + (seed >> 12) % 35
            sway_amplitude = 2 + (seed >> 18) % 12
            sway = int(math.sin((self.frame + (seed >> 7) % 113) / sway_rate) * sway_amplitude)
            flutter = ((self.frame // (3 + (seed >> 24) % 5) + seed) % 7) - 3
            x = 20 + ((seed >> 8) % (WIDTH - 40)) + sway + flutter
            x = max(18, min(WIDTH - 20, x))
            color = colors[(seed + self.frame // (7 + index % 5)) % len(colors)]
            shape = (seed + self.frame // 9) % 7
            if shape == 0:
                pyxel.line(x, y, x + 4, y + 2, color)
            elif shape == 1:
                pyxel.line(x, y + 2, x + 3, y - 1, color)
            elif shape == 2:
                pyxel.rect(x, y, 3, 1, color)
            elif shape == 3:
                pyxel.rect(x, y, 1, 3, color)
            elif shape == 4:
                pyxel.rect(x, y, 2, 2, color)
            else:
                pyxel.pset(x, y, color)

    def _confetti_noise(self, value: int) -> int:
        value = (value ^ (value >> 16)) * 0x7FEB352D
        value = (value ^ (value >> 15)) * 0x846CA68B
        return (value ^ (value >> 16)) & 0xFFFFFFFF

    def _draw_result_crew_crowd(self, summary: ResultSummary) -> None:
        if summary.joined_crew_count <= 0:
            jump = self._result_character_jump(seed=0, amplitude=12)
            self._draw_hero(WIDTH // 2 - 32, 350 - jump, scale=2)
            self._draw_text_centered(WIDTH // 2, 432, "HERO MADE IT HOME", COLOR_HUD, scale=2)
            return

        self._draw_hero(WIDTH // 2 - 16, 342 - self._result_character_jump(seed=0, amplitude=8), scale=1)
        crowd_members = self._result_crowd_members(summary)
        for draw_index, (planet_type, crew_index) in enumerate(crowd_members):
            x, y = self._result_crowd_position(draw_index, planet_type, crew_index, len(crowd_members))
            jump = self._result_character_jump(seed=draw_index + crew_index + 3, amplitude=7)
            self._draw_result_crew_member(planet_type, x, y - jump, draw_index + crew_index)

    def _result_crowd_members(self, summary: ResultSummary) -> list[tuple[str, int]]:
        max_visible = self._result_crowd_visible_limit(summary)
        visible_counts = self._result_crowd_visible_counts(summary)
        members: list[tuple[str, int]] = []
        for planet_type, visible_count in visible_counts.items():
            total_count = self.crew_count_by_type.get(planet_type, 0)
            if visible_count <= 0 or total_count <= 0:
                continue
            for slot_index in range(visible_count):
                crew_index = self._representative_result_crew_index(slot_index, visible_count, total_count)
                members.append((planet_type, crew_index))
        return sorted(
            members,
            key=lambda item: self._result_crowd_seed(item[0], item[1]) + self._result_crowd_slot_bias(item[0]),
        )[:max_visible]

    def _result_crowd_visible_counts(self, summary: ResultSummary) -> dict[str, int]:
        max_visible = self._result_crowd_visible_limit(summary)
        total_count = max(1, summary.joined_crew_count)
        active_types = [
            planet_type
            for planet_type in CREW_PLANET_TYPES
            if self.crew_count_by_type.get(planet_type, 0) > 0
        ]
        if not active_types:
            return {}
        counts: dict[str, int] = {planet_type: 0 for planet_type in CREW_PLANET_TYPES}
        remaining = max_visible
        for planet_type in active_types:
            if remaining <= 0:
                break
            counts[planet_type] = 1
            remaining -= 1
        remainders: list[tuple[float, str]] = []
        for planet_type in active_types:
            type_count = self.crew_count_by_type.get(planet_type, 0)
            quota = max_visible * type_count / total_count
            extra = max(0, int(math.floor(quota)) - counts[planet_type])
            assignable = min(extra, remaining, max(0, type_count - counts[planet_type]))
            counts[planet_type] += assignable
            remaining -= assignable
            remainders.append((quota - math.floor(quota), planet_type))
        for _fraction, planet_type in sorted(remainders, reverse=True):
            if remaining <= 0:
                break
            if counts[planet_type] >= self.crew_count_by_type.get(planet_type, 0):
                continue
            counts[planet_type] += 1
            remaining -= 1
        return counts

    def _result_crowd_visible_limit(self, summary: ResultSummary) -> int:
        if summary.crew_density == RESULT_DENSITY_NORMAL:
            return min(summary.joined_crew_count, 24)
        if summary.crew_density == RESULT_DENSITY_DENSE:
            return min(summary.joined_crew_count, 34)
        return min(summary.joined_crew_count, 44)

    def _representative_result_crew_index(self, slot_index: int, visible_count: int, total_count: int) -> int:
        if visible_count <= 1:
            return max(0, total_count // 2)
        return min(total_count - 1, int(round(slot_index * (total_count - 1) / (visible_count - 1))))

    def _result_crowd_slot_bias(self, planet_type: str) -> int:
        type_index = CREW_PLANET_TYPES.index(planet_type) if planet_type in CREW_PLANET_TYPES else 0
        return type_index * 211

    def _result_crowd_seed(self, planet_type: str, crew_index: int) -> int:
        type_index = CREW_PLANET_TYPES.index(planet_type) if planet_type in CREW_PLANET_TYPES else 0
        return (type_index + 1) * 97 + (crew_index + 3) * 53

    def _result_crowd_position(
        self,
        draw_index: int,
        planet_type: str,
        crew_index: int,
        crowd_size: int,
    ) -> tuple[int, int]:
        seed = self._confetti_noise(self._result_crowd_seed(planet_type, crew_index) + draw_index * 409)
        region_left = 24
        region_right = WIDTH - 56
        region_top = 392
        region_bottom = RESULT_TITLE_BUTTON_Y - 18
        region_width = region_right - region_left
        region_height = region_bottom - region_top
        sprite_size = 32
        slot_count = max(1, crowd_size)
        columns = max(1, math.ceil(math.sqrt(slot_count * region_width / max(1, region_height))))
        rows = max(1, math.ceil(slot_count / columns))
        cell_width = region_width / columns
        cell_height = region_height / rows
        column = draw_index % columns
        row = draw_index // columns
        jitter_x_limit = max(0, int((cell_width - sprite_size) * 0.42))
        jitter_y_limit = max(0, int((cell_height - sprite_size) * 0.42))
        jitter_x = 0 if jitter_x_limit <= 0 else int(seed % (jitter_x_limit * 2 + 1)) - jitter_x_limit
        jitter_y = 0 if jitter_y_limit <= 0 else int((seed >> 8) % (jitter_y_limit * 2 + 1)) - jitter_y_limit
        if row % 2 == 1:
            jitter_x += int(cell_width * 0.14)
        if column % 3 == 2:
            jitter_y -= int(cell_height * 0.10)
        x = int(region_left + column * cell_width + (cell_width - sprite_size) / 2 + jitter_x)
        y = int(region_top + row * cell_height + (cell_height - sprite_size) / 2 + jitter_y)
        return max(region_left, min(region_right, x)), max(region_top, min(region_bottom, y))

    def _draw_result_crew_member(self, planet_type: str, x: int, y: int, seed: int) -> None:
        resident = resident_for_planet_type(planet_type)
        sprite = resident.stage_sprites[STAGE_IDLE]
        drew_sprite = self.resident_resources.resident_stage_available(
            planet_type, STAGE_IDLE
        ) and self._try_draw_sprite(x, y, sprite, scale=1)
        if not drew_sprite:
            self._draw_result_fallback_crew_member(planet_type, x, y)
        if planet_type == PLANET_TYPE_ROCK:
            self._draw_result_rock_heart(x, y, seed)

    def _draw_result_rock_heart(self, x: int, y: int, seed: int) -> None:
        offset = self._result_rock_heart_offset(seed)
        if offset is None:
            return
        heart_x, heart_y, color = offset
        self._draw_pixel_heart(x + 14 + heart_x, y - 7 + heart_y, color, scale=2)

    def _result_rock_heart_offset(self, seed: int) -> tuple[int, int, int] | None:
        phase = (self.frame + seed * 23) % 150
        if phase >= 38:
            return None
        rise = int(phase * 0.48)
        sway = int(round(math.sin((phase + seed * 5) * 0.34) * 4))
        color = 8 if phase < 30 else COLOR_HUD
        return sway, -rise, color

    def _draw_pixel_heart(self, x: int, y: int, color: int, scale: int = 1) -> None:
        pyxel = self.pyxel
        assert pyxel is not None
        pixels = (
            "01010",
            "11111",
            "11111",
            "01110",
            "00100",
        )
        for row, pattern in enumerate(pixels):
            for column, pixel in enumerate(pattern):
                if pixel == "1":
                    pyxel.rect(x + column * scale, y + row * scale, scale, scale, color)

    def _draw_result_fallback_crew_member(self, planet_type: str, x: int, y: int) -> None:
        pyxel = self.pyxel
        assert pyxel is not None
        spec = planet_type_spec(planet_type)
        pyxel.rect(x + 3, y + 4, 26, 24, spec.color)
        pyxel.rectb(x + 3, y + 4, 26, 24, COLOR_HUD)
        pyxel.rect(x + 10, y + 13, 3, 3, 0)
        pyxel.rect(x + 19, y + 13, 3, 3, 0)
        pyxel.line(x + 8, y + 25, x + 24, y + 22, COLOR_TRAJECTORY)

    def _result_character_jump(self, seed: int, amplitude: int) -> int:
        phase = ((self.frame + seed * 11) % 48) / 48.0
        return int(abs(math.sin(phase * math.pi)) * amplitude)

    def _trigger_crew_celebration(self) -> None:
        self.crew_celebration_timer = CREW_CELEBRATION_FRAMES

    def _trigger_crew_type_celebration(self, planet_type: str) -> None:
        if planet_type in self.crew_type_celebration_timers:
            self.crew_type_celebration_timers[planet_type] = CREW_CELEBRATION_FRAMES

    def _crew_celebration_jump_offset(self) -> int:
        if self.crew_celebration_timer <= 0:
            return 0
        elapsed = CREW_CELEBRATION_FRAMES - self.crew_celebration_timer
        phase = (elapsed % 18) / 18.0
        return int(abs(math.sin(phase * math.pi)) * 8)

    def _crew_type_celebration_jump_offset(self, planet_type: str) -> int:
        timer = self.crew_type_celebration_timers.get(planet_type, 0)
        if timer <= 0:
            return 0
        elapsed = CREW_CELEBRATION_FRAMES - timer
        phase = ((elapsed + self._result_crowd_seed(planet_type, 0) % 9) % 20) / 20.0
        return int(abs(math.sin(phase * math.pi)) * 7)

    def _draw_crew_ui(self) -> None:
        pyxel = self.pyxel
        assert pyxel is not None

        total = total_joined_crew(self.crew_count_by_type)
        panel_x = 8
        panel_y = HEIGHT - 148
        panel_width = WIDTH - 16
        panel_height = 66
        pyxel.rect(panel_x, panel_y, panel_width, panel_height, 1)
        pyxel.rectb(panel_x, panel_y, panel_width, panel_height, COLOR_GRAVITY_WELL)

        hero_x = panel_x + 8
        hero_y = panel_y + 24 - self._crew_celebration_jump_offset()
        self._draw_crew_confetti(hero_x + 16, hero_y + 2)
        self._draw_hero(hero_x, hero_y, scale=1)
        self._draw_text_scaled(panel_x + 48, panel_y + 10, f"CREW {total}", COLOR_HUD, scale=2)
        self._draw_text_scaled(panel_x + 48, panel_y + 32, "HERO 1", COLOR_ALERT, scale=2)

        slot_x = panel_x + 126
        slot_y = panel_y + 8
        slot_gap = 49
        marker_size = 32
        label_scale = 2
        label_y = slot_y + marker_size + 8
        for index, planet_type in enumerate(CREW_PLANET_TYPES):
            spec = planet_type_spec(planet_type)
            count = self.crew_count_by_type.get(planet_type, 0)
            x = slot_x + index * slot_gap
            type_jump = self._crew_type_celebration_jump_offset(planet_type) if count > 0 else 0
            draw_y = slot_y - type_jump
            if count > 0 and self.crew_type_celebration_timers.get(planet_type, 0) > 0:
                self._draw_crew_confetti(x + marker_size // 2, draw_y + 2, self.crew_type_celebration_timers[planet_type])
            resident = resident_for_planet_type(planet_type)
            sprite = resident.stage_sprites[STAGE_IDLE]
            if count > 0 and self.resident_resources.resident_stage_available(planet_type, STAGE_IDLE):
                if not self._try_draw_sprite(x, draw_y, sprite, scale=1):
                    pyxel.rect(x, draw_y, marker_size, marker_size, spec.color)
                    pyxel.rectb(x, draw_y, marker_size, marker_size, COLOR_HUD)
            else:
                fill_color = spec.color if count > 0 else 1
                pyxel.rect(x, draw_y, marker_size, marker_size, fill_color)
                pyxel.rectb(x, draw_y, marker_size, marker_size, spec.color if count > 0 else COLOR_GRAVITY_WELL)
            label = spec.debug_label
            label_x = x + (marker_size - self._scaled_text_width(label, label_scale)) // 2
            self._draw_text_scaled(label_x, label_y, label, spec.color, scale=label_scale)

    def _draw_crew_confetti(self, center_x: int, top_y: int, timer: int | None = None) -> None:
        active_timer = self.crew_celebration_timer if timer is None else timer
        if active_timer <= 0:
            return
        pyxel = self.pyxel
        assert pyxel is not None
        elapsed = CREW_CELEBRATION_FRAMES - active_timer
        colors = (COLOR_ALERT, COLOR_TRAJECTORY, COLOR_HUD, COLOR_FLAME)
        for index in range(12):
            seed = self._confetti_noise(index * 83 + center_x * 5 + top_y * 7)
            drift = ((elapsed * (1 + seed % 4) + (seed >> 5)) % 42) - 21
            fall = (elapsed * (2 + (seed >> 11) % 3) + (seed >> 15)) % 36
            sway = int(math.sin((elapsed + (seed >> 20) % 31) / (5 + seed % 7)) * (2 + seed % 4))
            x = center_x + drift + sway
            y = top_y - 22 + fall // 2
            if y < top_y + 14:
                color = colors[(seed + elapsed // 3) % len(colors)]
                if seed % 3 == 0:
                    pyxel.line(x, y, x + 3, y + 1, color)
                else:
                    pyxel.rect(x, y, 2, 2, color)

    def _draw_center_message(self, title: str, subtitle: str) -> None:
        pyxel = self.pyxel
        assert pyxel is not None
        self._draw_text_centered(WIDTH // 2, HEIGHT // 2 - 16, title, COLOR_ALERT, scale=2)
        self._draw_text_centered(WIDTH // 2, HEIGHT // 2 + 8, subtitle, COLOR_HUD, scale=2)

    def _scaled_text_width(self, text: str, scale: int) -> int:
        if not text:
            return scale
        return ((len(text) - 1) * 4 + 3) * scale

    def _scaled_text_height(self, scale: int) -> int:
        return 5 * scale

    def _clamped_text_xy(self, x: int, y: int, text: str, scale: int, margin: int = 4) -> tuple[int, int]:
        width = self._scaled_text_width(text, scale)
        height = self._scaled_text_height(scale)
        max_x = max(margin, WIDTH - width - margin)
        max_y = max(margin, HEIGHT - height - margin)
        return (
            int(max(margin, min(max_x, x))),
            int(max(margin, min(max_y, y))),
        )

    def _draw_text_scaled_clamped(self, x: int, y: int, text: str, color: int, scale: int = 2) -> None:
        x, y = self._clamped_text_xy(x, y, text, scale)
        self._draw_text_scaled(x, y, text, color, scale=scale)

    def _draw_text_centered(self, center_x: int, y: int, text: str, color: int, scale: int = 2) -> None:
        x = int(center_x - self._scaled_text_width(text, scale) / 2)
        self._draw_text_scaled_clamped(x, y, text, color, scale=scale)

    def _draw_text_centered_shimmer(self, center_x: int, y: int, text: str, scale: int = 2) -> None:
        x = int(center_x - self._scaled_text_width(text, scale) / 2)
        x, y = self._clamped_text_xy(x, y, text, scale)
        self._draw_text_scaled_shimmer(x, y, text, scale=scale)

    def _draw_text_centered_jumping(self, center_x: int, y: int, text: str, color: int, scale: int = 2) -> None:
        x = int(center_x - self._scaled_text_width(text, scale) / 2)
        x, y = self._clamped_text_xy(x, y, text, scale)
        self._draw_text_scaled_jumping(x, y, text, color, scale=scale)

    def _draw_text_right_aligned(self, right_x: int, y: int, text: str, color: int, scale: int = 2) -> None:
        x = right_x - self._scaled_text_width(text, scale)
        self._draw_text_scaled_clamped(x, y, text, color, scale=scale)

    def _result_welcome_jump_offset(self, character_index: int) -> int:
        phase = (self.frame - character_index * 3) % 54
        if phase >= 18:
            return 0
        return int(round(math.sin(math.pi * phase / 18) * 7))

    def _draw_text_scaled_jumping(self, x: int, y: int, text: str, color: int, scale: int = 2) -> None:
        pyxel = self.pyxel
        assert pyxel is not None
        cursor_x = int(x)
        for index, character in enumerate(text.upper()):
            glyph = PIXEL_FONT_3X5.get(character, PIXEL_FONT_3X5["?"])
            jump = 0 if character == " " else self._result_welcome_jump_offset(index)
            for row, pixels in enumerate(glyph):
                for column, pixel in enumerate(pixels):
                    if pixel == "1":
                        pyxel.rect(
                            cursor_x + column * scale,
                            int(y) + row * scale - jump,
                            scale,
                            scale,
                            color,
                        )
            cursor_x += 4 * scale

    def _draw_text_scaled_shimmer(self, x: int, y: int, text: str, scale: int = 2) -> None:
        colors = (COLOR_ALERT, COLOR_HUD, COLOR_TRAJECTORY, 11, 12, 13)
        pyxel = self.pyxel
        assert pyxel is not None
        cursor_x = int(x)
        color_phase = self.frame // 6
        for index, character in enumerate(text.upper()):
            glyph = PIXEL_FONT_3X5.get(character, PIXEL_FONT_3X5["?"])
            color = colors[(color_phase - index) % len(colors)]
            for row, pixels in enumerate(glyph):
                for column, pixel in enumerate(pixels):
                    if pixel == "1":
                        pyxel.rect(
                            cursor_x + column * scale,
                            int(y) + row * scale,
                            scale,
                            scale,
                            color,
                        )
            cursor_x += 4 * scale

    def _draw_text_scaled(self, x: int, y: int, text: str, color: int, scale: int = 2) -> None:
        pyxel = self.pyxel
        assert pyxel is not None
        cursor_x = int(x)
        for character in text.upper():
            glyph = PIXEL_FONT_3X5.get(character, PIXEL_FONT_3X5["?"])
            for row, pixels in enumerate(glyph):
                for column, pixel in enumerate(pixels):
                    if pixel == "1":
                        pyxel.rect(
                            cursor_x + column * scale,
                            int(y) + row * scale,
                            scale,
                            scale,
                            color,
                        )
            cursor_x += 4 * scale
