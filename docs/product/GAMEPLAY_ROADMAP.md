# Gameplay Roadmap

Gravity Courier should grow from a readable swing-by prototype into a score-driven gravity-assist arcade game. The fixed product target remains `iphone16_large`, `393x852`, portrait-first.

Keep new work inside `prototypes/gravity_courier/`. Do not modify root `main.py`, Firework Observer gameplay files, HTML files, or external assets.

## Product Direction

- The player earns score by successfully performing swing-bys.
- Repeating swing-bys around the same planet increases score rewards.
- Higher lap counts increase speed and risk.
- Each planet type should provide a useful reward so no planet feels like a useless obstacle.
- Planet residents cheer when the player succeeds.
- Cut-ins and crew characters should share character assets.
- Interplanet space should eventually include obstacles and reward objects.
- Lap 3 milestones should eventually reserve delayed supply ships.
- Supply ship cargo should add crew, making the run feel like a growing journey.
- A finite course should eventually end at an Earth-like goal and result screen.
- The game should stay readable, lightweight, and portrait-first.

## Milestones

### GRC002: Add gameplay roadmap and system specs

Status: done.

Goal:
- Document score/lap, planet rewards, cheering, crew, and interplanet object plans.

Do not implement:
- Gameplay systems.
- Procedural generation.
- iOS wrapper.

### GRC003: Implement score, lap count, and planet lap display

Status: done.

Goal:
- Make swing-by success become a score game.

Implement:
- Score value.
- Per-planet lap count.
- Score gain on assist.
- Lap multiplier.
- Large lap display on or near the planet.
- HUD score display.
- Simple 3-stage cheer text feedback.

Do not implement:
- Full cut-in portraits.
- Crew system.
- Supply ships.
- Planet-type rewards.

### GRC004: Implement planet types and 2-lap reward activation

Status: done.

Goal:
- Make each planet type worth using.

Implement:
- Planet type enum/string.
- Wind, iron, water, forest, and rock initial type definitions.
- 2-lap reward activation rule.
- Wind acceleration bonus.
- Iron durability/shield bonus.
- Water score multiplier bonus.
- Forest propulsion gauge recovery bonus.
- Rock HP recovery bonus.
- Simple visual distinction per planet type.

Do not implement:
- Full resident art.
- Supply ship.
- Advanced procedural generation.

### GRC005: Implement resource-backed shared cheer cut-in framework

Status: done.

Goal:
- Make swing-by success emotionally satisfying.

Implement:
- Shared cut-in component.
- Character registry.
- Resident registry with `32x32` sprite metadata.
- Resource-backed cut-in portraits using `prototypes/gravity_courier/assets/gravity_courier.pyxres` when available.
- Primitive fallback portraits when the resource file is not available.
- Planet-specific resident IDs.
- Cheer stage 1/2/3 visual effects.
- Cut-in timing and cooldown.

Do not implement:
- Final character art.
- Crew system.
- Supply ships.
- Interplanet obstacles.
- Complex dialogue system.

### GRC006: Implement interplanet obstacles and collectibles

Status: done.

Goal:
- Make travel between planets interesting.

Implement:
- Floating asteroids.
- Crossing rockets as moving obstacles.
- Supply items as collectibles.
- Basic collision/collection logic.
- Scoring/recovery rewards.

Do not implement:
- Supply ships.
- Crew growth.
- Final goal.
- Result screen.
- Crossing meteor swarms.

### GRC007: Implement supply ship and crew growth UI

Status: done.

Goal:
- Make long runs feel like a growing journey.

Implement:
- Lap 3 milestone supply ship reservations.
- Supply ship spawning 2 or 3 planet gaps after reservation.
- Supply cargo collection.
- Score and propulsion recovery from supply cargo.
- Planet-type crew counts.
- Crew join sequence `[1, 2, 4, 8, 16, 32, 64]`.
- Missed cargo rule: success tier does not advance, but the spawn event is consumed.
- Protagonist crew member from start.
- Representative lower-left/lower-right crew display.

