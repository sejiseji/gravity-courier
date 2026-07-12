# Done Log

## GRC000

- Created isolated Gravity Courier scaffold.
- Added product, architecture, and development docs.
- Added goal tracking files and GPT handoff.
- Added importable source skeleton and lightweight tests.
- Documented `GRC001` as the next recommended task.

## GRC001

- Implemented the first playable Gravity Courier prototype.
- Added desktop controls, rocket boost, planet gravity, camera follow, trajectory preview, HUD, crash state, restart, and debug HUD.
- Increased the planet course from 3 starter planets to 30 sequential planets for better operation-feel testing.
- Added demo mode for an autopilot showcase route through the planets.
- Added orbit assist and demo orbit dwell so the prototype better matches the intended "circle planets, then transfer" fantasy.
- Added swing-by exit boost and a short same-planet orbit-assist cooldown to reduce recapture after a successful assist.
- Gated swing-by exit boost/cooldown behind a forward-destination check so successful assists do not suddenly reverse toward a planet behind the rocket.
- Tightened transfer boost gating to require the next planet to be both ahead and above the rocket, and added a visible `TRANSFER BOOST!` destination line.
- Added gravity assist state tracking and tests.
- Updated README, runbook, tuning notes, handoff, and goal files.
- Pure validation passed; manual Pyxel launch was not performed because Pyxel is not installed in this environment.

## GRC002

- Added gameplay roadmap and system specs for score/lap, planet rewards, cheer/cut-in/crew, and interplanet objects.
- Documented the score-driven swing-by arcade direction.
- Documented lap count as the core scoring multiplier.
- Documented the provisional score formula and risk/reward loop.
- Documented the 2-lap planet reward activation rule.
- Documented planned Wind, Iron, Water, Forest, Rock, and Black Hole/Strong Gravity Object roles.
- Documented the 3-stage cheer plan and shared character registry direction for cut-ins and crew.
- Documented crossing rockets, floating asteroids, supply items, and supply ships as future interplanet objects.
- Updated README, GPT handoff, goal state, task queue, decision log, and done log.

## GRC002A

- Locked Forest Planet as propulsion gauge recovery.
- Locked Rock Planet as HP recovery.
- Clarified Iron Planet as defensive capacity, prevention, armor, and shield.
- Clarified Rock Planet as healing, repair, and recovery.
- Updated planet reward specs, roadmap wording, handoff, and decision log.

## GRC003

- Added formal score tracking separate from distance.
- Added per-planet lap counts for successful swing-by assists.
- Added provisional lap multiplier scoring.
- Added large on-planet lap labels using `1`, `2`, and `3+`.
- Added HUD `SCORE`.
- Added simple 3-stage ASCII cheer text feedback.
- Added pure scoring helper tests and app-level lap/score tests.
- Kept planet-type rewards, full cut-ins, crew, supply ships, and interplanet obstacles out of scope.

## GRC004

- Added planet type definitions for Wind, Iron, Water, Forest, Rock, and future Black Hole.
- Assigned Wind, Iron, Water, Forest, and Rock planets across the fixed initial course.
- Added per-planet reward claiming at lap 2.
- Added Wind gravity multiplier reward.
- Added Iron shield reward.
- Added Water future score bonus uses.
- Added Forest fuel recovery reward.
- Added Rock HP recovery reward.
- Added HP, shield, and damage cooldown fields to the rocket.
- Replaced instant planet collision crash with shield/HP damage, bounce, cooldown, and crash at 0 HP.
- Added HUD display for HP and shield.
- Added planet type labels and reward feedback text.
- Added debug HUD lines for reward count, last reward, water bonus uses, HP/shield, and active planet type/multiplier.
- Added tests for reward activation, reward effects, water scoring, wind gravity multiplier, and damage behavior.
- Kept supply ships, crew, interplanet obstacles, full cut-in portraits, procedural generation, external assets, and HTML changes out of scope.

## GRC005 Planning

- Updated cheer/cut-in/crew specs for `32x32` resident sprites authored in Pyxel Editor.
- Set cut-in portrait target display to 2x or 3x, with 3x (`96x96`) preferred first.
- Set future crew UI to reuse the same `32x32` sprite source at 1x or selected 2x states.
- Reserved `prototypes/gravity_courier/assets/gravity_courier.pyxres` as the Pyxel resource path.
- Required primitive fallback rendering when the `.pyxres` file is not available.
- Updated roadmap, GPT handoff, goal state, task queue, and decision log to reflect the resource-backed GRC005 direction.

