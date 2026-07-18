# Decision Log

## GRC000

- Gravity Courier is isolated under `prototypes/gravity_courier/`.
- Target screen is fixed to `iphone16_large`, `393x852`.
- No intermediate resolution will be used.
- Firework Observer files are protected.
- First prototype prioritizes gameplay readability over orbital realism.

## GRC001

- Gameplay is implemented in `app.py` with pure logic kept in `physics.py`, `trajectory.py`, `scoring.py`, `camera.py`, and `entities.py`.
- Pyxel is imported lazily so pure tests can run without opening a window.
- Trajectory preview uses the same gravity model as gameplay and does not mutate the live rocket.
- Preview keeps planet positions static for readability in the first playable version.
- Gravity assist detection triggers once after exiting a planet well with sufficient speed gain.
- The first planet is tuned with a larger readable gravity well so an early assist can be observed.
- No external assets or HTML files were added.

## GRC002

- Gravity Courier will become a score-driven swing-by arcade game.
- Swing-by lap count is the core scoring multiplier.
- Planet rewards should generally activate after 2 successful swing-bys on the same planet.
- Cheer feedback has 3 stages.
- Stage 3+ reuses the maximum cheer presentation while score continues scaling.
- Cut-ins and crew display should share character assets.
- Interplanet space will eventually include crossing rockets, floating asteroids, supply items, and supply ships.
- Character designs inspired by existing works must remain original and not directly copy protected characters.

## GRC002A

- Forest Planet reward is propulsion gauge recovery after 2 successful swing-bys around the Forest Planet.
- If the current implementation uses `fuel`, fuel is treated as the propulsion/boost gauge for the first Forest reward implementation.
- Forest Planet's provisional recovery value is 25% of max gauge, clamped to the maximum gauge value.
- Rock Planet reward is rocket HP recovery after 2 successful swing-bys around the Rock Planet.
- If HP/durability is not implemented yet, Rock Planet HP recovery remains pending until that system exists.
- Rock Planet's provisional recovery value is 1 HP or 25% of max HP, clamped to max HP.
- Iron Planet improves defensive capacity.
- Rock Planet restores lost health.
- Iron = prevention / armor / shield.
- Rock = healing / repair / recovery.

## GRC003

- GRC003 implements score/lap/cheer only; planet-type rewards remain reserved for GRC004.
- Formal score is separate from distance.
- Each planet tracks a local lap count when successful swing-by assists are chained on that planet.
- Planet lap labels display as `1`, `2`, or `3+`; exact lap count remains internal for scoring.
- Score gain uses `base_assist_score = 100`.
- Lap multipliers are x1.0 for lap 1, x1.5 for lap 2, x2.0 for lap 3, and `x2.0 + 0.25 * (lap - 3)` for lap 4+.
- Simple GRC003 cheer feedback uses ASCII text only: `WAA!`, `CLAP! CLAP!`, and `WOOO! WHISTLE!`.

## GRC004

- Planet rewards trigger once per planet per run when that planet reaches lap 2.
- Lap 3+ does not retrigger an already claimed planet reward.
- Wind Planet reward sets that planet's gravity multiplier to `1.25`.
- Iron Planet reward adds shield and remains prevention / armor / shield.
- Water Planet reward grants 3 future assist score bonus uses at x1.25.
- Water reward does not retroactively multiply the lap 2 assist that grants it.
- Score bonus rounding continues to use the existing rounded score helper.
- Forest Planet reward restores 25% max fuel and remains propulsion recovery.
- Rock Planet reward restores 1 HP and remains healing / repair / recovery.
- Planet collision now uses shield before HP, with a damage cooldown and bounce.
- HP reaching 0 causes crash/game over.
- GRC004 does not add supply ships, crew, interplanet obstacles, procedural generation, or full cut-in portraits.

## GRC005 Planning

- Resident and future crew characters should use shared `32x32` Pyxel Editor sprites.
- Cut-ins should render the same `32x32` sprites at 2x or 3x, with 3x (`96x96`) preferred first.
- Future crew UI should render the same sprites at 1x, with optional 2x highlight/join feedback.
- The resident registry should own sprite coordinates, resident IDs, display names, planet type mapping, and cheer lines.
- `prototypes/gravity_courier/assets/gravity_courier.pyxres` is the reserved Pyxel resource path.
- If `.pyxres` is missing, cut-in rendering must fall back to primitive portraits so app startup and tests remain robust.
- Primitive portraits are a fallback, not the preferred long-term representation.
- Crew UI should eventually cap visible members around 5-6 and use `+N` for overflow.
- Character designs must remain original and avoid direct copying of protected characters or designs.

