# GPT Handoff

## Current Status

- Goal: `GRC011A Performance measurement and first optimization pass`
- Target resolution: `393x852`
- Profile: `iphone16_large`
- Status: Journey Progress, Earth-like final goal, result state, final score, rank, density-based crew celebration, demo orbit showcase tuning, camera/readability tuning, fixed-width pixel text rendering, Normal/Hard modes, result-screen test helper, mobile touch controls, audio foundation, title screen, and first performance pass are implemented; final resident art remains future work

## Implemented

- Rocket starts near the lower screen and is now camera-anchored closer to screen center for better orbit readability.
- Left / Right steers relative to the current travel direction.
- Up boosts along the current travel direction and consumes fuel.
- Down brakes by damping velocity.
- Space toggles dotted trajectory preview.
- R restarts.
- D toggles debug HUD.
- Escape quits.
- M and the top-right `DEMO` button toggle demo mode.
- Demo mode automatically targets offset passes around the next planet and keeps fuel full for showcase play.
- Demo mode now circles nearby planets for about `2.4` turns before transferring, and every third demo planet waits for `3.0` turns to show lap 3+ behavior.
- Orbit assist nudges velocity toward tangential motion inside gravity wells so planets feel like places to circle, not only slingshot past.
- Orbit assist now preserves fast entry speed instead of forcing the rocket down to the target orbit speed when entering a gravity well.
- Orbit speed bonus now starts while simply riding an orbit, before a completed lap, and still grows with completed/accumulated turns.
- Planets exert softened 2D gravity.
- Planet course now creates a seeded 35-planet finite course arranged upward from the start area.
- Planet collision now consumes shield before HP, bounces the rocket away, and only crashes when HP reaches 0.
- Signed angular orbit progress now drives lap completion while the rocket remains inside a planet gravity well.
- Each completed lap triggers `GRAVITY ASSIST!`, score, lap label updates, cheer text, resident cut-in feedback, and the generic assist fuel reward.
- Transfer Boost is separate from lap scoring: after at least one completed lap in the current visit, `TRANSFER READY` appears, and exiting that gravity well triggers `TRANSFER BOOST!` once for that visit.
- HUD shows distance, speed, assist count, fuel, and controls hint.
- HUD and gameplay messages are rendered with a fixed-width custom pixel font so centering/right alignment stays stable at large sizes.
- HUD now shows formal `SCORE`.
- Completed laps add score using the provisional GRC003 lap multiplier formula.
- Each planet tracks its own local lap count.
- Planets with completed laps or active orbit visits display large lap labels centered on the planet: `1`, `2`, or `3+`.
- Simple 3-stage ASCII cheer feedback is implemented: `WAA!`, `CLAP! CLAP!`, `FWEET!`.
- Planets have types: Wind, Iron, Water, Forest, and Rock.
- Planet type labels and color distinctions are visible in the seeded finite course.
- A planet's special reward activates once per planet per run when that planet reaches lap 2.
- Wind reward sets that planet's `gravity_multiplier` to `1.25`.
- Iron reward adds `SHIELD +1`, clamped to max shield.
- Water reward grants 3 future assist score bonus uses at x1.25.
- Forest reward restores 25% max fuel, clamped.
- Rock reward restores 1 HP, clamped.
- HUD shows `HP` and `SHIELD`.
- Debug HUD shows reward count, last reward, water bonus uses, HP/shield, and active planet type/multiplier.
- Completed laps start a shared cut-in panel.
- Cut-ins use the assisting planet type to select a resident.
- Cut-ins slide in from the screen side opposite the assisting planet and now use an upper-screen vertical band to reduce overlap with the centered rocket.
- The separate gravity-assist message was compressed into compact HUD-adjacent lines so it does not overlap the raised cut-in card.
- Residents are registered in `residents.py` with `32x32` sprite coordinates and fallback style IDs.
- Optional `.pyxres` loading is handled by `resources.py`; missing resources fall back to primitive portraits.
- Cut-in state is pure and covered in `cutin.py`.
- Debug HUD exposes active orbit planet, lap angle/progress, visit laps, total laps, transfer ready state, last lap planet, last transfer planet, and last cut-in side.
- Floating asteroids are implemented as deterministic interplanet hazards.
- Crossing rockets are implemented with warning timing before horizontal movement.
- Normal supply items are implemented as one-time score/fuel pickups.
- Interplanet object damage uses the same shield/HP rule as planet collision.
- Debug HUD shows active interplanet object count, crossing warnings, last supply item, and last damage source.
- Lap 3 milestones reserve supply ships for the source planet type.
- Supply ships use a deterministic 2-3 Transfer Boost delay approximation and do not spawn immediately.
- Ready supply ships wait in SUPPLY ZONE lanes by planet type until collected.
- Supply cargo grants score, fuel recovery, and planet-type crew.
- Crew join counts follow `[1, 2, 4, 8, 16, 32, 64]` per planet type.
- Waiting supply cargo does not advance the crew success tier until collected.
- HUD includes a full-width lower crew strip with joined total, HERO, and all five type counters, keeping the right side of the playfield clearer.
- The crew strip Hero jumps and emits small confetti on positive events: completed gravity-assist laps, supply cargo crew joins, normal supply recovery, and Transfer Boost exits.
- Debug HUD shows supply reservation/ship counts and last supply ship status.
- `course.py` generates a shuffle-bag course with Wind, Iron, Water, Forest, and Rock appearing exactly 7 times each.
- Course generation is deterministic by `COURSE_SEED`.
- The first implementation prevents 3 same-type planets in a row and ensures the first 5 include Forest or Rock.
- Course gaps are represented with adjacent planet IDs, center positions, width hints, supply-zone flags, and meteor-swarm flags.
- Supply ship reservations now mark future course gaps, then synchronize ready ships into the current/next visible SUPPLY ZONE.
- Difficulty helpers scale from 1.0 near the start to 1.75 near the end.
- Crossing meteor swarms exist as distinct warning-based hazards in selected gaps.
- Debug HUD shows course gap/supply gap counts and active meteor swarm count.
- Compact Journey Progress shows route progress toward `GOAL` during gameplay.
- The Earth-like final goal is separate from normal planets and is not part of gravity, lap, reward, or supply-ship planet logic.
- Reaching the final goal enters a separate `result` state instead of crash/lost.
- `goal.py` contains pure final-goal and journey progress helpers.
- `result.py` contains pure result score, rank, crew bonus, and crew density helpers.
- Result summary includes final score, run score, crew bonus, crew count, laps, collected supply cargo count, HP, shield, fuel, rank, and crew display density.
- Result screen renders shimmer title text, a larger crew celebration heading, separated Hero/message placement, and staggered crew jumping using density tiers for normal, dense, and crowd counts.
- DEBUG HUD can show timing for starfield, trajectory prediction, planet drawing, object drawing, and non-orbit DEMO AI sections.
- Trajectory preview points are cached and recalculated every 2 frames.
- Gameplay starfield draws fewer points than the title screen.
- Planet rendering uses LOD so detailed surface/atmosphere/particle layers are skipped when they are not useful.
- Orbit focus line count, result confetti, and crew UI confetti were reduced for lower draw cost.
- Non-orbit DEMO navigation decisions are cached for short intervals.
- Hot collision/range checks use squared-distance comparisons where exact distance is not needed.

