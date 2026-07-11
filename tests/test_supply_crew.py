import unittest

from dataclasses import replace

import _path  # noqa: F401

from gravity_courier.app import GravityCourierApp
from gravity_courier.constants import (
    CREW_CELEBRATION_FRAMES,
    CREW_JOIN_SEQUENCE,
    ROCKET_FUEL_MAX,
    SUPPLY_PICKUP_RADIUS_BONUS,
    SUPPLY_SHIP_CARGO_FUEL_RATIO,
    SUPPLY_SHIP_CARGO_SCORE,
    SUPPLY_SHIP_DELAY_GAPS_MAX,
    SUPPLY_SHIP_DELAY_GAPS_MIN,
    SUPPLY_SHIP_STATION_FRAMES,
    WIDTH,
)
from gravity_courier.crew import (
    apply_crew_join,
    compact_crew_counts,
    crew_join_count_for_tier,
    initial_crew_count_by_type,
    initial_supply_success_tier_by_type,
    representative_crew_types,
    total_joined_crew,
)
from gravity_courier.entities import Planet, Rocket, Vec2
from gravity_courier.planet_types import PLANET_TYPE_ROCK, PLANET_TYPE_WATER, PLANET_TYPE_WIND
from gravity_courier.supply import (
    SUPPLY_STATUS_COLLECTED,
    SUPPLY_STATUS_MISSED,
    SUPPLY_STATUS_RESERVED,
    SUPPLY_STATUS_SPAWNED,
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


class SupplyReservationTest(unittest.TestCase):
    def test_lap_three_milestone_reserves_supply_ship(self) -> None:
        chances = initial_supply_success_tier_by_type()
        tiers = initial_supply_success_tier_by_type()

        self.assertFalse(should_reserve_supply_ship(1, PLANET_TYPE_ROCK, chances, tiers))
        self.assertFalse(should_reserve_supply_ship(2, PLANET_TYPE_ROCK, chances, tiers))
        self.assertTrue(should_reserve_supply_ship(3, PLANET_TYPE_ROCK, chances, tiers))
        self.assertTrue(should_reserve_supply_ship(6, PLANET_TYPE_ROCK, chances, tiers))

    def test_reservation_stores_source_and_uses_deterministic_delay(self) -> None:
        first = create_supply_reservation(1, PLANET_TYPE_WIND, 4, 3)
        second = create_supply_reservation(2, PLANET_TYPE_WATER, 5, 6)

        self.assertEqual(first.planet_type, PLANET_TYPE_WIND)
        self.assertEqual(first.source_planet_id, 4)
        self.assertEqual(first.source_lap_count, 3)
        self.assertEqual(first.remaining_gap_count, SUPPLY_SHIP_DELAY_GAPS_MIN)
        self.assertEqual(second.remaining_gap_count, SUPPLY_SHIP_DELAY_GAPS_MAX)
        self.assertEqual(first.status, SUPPLY_STATUS_RESERVED)

    def test_gap_advancement_spawns_after_delay_not_immediately(self) -> None:
        reservation = create_supply_reservation(1, PLANET_TYPE_ROCK, 0, 3)

        self.assertFalse(is_reservation_ready_to_spawn(reservation))
        once = advance_reserved_gap(reservation)
        self.assertFalse(is_reservation_ready_to_spawn(once))
        twice = advance_reserved_gap(once)
        self.assertTrue(is_reservation_ready_to_spawn(twice))

        spawned = mark_reservation_spawned(twice)
        self.assertEqual(spawned.status, SUPPLY_STATUS_SPAWNED)


class CrewJoinSequenceTest(unittest.TestCase):
    def test_join_sequence_doubles_and_clamps(self) -> None:
        crew = initial_crew_count_by_type()
        tiers = initial_supply_success_tier_by_type()
        joined = [apply_crew_join(crew, tiers, PLANET_TYPE_ROCK) for _ in range(8)]

        self.assertEqual(tuple(joined[:7]), CREW_JOIN_SEQUENCE)
        self.assertEqual(joined[7], 0)
        self.assertEqual(crew[PLANET_TYPE_ROCK], sum(CREW_JOIN_SEQUENCE))
        self.assertEqual(tiers[PLANET_TYPE_ROCK], len(CREW_JOIN_SEQUENCE))

    def test_per_type_crew_counts_are_independent(self) -> None:
        crew = initial_crew_count_by_type()
        tiers = initial_supply_success_tier_by_type()

        self.assertEqual(apply_crew_join(crew, tiers, PLANET_TYPE_ROCK), 1)
        self.assertEqual(apply_crew_join(crew, tiers, PLANET_TYPE_WIND), 1)
        self.assertEqual(apply_crew_join(crew, tiers, PLANET_TYPE_ROCK), 2)

        self.assertEqual(crew[PLANET_TYPE_ROCK], 3)
        self.assertEqual(crew[PLANET_TYPE_WIND], 1)
        self.assertEqual(tiers[PLANET_TYPE_WIND], 1)

    def test_crew_ui_helpers_are_stable(self) -> None:
        crew = initial_crew_count_by_type()
        crew[PLANET_TYPE_WIND] = 4
        crew[PLANET_TYPE_ROCK] = 2

        self.assertEqual(total_joined_crew(crew), 6)
        self.assertEqual(compact_crew_counts(crew)[0], ("WIND", 4))
        self.assertEqual(representative_crew_types(crew, max_types=1), (PLANET_TYPE_WIND,))
        self.assertEqual(crew_join_count_for_tier(7), 0)


class SupplyCargoTest(unittest.TestCase):
    def test_cargo_reward_adds_score_fuel_and_crew_count_payload(self) -> None:
        reservation = create_supply_reservation(1, PLANET_TYPE_ROCK, 0, 3)
        ship = make_supply_ship_from_reservation(reservation, y=100.0, direction=1)
        collected_ship, collection = collect_supply_cargo(ship, crew_join_count=4)
        rocket = Rocket(fuel=ROCKET_FUEL_MAX - 1.0)

        score, fuel = apply_supply_cargo_reward(rocket, 200, collection, ROCKET_FUEL_MAX)

        self.assertTrue(collection.collected)
        self.assertFalse(collected_ship.active)
        self.assertEqual(collection.score_gain, SUPPLY_SHIP_CARGO_SCORE)
        self.assertEqual(collection.fuel_gain_ratio, SUPPLY_SHIP_CARGO_FUEL_RATIO)
        self.assertEqual(collection.crew_join_count, 4)
        self.assertEqual(score, 200 + SUPPLY_SHIP_CARGO_SCORE)
        self.assertEqual(fuel, ROCKET_FUEL_MAX)

    def test_cargo_cannot_be_collected_twice(self) -> None:
        reservation = create_supply_reservation(1, PLANET_TYPE_ROCK, 0, 3)
        ship = make_supply_ship_from_reservation(reservation, y=100.0, direction=1)

        collected_ship, first = collect_supply_cargo(ship, crew_join_count=1)
        again, second = collect_supply_cargo(collected_ship, crew_join_count=2)

        self.assertTrue(first.collected)
        self.assertFalse(second.collected)
        self.assertEqual(again, collected_ship)

    def test_missed_cargo_consumes_event_without_advancing_tier(self) -> None:
        crew = initial_crew_count_by_type()
        tiers = initial_supply_success_tier_by_type()
        reservation = create_supply_reservation(1, PLANET_TYPE_ROCK, 0, 3)

        missed = mark_reservation_missed(reservation)
        join_count = apply_crew_join(crew, tiers, PLANET_TYPE_ROCK)

        self.assertEqual(missed.status, SUPPLY_STATUS_MISSED)
        self.assertEqual(join_count, 1)
        self.assertEqual(crew[PLANET_TYPE_ROCK], 1)

    def test_collected_status_is_recorded(self) -> None:
        reservation = create_supply_reservation(1, PLANET_TYPE_ROCK, 0, 3)

        self.assertEqual(mark_reservation_collected(reservation).status, SUPPLY_STATUS_COLLECTED)

    def test_supply_cargo_overlap_requires_active_cargo_after_warning(self) -> None:
        reservation = create_supply_reservation(1, PLANET_TYPE_ROCK, 0, 3)
        ship = make_supply_ship_from_reservation(reservation, y=100.0, direction=1)
        rocket_pos = ship.cargo_pos

        self.assertFalse(supply_cargo_overlaps(ship, rocket_pos, rocket_radius=10.0))
        ready_ship = replace(ship, warning_timer=0)
        self.assertTrue(supply_cargo_overlaps(ready_ship, rocket_pos, rocket_radius=10.0))

    def test_supply_cargo_overlap_accepts_ship_body_contact(self) -> None:
        reservation = create_supply_reservation(1, PLANET_TYPE_ROCK, 0, 3)
        ship = make_supply_ship_from_reservation(reservation, y=100.0, direction=1)
        ready_ship = replace(ship, warning_timer=0)

        self.assertTrue(supply_cargo_overlaps(ready_ship, ready_ship.pos, rocket_radius=10.0))

    def test_supply_cargo_overlap_has_pickup_padding(self) -> None:
        reservation = create_supply_reservation(1, PLANET_TYPE_ROCK, 0, 3)
        ship = make_supply_ship_from_reservation(reservation, y=100.0, direction=1)
        ready_ship = replace(ship, warning_timer=0)
        padded_edge = ready_ship.cargo_radius + 10.0 + SUPPLY_PICKUP_RADIUS_BONUS - 0.1
        near_cargo = ready_ship.cargo_pos + Vec2(padded_edge, 0.0)

        self.assertTrue(supply_cargo_overlaps(ready_ship, near_cargo, rocket_radius=10.0))

    def test_supply_ship_stations_between_planets_before_departing(self) -> None:
        reservation = create_supply_reservation(1, PLANET_TYPE_ROCK, 0, 3)
        ship = make_supply_ship_from_reservation(reservation, y=100.0, direction=1)
        ready_ship = replace(ship, warning_timer=0)

        stationed = update_supply_ship(ready_ship)

        self.assertEqual(ship.pos.x, WIDTH * 0.5)
        self.assertEqual(stationed.pos, ready_ship.pos)
        self.assertEqual(stationed.station_timer, SUPPLY_SHIP_STATION_FRAMES - 1)

    def test_supply_ship_departs_after_station_timer(self) -> None:
        reservation = create_supply_reservation(1, PLANET_TYPE_ROCK, 0, 3)
        ship = make_supply_ship_from_reservation(reservation, y=100.0, direction=1)
        ready_ship = replace(ship, warning_timer=0, station_timer=0)

        moved = update_supply_ship(ready_ship)

        self.assertGreater(moved.pos.x, ready_ship.pos.x)

    def test_stationary_supply_ship_waits_without_departing(self) -> None:
        reservation = create_supply_reservation(1, PLANET_TYPE_ROCK, 0, 3)
        ship = make_supply_ship_from_reservation(reservation, y=100.0, direction=1)
        waiting_ship = replace(ship, warning_timer=0, station_timer=0, lifetime=1, stationary=True)

        updated = update_supply_ship(waiting_ship)

        self.assertEqual(updated, waiting_ship)


class SupplyAppIntegrationTest(unittest.TestCase):
    def test_lap_three_creates_reservation_in_app(self) -> None:
        app = GravityCourierApp()
        app.planets = [
            Planet(
                position=Vec2(0.0, 0.0),
                mass=3000.0,
                radius=20.0,
                gravity_well_radius=80.0,
                planet_type=PLANET_TYPE_ROCK,
            )
        ]
        app.planet_lap_counts = [2]

        app._handle_lap_completed(0)

        self.assertEqual(len(app.supply_reservations), 1)
        self.assertEqual(app.supply_reservations[0].planet_type, PLANET_TYPE_ROCK)
        self.assertEqual(app.supply_reservations[0].source_lap_count, 3)
        self.assertIsNotNone(app.supply_reservations[0].target_gap_id)
        assert app.supply_reservations[0].target_gap_id is not None
        self.assertTrue(app.course_gaps[app.supply_reservations[0].target_gap_id].is_supply_wide_gap)

    def test_transfer_gap_advancement_spawns_ship_after_delay(self) -> None:
        app = GravityCourierApp()
        app.supply_reservations = [create_supply_reservation(1, PLANET_TYPE_ROCK, 0, 3)]

        app._advance_supply_reservations_after_transfer()
        self.assertEqual(len(app.supply_ships), 0)
        app._advance_supply_reservations_after_transfer()

        self.assertEqual(len(app.supply_ships), 0)
        self.assertEqual(app.supply_reservations[0].status, SUPPLY_STATUS_SPAWNED)

        app._update_supply_ships()

        self.assertEqual(len(app.supply_ships), 1)
        self.assertTrue(app.supply_ships[0].stationary)
        self.assertEqual(app.supply_ships[0].warning_timer, 0)

    def test_spawned_supply_ship_waits_across_supply_zone_updates(self) -> None:
        app = GravityCourierApp()
        reservation = mark_reservation_spawned(create_supply_reservation(1, PLANET_TYPE_ROCK, 0, 3))
        app.supply_reservations = [reservation]

        for _ in range(5):
            app._update_supply_ships()

        self.assertEqual(len(app.supply_ships), 1)
        self.assertTrue(app.supply_ships[0].active)
        self.assertTrue(app.supply_ships[0].stationary)
        self.assertEqual(app.supply_reservations[0].status, SUPPLY_STATUS_SPAWNED)

    def test_waiting_supply_ship_does_not_follow_camera_after_spawn(self) -> None:
        app = GravityCourierApp()
        reservation = mark_reservation_spawned(create_supply_reservation(1, PLANET_TYPE_ROCK, 0, 3))
        app.supply_reservations = [reservation]
        app._update_supply_ships()
        original_pos = app.supply_ships[0].pos

        app.camera.position = app.camera.position + Vec2(72.0, -180.0)
        app.rocket = replace(app.rocket, position=app.rocket.position + Vec2(72.0, -180.0))
        app._update_supply_ships()

        self.assertEqual(app.supply_ships[0].pos, original_pos)

    def test_multiple_waiting_supply_ships_align_by_planet_type(self) -> None:
        app = GravityCourierApp()
        app.supply_reservations = [
            mark_reservation_spawned(create_supply_reservation(1, PLANET_TYPE_WIND, 0, 3)),
            mark_reservation_spawned(create_supply_reservation(2, PLANET_TYPE_ROCK, 1, 3)),
        ]

        app._update_supply_ships()

        ships_by_type = {ship.planet_type: ship for ship in app.supply_ships}
        self.assertEqual(len(ships_by_type), 2)
        self.assertTrue(all(ship.stationary for ship in ships_by_type.values()))
        self.assertLess(ships_by_type[PLANET_TYPE_WIND].pos.x, ships_by_type[PLANET_TYPE_ROCK].pos.x)

    def test_same_type_waiting_supply_ships_stack_vertically(self) -> None:
        app = GravityCourierApp()
        app.supply_reservations = [
            mark_reservation_spawned(create_supply_reservation(1, PLANET_TYPE_ROCK, 0, 3)),
            mark_reservation_spawned(create_supply_reservation(2, PLANET_TYPE_ROCK, 1, 6)),
        ]

        app._update_supply_ships()

        self.assertEqual(len(app.supply_ships), 2)
        self.assertEqual(app.supply_ships[0].pos.x, app.supply_ships[1].pos.x)
        self.assertNotEqual(app.supply_ships[0].pos.y, app.supply_ships[1].pos.y)

    def test_collected_waiting_supply_ship_leaves_queue(self) -> None:
        app = GravityCourierApp()
        app.supply_reservations = [
            mark_reservation_spawned(create_supply_reservation(1, PLANET_TYPE_ROCK, 0, 3)),
        ]
        app._update_supply_ships()
        app.rocket = replace(app.rocket, position=app.supply_ships[0].cargo_pos)

        app._update_supply_ships()

        self.assertEqual(app.supply_reservations[0].status, SUPPLY_STATUS_COLLECTED)
        self.assertEqual(app.crew_count_by_type[PLANET_TYPE_ROCK], 1)

        app._update_supply_ships()

        self.assertEqual(app.supply_ships, [])

    def test_transfer_boost_starts_crew_ui_celebration(self) -> None:
        app = GravityCourierApp()
        app.orbit_progress[0].transfer_ready = True
        app.orbit_progress[0].in_orbit = True

        app._trigger_transfer_boost(0)

        self.assertEqual(app.crew_celebration_timer, CREW_CELEBRATION_FRAMES)

    def test_supply_ship_cargo_starts_crew_ui_celebration(self) -> None:
        app = GravityCourierApp()
        reservation = create_supply_reservation(1, PLANET_TYPE_ROCK, 0, 3)
        app.supply_reservations = [reservation]
        ship = make_supply_ship_from_reservation(reservation, y=100.0, direction=1)
        ready_ship = replace(ship, warning_timer=0)

        app._collect_supply_ship_cargo(ready_ship)

        self.assertEqual(app.crew_count_by_type[PLANET_TYPE_ROCK], 1)
        self.assertEqual(app.crew_celebration_timer, CREW_CELEBRATION_FRAMES)
        self.assertEqual(app.crew_type_celebration_timers[PLANET_TYPE_ROCK], CREW_CELEBRATION_FRAMES)

    def test_lap_completion_starts_matching_crew_type_celebration(self) -> None:
        app = GravityCourierApp()
        planet_type = app.planets[0].planet_type
        app.crew_count_by_type[planet_type] = 1

        app._handle_lap_completed(0)

        self.assertEqual(app.crew_type_celebration_timers[planet_type], CREW_CELEBRATION_FRAMES)

    def test_restart_resets_supply_and_crew_state(self) -> None:
        app = GravityCourierApp()
        app.supply_reservations = [create_supply_reservation(1, PLANET_TYPE_ROCK, 0, 3)]
        app.crew_count_by_type[PLANET_TYPE_ROCK] = 7
        app.supply_success_tier_by_type[PLANET_TYPE_ROCK] = 3
        app.supply_ship_chance_count_by_type[PLANET_TYPE_ROCK] = 2

        app.restart()

        self.assertEqual(app.supply_reservations, [])
        self.assertEqual(app.supply_ships, [])
        self.assertEqual(total_joined_crew(app.crew_count_by_type), 0)
        self.assertEqual(app.supply_success_tier_by_type[PLANET_TYPE_ROCK], 0)
        self.assertEqual(app.supply_ship_chance_count_by_type[PLANET_TYPE_ROCK], 0)


if __name__ == "__main__":
    unittest.main()
