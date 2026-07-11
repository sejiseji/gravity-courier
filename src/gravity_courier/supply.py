"""Supply ship reservation and cargo helpers for Gravity Courier."""

from __future__ import annotations

from dataclasses import dataclass, replace

from .constants import (
    MAX_SUPPLY_SHIP_CHANCES_PER_TYPE,
    MAX_SUPPLY_TIERS_PER_TYPE,
    SUPPLY_CARGO_RADIUS,
    SUPPLY_LAP_INTERVAL,
    SUPPLY_PICKUP_RADIUS_BONUS,
    SUPPLY_SHIP_CARGO_FUEL_RATIO,
    SUPPLY_SHIP_CARGO_SCORE,
    SUPPLY_SHIP_DELAY_GAPS_MAX,
    SUPPLY_SHIP_DELAY_GAPS_MIN,
    SUPPLY_SHIP_LIFETIME_FRAMES,
    SUPPLY_SHIP_RADIUS,
    SUPPLY_SHIP_SPEED,
    SUPPLY_SHIP_STATION_FRAMES,
    SUPPLY_SHIP_WARNING_FRAMES,
    WIDTH,
    INTERPLANET_OBJECT_DESPAWN_MARGIN,
)
from .crew import CREW_PLANET_TYPES
from .entities import Rocket, Vec2

SUPPLY_STATUS_RESERVED = "reserved"
SUPPLY_STATUS_SPAWNED = "spawned"
SUPPLY_STATUS_COLLECTED = "collected"
SUPPLY_STATUS_MISSED = "missed"


@dataclass(frozen=True)
class SupplyShipReservation:
    reservation_id: int
    planet_type: str
    source_planet_id: int
    source_lap_count: int
    remaining_gap_count: int
    target_gap_id: int | None = None
    status: str = SUPPLY_STATUS_RESERVED


@dataclass(frozen=True)
class SupplyShip:
    reservation_id: int
    planet_type: str
    pos: Vec2
    vel: Vec2
    radius: float = SUPPLY_SHIP_RADIUS
    cargo_radius: float = SUPPLY_CARGO_RADIUS
    warning_timer: int = SUPPLY_SHIP_WARNING_FRAMES
    station_timer: int = SUPPLY_SHIP_STATION_FRAMES
    lifetime: int = SUPPLY_SHIP_LIFETIME_FRAMES
    active: bool = True
    cargo_active: bool = True
    cargo_collected: bool = False
    stationary: bool = False

    @property
    def cargo_pos(self) -> Vec2:
        return self.pos + Vec2(0.0, self.radius + self.cargo_radius + 4.0)


@dataclass(frozen=True)
class SupplyCargoCollection:
    collected: bool
    planet_type: str = ""
    score_gain: int = 0
    fuel_gain_ratio: float = 0.0
    crew_join_count: int = 0


def deterministic_supply_delay(reservation_id: int) -> int:
    return SUPPLY_SHIP_DELAY_GAPS_MIN if reservation_id % 2 == 1 else SUPPLY_SHIP_DELAY_GAPS_MAX


def should_reserve_supply_ship(
    lap_count: int,
    planet_type: str,
    supply_ship_chance_count_by_type: dict[str, int],
    supply_success_tier_by_type: dict[str, int],
) -> bool:
    if planet_type not in CREW_PLANET_TYPES:
        return False
    if lap_count <= 0 or lap_count % SUPPLY_LAP_INTERVAL != 0:
        return False
    if supply_ship_chance_count_by_type.get(planet_type, 0) >= MAX_SUPPLY_SHIP_CHANCES_PER_TYPE:
        return False
    if supply_success_tier_by_type.get(planet_type, 0) >= MAX_SUPPLY_TIERS_PER_TYPE:
        return False
    return True


def create_supply_reservation(
    reservation_id: int,
    planet_type: str,
    source_planet_id: int,
    source_lap_count: int,
    target_gap_id: int | None = None,
) -> SupplyShipReservation:
    return SupplyShipReservation(
        reservation_id=reservation_id,
        planet_type=planet_type,
        source_planet_id=source_planet_id,
        source_lap_count=source_lap_count,
        remaining_gap_count=deterministic_supply_delay(reservation_id),
        target_gap_id=target_gap_id,
    )