## GRC005

- Successful assists trigger a shared resident cut-in panel.
- The cut-in uses the assisting planet type to select a resident.
- The resident registry is the shared source for cut-ins and future crew UI.
- The `.pyxres` file is optional at runtime; missing or failed resource loading falls back to primitive portraits.
- GRC005 creates only `assets/README.md`, not a fake or empty `.pyxres`.
- Cut-ins use stage 1 for lap 1, stage 2 for lap 2, and stage 3 for lap 3+.
- GRC005 does not implement final art, full crew UI, supply ships, or interplanet obstacles.

## GRC005A

- Lap Completed and Transfer Boost are separate events.
- Lap count is now driven by signed angular orbit progress inside a planet gravity well, not by gravity-well exit speed gain.
- The first implementation uses `LAP_COMPLETION_RADIANS = math.tau * 0.90` for a readable arcade lap.
- Completed laps trigger score, lap label updates, cheer text, resident cut-ins, and lap 2 reward activation.
- Transfer Boost becomes ready after at least one completed lap in the current planet visit.
- Leaving the gravity well after Transfer Ready triggers `TRANSFER BOOST!` once for that visit.
- Destination alignment can help draw a route line, but it no longer gates the player-facing Transfer Boost trigger.
- Cut-ins slide in around mid-screen from the side opposite the assisting planet.
- Lower screen space is preserved for fuel, controls, and future crew UI.

## GRC005B

- Normal crew-bearing planet types should each appear at most 7 times in the finite course.
- Future planet order should use shuffle-bag generation with constraints against bad early recovery distribution and long same-type streaks.
- Completing lap 3 around a planet reserves a supply ship for that planet type.
- Supply ships should become ready later, generally 2 or 3 planet gaps after reservation.
- Supply ship cargo grants score, propulsion recovery, and planet-type crew.
- Ready supply ships should wait in SUPPLY ZONE until collected; ordinary misses should not consume the opportunity.
- Crew join counts use `[1, 2, 4, 8, 16, 32, 64]`.
- Maximum joined crew per normal planet type is 127.
- Maximum joined crew across the five normal planet types is 635.
- In-run crew UI should show representative crew plus a count, not every crew member.
- The finite journey should end at an Earth-like goal.
- The result screen should show score, crew count, resources, rank, and a staggered jumping crew celebration.
- Crossing meteor swarms are future hazard sections that reinforce HP/shield value and should not be part of GRC006.

## GRC006

- GRC006 implements only the first interplanet object layer: floating asteroids, crossing rockets, and normal supply items.
- Normal supply items grant score and fuel recovery only; they do not add crew.
- Supply ship cargo remains the future crew-adding collectible for GRC007.
- Interplanet object placement remains deterministic and hand-tuned for the current fixed course.
- Floating asteroids and crossing rockets use the existing shield/HP damage model.
- Crossing rockets should show a warning before becoming dangerous.
- GRC006 does not implement supply ships, crew growth, crew UI, final goal, result screen, shuffle-bag generation, or crossing meteor swarms.

## GRC007

- Lap 3 and later multiples of 3 reserve a supply ship for the source planet type when type limits allow it.
- Supply ships do not spawn immediately.
- Until finite course generation exists, the 2-3 planet-gap delay is approximated by counting Transfer Boost exits.
- Odd reservation IDs use a 2-gap delay; even reservation IDs use a 3-gap delay for deterministic tuning.
- Supply ship cargo is the crew-adding collectible; normal supply items remain score/fuel only.
- Supply cargo grants score, propulsion recovery, and crew for the source planet type.
- Crew join counts use `[1, 2, 4, 8, 16, 32, 64]` per planet type.
- Missed supply cargo consumes that spawn event but does not advance the crew success tier.
- In-run crew UI shows compact representative/type counts and does not attempt to draw every crew member.
- GRC007 does not implement final goal, result screen, shuffle-bag course generation, or crossing meteor swarms.

## GRC008

- The normal finite course uses exactly 35 planets: Wind, Iron, Water, Forest, and Rock each appear 7 times.
- Planet order is generated from a deterministic shuffle bag using `COURSE_SEED`.
- The first fairness constraints are no 3 identical planet types in a row and at least one Forest or Rock in the first 5 planets.
- Course gaps are first-class metadata with adjacent planet IDs, center position, width hint, supply-zone flag, and meteor-swarm flag.
- Supply ship reservations now mark a future course gap when one exists, while retaining the Transfer Boost countdown for spawn timing.
- Supply zones are drawn as simple in-world markers and provide spawn placement context, not a full route-map UI.
- Crossing meteor swarms are distinct from floating asteroids: they are multiple small moving hazards with warning timing.
- Meteor swarms are deterministic and selected by gap index.
- Difficulty helpers scale deterministically from 1.0 near the start to 1.75 near the end.
- GRC008 does not implement the Earth-like final goal, result screen, final ranking, or result crew crowd rendering.