Do not implement:
- Final art polish.
- Complex crew abilities unless trivial.
- Final goal/result screen.
- Crossing meteor swarms.

GRC007 first implementation notes:
- "2 or 3 planet gaps" is approximated by counting Transfer Boost exits until course navigation is more explicit.
- Supply ship cargo adds score, fuel, and crew.
- Normal supply items remain score/fuel only and do not add crew.
- In-run crew UI is compact and does not draw every crew member.

### GRC008: Tune difficulty progression and route generation

Status: done.

Goal:
- Balance score, speed, risk, and readability.

Implement/tune:
- Max 7 appearances per normal planet type.
- Shuffle-bag course generation.
- Seeded generation for reproducible tuning.
- Wider supply-ship gaps.
- Crossing meteor swarms.
- Speed growth.
- Lap score scaling.
- Obstacle spawn rates.
- Supply frequency.
- Planet spacing.
- Camera smoothing.
- Preview length.
- Fuel/boost economy.

GRC008 first implementation notes:
- Generates a seeded 35-planet finite course.
- Wind, Iron, Water, Forest, and Rock each appear exactly 7 times.
- Prevents 3 identical planet types in a row.
- Ensures the first 5 planets include Forest or Rock.
- Adds course gap metadata and supply-zone marking.
- Supply ship reservations can target real future course gaps while still using Transfer Boost countdowns.
- Adds deterministic crossing meteor swarms in selected gaps.
- Adds simple difficulty helpers from 1.0 to 1.75.

### GRC009: Implement final goal and result screen

Status: implemented.

Goal:
- Give the finite journey a clear destination and celebration payoff.

Implement:
- Earth-like goal.
- Journey Progress UI.
- Compact `PLANET current/35` display.
- Compact progress bar toward `GOAL`.
- Optional small `NEXT SUPPLY` or `SUPPLY NEXT GAP` hint when supply gap data is available.
- Goal arrival detection.
- Final score.
- Crew bonus.
- Result screen.
- Crew count display.
- Result crew/crowd rendering.
- Staggered crew jump celebration.
- Rank display.

Implemented notes:
- Final goal is Earth-like and separate from normal planet gravity/lap/reward logic.
- Result state is separate from crash/lost state.
- Final score currently uses run score plus crew bonus.
- Result screen uses crew-density tiers for normal, dense, and crowd displays.

Important:
- Keep the result readable at `393x852`.
- Keep Journey Progress compact and readable without covering the top HUD, demo button, side cut-ins, or crew UI.
- Journey Progress should not become a full minimap or route-management UI.
- Scale crowd density for large crew counts.
- Do not require final character art.

### GRC009P: Document post-goal polish, mode, navigation, and asset roadmap

Status:
- planning task

Goal:
- Convert post-GRC009 improvement ideas into implementation-ready specs.

Deliverables:
- Normal/Hard mode spec.
- Off-course helper spec.
- Orbit focus presentation spec.
- Resident, Hero, and rocket sprite asset plan.
- Procedural planet visual spec.
- Result test helper spec.
- Title screen spec.
- Post-GRC009 roadmap.

No gameplay implementation is required.

### GRC009A: Add result-screen test helper

Goal:
- Make result-screen crew-density verification fast.

Implement:
- Bottom-right `GOAL TEST` button.
- DEBUG/DEMO-only visibility.
- Crew presets: `12`, `50`, `51`, `200`, `201`, `635`.
- Score/resource test state.
- Safe pre-goal placement.
- Normal result transition verification.

### GRC009F: Add Normal and Hard course modes

Status: implemented.

Goal:
- Support a shorter standard route and the current long score-attack route.

Implement:
- Normal mode: 20 planets, 4 appearances per normal type.
- Hard mode: 35 planets, 7 appearances per normal type.
- Shared rewards, crew sequence, supply rules, controls, final goal, and result structure.
- Mode-specific difficulty/rank tuning.
- Selected mode shown in result summary.

