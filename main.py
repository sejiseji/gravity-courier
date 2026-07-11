"""Launcher for the Gravity Courier scaffold."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from gravity_courier.app import GravityCourierApp


def main() -> int:
    app = GravityCourierApp()
    try:
        app.run()
    except RuntimeError as exc:
        print(f"{exc} Install Pyxel to play: python3 -m pip install pyxel")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
