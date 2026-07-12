"""Run lightweight validation for Gravity Courier."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]


def run(command: list[str]) -> int:
    print("+ " + " ".join(command))
    return subprocess.call(command, cwd=REPO)


def main() -> int:
    has_pytest = (
        subprocess.call(
            ["python3", "-m", "pytest", "--version"],
            cwd=REPO,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        == 0
    )
    test_command = ["python3", "-m", "pytest", "prototypes/gravity_courier/tests"]
    if not has_pytest:
        test_command = [
            "python3",
            "-m",
            "unittest",
            "discover",
            "prototypes/gravity_courier/tests",
        ]

    commands = [
        ["python3", "-m", "compileall", "prototypes/gravity_courier"],
        test_command,
        ["git", "diff", "--check"],
    ]
    for command in commands:
        result = run(command)
        if result:
            return result
    return 0


if __name__ == "__main__":
    sys.exit(main())
