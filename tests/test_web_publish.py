"""Tests for Gravity Courier web publishing helpers."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "patch_web_html.py"
SPEC = importlib.util.spec_from_file_location("patch_web_html", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
patch_web_html = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(patch_web_html)


class WebPublishTests(unittest.TestCase):
    def test_patch_adds_mobile_safari_viewport_fit(self) -> None:
        html = (
            "<!doctype html>\n"
            '<script src="https://cdn.jsdelivr.net/gh/kitao/pyxel@2.4.10/wasm/pyxel.js"></script>\n'
            "<script>\n"
            'launchPyxel({ command: "play", name: "gravity-courier-webapp-src.pyxapp", '
            'gamepad: "enabled", base64: "abc" });\n'
            "</script>\n"
        )

        patched = patch_web_html.patch_pyxel_html(html)

        self.assertIn('name: "gravity-courier-public.pyxapp"', patched)
        self.assertIn('gamepad: "disabled"', patched)
        self.assertIn("viewport-fit=cover", patched)
        self.assertIn("window.visualViewport", patched)
        self.assertIn("const GAME_WIDTH = 393;", patched)
        self.assertIn("const GAME_HEIGHT = 852;", patched)
        self.assertIn("fitCanvasToVisibleViewport", patched)

    def test_patch_is_idempotent(self) -> None:
        html = (
            "<!doctype html>\n"
            "<script>\n"
            'launchPyxel({ command: "play", name: "old.pyxapp", gamepad: "enabled", base64: "abc" });\n'
            "</script>\n"
        )

        patched_once = patch_web_html.patch_pyxel_html(html)
        patched_twice = patch_web_html.patch_pyxel_html(patched_once)

        self.assertEqual(patched_once, patched_twice)
        self.assertEqual(patched_twice.count(patch_web_html.PATCH_MARKER), 1)


if __name__ == "__main__":
    unittest.main()
