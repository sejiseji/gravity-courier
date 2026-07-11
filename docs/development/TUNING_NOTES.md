# Tuning Notes

## Current GRC001 Values

- Gravity strength: `GRAVITY_G = 0.08`
- Gravity softening: `GRAVITY_SOFTENING = 64.0`
- Camera anchor: `CAMERA_ANCHOR_X_RATIO = 0.5`, `CAMERA_ANCHOR_Y_RATIO = 0.58`
- Camera smoothing: `CAMERA_SMOOTHING = 0.18`
- Substeps: `SUB_STEPS = 3`
- Relative steering power: `ROCKET_STRAFE_POWER = 0.060`
- Max relative steering speed: `ROCKET_MAX_HORIZONTAL_SPEED = 3.0`
- Turn rate: `ROCKET_TURN_RATE = 0.032`
- Turn speed response: `ROCKET_TURN_SPEED_RESPONSE = 0.004`
- Turn rate max: `ROCKET_TURN_RATE_MAX = 0.052`
- Rocket forward boost: `ROCKET_THRUST_POWER = 0.045`
- Rocket brake damping: `ROCKET_BRAKE_DAMPING = 0.965`
- Orbit assist strength: `ORBIT_ASSIST_STRENGTH = 0.035`
- Demo orbit assist strength: `ORBIT_DEMO_ASSIST_STRENGTH = 0.070`
- Orbit target radius ratio: `ORBIT_TARGET_RADIUS_RATIO = 0.58`
- Orbit target speed: `ORBIT_TARGET_SPEED = 2.65`
- Orbit speed bonus base: `ORBIT_SPEED_BONUS_BASE = 0.010`
- Orbit speed bonus per turn: `ORBIT_SPEED_BONUS_PER_TURN = 0.007`
- Orbit speed bonus max per frame: `ORBIT_SPEED_BONUS_MAX = 0.036`
- Orbit speed bonus max speed: `ORBIT_SPEED_BONUS_MAX_SPEED = 4.8`
- Orbit track guide strength: `ORBIT_TRACK_GUIDE_STRENGTH = 0.13`
- Orbit track guide decay per lap: `ORBIT_TRACK_GUIDE_DECAY_PER_LAP = 0.035`
- Orbit track guide min strength: `ORBIT_TRACK_GUIDE_MIN_STRENGTH = 0.035`
- Orbit track guide radial correction: `ORBIT_TRACK_GUIDE_RADIAL_CORRECTION = 0.016`
- Lap completion threshold: `LAP_COMPLETION_RADIANS = math.tau * 0.90`
- Fuel max: `ROCKET_FUEL_MAX = 100.0`
- Fuel cost: `ROCKET_FUEL_COST = 0.9`
- Rocket max HP: `ROCKET_MAX_HP = 3`
- Rocket max shield: `ROCKET_MAX_SHIELD = 3`
- Damage cooldown: `ROCKET_DAMAGE_COOLDOWN_FRAMES = 45`
- Collision escape frames: `COLLISION_ESCAPE_FRAMES = 60`
- Collision escape gravity scale: `COLLISION_ESCAPE_GRAVITY_SCALE = 0.18`
- Collision escape orbit assist scale: `COLLISION_ESCAPE_ORBIT_ASSIST_SCALE = 0.25`
- Preview steps: `TRAJECTORY_STEPS = 180`
- Preview dot interval: `TRAJECTORY_DOT_INTERVAL = 4`
- Planet count: `PLANET_COUNT = 35`
- Planet vertical spacing: `PLANET_VERTICAL_SPACING = HEIGHT * 0.34`
- Demo target upward speed: `DEMO_TARGET_UPWARD_SPEED = -3.1`
- Demo max speed: `DEMO_MAX_SPEED = 5.4`
- Demo steer gain: `DEMO_STEER_GAIN = 0.030`
- Demo steer damping: `DEMO_STEER_DAMPING = 0.30`
- Demo pass offset ratio: `DEMO_PASS_OFFSET_RATIO = 0.60`
- Demo fuel cost: `DEMO_FUEL_COST = 0.12`
- Demo orbit turns before transfer: `DEMO_ORBIT_TURNS = 2.4`
- Demo long orbit cadence: `DEMO_ORBIT_LONG_TURNS = 3.0`, `DEMO_ORBIT_LONG_INTERVAL = 3`
- Assist threshold: `ASSIST_SPEED_GAIN_THRESHOLD = 0.30`
- Assist fuel reward: `ASSIST_FUEL_REWARD = 8.0`
- Assist exit boost: `ASSIST_EXIT_BOOST = 1.85`
- Assist exit min speed: `ASSIST_EXIT_MIN_SPEED = 4.25`
- Assist exit radial weight: `ASSIST_EXIT_RADIAL_WEIGHT = 0.65`
- Assist orbit cooldown: `ASSIST_ORBIT_COOLDOWN_FRAMES = 75`
- Destination-line alignment helper: `ASSIST_TRANSFER_ALIGNMENT_DEGREES = 3.0`
- Destination-line upward gap helper: `ASSIST_MIN_UPWARD_DESTINATION_GAP = 80.0`
- Wind reward gravity multiplier: `WIND_REWARD_GRAVITY_MULTIPLIER = 1.25`
- Iron reward shield gain: `IRON_REWARD_SHIELD_GAIN = 1`
- Water reward score multiplier: `WATER_REWARD_SCORE_MULTIPLIER = 1.25`
- Water reward score uses: `WATER_REWARD_SCORE_USES = 3`
- Forest reward fuel ratio: `FOREST_REWARD_FUEL_RATIO = 0.25`
- Rock reward HP gain: `ROCK_REWARD_HP_GAIN = 1`
- Asteroid radius: `ASTEROID_RADIUS = 14.0`
- Asteroid damage: `ASTEROID_DAMAGE = 1`
- Asteroid drift speed: `ASTEROID_DRIFT_SPEED = 0.05`
- Crossing rocket radius: `CROSSING_ROCKET_RADIUS = 8.0`
- Crossing rocket speed: `CROSSING_ROCKET_SPEED = 2.2`
- Crossing rocket damage: `CROSSING_ROCKET_DAMAGE = 1`
- Crossing rocket warning: `CROSSING_ROCKET_WARNING_FRAMES = 45`
- Supply item radius: `SUPPLY_ITEM_RADIUS = 9.0`
- Supply item score: `SUPPLY_ITEM_SCORE = 75`
- Supply item fuel ratio: `SUPPLY_ITEM_FUEL_RATIO = 0.15`
- Resident sprite size: `RESIDENT_SPRITE_SIZE = 32`
- Cut-in resident scale: `CUTIN_RESIDENT_SCALE = 3`
- Cut-in resident draw size: `CUTIN_RESIDENT_DRAW_SIZE = 96`
- Cut-in duration: `CUTIN_DURATION_FRAMES = 72`
- Cut-in panel size: `CUTIN_PANEL_WIDTH = 300`, `CUTIN_PANEL_HEIGHT = 120`
- Cut-in slide frames: `CUTIN_SLIDE_IN_FRAMES = 12`, `CUTIN_SLIDE_OUT_FRAMES = 10`
- Cut-in vertical range: `CUTIN_MIN_Y_RATIO = 0.10`, `CUTIN_MAX_Y_RATIO = 0.24`
- Text scales: `HUD_TEXT_SCALE = 3`, `WORLD_LABEL_SCALE = 2`, `ORBIT_COUNT_LABEL_SCALE = 4`
- Future crew resident scale: `CREW_RESIDENT_SCALE = 1`
- Future crew highlight scale: `CREW_HIGHLIGHT_SCALE = 2`
- Supply lap interval: `SUPPLY_LAP_INTERVAL = 3`
- Supply ship delay approximation: `SUPPLY_SHIP_DELAY_GAPS_MIN = 2`, `SUPPLY_SHIP_DELAY_GAPS_MAX = 3`
- Crew join sequence: `CREW_JOIN_SEQUENCE = (1, 2, 4, 8, 16, 32, 64)`
- Max supply tiers per type: `MAX_SUPPLY_TIERS_PER_TYPE = 7`
- Max supply ship chances per type: `MAX_SUPPLY_SHIP_CHANCES_PER_TYPE = 7`
- Supply cargo reward: `SUPPLY_SHIP_CARGO_SCORE = 100`, `SUPPLY_SHIP_CARGO_FUEL_RATIO = 0.15`
- Supply ship movement: `SUPPLY_SHIP_SPEED = 1.15`, `SUPPLY_SHIP_RADIUS = 18.0`, `SUPPLY_CARGO_RADIUS = 10.0`
- Supply ship warning: `SUPPLY_SHIP_WARNING_FRAMES = 60`
- Supply ship station frames: `SUPPLY_SHIP_STATION_FRAMES = 180`