## GRC005

- Added `residents.py` with resident registry entries for Wind, Iron, Water, Forest, Rock, and future Black Hole.
- Added `cutin.py` with pure cut-in payload/state handling.
- Added `resources.py` with fallback-safe optional `.pyxres` loading.
- Added `assets/README.md` documenting the reserved Pyxel resource path and `32x32` atlas layout.
- Connected successful assist events to the shared resident cut-in panel.
- Added primitive fallback portraits for Wind, Iron, Water, Forest, and Rock.
- Added tests for resident registry coverage, cut-in state, missing resource fallback, and app assist cut-in activation.
- Kept final art, full crew UI, supply ships, interplanet obstacles, procedural generation, external image assets, and HTML changes out of scope.

## GRC005A

- Added pure signed-angle orbit lap tracking helpers.
- Changed runtime scoring flow so completed orbit laps drive score, lap labels, cheers, resident cut-ins, and lap 2 rewards.
- Kept Transfer Boost separate from lap scoring and made it trigger once on gravity-well exit after at least one completed lap.
- Added `TRANSFER READY` feedback while still inside the gravity well after a lap.
- Moved cut-in panels from the lower screen to side slide-ins around the screen middle.
- Added visible backing behind planet lap labels.
- Expanded debug HUD with active orbit, lap progress, visit laps, total laps, transfer state, last lap event, last transfer event, and cut-in side.
- Added tests for angle wrapping, lap accumulation, jitter rejection, lap event scoring/reward flow, cut-in side selection, and Transfer Boost exit behavior.
- Kept GRC006 interplanet obstacles, supply ships, crew UI, procedural generation, external assets, and HTML changes out of scope.

## GRC005B

- Added `docs/product/SUPPLY_CREW_GOAL_RESULT_SPEC.md`.
- Documented supply ship reservation at lap 3 milestones and delayed spawning 2 or 3 planet gaps later.
- Documented supply cargo rewards, missed-cargo behavior, and crew success tier rules.
- Documented crew join sequence `[1, 2, 4, 8, 16, 32, 64]`.
- Documented max 7 normal planet appearances per type, max 127 joined crew per type, and max 635 joined crew across normal types.
- Documented representative in-run crew UI and dense result-screen crew/crowd rendering.
- Documented an Earth-like final goal, final score, crew bonus, rank, and staggered crew jump celebration.
- Documented crossing meteor swarms as a future hazard for GRC008 or later, not GRC006.
- Updated roadmap, handoff, task queue, goal state, and decision log to keep GRC006 focused.

## GRC006

- Added `interplanet_objects.py` with simple data structures for floating asteroids, crossing rockets, normal supply items, supply collection, and object updates.
- Added deterministic initial interplanet object placement for the current fixed course.
- Added floating asteroid obstacles using Pyxel primitive rendering.
- Added crossing rockets with warning timing and primitive directional rendering.
- Added normal supply items that grant score and fuel recovery, then disappear after collection.
- Reused shield/HP damage behavior for planet, asteroid, and crossing rocket damage.
- Added interplanet feedback text for supply pickup and obstacle damage.
- Added debug HUD lines for active object count, crossing warnings, last supply item, and last damage source.
- Added tests for object updates, warning timing, collision checks, supply reward behavior, one-time collection, and obstacle damage integration.
- Kept supply ships, crew growth, crew UI, final goal, result screen, shuffle-bag generation, crossing meteor swarms, external assets, and HTML changes out of scope.

## GRC007

- Added `supply.py` for supply ship reservation, delayed spawn, ship/cargo state, missed/collected status, and cargo rewards.
- Added `crew.py` for planet-type crew counts, crew success tiers, join sequence helpers, total count, and compact display helpers.
- Added lap 3 milestone supply ship reservations from the Lap Completed event flow.
- Added deterministic 2-3 Transfer Boost delay approximation for supply ship spawns.
- Added primitive supply ship warning, ship, and cargo rendering.
- Added supply cargo collection that grants score, fuel recovery, and planet-type crew.
- Added missed-cargo behavior where the event is consumed but the crew success tier does not advance.
- Added compact in-run crew UI showing joined total, HERO, representative joined types, and type counts.
- Added debug HUD lines for supply reservation/ship counts and last supply ship status.
- Added tests for reservation conditions, gap advancement, crew join sequence, missed cargo, cargo rewards, helper stability, and app reset behavior.
- Kept final goal, result screen, shuffle-bag course generation, crossing meteor swarms, external assets, and HTML changes out of scope.

