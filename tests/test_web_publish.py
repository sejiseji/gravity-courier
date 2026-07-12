"""Tests for Gravity Courier web publishing helpers."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "patch_web_html.py"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
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
        self.assertIn("gc-start-overlay", patched)
        self.assertIn("TAP TO START", patched)
        self.assertIn("resolveInput", patched)
        self.assertIn("document.documentElement.appendChild(startOverlay)", patched)
        self.assertIn('document.addEventListener("pointerdown", tryStart, true)', patched)

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

    def test_local_index_html_is_publishable_source_of_truth(self) -> None:
        html = (PROJECT_ROOT / "index.html").read_text(encoding="utf-8")

        self.assertIn(patch_web_html.PATCH_MARKER, html)
        self.assertIn("window.visualViewport", html)
        self.assertIn('name: "gravity-courier-public.pyxapp"', html)
        self.assertIn('gamepad: "disabled"', html)
        self.assertIn("gc-start-overlay", html)
        self.assertIn("TAP TO START", html)
        self.assertIn("resolveInput", html)
        self.assertIn("document.documentElement.appendChild(startOverlay)", html)
        self.assertIn('document.addEventListener("pointerdown", tryStart, true)', html)
        forbidden_fragments = (
            "/Users/",
            "toytoytoy330",
            "Desktop/AllMyFiles",
            "/private/",
            "TemporaryItems",
            "NSIRD",
            ".codex",
        )
        for fragment in forbidden_fragments:
            with self.subTest(fragment=fragment):
                self.assertNotIn(fragment, html)


if __name__ == "__main__":
    unittest.main()