## GRC009 Planning

- GRC009 should add Journey Progress alongside the final goal and result screen.
- Journey Progress should make the finite 35-planet journey visible during gameplay.
- Journey Progress should show compact `PLANET current/35` text and a small progress bar toward `GOAL`.
- Journey Progress may show small supply anticipation hints such as `NEXT SUPPLY` or `SUPPLY NEXT GAP`.
- Journey Progress must remain compact and should not become a full minimap, full route map, or supply management screen.
- The result screen should feel like the end of a journey, not only a score table.

## GRC009

- Final goal is an Earth-like destination rendered separately from normal planets.
- Final goal is not part of planet gravity, lap counting, planet rewards, or supply-ship source logic.
- Reaching the final goal transitions to a separate `result` state.
- Crash/lost state remains separate from result/clear state.
- Journey Progress is compact and placed away from the top-left HUD and top-right DEMO button.
- Final score currently uses `run_score + crew_bonus`.
- Crew bonus uses joined crew only; the protagonist is displayed but not scored as joined crew.
- Result crew rendering uses density tiers: normal, dense, and crowd.
- Result crew celebration uses deterministic staggered jump timing.

## GRC009P

- Normal mode uses 20 planets: 4 appearances per normal planet type.
- Hard mode uses 35 planets: 7 appearances per normal planet type.
- Normal and Hard share the same crew join sequence.
- Off-course guidance targets the next expected course planet, not a completed nearest planet.
- Orbit focus uses restrained zoom with maximum around `1.12`.
- Concentration lines are deterministic and do not use flashing effects.
- Resident minimum asset plan contains 23 sprites.
- Rocket minimum sprite plan contains idle, thrust, and damage.
- Planets remain procedurally rendered rather than requiring image assets.
- `GOAL TEST` is developer-only and uses boundary-focused crew presets.
- Title screen includes START, mode selection, and DEMO.
- Mobile trajectory preview remains always on.
- Horizontal touch input prioritizes responsive high-speed steering.
- Vertical swipe input changes speed gradually.
- Primitive fallbacks remain supported after `.pyxres` integration.

## GRC009E1

- The first developer-authored Hero sprite and five normal resident idle sprites live in `prototypes/gravity_courier/assets/gravity_courier.pyxres`.
- Hero uses image bank 0, `(u=0, v=0)`, `32x32`, with palette color `14` as the transparent key.
- Resident idle sprites use image bank 0, `u=0`, rows `v=32..160`, with palette color `14` as the transparent key.
- Loading the `.pyxres` enables Hero rendering and the five initial resident sprites.
- Resident cheer stages reuse the idle cell until dedicated expression columns are authored.
- Resident atlas rows start below Hero: Wind `v=32`, Iron `v=64`, Water `v=96`, Forest `v=128`, Rock `v=160`.
- Rocket sprite replacement remains future work.

## GRC010 Planning

- Mobile gameplay should keep trajectory preview always visible.
- Mobile gameplay should not expose a touch toggle for trajectory preview.
- Horizontal touch drag controls continuous high-sensitivity rocket rotation.
- Rotation should use clamped angular response so the rocket can turn strongly without sudden uncontrolled reversal.
- A mild high-speed turn-assist multiplier should keep orbit entry practical as velocity rises.
- Upward swipe should trigger a short gentle forward-thrust pulse.
- Downward swipe should trigger a short gentle braking or reverse-thrust pulse.
- Vertical swipes should not apply large instantaneous velocity impulses.
- Touch and keyboard controls should feed a shared `ControlIntent` model.
- Tap remains reserved for future pause, cut-in advance, or special action.
- Swipe detection should use screen-space coordinates and should not depend on camera zoom.

## GRC011A

- Performance work should begin with DEBUG-visible timing instead of guessing blindly.
- Trajectory prediction may be cached for a short interval; 2-frame recalculation is acceptable for readability and responsiveness.
- Gameplay starfield can draw fewer stars than the title screen.
- Orbit focus concentration lines should stay restrained; 8-16 lines is the current first optimization target.
- Planet rendering should use LOD so offscreen body details, atmosphere, and particles are skipped when they do not improve readability.
- Result and crew confetti should keep celebration readable without drawing excessive particles.
- DEMO navigation decisions do not need to run every frame when the rocket is not actively orbiting.
- Collision and range checks should use squared-distance comparisons when exact display distance is not required.