## GRC008

- Added `course.py` with deterministic finite course generation.
- Generated a 35-planet route where Wind, Iron, Water, Forest, and Rock each appear exactly 7 times.
- Added shuffle-bag fairness constraints to prevent 3 same-type planets in a row and ensure early Forest/Rock availability.
- Added course gap metadata with center positions, width hints, supply-zone flags, and meteor-swarm flags.
- Connected app restart to regenerate the same seeded course, gaps, interplanet objects, and meteor swarms.
- Updated supply ship reservation to target and mark future course gaps when possible.
- Added simple supply-zone markers and gap-centered supply ship spawn placement.
- Added `meteor_swarm.py` with warning-based crossing meteor swarm hazards.
- Integrated meteor swarm update, rendering, and shield/HP collision damage into the app loop.
- Added deterministic difficulty helper functions.
- Added tests for course generation, placement, gap metadata, supply gap marking, difficulty helpers, meteor swarms, and supply gap reservation integration.
- Kept Earth-like final goal, result screen, final ranking, result crew crowd rendering, external assets, and HTML changes out of scope.

## GRC009 Planning Updates

- Documented Journey Progress as part of GRC009.
- Added the requirement for compact `PLANET current/35` progress toward `GOAL`.
- Added optional small `NEXT SUPPLY` or `SUPPLY NEXT GAP` hint planning.
- Added a right-top DEMO toggle button for easier playtest/demo entry.
- Clarified stage 3 cheer text as `WOOO! WHISTLE!`.
- Documented mobile control direction with always-on trajectory preview, horizontal drag steering, and gentle vertical thrust/brake swipes.

## GRC009

- Added `goal.py` with final goal creation, goal arrival, and Journey Progress helpers.
- Added `result.py` with crew bonus, final score, rank, crew-density, and result summary helpers.
- Added an Earth-like final goal after the finite planet course.
- Kept final goal separate from normal planet gravity, lap, reward, and supply-ship source logic.
- Added compact Journey Progress with `GOAL`, a progress bar, `P current/35`, and optional `NEXT SUPPLY` hint.
- Added `game_state` separation for playing, crashed/lost, and result.
- Added final goal arrival detection that transitions to result state.
- Added final score calculation using run score plus crew bonus.
- Added rank display using initial score thresholds.
- Added result screen summary rows for final score, run score, crew bonus, crew count, laps, supply cargo, HP, and fuel.
- Added density-based result crew rendering for normal, dense, and crowd crew counts.
- Added staggered crew celebration motion.
- Added tests for final goal creation/reach checks, Journey Progress monotonicity, final score/rank/density helpers, result transition, restart reset, and crash/result separation.

## GRC009P

- Added `docs/product/GAME_MODE_SPEC.md`.
- Added `docs/product/OFF_COURSE_HELPER_SPEC.md`.
- Added `docs/product/ORBIT_FOCUS_PRESENTATION_SPEC.md`.
- Added `docs/product/SPRITE_ASSET_PLAN.md`.
- Added `docs/product/PLANET_VISUAL_SPEC.md`.
- Added `docs/product/RESULT_TEST_HELPER_SPEC.md`.
- Added `docs/product/TITLE_SCREEN_SPEC.md`.
- Added `docs/product/POST_GRC009_ROADMAP.md`.
- Specified Normal mode as 20 planets, 4 appearances per normal planet type.
- Specified Hard mode as 35 planets, 7 appearances per normal planet type.
- Specified off-course guidance toward the next expected course planet.
- Specified restrained orbit focus zoom and deterministic concentration lines.
- Specified the 23-sprite minimum resident/Hero atlas and 3-state rocket sprite plan.
- Specified richer procedural planet visuals without required image assets.
- Specified DEBUG/DEMO-only `GOAL TEST` behavior and crew presets.
- Specified title/start screen behavior with START, Normal/Hard selection, and DEMO.
- Updated roadmap, handoff, goal state, task queue, decision log, README, runbook, tuning notes, mobile controls, and supply/goal/result specs.
- Kept gameplay implementation, fake `.pyxres` files, external assets, HTML changes, root `main.py`, and Firework Observer changes out of scope.

