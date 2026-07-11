# Gravity Courier

Gravity Courier is a portrait Pyxel prototype for a 2D gravity-assist rocket game. The player moves a small rocket left and right while boosting upward past moving planets, using readable swing-bys and speed changes to travel farther without relying only on fuel.

## Status

Playable prototype with orbit focus presentation, Journey Progress, Normal/Hard courses, final goal, result screen, and result test helper.

The prototype now has velocity-relative steering, forward boost, orbit assist around planets, restrained orbit focus zoom with concentration lines, Normal/Hard finite courses, dotted trajectory preview, HP/shield collision damage, restart, larger HUD text, demo mode with a top-right toggle button, formal score, per-planet lap count, on-planet lap labels, HUD score, lap multipliers, simple 3-stage cheer text, planet types, 2-lap planet rewards, a shared resident cut-in panel, deterministic interplanet objects, delayed supply ships, supply cargo, planet-type crew growth, course gaps, crossing meteor swarms, Journey Progress, an Earth-like final goal, a result state, final score, rank, density-based crew celebration, a developer-only result test helper, documented mobile controls, and documented post-GRC009 polish roadmap.

GRC005A separates lap completion from Transfer Boost. Laps now complete from signed angular orbit progress while the rocket remains inside a planet gravity well. Each completed lap awards score, updates the planet lap label, triggers cheer/cut-in feedback, and can trigger the lap 2 planet reward. Transfer Boost is now an exit event: after at least one completed lap in the current visit, `TRANSFER READY` appears; leaving the gravity well triggers `TRANSFER BOOST!` once for that visit.

GRC006 adds floating asteroids, crossing rockets with warning timing, and normal supply items. Normal supply items add score and fuel only; they do not add crew. GRC007 adds lap 3 supply ship reservations, supply cargo that adds score/fuel/crew, missed-cargo rules, and a compact in-run crew UI. GRC008 replaces the fixed type sequence with seeded shuffle-bag course generation, creates course gap metadata, marks future supply gaps, and adds warning-based crossing meteor swarms. GRC009 adds Journey Progress, an Earth-like final goal outside normal planet logic, result scoring, a separate result state, and crew celebration rendering. GRC009F adds Normal/Hard course modes. GRC009A adds a DEBUG/DEMO-only `GOAL TEST` helper for result-density testing. GRC009B adds restrained orbit focus presentation without changing orbit physics. Title screen, procedural endless generation, sound, and iOS wrapper work remain out of scope.

## Fixed Screen Profile

- Profile: `iphone16_large`
- Resolution: `393x852`
- Orientation: portrait

All gameplay layout, camera behavior, HUD, trajectory preview, and planet placement are tuned for this portrait profile. Do not use intermediate prototype resolutions such as `160x240`, `236x512`, or `256x144`.

## Run

```bash
python3 main.py
```

