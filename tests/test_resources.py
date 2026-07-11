import tempfile
import unittest
from pathlib import Path

import _path  # noqa: F401

from gravity_courier.app import GravityCourierApp
from gravity_courier.constants import (
    ASSETS_DIR,
    COLOR_GRAVITY_WELL,
    CUTIN_PANEL_HEIGHT,
    CUTIN_RESIDENT_DRAW_SIZE,
    CUTIN_RESIDENT_SCALE,
    HEIGHT,
    HERO_SPRITE_COLKEY,
    RESIDENT_RESOURCE_PATH,
    SPRITE_TRANSPARENT_COLKEY,
    WIDTH,
)
from gravity_courier.crew import CREW_PLANET_TYPES
from gravity_courier.cutin import CUTIN_SIDE_LEFT
from gravity_courier.planet_types import PLANET_TYPE_WIND, planet_type_spec
from gravity_courier.resources import (
    HERO_SPRITE,
    ROCKET_SPRITE,
    ResidentResourceState,
    load_resident_resources,
    resident_resource_exists,
)


class FakePyxelLoader:
    def __init__(self, fail: bool = False) -> None:
        self.fail = fail
        self.loaded_paths: list[str] = []

    def load(self, path: str) -> None:
        self.loaded_paths.append(path)
        if self.fail:
            raise RuntimeError("load failed")


class FakeImage:
    def __init__(self, lit_pixels: set[tuple[int, int]], color: int = 7, colkey: int = SPRITE_TRANSPARENT_COLKEY) -> None:
        self.lit_pixels = lit_pixels
        self.color = color
        self.colkey = colkey

    def pget(self, x: int, y: int) -> int:
        return self.color if (x, y) in self.lit_pixels else self.colkey


class RecordingPyxel:
    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple[object, ...], dict[str, object]]] = []
        self.images = [FakeImage(set())]

    def blt(self, *args: object, **kwargs: object) -> None:
        self.calls.append(("blt", args, kwargs))

    def circ(self, *args: object, **kwargs: object) -> None:
        self.calls.append(("circ", args, kwargs))

    def rect(self, *args: object, **kwargs: object) -> None:
        self.calls.append(("rect", args, kwargs))

    def rectb(self, *args: object, **kwargs: object) -> None:
        self.calls.append(("rectb", args, kwargs))

    def line(self, *args: object, **kwargs: object) -> None:
        self.calls.append(("line", args, kwargs))

    def pset(self, *args: object, **kwargs: object) -> None:
        self.calls.append(("pset", args, kwargs))


