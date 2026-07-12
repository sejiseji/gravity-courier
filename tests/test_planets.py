import unittest

import _path  # noqa: F401

from gravity_courier.app import GravityCourierApp, PLANET_RENDERERS, STATE_PLAYING, STATE_TITLE, create_initial_planets
from gravity_courier.constants import COLOR_BACKGROUND, COLOR_STAR, COLOR_STAR_DIM, PLANET_COUNT
from gravity_courier.planet_types import (
    PLANET_TYPE_BLACK_HOLE,
    PLANET_TYPE_FOREST,
    PLANET_TYPE_IRON,
    PLANET_TYPE_ROCK,
    PLANET_TYPE_WATER,
    PLANET_TYPE_WIND,
)


class RecordingPyxel:
    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple[int, ...]]] = []

    def circ(self, *args: int) -> None:
        self.calls.append(("circ", args))

    def circb(self, *args: int) -> None:
        self.calls.append(("circb", args))

    def line(self, *args: int) -> None:
        self.calls.append(("line", args))

    def rect(self, *args: int) -> None:
        self.calls.append(("rect", args))

    def tri(self, *args: int) -> None:
        self.calls.append(("tri", args))

    def pset(self, *args: int) -> None:
        self.calls.append(("pset", args))


class PlanetLayoutTest(unittest.TestCase):
    def test_initial_planets_use_normal_course_count(self) -> None:
        planets = create_initial_planets()

        self.assertEqual(len(planets), PLANET_COUNT)
        self.assertEqual(PLANET_COUNT, 20)

    def test_planets_progress_upward_in_sequence(self) -> None:
        planets = create_initial_planets()

        self.assertLess(planets[-1].position.y, planets[0].position.y)

    def test_rich_planet_surface_draws_type_specific_marks(self) -> None:
        planet_types = (
            PLANET_TYPE_WIND,
            PLANET_TYPE_WATER,
            PLANET_TYPE_ROCK,
            PLANET_TYPE_FOREST,
            PLANET_TYPE_IRON,
            PLANET_TYPE_BLACK_HOLE,
        )

        signatures: set[tuple[str, ...]] = set()
        for index, planet_type in enumerate(planet_types):
            app = GravityCourierApp()
            pyxel = RecordingPyxel()
            app.pyxel = pyxel

            app._draw_planet_surface(50, 50, 20, planet_type, index)

            self.assertGreaterEqual(len(pyxel.calls), 2)
            signatures.add(tuple(call[0] for call in pyxel.calls))

        self.assertGreaterEqual(len(signatures), 4)

    def test_planet_renderer_dispatch_covers_core_types(self) -> None:
        self.assertEqual(
            set(PLANET_RENDERERS),
            {
                PLANET_TYPE_WIND,
                PLANET_TYPE_WATER,
                PLANET_TYPE_ROCK,
                PLANET_TYPE_FOREST,
                PLANET_TYPE_IRON,
                PLANET_TYPE_BLACK_HOLE,
            },
        )

    def test_planet_visual_layers_draw_base_surface_atmosphere_and_particles(self) -> None:
        app = GravityCourierApp()
        pyxel = RecordingPyxel()
        app.pyxel = pyxel

        app._draw_planet_base(50, 50, 20, 6)
        app._draw_planet_surface(50, 50, 20, PLANET_TYPE_WIND, 0)
        app._draw_planet_atmosphere(50, 50, 20, PLANET_TYPE_WIND, 0)
        app._draw_planet_particles(50, 50, 20, PLANET_TYPE_WIND, 0)

        call_names = [name for name, _args in pyxel.calls]
        self.assertIn("circ", call_names)
        self.assertIn("circb", call_names)
        self.assertIn("line", call_names)
        self.assertIn("pset", call_names)

    def test_type_specific_visuals_are_distinct_by_operation_mix(self) -> None:
        operation_mix: dict[str, tuple[str, ...]] = {}
        for index, planet_type in enumerate(
            (
                PLANET_TYPE_WIND,
                PLANET_TYPE_WATER,
                PLANET_TYPE_ROCK,
                PLANET_TYPE_FOREST,
                PLANET_TYPE_IRON,
            )
        ):
            app = GravityCourierApp()
            pyxel = RecordingPyxel()
            app.pyxel = pyxel

            app._draw_planet_surface(50, 50, 20, planet_type, index)
            app._draw_planet_atmosphere(50, 50, 20, planet_type, index)

            operation_mix[planet_type] = tuple(name for name, _args in pyxel.calls)

        self.assertGreaterEqual(len(set(operation_mix.values())), 5)

    def test_title_starfield_twinkles_over_time(self) -> None:
        app = GravityCourierApp()
        app.game_state = STATE_TITLE
        app.frame = 0
        first_colors = [app._starfield_color(index) for index in range(128)]
        app.frame = 96
        later_colors = [app._starfield_color(index) for index in range(128)]
        changed_count = sum(1 for first, later in zip(first_colors, later_colors) if first != later)

        self.assertNotEqual(first_colors, later_colors)
        self.assertLess(changed_count, 48)
        self.assertIn(COLOR_STAR, first_colors + later_colors)
        self.assertIn(COLOR_STAR_DIM, first_colors + later_colors)
        self.assertIn(COLOR_BACKGROUND, first_colors + later_colors)

    def test_gameplay_starfield_keeps_stable_brightness(self) -> None:
        app = GravityCourierApp()
        app.game_state = STATE_PLAYING
        app.frame = 0
        first_colors = [app._starfield_color(index) for index in range(32)]
        app.frame = 96
        later_colors = [app._starfield_color(index) for index in range(32)]

        self.assertEqual(first_colors, later_colors)