If the system Python blocks package installs with PEP 668, use the project virtual environment:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install pyxel
.venv/bin/python main.py
```

Pyxel is required for the playable window.

## Controls

Current desktop prototype controls:

- Left / Right: steer left/right relative to the current travel direction
- Up: boost along the current travel direction and consume fuel
- Down: brake by damping velocity
- Space: toggle dotted trajectory preview
- M or top-right `DEMO` button: toggle demo mode
- R: restart
- D: toggle debug HUD
- Escape: quit

Planned mobile controls are documented in `docs/product/MOBILE_CONTROL_SPEC.md`. The mobile direction is horizontal drag for high-sensitivity rotation, upward swipe for gentle forward thrust, downward swipe for gentle braking, and always-on trajectory preview with no gameplay preview toggle.

## Validate

```bash
python3 -m compileall main.py src tests scripts
python3 scripts/check_all.py
python3 -m unittest discover tests
git diff --check
```

`scripts/check_all.py` uses `pytest` when available and falls back to `unittest` otherwise.

## Current Limitations

- No touch controls yet.
- No procedural endless universe yet; the current course is finite and seeded.
- No sound, BGM, or iOS wrapper.
- No title-screen mode selection yet; `N` toggles Normal/Hard during the prototype.
- No title screen yet.
- Trajectory preview treats planet positions as static for readability.
- Physics favors readable arcade swing-bys over strict orbital realism.
- Orbit assist is intentionally game-like: it helps the rocket circle planets instead of instantly leaving every gravity well.
- Transfer Boost is separate from lap scoring. It becomes ready after at least one completed lap in the current planet visit, then triggers once when the rocket exits that planet's gravity well.
- Course generation is deterministic and finite: Normal has 20 planets and Hard has 35 planets.
- Supply ship delay still counts Transfer Boost exits, but ready reservations now queue in SUPPLY ZONE lanes by planet type until collected.

## Tuning Constants

Core tuning lives in `src/gravity_courier/constants.py`:

- `GRAVITY_G`
- `GRAVITY_SOFTENING`
- `SUB_STEPS`
- `ROCKET_STRAFE_POWER`
- `ROCKET_MAX_HORIZONTAL_SPEED`
- `ROCKET_LATERAL_DAMPING`
- `ROCKET_THRUST_POWER`
- `ROCKET_BRAKE_DAMPING`
- `ROCKET_MAX_HP`
- `ROCKET_MAX_SHIELD`
- `ROCKET_DAMAGE_COOLDOWN_FRAMES`
- orbit assist constants: `ORBIT_ASSIST_STRENGTH`, `ORBIT_TARGET_RADIUS_RATIO`, `ORBIT_TARGET_SPEED`, `ORBIT_SPEED_BONUS_BASE`, `ORBIT_SPEED_BONUS_PER_TURN`, `ORBIT_SPEED_BONUS_MAX_SPEED`
- lap tracking constant: `LAP_COMPLETION_RADIANS`
- Transfer Boost constants: `ASSIST_EXIT_BOOST`, `ASSIST_EXIT_RADIAL_WEIGHT`, `ASSIST_ORBIT_COOLDOWN_FRAMES`
- destination-line helper constants: `ASSIST_TRANSFER_ALIGNMENT_DEGREES`, `ASSIST_MIN_UPWARD_DESTINATION_GAP`
- reward constants: `WIND_REWARD_GRAVITY_MULTIPLIER`, `IRON_REWARD_SHIELD_GAIN`, `WATER_REWARD_SCORE_MULTIPLIER`, `WATER_REWARD_SCORE_USES`, `FOREST_REWARD_FUEL_RATIO`, `ROCK_REWARD_HP_GAIN`
- interplanet object constants: `ASTEROID_RADIUS`, `ASTEROID_DAMAGE`, `ASTEROID_DRIFT_SPEED`, `CROSSING_ROCKET_RADIUS`, `CROSSING_ROCKET_SPEED`, `CROSSING_ROCKET_DAMAGE`, `CROSSING_ROCKET_WARNING_FRAMES`, `SUPPLY_ITEM_RADIUS`, `SUPPLY_ITEM_SCORE`, `SUPPLY_ITEM_FUEL_RATIO`
- course constants: `COURSE_SEED`, `MAX_PLANET_APPEARANCES_PER_TYPE`, `COURSE_START_Y`, `PLANET_BASE_SPACING_Y`, `PLANET_SPACING_Y_GROWTH`, `PLANET_X_MIN`, `PLANET_X_MAX`
- meteor swarm constants: `METEOR_SWARM_METEOR_COUNT`, `METEOR_SWARM_RADIUS`, `METEOR_SWARM_SPEED`, `METEOR_SWARM_DAMAGE`, `METEOR_SWARM_WARNING_FRAMES`, `METEOR_SWARM_GAP_START_INDEX`, `METEOR_SWARM_EVERY_N_GAPS`
- supply ship/crew constants: `SUPPLY_LAP_INTERVAL`, `SUPPLY_SHIP_DELAY_GAPS_MIN`, `SUPPLY_SHIP_DELAY_GAPS_MAX`, `CREW_JOIN_SEQUENCE`, `MAX_SUPPLY_TIERS_PER_TYPE`, `MAX_SUPPLY_SHIP_CHANCES_PER_TYPE`, `SUPPLY_SHIP_CARGO_SCORE`, `SUPPLY_SHIP_CARGO_FUEL_RATIO`, `SUPPLY_SHIP_SPEED`, `SUPPLY_SHIP_RADIUS`, `SUPPLY_CARGO_RADIUS`, `SUPPLY_SHIP_WARNING_FRAMES`
- final goal/result constants: `FINAL_GOAL_RADIUS`, `FINAL_GOAL_ARRIVAL_RADIUS`, `FINAL_GOAL_SPACING_Y`, `CREW_SCORE_VALUE`, `RESULT_RANK_THRESHOLDS`
- cut-in/resource constants: `ASSETS_DIR`, `RESIDENT_RESOURCE_PATH`, `RESIDENT_SPRITE_SIZE`, `CUTIN_RESIDENT_SCALE`, `CUTIN_RESIDENT_DRAW_SIZE`, `CUTIN_PANEL_WIDTH`, `CUTIN_PANEL_HEIGHT`, `CUTIN_SLIDE_IN_FRAMES`, `CUTIN_SLIDE_OUT_FRAMES`, `CREW_RESIDENT_SCALE`, `CREW_HIGHLIGHT_SCALE`, `CUTIN_DURATION_FRAMES`
- `ROCKET_FUEL_COST`
- `TRAJECTORY_STEPS`
- `TRAJECTORY_DOT_INTERVAL`
- `PLANET_COUNT`
- `PLANET_VERTICAL_SPACING`
- demo steering constants: `DEMO_TARGET_UPWARD_SPEED`, `DEMO_MAX_SPEED`, `DEMO_STEER_GAIN`
- `ASSIST_SPEED_GAIN_THRESHOLD`
- `ASSIST_FUEL_REWARD`

## Known Next Improvements

- GRC009C: add off-course recovery helper.
- GRC009D: enrich procedural planet visuals.
- GRC009E: integrate developer-authored resident and rocket sprite assets when ready.
- GRC010: prepare mobile/touch readiness.
- GRC010A: add title screen and mode selection.
- GRC011: polish toward a release candidate prototype.

## Planned Gameplay Roadmap

Gravity Courier should evolve from a simple "go farther with swing-bys" prototype into a score-driven gravity-assist arcade game.

The planned core loop is:

1. Enter a planet gravity well.
2. Complete a signed angular lap around that planet while still inside the gravity well.
3. Increase the local lap count for that planet.
4. Add score and cheer/cut-in feedback.
5. Trigger the planet reward once at lap 2.
6. After at least one lap, leave the gravity well to trigger Transfer Boost.

Current score implementation:

- `base_assist_score = 100`
- lap 1: x1.0
- lap 2: x1.5
- lap 3: x2.0
- lap 4+: `x2.0 + 0.25 * (lap - 3)`
- planet lap labels display as `1`, `2`, or `3+`.
- stage 3+ reuses the maximum cheer presentation while exact lap count continues scaling score.
- Water bonus uses the existing rounded score helper: lap 2 x1.25 becomes 188.

Current planet rewards activate once per planet per run at lap 2:

- Wind: sets that planet's `gravity_multiplier` to `1.25`.
- Iron: adds `SHIELD +1`, clamped to max shield.
- Water: grants 3 future assist score bonus uses at x1.25.
- Forest: restores fuel by 25% of max fuel, clamped.
- Rock: restores 1 HP, clamped.

Current cut-in implementation:

- Completed laps start a shared resident cut-in panel.
- Resident registry maps planet types to original resident IDs and names.
- Resident sprites are planned as `32x32` Pyxel Editor cells.
- Reserved resource path: `assets/gravity_courier.pyxres`
- Hero sprite is available at image bank 0, `(u=0, v=0)`, `32x32`, using palette color `14` as transparent.
- Five resident idle sprites are available below Hero at `v=32..160`, also using palette color `14` as transparent.
- Loading the `.pyxres` enables Hero plus the five resident idle sprites; resident cheer stages reuse idle until dedicated expressions are authored.
- If the `.pyxres` file is missing or cannot load, primitive fallback portraits and Hero markers are used.
- Cut-in stage 3 is reused for lap 3+.
- Cut-ins slide in near the middle of the screen from the side opposite the assisting planet, preserving lower screen space for future crew UI.

Current interplanet object implementation:

- Floating asteroids damage the rocket with the same shield/HP rules as planet collisions.
- Crossing rockets show a warning before moving across the play area and damage through shield/HP.
- Normal supply items add `+75` score and restore 15% max fuel.
- Normal supply items disappear after collection and do not add crew.
- Restart resets object placement, collection state, warnings, and interplanet feedback.

Current supply ship and crew implementation:

- Lap 3, 6, 9, and later multiples of 3 can reserve a supply ship for that planet type.
- Supply ships do not appear immediately. They use a deterministic 2-3 Transfer Boost delay approximation before becoming ready.
- Ready supply ships wait in the current/next SUPPLY ZONE, arranged horizontally by planet type, and remain available until collected.
- Supply ship cargo adds `+100` score, restores 15% max fuel, and adds crew of the source planet type.
- Crew join counts use `[1, 2, 4, 8, 16, 32, 64]` per planet type.
- The waiting SUPPLY ZONE queue prevents ordinary misses from consuming crew opportunities.
- Normal supply items still do not add crew.
- The in-run crew UI shows joined crew total, a protagonist marker, joined type representatives, and compact type counts.
- Restart resets reservations, active ships, crew counts, success tiers, chance counts, and supply feedback.

Current finite course and meteor swarm implementation:

- `course.py` generates a seeded 35-planet course using five normal planet types.
- Wind, Iron, Water, Forest, and Rock each appear exactly 7 times.
- The shuffle-bag order prevents 3 identical planet types in a row and ensures the first 5 planets include Forest or Rock.
- Course gaps reference adjacent planet IDs and expose center positions, width hints, supply-zone flags, and meteor swarm flags.
- Supply ship reservations can mark future course gaps as supply zones, and ready ships are synchronized into the current/next visible supply zone.
- Difficulty helpers provide deterministic start-to-end scaling from 1.0 to 1.75.
- `meteor_swarm.py` adds crossing meteor swarms for selected gaps with warnings before damage.
- Restart regenerates the same seeded course, gaps, interplanet objects, meteor swarms, supply, crew, and scoring state.

Current final goal and result implementation:

- `goal.py` creates an Earth-like final goal after the generated planet course.
- The final goal is not included in normal planet gravity, lap, reward, or supply-ship logic.
- Journey Progress shows `GOAL`, a compact bar, and `P current/35`.
- Supply gap data can add a small `NEXT SUPPLY` hint.
- Reaching the final goal enters a separate result state.
- `result.py` calculates crew bonus, final score, rank, and crew display density.
- Result screen shows final score, run score, crew bonus, crew count, laps, supply cargo count, HP, fuel, rank, and a staggered crew celebration.

Journey Progress behavior:

- Show finite route progress during gameplay.
- Display compact `PLANET current/35` text and a small progress bar toward `GOAL`.
- Optionally show a small `NEXT SUPPLY` or `SUPPLY NEXT GAP` hint when supply gap data is available.
- Keep this compact; it is not a full minimap or route-management UI.

Planned mobile control direction:

- Touch input should become a shared `ControlIntent` path used alongside keyboard controls.
- Horizontal drag should control high-sensitivity continuous rotation with clamped angular response.
- High-speed turn assist should keep orbit entry practical as velocity rises.
- Up and down swipes should create short gentle thrust/brake pulses, not large instant speed impulses.
- Trajectory preview should be always visible during mobile gameplay, with no touch gameplay toggle.
- Tap remains reserved for future pause, cut-in advance, or special action.

Post-GRC009 roadmap direction:

- Normal mode is the standard route: 20 planets, 4 appearances per normal planet type.
- Hard mode preserves the long route: 35 planets, 7 appearances per normal planet type.
- Off-course guidance should point toward the next expected course planet, not just the nearest planet.
- Orbit focus presentation uses restrained zoom, deterministic concentration lines, and smooth release on Transfer Boost.
- Planet visuals should become richer through procedural type-specific rendering, without requiring image assets.
- Resident/Hero sprites use a `32x32` atlas with Hero on row 0 and resident rows starting at `v=32`.
- Rocket visuals should later use a 3-state `32x32` sprite plan: idle, thrust, damage.
- The developer-only `GOAL TEST` helper speeds up result-screen crew-density verification.
- A title screen should eventually provide START, Normal/Hard selection, DEMO, and concise mobile control guidance.

Roadmap/spec docs:

- `docs/product/GAMEPLAY_ROADMAP.md`
- `docs/product/SCORE_AND_LAP_SPEC.md`
- `docs/product/PLANET_TYPES_AND_REWARDS.md`
- `docs/product/CHEER_CUTIN_AND_CREW_SPEC.md`
- `docs/product/INTERPLANET_OBJECTS_SPEC.md`
- `docs/product/SUPPLY_CREW_GOAL_RESULT_SPEC.md`
- `docs/product/MOBILE_CONTROL_SPEC.md`
- `docs/product/GAME_MODE_SPEC.md`
- `docs/product/OFF_COURSE_HELPER_SPEC.md`
- `docs/product/ORBIT_FOCUS_PRESENTATION_SPEC.md`
- `docs/product/SPRITE_ASSET_PLAN.md`
- `docs/product/PLANET_VISUAL_SPEC.md`
- `docs/product/RESULT_TEST_HELPER_SPEC.md`
- `docs/product/TITLE_SCREEN_SPEC.md`
- `docs/product/POST_GRC009_ROADMAP.md`