def advance_reserved_gap(reservation: SupplyShipReservation) -> SupplyShipReservation:
    if reservation.status != SUPPLY_STATUS_RESERVED:
        return reservation
    return replace(reservation, remaining_gap_count=max(0, reservation.remaining_gap_count - 1))


def is_reservation_ready_to_spawn(reservation: SupplyShipReservation) -> bool:
    return reservation.status == SUPPLY_STATUS_RESERVED and reservation.remaining_gap_count <= 0


def mark_reservation_spawned(reservation: SupplyShipReservation) -> SupplyShipReservation:
    return replace(reservation, status=SUPPLY_STATUS_SPAWNED)


def mark_reservation_collected(reservation: SupplyShipReservation) -> SupplyShipReservation:
    return replace(reservation, status=SUPPLY_STATUS_COLLECTED)


def mark_reservation_missed(reservation: SupplyShipReservation) -> SupplyShipReservation:
    return replace(reservation, status=SUPPLY_STATUS_MISSED)


def make_supply_ship_from_reservation(
    reservation: SupplyShipReservation,
    y: float,
    direction: int,
) -> SupplyShip:
    speed = SUPPLY_SHIP_SPEED if direction >= 0 else -SUPPLY_SHIP_SPEED
    return SupplyShip(
        reservation_id=reservation.reservation_id,
        planet_type=reservation.planet_type,
        pos=Vec2(WIDTH * 0.5, y),
        vel=Vec2(speed, 0.0),
    )


def update_supply_ship(ship: SupplyShip) -> SupplyShip:
    if not ship.active:
        return ship
    if ship.stationary:
        return ship
    if ship.warning_timer > 0:
        return replace(ship, warning_timer=ship.warning_timer - 1)
    next_lifetime = ship.lifetime - 1
    if ship.station_timer > 0:
        return replace(ship, station_timer=ship.station_timer - 1, lifetime=next_lifetime)
    next_ship = replace(ship, pos=ship.pos + ship.vel, lifetime=next_lifetime)
    if next_lifetime <= 0 or supply_ship_out_of_range(next_ship):
        return replace(next_ship, active=False, cargo_active=False)
    return next_ship


def supply_ship_out_of_range(ship: SupplyShip) -> bool:
    margin = INTERPLANET_OBJECT_DESPAWN_MARGIN
    return ship.pos.x < -margin or ship.pos.x > WIDTH + margin


def supply_cargo_overlaps(ship: SupplyShip, rocket_pos: Vec2, rocket_radius: float) -> bool:
    if not ship.active or not ship.cargo_active or ship.cargo_collected or ship.warning_timer > 0:
        return False
    pickup_radius = rocket_radius + SUPPLY_PICKUP_RADIUS_BONUS
    cargo_overlap = ship.cargo_pos.distance_to(rocket_pos) <= ship.cargo_radius + pickup_radius
    ship_overlap = ship.pos.distance_to(rocket_pos) <= ship.radius + rocket_radius
    return cargo_overlap or ship_overlap


def collect_supply_cargo(ship: SupplyShip, crew_join_count: int) -> tuple[SupplyShip, SupplyCargoCollection]:
    if not ship.active or not ship.cargo_active or ship.cargo_collected:
        return ship, SupplyCargoCollection(collected=False)
    return (
        replace(ship, active=False, cargo_active=False, cargo_collected=True),
        SupplyCargoCollection(
            collected=True,
            planet_type=ship.planet_type,
            score_gain=SUPPLY_SHIP_CARGO_SCORE,
            fuel_gain_ratio=SUPPLY_SHIP_CARGO_FUEL_RATIO,
            crew_join_count=crew_join_count,
        ),
    )


def apply_supply_cargo_reward(
    rocket: Rocket,
    current_score: int,
    collection: SupplyCargoCollection,
    max_fuel: float,
) -> tuple[int, float]:
    if not collection.collected:
        return current_score, rocket.fuel
    return (
        current_score + collection.score_gain,
        min(max_fuel, rocket.fuel + max_fuel * collection.fuel_gain_ratio),
    )
