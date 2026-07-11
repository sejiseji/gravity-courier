# Runbook

## Run The Prototype

```bash
python3 main.py
```

Pyxel must be installed for this command to open the `393x852` game window.

For Homebrew-managed Python environments that block system installs, run through the local project virtual environment:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install pyxel
.venv/bin/python main.py
```

## Controls

Current desktop prototype controls:

- Left / Right: steer left/right relative to the current travel direction
- Up: boost along the current travel direction and consume fuel
- Down: brake by damping velocity
- Space: toggle trajectory preview
- M or top-right `DEMO` button: toggle demo mode
- R: restart
- D: toggle debug HUD
- Escape: quit

Planned mobile controls are documented in `docs/product/MOBILE_CONTROL_SPEC.md`. Mobile gameplay should keep trajectory preview always visible, use horizontal drag for continuous rotation, use upward/downward swipes for gentle thrust/brake pulses, and leave tap reserved for future actions.

## Validation

```bash
python3 -m compileall main.py src tests scripts
python3 scripts/check_all.py
python3 -m unittest discover tests
git diff --check
```

`scripts/check_all.py` uses `pytest` if it is installed. Otherwise it runs:

```bash
python3 -m unittest discover tests
```

Docs-only planning tasks such as GRC009P do not require manual Pyxel launch, but they should still run the validation commands above and `git diff --check`.

## Planning Specs

Post-GRC009 planning specs live under `docs/product/`:

- `GAME_MODE_SPEC.md`
- `OFF_COURSE_HELPER_SPEC.md`
- `ORBIT_FOCUS_PRESENTATION_SPEC.md`
- `SPRITE_ASSET_PLAN.md`
- `PLANET_VISUAL_SPEC.md`
- `RESULT_TEST_HELPER_SPEC.md`
- `TITLE_SCREEN_SPEC.md`
- `POST_GRC009_ROADMAP.md`

## Manual QA Checklist

- Window opens at `393x852`.
- Rocket appears below screen center.
- Left / Right relative steering bends the current travel direction.
- Up boost follows the current travel direction and shows flame.
- Down brake visibly reduces speed.
- M demo mode steers through the planet course and shows a `DEMO` label.
- The top-right `DEMO` button toggles demo mode with mouse/touch input.
- Planets bend the path.
- Space toggles trajectory dots.
- Journey Progress appears without covering the DEMO button or core HUD.
- The Earth-like final goal is visible near the end of the course.
- Reaching the final goal opens the result screen.
- Result screen shows final score, crew count, rank, and crew celebration.
- Collision shows crash.
- R restarts.
- A close pass can show `GRAVITY ASSIST!`.
