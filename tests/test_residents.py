import unittest

import _path  # noqa: F401

from gravity_courier.constants import SPRITE_TRANSPARENT_COLKEY
from gravity_courier.planet_types import (
    PLANET_TYPE_FOREST,
    PLANET_TYPE_IRON,
    PLANET_TYPE_ROCK,
    PLANET_TYPE_WATER,
    PLANET_TYPE_WIND,
)
from gravity_courier.residents import (
    CHEER_STAGES,
    RESIDENTS_BY_PLANET_TYPE,
    SPRITE_STAGES,
    resident_for_planet_type,
    stage_for_lap,
)


class ResidentRegistryTest(unittest.TestCase):
    def test_required_planet_types_have_residents(self) -> None:
        for planet_type in (
            PLANET_TYPE_WIND,
            PLANET_TYPE_IRON,
            PLANET_TYPE_WATER,
            PLANET_TYPE_FOREST,
            PLANET_TYPE_ROCK,
        ):
            self.assertIn(planet_type, RESIDENTS_BY_PLANET_TYPE)

    def test_resident_ids_are_unique(self) -> None:
        ids = [resident.resident_id for resident in RESIDENTS_BY_PLANET_TYPE.values()]

        self.assertEqual(len(ids), len(set(ids)))

    def test_each_resident_has_required_cheer_lines_and_sprites(self) -> None:
        for resident in RESIDENTS_BY_PLANET_TYPE.values():
            for stage in CHEER_STAGES:
                self.assertIn(stage, resident.cheer_lines)
                self.assertGreater(len(resident.cheer_lines[stage]), 0)
                self.assertTrue(resident.cheer_lines[stage][0])
            for stage in SPRITE_STAGES:
                sprite = resident.stage_sprites[stage]
                self.assertEqual(sprite.w, 32)
                self.assertEqual(sprite.h, 32)
                self.assertEqual(sprite.colkey, SPRITE_TRANSPARENT_COLKEY)

    def test_lookup_by_planet_type(self) -> None:
        self.assertEqual(resident_for_planet_type(PLANET_TYPE_WIND).resident_id, "wind_gale")
        self.assertEqual(resident_for_planet_type(PLANET_TYPE_ROCK).resident_id, "rock_rokka")

    def test_resident_atlas_rows_start_below_hero_row(self) -> None:
        expected_rows = {
            PLANET_TYPE_WIND: 32,
            PLANET_TYPE_IRON: 64,
            PLANET_TYPE_WATER: 96,
            PLANET_TYPE_FOREST: 128,
            PLANET_TYPE_ROCK: 160,
        }

        for planet_type, expected_v in expected_rows.items():
            resident = RESIDENTS_BY_PLANET_TYPE[planet_type]

            self.assertEqual(resident.stage_sprites[0].v, expected_v)

    def test_initial_resident_art_reuses_idle_cell_for_all_cheer_stages(self) -> None:
        for planet_type in (PLANET_TYPE_WIND, PLANET_TYPE_IRON, PLANET_TYPE_WATER, PLANET_TYPE_FOREST, PLANET_TYPE_ROCK):
            resident = RESIDENTS_BY_PLANET_TYPE[planet_type]
            idle = resident.stage_sprites[0]

            for stage in SPRITE_STAGES:
                self.assertEqual(resident.stage_sprites[stage], idle)

    def test_lap_three_and_beyond_maps_to_stage_three(self) -> None:
        self.assertEqual(stage_for_lap(1), 1)
        self.assertEqual(stage_for_lap(2), 2)
        self.assertEqual(stage_for_lap(3), 3)
        self.assertEqual(stage_for_lap(9), 3)


if __name__ == "__main__":
    unittest.main()
