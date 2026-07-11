import unittest

import _path  # noqa: F401

from gravity_courier.constants import CUTIN_PANEL_HEIGHT, HEIGHT, PROFILE_NAME, WIDTH


class ConstantsTest(unittest.TestCase):
    def test_fixed_iphone16_large_profile(self) -> None:
        self.assertEqual(PROFILE_NAME, "iphone16_large")
        self.assertEqual(WIDTH, 393)
        self.assertEqual(HEIGHT, 852)

    def test_cutin_panel_height_stays_compact(self) -> None:
        self.assertEqual(CUTIN_PANEL_HEIGHT, 120)
