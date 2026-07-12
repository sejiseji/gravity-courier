# Runbook

## Run The Prototype

```bash
python3 prototypes/gravity_courier/main.py
```

Pyxel must be installed for this command to open the `393x852` game window.

For Homebrew-managed Python environments that block system installs, run through the local project virtual environment:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install pyxel
.venv/bin/python prototypes/gravity_courier/main.py
```

## Controls

Current desktop prototype controls:

- Title START / Z / Enter: start selected mode
- Title MODE / Left / Right: switch Normal/Hard mode
- Title DEMO / M: start demo run
- Title SOUND / S: toggle sound
- Left / Right: steer left/right relative to the current travel direction
- Up: boost along the current travel direction and consume fuel
- Down: brake by damping velocity
- Space: desktop preview flag toggle, though gameplay preview is currently always visible
- M or top-right `DEMO` button: toggle demo mode
- R: restart
- D: toggle debug HUD
- S: toggle sound
- Escape: quit

Mobile/touch controls use horizontal drag for continuous steering, upward swipes for gentle thrust pulses, and downward swipes for gentle brake pulses. Tap remains reserved for future actions.

## Validation

```bash
python3 -m compileall prototypes/gravity_courier
python3 prototypes/gravity_courier/scripts/check_all.py
python3 -m unittest discover prototypes/gravity_courier/tests
git diff --check
```

`scripts/check_all.py` uses `pytest` if it is installed. Otherwise it runs:

```bash
python3 -m unittest discover prototypes/gravity_courier/tests
```

Docs-only planning tasks such as GRC009P do not require manual Pyxel launch, but they should still run the validation commands above and `git diff --check`.

## Web Publish HTML Patch

`index.html` at the Gravity Courier project root is the local source of truth for the published GitHub Pages wrapper. Keep it in sync with the public `sejiseji/gravity-courier` repository instead of treating the generated public-worktree file as an untracked one-off artifact.

Pyxel `app2html` creates a minimal web wrapper. Before publishing the generated HTML, run the Gravity Courier patch step so the page uses the visible Safari viewport instead of the taller layout viewport:

```bash
python3 prototypes/gravity_courier/scripts/patch_web_html.py generated.html prototypes/gravity_courier/index.html
```

The patch also renames the embedded app to `gravity-courier-public.pyxapp` and disables the web gamepad overlay. When deploying, copy this local `index.html` to the public repository root together with the current source files.

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
- Title screen appears before gameplay.
- Title screen plays layered title BGM with low accompaniment and high music-box harmony when sound is on.
- START begins Normal by default.
- MODE or Left/Right switches Normal/Hard before START.
- DEMO starts the same demo autopilot from the title screen.
- SOUND toggles layered title audio without starting gameplay BGM while still on the title screen.
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
