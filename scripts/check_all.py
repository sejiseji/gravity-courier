"""Run lightweight validation for Gravity Courier."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str]) -> int:
    print("+ " + " ".join(command))
    return subprocess.call(command, cwd=ROOT)


def main() -> int:
    has_pytest = (
        subprocess.call(
            ["python3", "-m", "pytest", "--version"],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        == 0
    )
    test_command = ["python3", "-m", "pytest", "tests"]
    if not has_pytest:
        test_command = [
            "python3",
            "-m",
            "unittest",
            "discover",
            "tests",
        ]

    commands = [
        ["python3", "-m", "compileall", "main.py", "src", "tests", "scripts"],
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