## Product Direction

- 2D gravity-assist rocket game.
- Portrait iPhone-oriented Pyxel prototype.
- Swing-by readability and satisfying feedback matter more than strict orbital realism.
- Gravity Courier should evolve into a score-driven swing-by arcade game.
- Swing-by lap count is the core scoring multiplier.
- Lap count is based on angular progress around a planet while inside its gravity well, not on leaving the gravity well.
- Transfer Boost is an exit event after at least one completed lap in the current visit.
- Each planet type should provide a meaningful benefit when used well.
- Planet rewards should generally activate after 2 successful swing-bys on the same planet.
- Forest Planet recovers the propulsion gauge; if the implementation still uses `fuel`, treat fuel as the propulsion/boost gauge.
- Rock Planet restores lost HP.
- Iron Planet improves defensive capacity. Iron = prevention/armor/shield; Rock = healing/repair/recovery.
- Cheer feedback has 3 stages: normal cheers, cheers plus clapping, then cheers plus clapping plus whistles.
- Stage 3+ reuses the maximum cheer presentation while exact lap count continues scaling score.
- Cut-ins and crew display should share character assets through a character registry.
- Interplanet space will eventually include crossing rockets, floating asteroids, supply items, and supply ships.
- Normal planet types should eventually appear at most 7 times each in a finite shuffle-bag course.
- Lap 3 milestones should reserve delayed supply ships that become ready 2 or 3 planet gaps later and wait in SUPPLY ZONE until collected.
- Supply cargo should add score, propulsion recovery, and planet-type crew.
- Crew joins should use `[1, 2, 4, 8, 16, 32, 64]`, capped at 7 success tiers per planet type.
- The finite journey should end at an Earth-like goal and a result screen with score, crew count, and crew celebration.
- GRC009 should add compact Journey Progress during gameplay so players can see the finite route approaching `GOAL`.
- Journey Progress should show `PLANET current/35`, a small progress bar, and optionally a small `NEXT SUPPLY` or `SUPPLY NEXT GAP` hint when supply gap data is available.
- Journey Progress should remain compact and should not become a full minimap or route-management UI.
- Mobile controls should use horizontal drag for high-sensitivity continuous rotation, with clamped angular response and mild high-speed turn assist.
- Mobile upward/downward swipes should create short gentle thrust/brake pulses instead of large instantaneous velocity impulses.
- Mobile gameplay should keep trajectory preview always visible and should not expose a touch gameplay toggle for preview visibility.
- Touch and keyboard input should eventually flow through a shared `ControlIntent` model.
- Normal mode should use 20 planets with 4 appearances per normal type.
- Hard mode should preserve the current 35-planet route with 7 appearances per normal type.
- Off-course guidance should point to the next expected course planet, not a completed nearest planet.
- Orbit focus presentation should use restrained zoom up to about `1.12` and deterministic concentration lines.
- Resident/Hero sprite integration should target a 23-sprite minimum `32x32` atlas and retain primitive fallback.
- Rocket sprite integration should target `32x32` idle, thrust, and damage states.
- Procedural planet visuals should be enriched without requiring image assets.
- The developer-only result helper should use boundary crew presets: `12`, `50`, `51`, `200`, `201`, `635`.
- The title screen includes START, Normal/Hard mode selection, DEMO, SOUND, and concise keyboard/touch guidance.
- Character designs inspired by existing works must remain original and must not directly copy protected characters.