class ResourceLoadingTest(unittest.TestCase):
    def test_resident_resource_path_is_under_assets_dir(self) -> None:
        self.assertEqual(RESIDENT_RESOURCE_PATH.parent, ASSETS_DIR)
        self.assertEqual(RESIDENT_RESOURCE_PATH.name, "gravity_courier.pyxres")

    def test_missing_resource_is_not_available_and_does_not_raise(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            missing = Path(tmpdir) / "missing.pyxres"

            state = load_resident_resources(pyxel_module=object(), path=missing)

        self.assertFalse(state.sprite_available)
        self.assertFalse(state.hero_sprite_available)
        self.assertEqual(state.warning, "")

    def test_missing_resource_exists_helper_returns_false(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            missing = Path(tmpdir) / "missing.pyxres"

            self.assertFalse(resident_resource_exists(missing))

    def test_hero_sprite_reference_uses_first_atlas_cell_and_colkey_fourteen(self) -> None:
        self.assertEqual(HERO_SPRITE.image_bank, 0)
        self.assertEqual(HERO_SPRITE.u, 0)
        self.assertEqual(HERO_SPRITE.v, 0)
        self.assertEqual(HERO_SPRITE.w, 32)
        self.assertEqual(HERO_SPRITE.h, 32)
        self.assertEqual(HERO_SPRITE.colkey, HERO_SPRITE_COLKEY)
        self.assertEqual(HERO_SPRITE_COLKEY, SPRITE_TRANSPARENT_COLKEY)
        self.assertEqual(SPRITE_TRANSPARENT_COLKEY, 14)

    def test_rocket_sprite_reference_uses_vertical_rocket_cell(self) -> None:
        self.assertEqual(ROCKET_SPRITE.image_bank, 0)
        self.assertEqual(ROCKET_SPRITE.u, 0)
        self.assertEqual(ROCKET_SPRITE.v, 192)
        self.assertEqual(ROCKET_SPRITE.w, 16)
        self.assertEqual(ROCKET_SPRITE.h, 32)
        self.assertEqual(ROCKET_SPRITE.colkey, SPRITE_TRANSPARENT_COLKEY)

    def test_loaded_resource_enables_hero_and_initial_residents(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            resource = Path(tmpdir) / "gravity_courier.pyxres"
            resource.write_bytes(b"fake resource")
            pyxel = FakePyxelLoader()

            state = load_resident_resources(pyxel_module=pyxel, path=resource)

        self.assertTrue(state.resource_loaded)
        self.assertTrue(state.hero_sprite_available)
        self.assertTrue(state.resident_sprite_available)
        self.assertTrue(state.rocket_sprite_available)
        self.assertTrue(state.sprite_available)
        self.assertEqual(len(pyxel.loaded_paths), 1)

    def test_resource_load_failure_keeps_hero_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            resource = Path(tmpdir) / "gravity_courier.pyxres"
            resource.write_bytes(b"fake resource")

            state = load_resident_resources(pyxel_module=FakePyxelLoader(fail=True), path=resource)

        self.assertFalse(state.resource_loaded)
        self.assertFalse(state.hero_sprite_available)
        self.assertFalse(state.resident_sprite_available)
        self.assertFalse(state.rocket_sprite_available)
        self.assertIn("Could not load", state.warning)

    def test_hero_draw_uses_sprite_only_when_hero_resource_is_ready(self) -> None:
        app = GravityCourierApp()
        pyxel = RecordingPyxel()
        app.pyxel = pyxel
        app.resident_resources = ResidentResourceState(
            path=RESIDENT_RESOURCE_PATH,
            resource_loaded=True,
            hero_sprite_available=True,
            resident_sprite_available=False,
        )

        app._draw_hero(4, 5, scale=1)

        self.assertEqual(pyxel.calls[0][0], "blt")
        self.assertEqual(pyxel.calls[0][1][:7], (4, 5, 0, 0, 0, 32, 32))
        self.assertEqual(pyxel.calls[0][1][7], HERO_SPRITE_COLKEY)
        self.assertEqual(pyxel.calls[0][2], {"scale": 1})

    def test_rocket_draw_rotates_sprite_when_resource_is_ready(self) -> None:
        app = GravityCourierApp()
        pyxel = RecordingPyxel()
        pyxel.images[0] = FakeImage({(ROCKET_SPRITE.u + ROCKET_SPRITE.w // 2, ROCKET_SPRITE.v)})
        app.pyxel = pyxel
        app.rocket.angle = 0.0
        app.resident_resources = ResidentResourceState(
            path=RESIDENT_RESOURCE_PATH,
            resource_loaded=True,
            hero_sprite_available=False,
            resident_sprite_available=False,
            rocket_sprite_available=True,
        )

        app._draw_rocket()

        pset_calls = [call for call in pyxel.calls if call[0] == "pset"]
        self.assertGreater(len(pset_calls), 0)
        self.assertTrue(any(args[0] > WIDTH // 2 + 10 for _name, args, _kwargs in pset_calls))
        self.assertEqual([call for call in pyxel.calls if call[0] == "blt"], [])

    def test_hero_draw_uses_primitive_fallback_when_resource_is_missing(self) -> None:
        app = GravityCourierApp()
        pyxel = RecordingPyxel()
        app.pyxel = pyxel

        app._draw_hero(4, 5, scale=1)

        self.assertNotIn("blt", {name for name, _args, _kwargs in pyxel.calls})
        self.assertIn("circ", {name for name, _args, _kwargs in pyxel.calls})

    def test_crew_ui_uses_full_width_bottom_panel(self) -> None:
        app = GravityCourierApp()
        pyxel = RecordingPyxel()
        app.pyxel = pyxel

        app._draw_crew_ui()

        self.assertEqual(pyxel.calls[0], ("rect", (8, HEIGHT - 148, WIDTH - 16, 66, 1), {}))
        self.assertEqual(pyxel.calls[1], ("rectb", (8, HEIGHT - 148, WIDTH - 16, 66, COLOR_GRAVITY_WELL), {}))
        marker_borders = [
            args
            for name, args, _kwargs in pyxel.calls
            if name == "rectb" and len(args) >= 4 and args[2:4] == (32, 32)
        ]
        self.assertEqual(len(marker_borders), len(CREW_PLANET_TYPES))

    def test_crew_ui_labels_slots_with_large_planet_names(self) -> None:
        app = GravityCourierApp()
        pyxel = RecordingPyxel()
        app.pyxel = pyxel
        labels: list[tuple[str, int]] = []

        def record_text(_x: int, _y: int, text: str, _color: int, scale: int = 1) -> None:
            labels.append((text, scale))

        app._draw_text_scaled = record_text  # type: ignore[method-assign]

        app._draw_crew_ui()

        for planet_type in CREW_PLANET_TYPES:
            self.assertIn((planet_type_spec(planet_type).debug_label, 2), labels)
        self.assertNotIn(("W0", 1), labels)

    def test_crew_ui_uses_resident_sprite_for_joined_type_when_available(self) -> None:
        app = GravityCourierApp()
        pyxel = RecordingPyxel()
        app.pyxel = pyxel
        app.resident_resources = ResidentResourceState(
            path=RESIDENT_RESOURCE_PATH,
            resource_loaded=True,
            hero_sprite_available=True,
            resident_sprite_available=True,
        )
        app.crew_count_by_type[PLANET_TYPE_WIND] = 1

        app._draw_crew_ui()

        blt_calls = [args for name, args, _kwargs in pyxel.calls if name == "blt"]
        resident_calls = [args for args in blt_calls if args[:7] == (134, HEIGHT - 140, 0, 0, 32, 32, 32)]
        self.assertEqual(len(resident_calls), 1)
        self.assertEqual(resident_calls[0][7], SPRITE_TRANSPARENT_COLKEY)

    def test_crew_ui_draws_confetti_during_celebration(self) -> None:
        app = GravityCourierApp()
        pyxel = RecordingPyxel()
        app.pyxel = pyxel
        app._trigger_crew_celebration()

        app._draw_crew_ui()

        confetti_rects = [
            args
            for name, args, _kwargs in pyxel.calls
            if name == "rect" and len(args) >= 4 and args[2:4] == (2, 2)
        ]
        self.assertGreater(len(confetti_rects), 0)

    def test_crew_ui_joined_type_jumps_during_matching_celebration(self) -> None:
        app = GravityCourierApp()
        pyxel = RecordingPyxel()
        app.pyxel = pyxel
        app.resident_resources = ResidentResourceState(
            path=RESIDENT_RESOURCE_PATH,
            resource_loaded=True,
            hero_sprite_available=True,
            resident_sprite_available=True,
        )
        app.crew_count_by_type[PLANET_TYPE_WIND] = 1
        app._trigger_crew_type_celebration(PLANET_TYPE_WIND)

        app._draw_crew_ui()

        blt_calls = [args for name, args, _kwargs in pyxel.calls if name == "blt"]
        wind_calls = [args for args in blt_calls if args[0] == 134 and args[3:7] == (0, 32, 32, 32)]
        self.assertEqual(len(wind_calls), 1)
        self.assertLess(wind_calls[0][1], HEIGHT - 140)

    def test_cutin_resident_sprite_is_centered_inside_compact_card(self) -> None:
        app = GravityCourierApp()
        pyxel = RecordingPyxel()
        app.pyxel = pyxel
        app.resident_resources = ResidentResourceState(
            path=RESIDENT_RESOURCE_PATH,
            resource_loaded=True,
            hero_sprite_available=True,
            resident_sprite_available=True,
        )
        app.cutin.start(PLANET_TYPE_WIND, lap_count=1, score_gain=100, side=CUTIN_SIDE_LEFT, target_y=100)
        app.cutin.timer -= 20

        app._draw_cutin_panel()

        blt_calls = [args for name, args, _kwargs in pyxel.calls if name == "blt"]
        self.assertEqual(blt_calls[0][:7], (44, 142, 0, 0, 32, 32, 32))
        self.assertEqual(blt_calls[0][7], SPRITE_TRANSPARENT_COLKEY)
        self.assertEqual(CUTIN_RESIDENT_SCALE, 3)
        self.assertEqual(CUTIN_RESIDENT_DRAW_SIZE, 96)
        self.assertEqual(CUTIN_PANEL_HEIGHT, 120)


if __name__ == "__main__":
    unittest.main()