## Planet Course

GRC008 replaces the earlier fixed type sequence with a deterministic finite course:

- `COURSE_SEED = 12345`
- 35 normal planets total.
- Wind, Iron, Water, Forest, and Rock each appear exactly 7 times.
- The first shuffle-bag constraints prevent 3 same-type planets in a row and ensure the first 5 include Forest or Rock.
- Planets progress upward in world space from `COURSE_START_Y`.
- X positions use deterministic lanes clamped between `PLANET_X_MIN` and `PLANET_X_MAX`.
- Gap metadata is generated between every adjacent planet pair.

Planet type reward roles remain:
- Wind: stronger gravity multiplier after lap 2.
- Iron: shield gain after lap 2.
- Water: future score bonus uses after lap 2.
- Forest: fuel recovery after lap 2.
- Rock: HP recovery after lap 2.

Difficulty helpers:

```text
difficulty = 1.0 + progress * 0.75
```

This is intentionally simple. GRC008 creates hooks and deterministic course structure; deeper tuning remains future work.

## Demo Mode

Press `M` to toggle demo mode. The autopilot now catches each nearby planet, circles for roughly `2.4` turns, and every third planet waits for `3.0` turns before pushing away toward the next planet. This is intentionally more "orbit hop" than pure fly-by so the intended game image is visible, including lap 3+ effects.