## Next Recommended Task

`GRC011 Polish and release candidate prototype`

Recommended scope: manual playtest tuning, UI hierarchy, route duration tuning, feedback polish, debug/release feature separation, and final prototype readiness.

## Product Specs

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

## GRC003 Implementation Notes

- Score helpers live in `src/gravity_courier/scoring.py`.
- `GravityCourierApp` tracks `score`, `planet_lap_counts`, `last_score_gain`, `last_lap_count`, and `cheer_text`.
- GRC004 adds `planet_types.py`, `Planet.planet_type`, `Planet.gravity_multiplier`, and the first reward activation layer.
- Existing GRC001 generic assist fuel reward still exists alongside Forest's planet-specific fuel recovery.
- Water score bonus applies starting from future assist events, not retroactively to the lap 2 assist that grants it.
- Score bonus rounding uses the existing rounded scoring helper: lap 2 x1.25 becomes 188.
- GRC005 adds `residents.py`, `cutin.py`, `resources.py`, and `assets/README.md`.
- Reserved resource path is `prototypes/gravity_courier/assets/gravity_courier.pyxres`; do not create an empty/fake `.pyxres`.
- Missing or failed `.pyxres` loading uses primitive fallback portraits.
- Future crew UI should reuse the resident registry and `32x32` sprite source.
- GRC005A adds `orbit.py` for pure signed-angle lap tracking helpers.
- `LAP_COMPLETION_RADIANS` is currently `math.tau * 0.90` so a near-complete orbit can count as a readable arcade lap.
- Lap 2 rewards are now triggered from the lap completion flow, not an exit-speed gravity assist flow.
- GRC005B adds the supply ship, crew growth, finite course, final goal, result, and crossing meteor swarm spec.
- GRC006 remains limited to floating asteroids, crossing rockets, and normal supply items.
- GRC007 adds `supply.py` and `crew.py` for supply ship reservations, delayed spawns, cargo collection, crew growth, and representative crew UI.
- GRC007 approximates "2-3 planet gaps" by counting Transfer Boost exits.
- Normal GRC006 supply items remain score/fuel only; GRC007 supply ship cargo is the crew-adding collectible.
- GRC008 adds `course.py` and `meteor_swarm.py`.
- GRC008 keeps supply ship Transfer Boost countdowns, but reservations now also target and mark real course gaps.
- GRC008 implements deterministic finite route structure but does not add the final Earth-like goal.
- GRC009 adds Journey Progress, the Earth-like goal, and result screen.
- GRC009P adds post-goal polish, mode, navigation, presentation, asset, test helper, title screen, and post-GRC009 roadmap specs.
- GRC010A adds the launch title state with START, Normal/Hard mode selection, DEMO entry, SOUND toggle, concise control guidance, and title-safe audio behavior.
- GRC011A adds cached trajectory preview, planet LOD, gameplay starfield stride, reduced focus/confetti draw counts, DEMO AI throttling, squared-distance hot checks, and DEBUG timing readouts.
- `assets/gravity_courier.pyxres` now contains the first developer-authored Hero sprite copied from root `main.pyxres`.
- Hero is image bank 0 at `(u=0, v=0)`, `32x32`, with transparent color key `14`.
- Five resident idle sprites are enabled below Hero at `u=0`, rows `v=32..160`, with transparent color key `14`.
- Resident cheer stages currently reuse idle until dedicated expression columns are authored.
- Resident atlas rows now start below Hero: Wind `v=32`, Iron `v=64`, Water `v=96`, Forest `v=128`, Rock `v=160`.
- Do not create fake or invalid resource files.
- GRC009A should add a result-screen testing shortcut; it should not replace the normal goal collision path.
- GRC010 should implement the mobile control direction in `MOBILE_CONTROL_SPEC.md`: shared `ControlIntent`, horizontal drag rotation, vertical thrust/brake pulses, always-on trajectory preview for mobile, and preserved keyboard controls.
- The title screen plays layered title BGM with low accompaniment and high music-box harmony; gameplay BGM starts after START, DEMO, retry, or restart into play.

## Protected Areas

- Existing Firework Observer root `main.py`.
- Existing Firework Observer gameplay modules.
- Existing HTML files.

## Validation Commands

```bash
python3 -m compileall prototypes/gravity_courier
python3 prototypes/gravity_courier/scripts/check_all.py
python3 -m unittest discover prototypes/gravity_courier/tests
git diff --check
```

Manual launch command:

```bash
.venv/bin/python prototypes/gravity_courier/main.py
```

For gameplay implementation tasks, Pyxel is installed in the local project `.venv`. Use `.venv/bin/python` or activate the venv before launching. Manual launch is useful after GRC005 to judge cut-in placement and readability.

## Known Non-Goals Still In Place

- No external assets.
- No external audio assets; current audio uses lightweight Pyxel synth patterns.
- No iOS wrapper.
- No HTML changes.
- No Firework Observer gameplay changes.
