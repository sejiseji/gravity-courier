import unittest

import _path  # noqa: F401

from gravity_courier.app import GravityCourierApp, create_initial_planets
from gravity_courier.constants import PLANET_COUNT
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