## Orbit Assist

Inside a planet gravity well, orbit assist gently blends the rocket velocity toward a tangential orbit at a readable radius. This is a gameplay helper, not a strict orbital simulation. The goal is for the player to feel the rocket get caught, circle, and then transfer to the next planet.

## Lap Completion And Transfer Boost

GRC005A separates lap completion from Transfer Boost.

Lap completion:
- The active planet visit tracks signed wrapped angular progress around the planet.
- `LAP_COMPLETION_RADIANS = math.tau * 0.90` counts a readable near-complete arcade orbit as a lap.
- Lap completion happens inside the gravity well and immediately triggers score, cheer, cut-in, and lap 2 reward logic.
- Back-and-forth jitter should not count because the accumulated angle is signed.

Transfer Boost:
- After at least one completed lap in the current visit, the game shows `TRANSFER READY`.
- Leaving that gravity well triggers `TRANSFER BOOST!` once for the visit.
- The next-destination alignment helper is still used to draw a destination line when a good target exists, but it no longer gates the player-facing Transfer Boost feedback.

## Damage Model

GRC004 replaces instant planet collision crash with a minimal HP/shield model:
- Shield absorbs collision damage before HP.
- HP is reduced only when shield is 0.
- The rocket bounces away from the planet after damage.
- Damage cooldown prevents repeated immediate damage while overlapping a planet.
- HP reaching 0 causes crash/game over.

GRC006 reuses the same shield/HP damage helper for floating asteroids and crossing rockets. Damage cooldown also prevents repeated immediate obstacle damage while overlapping an interplanet object.

This likely makes early play more forgiving and remains a tuning target after GRC008.

## Interplanet Objects

GRC006 adds a deterministic first pass of interplanet objects:

- Floating asteroids are static or slowly drifting hazards placed in planet gaps.
- Crossing rockets have a warning countdown before moving horizontally across the route.
- Normal supply items are collectible score/fuel rewards and do not add crew.

Initial normal supply reward:

```text
score +75
fuel +15% max fuel, clamped to max
```

These placements are now derived from course gaps where practical, while preserving a small deterministic early layout for readability. Final goal and result screen remain future tasks.

## Supply Ships And Crew

GRC007 adds the first supply ship and crew growth layer:

- Lap milestones at `SUPPLY_LAP_INTERVAL = 3` reserve supply ships for the source planet type.
- Reservations do not spawn immediately.
- Reservations count Transfer Boost exits as the deterministic 2-3 gap delay approximation.
- Odd reservation IDs use the 2-gap delay; even reservation IDs use the 3-gap delay.
- Ready reservations now place stationary supply ships in the current/next SUPPLY ZONE.
- Waiting supply ships are arranged horizontally by planet type and remain available until collected.
- The supply ship itself is treated as an opportunity/cargo source in this implementation, not as a damaging hazard.
- Supply cargo adds `+100` score, restores 15% max fuel, and joins crew for the ship's planet type.
- Crew success tiers advance only on successful cargo collection.
- Ordinary SUPPLY ZONE waiting ships are no longer consumed by a miss.
- Normal GRC006 supply items remain score/fuel pickups only.
- The in-run crew UI shows compact total/type counts and representative joined types instead of drawing hundreds of crew during play.

GRC008 adds course gap metadata. Supply ship reservations now mark future gaps when possible, and ready reservations are synchronized into the current/next visible supply zone so DEMO and normal play can reliably collect queued supply opportunities.

## Meteor Swarms