## GRC009E1

- Integrated the developer-authored Hero art and five resident idle sprites from `assets/gravity_courier.pyxres`.
- Added Hero sprite metadata for image bank 0, `(u=0, v=0)`, `32x32`.
- Set the shared sprite transparent color key to palette index `14`.
- Enabled resident sprite readiness for the five initial idle sprites while keeping missing-resource fallback support.
- Shifted resident atlas rows down by one 32px row: Wind `v=32`, Iron `v=64`, Water `v=96`, Forest `v=128`, Rock `v=160`.
- Reused each resident idle cell for cheer stages until dedicated expression cells are authored.
- Rendered Hero and resident sprites via `pyxel.blt` when the resource is ready, with primitive fallback otherwise.
- Expanded the in-run crew UI into a full-width lower HUD strip so the playfield is not blocked by a right-side card and all five type counters can remain visible.
- Added a compact Hero jump and confetti reaction in the crew UI for positive events: lap/Gravity Assist success, supply cargo crew joins, normal supply recovery, and Transfer Boost exits.
- Reduced the resident cut-in card height from `144` to `120` px.
- Polished the result screen with shimmer-colored `RETURN COMPLETE`, larger `CREW CELEBRATION`, separated Hero/message placement, and deterministic staggered jumping.
- Kept rocket rendering, resident cut-ins, scoring, and gameplay behavior unchanged.

## GRC009E2

- Changed ready supply ship reservations from one-shot crossing opportunities into stationary SUPPLY ZONE waiting ships.
- Queued ready ships horizontally by planet type, with same-type ships stacked vertically.
- Kept ready reservations in `spawned` state until cargo collection so DEMO and normal play do not consume earned crew opportunities through ordinary misses.
- Synchronized waiting ships into the current/next visible SUPPLY ZONE and marked that gap as a supply zone when needed.
- Added tests for stationary waiting ships, delayed readiness, persistent spawned reservations, and multi-type lane ordering.

## GRC009E

- Scoped the remaining sprite work to resident and Hero integration; rocket sprite work is treated as already complete.
- Added Hero state readiness for `idle`, `cheer`, and `result`; only `idle` is currently ready.
- Added resident per-type and per-stage readiness for Wind, Iron, Water, Forest, and Rock.
- Marked only the five resident `idle` cells as ready; `cheer1`, `cheer2`, and `cheer3` now keep primitive fallback until authored.
- Added resident and Hero asset inventory helpers for Pyxel Editor progress tracking.
- Updated cut-ins, crew UI, and result crowd drawing to use sprites only when the specific state/stage is ready.
- Updated sprite documentation with the current readiness matrix and fallback policy.
- Added tests for readiness inventories, state/stage-specific fallback, and incremental stage enablement.

## GRC009F

- Added Normal and Hard course modes.
- Made Normal the default course with 20 planets and 4 appearances per normal planet type.
- Preserved Hard as the long course with 35 planets and 7 appearances per normal planet type.
- Added mode metadata to generated courses and result summaries.
- Added mode-specific rank thresholds so Normal and Hard score ranks can be tuned separately.
- Added `N` key mode toggling before the future title-screen mode selector.
- Updated Journey Progress and final goal generation to use the active course length.
- Added tests for Normal/Hard generation, mode toggling, mode-specific ranks, and default Normal app startup.

## GRC009A

- Added a DEBUG/DEMO-only bottom-right `GOAL TEST` button.
- Added `G` as a keyboard fallback while DEBUG or DEMO is enabled.
- Added deterministic joined-crew presets `12`, `50`, `51`, `200`, `201`, and `635`.
- Distributed result-test crew across Wind, Iron, Water, Forest, and Rock in stable order.
- Assigned test score, HP, shield, fuel, and lap counts for fast result-screen inspection.
- Placed the rocket just before the final goal with safe forward velocity so normal goal arrival triggers the result state.
- Added Normal and Hard result-helper tests covering preset cycling, safe pre-goal placement, and mode-specific result summaries.

## GRC009B