Implementation note:
- Normal is the default course.
- `N` toggles Normal/Hard until the title-screen mode selector is implemented.

### GRC009B: Add orbit focus presentation

Goal:
- Make active orbiting feel tense and visually focused.

Implement:
- Orbit focus strength.
- Restrained camera zoom up to about `1.12`.
- Camera focus blend toward the rocket/planet midpoint.
- Deterministic concentration lines.
- Cut-in attenuation.
- Smooth Transfer Boost release.

Do not implement:
- Screen shake.

### GRC009C: Add off-course recovery helper

Goal:
- Help players return to the route without taking control away.

Implement:
- Next expected course planet selection.
- Off-course detection.
- Screen-edge arrow.
- Optional distance display.
- Safe HUD placement.

### GRC009D: Enrich procedural planet visuals

Goal:
- Make planet types more readable and memorable without requiring image assets.

Implement:
- Shared planet render architecture.
- Type-specific surface patterns.
- Lightweight atmospheric animation.
- Collision/render separation.

### GRC009E: Complete resident and Hero sprite integration

Goal:
- Track authored resident and Hero sprites precisely while retaining primitive fallback.

Implement:
- `.pyxres` resource integration.
- 23-sprite minimum resident/Hero atlas.
- Per-Hero-state readiness.
- Per-resident-stage readiness.
- Primitive fallback retained.
- Atlas documentation and validation.

Important:
- This task may wait until Pyxel Editor sprites are ready.
- Do not create fake `.pyxres` assets.
- Rocket sprite work is handled separately and is not part of this remaining scope.

### GRC010: Mobile/touch readiness pass

Goal:
- Prepare portrait play for future iPhone wrapper.

Implement/plan:
- Shared `ControlIntent` model for keyboard and touch input.
- Horizontal drag as high-sensitivity continuous rocket rotation.
- Mild high-speed turn assist so orbit entry remains practical as velocity rises.
- Clamped maximum angular response to prevent sudden uncontrollable rotation.
- Upward swipe as a short gentle forward-thrust pulse.
- Downward swipe as a short gentle brake/reverse-thrust pulse.
- Always-on trajectory preview during mobile gameplay.
- No gameplay touch toggle for trajectory preview.
- Lower UI safe areas.
- Thumb-friendly controls.
- UI readability at `393x852`.
- Optional touch debug overlay.

Do not implement:
- iOS wrapper.
- Gesture-dependent trajectory preview toggle.
- Large instantaneous swipe velocity impulses.
- Removal of keyboard controls.

### GRC009G: Add gameplay audio manager and stage sounds

Goal:
- Add a lightweight audio foundation before title-screen SOUND controls.

Implemented:
- Fallback-safe `AudioManager`.
- Layered title BGM with low accompaniment and high music-box harmony.
- Thin looping cruise BGM.
- Gentle looping result BGM.
- Lap 1, lap 2, and lap 3+ stage sounds.
- Transfer Boost, supply, damage, crash, and result sounds.
- Temporary `S` key sound toggle.

### GRC010A: Implement title screen and mode selection

Goal:
- Add a simple start flow before gameplay.

Implemented:
- Title state.
- START button and Z/Enter start.
- Normal/Hard selection button and Left/Right selection.
- DEMO title entry using the existing demo mode.
- SOUND title control sharing the same sound-enabled state as `S`.
- Concise control guidance.
- Touch/click and keyboard navigation.
- Title screen plays layered title audio; START/DEMO switches to gameplay BGM.

Dependency:
- If course modes are not implemented yet, GRC009F should precede this task.

### GRC011: Polish and release candidate prototype

Goal:
- Make a satisfying shareable prototype.

Implement:
- Visual polish.
- Sound effects if appropriate.
- Better feedback.
- Improved retry loop.
- Title/game over flow.
- High score persistence if appropriate.