GRC008 adds crossing meteor swarms:

- Meteor swarms are distinct from floating asteroids.
- Each swarm has a warning phase before meteors move.
- A swarm contains multiple small meteors crossing the selected gap.
- Meteors use the same shield/HP damage path as other hazards.
- Swarm placement is deterministic by gap index.
- Current tuning starts meteor swarms at `METEOR_SWARM_GAP_START_INDEX = 6` and repeats every `METEOR_SWARM_EVERY_N_GAPS = 5`.

Tune after manual playtesting:
- warning readability
- meteor count
- meteor speed
- gap spacing around swarm sections
- whether Iron/Rock/Forest rewards are strong enough before swarm-heavy sections

## Cut-in Presentation

GRC005A places the shared resident cut-in panel around the middle of the `393x852` screen, sliding in from the side opposite the assisting planet. This keeps the lower screen clear for fuel, controls, and future crew UI. It uses a `96x96` portrait centered in the left area before the divider and text for resident name, assist message, lap/score, cheer line, and reward text.

If `assets/gravity_courier.pyxres` exists and loads, the portrait path uses `32x32` resident sprites at 3x scale. If the resource is missing or loading/rendering fails, the panel uses primitive fallback portraits.

Tune after manual playtesting:
- Panel position relative to future crew UI.
- Whether the existing top assist text should be shortened when the cut-in panel is active.
- Duration of `72` frames.
- Fallback portrait readability.

## Mobile Controls

GRC010 should implement touch controls through a shared `ControlIntent` model rather than direct gameplay mutations from gestures.

Confirmed mobile direction:

- Trajectory preview is always visible during gameplay.
- Horizontal drag controls continuous high-sensitivity rotation.
- Rotation response should be clamped to avoid sudden uncontrollable reversal.
- High-speed turn assist should raise touch turn sensitivity by about `1.3x` to `1.5x` at maximum.
- Upward swipe creates a short gentle forward-thrust pulse.
- Downward swipe creates a short gentle brake or reverse-thrust pulse.
- Vertical swipes should not apply large one-frame velocity impulses.
- Swipe detection should use screen-space coordinates and should not depend on camera zoom.
- Tap remains unused in core flight for now.

Provisional constants:

```text
BASE_TOUCH_TURN_SENSITIVITY = 0.0045
HIGH_SPEED_TURN_ASSIST = 0.45
TOUCH_THRUST_PULSE_FRAMES = 18
TOUCH_THRUST_PULSE_STRENGTH = 0.35
TOUCH_BRAKE_PULSE_FRAMES = 18
TOUCH_BRAKE_PULSE_STRENGTH = 0.25
TRAJECTORY_PREVIEW_ALWAYS_ON = True
```

If always-on trajectory dots become too dense at high speed, increase dot interval slightly with speed or reduce sample density while preserving the same approximate prediction time window.

## Post-GRC009 Tuning Targets

GRC009P defines the polishing roadmap after the first final-goal/result implementation.

Mode tuning:

- Normal mode starts at 20 planets, 4 appearances per normal planet type.
- Hard mode preserves the current 35 planets, 7 appearances per normal planet type.
- Normal and Hard share the same crew sequence and reward rules.
- Hard may use higher hazard, meteor, crossing rocket, and rank thresholds.

Navigation tuning:

- Off-course helper should target the next expected course planet.
- Initial thresholds are `OFF_COURSE_DISTANCE_THRESHOLD = 600.0`, `OFF_COURSE_STALL_FRAMES = 180`, and `OFF_COURSE_MARGIN = 24`.
- The helper should guide without altering physics.

Orbit presentation tuning:

- Orbit focus starts after about 15% current-lap progress.
- Zoom should stay restrained, with a safe maximum around `1.12`.
- Cut-ins reduce effective focus strength so resident text remains readable.
- Concentration lines are deterministic and subdued.

Asset tuning:

- Minimum resident/Hero sprite plan is 23 sprites.
- Rocket minimum sprite plan is idle, thrust, and damage.
- Primitive fallbacks stay mandatory after `.pyxres` integration.

Result testing:

- `GOAL TEST` should be DEBUG/DEMO-only.
- Crew presets are `12`, `50`, `51`, `200`, `201`, and `635`.

## Future Tuning Targets

- Make intentional player input feel more important than the no-input path.
- Keep the first near-miss readable on `393x852`.
- Avoid planet wells visually overwhelming the trajectory preview.
- Tune crash radius, fuel cost, and assist reward after manual Pyxel playtesting.
- Keep lower screen space clean for future touch controls.