- Added zoom-aware camera world/screen transforms while keeping HUD and buttons in screen space.
- Added orbit focus strength from current lap progress and completed orbit laps.
- Capped orbit focus zoom at `1.12`.
- Blended the camera follow target slightly toward the rocket/planet midpoint during active focus.
- Added deterministic screen-space concentration lines that remain behind HUD and cut-ins.
- Attenuated orbit focus while resident cut-ins are active.
- Released focus smoothly during Transfer Boost without adding screen shake.
- Scaled key world-space radii for planets, gravity wells, orbit tracks, and the final goal while focused.
- Added tests for camera zoom round-trip, focus start threshold, cut-in attenuation, Transfer Boost release, zoom cap, and concentration line limits.

## GRC009C

- Added off-course recovery detection for the next expected course target.
- Kept target selection course-order based, so past or nearest planets do not steal guidance.
- Switched the target to the final goal after the last course planet is passed.
- Added screen-edge `NEXT`/`GOAL` arrow rendering with distance text.
- Kept the helper inside safe HUD bounds and hidden during resident cut-ins.
- Added debug HUD state for active target, distance, and stall frames.
- Added tests for edge placement, ordered targeting, final-goal targeting, activation, stall detection, safe drawing, and cut-in suppression.

## GRC009D

- Split planet drawing into base, surface, atmosphere, and sparse particle layers.
- Added a `PLANET_RENDERERS` dispatch table for Wind, Iron, Water, Forest, Rock, and Black Hole renderers.
- Enriched Wind with cloud bands, flow marks, a light atmospheric ring, and small moving particles.
- Enriched Iron with panel seams, rivets, segmented bands, metallic rings, and blinking light points.
- Enriched Water with wave bands, bubbles, and a bright atmosphere ring.
- Enriched Forest with green clusters, sprout/leaf marks, spores, and layered outer rings.
- Enriched Rock with craters, cracks, irregular outline accents, and tiny visual fragments.
- Kept planet physics, gravity wells, collision radius, rewards, type labels, and lap labels unchanged.
- Added tests for renderer dispatch coverage, layered drawing, and distinct type-specific operation mixes.

## GRC010

- Added a shared `ControlIntent` path for keyboard and touch controls.
- Kept desktop keyboard controls supported while routing flight input through the same intent model.
- Added screen-space touch/mouse drag steering that is independent of camera zoom.
- Added high-speed turn assist and clamped touch rotation response for orbit entry at higher speeds.
- Added upward swipe thrust pulses and downward swipe brake pulses as short gentle effects instead of one-frame impulses.
- Kept tap reserved for future actions and prevented top-level UI button presses from becoming flight drag input.
- Made trajectory preview always enabled for mobile readiness.
- Updated lower HUD guidance to mention drag and swipe controls.
- Added tests for keyboard intent, touch drag, high-speed touch assist, swipe pulses, gentle pulse strength, and always-on preview.

## GRC009G

- Added a fallback-safe `AudioManager` for Pyxel sound setup and playback.
- Added layered title BGM with low accompaniment and high music-box harmony.
- Added a thin looping cruise BGM for current no-title gameplay startup.
- Added a gentle, music-box-like looping result BGM for the return-complete screen.
- Added a short rising orbit-entry cue when the rocket starts riding a planet orbit.
- Added staged lap sounds for lap 1, lap 2, and lap 3+.
- Added SE hooks for Transfer Boost, supply collection, damage, crash/lost, and result arrival.
- Stopped only the BGM channel on result/crash so event SE can still play.
- Added temporary `S` key sound toggle and HUD sound state text ahead of title-screen SOUND controls.
- Added tests for sound registration, looping BGM, lap-stage clamping, disabled audio behavior, sound toggling, and app event integration.

## GRC010A

- Added a formal `title` game state for launch flow while preserving existing play/result/crash states.
- Added title-screen START, Normal/Hard mode selection, DEMO entry, and SOUND ON/OFF controls.
- Added keyboard support for title flow: Left/Right changes mode, Z/Enter starts, M starts DEMO, and S toggles sound.
- Kept title mode selection as selection-only; the selected course is generated when START or DEMO begins the run.
- Plays layered title audio while waiting, then starts gameplay BGM on START, DEMO, retry, or restart into play.
- Added concise title guidance for drag steering, swipe speed control, keyboard mode selection, and demo start.
- Added tests for title button layout, mode selection, start/demo entry, and title-safe sound toggling.
