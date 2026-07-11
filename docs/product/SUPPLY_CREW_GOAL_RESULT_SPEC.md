# Supply Crew Goal Result Spec

This spec defines the medium-term supply ship, crew growth, final goal, and result-screen direction for Gravity Courier. The fixed target remains `iphone16_large`, `393x852`, portrait-first.

## 0. Purpose

Gravity Courier should become more than a game about traveling farther with swing-bys. The intended arc is:

```text
orbit a planet
complete laps and earn score
complete lap 3 to call a supply ship
collect supply cargo
gain crew
carry the growing crew toward the final goal
reach an Earth-like destination
show a result screen where the crew celebrates
```

The provisional final goal is an Earth-like destination. On arrival, the result screen should evaluate:

- final score
- run score
- crew bonus
- crew count
- remaining HP
- remaining propulsion gauge
- successful lap count
- collected supply ships or cargo
- rank

## 1. Planet Types And Maximum Appearances

Normal course planet types:

| Planet type | Role |
| --- | --- |
| Wind | Acceleration, high risk, high reward |
| Iron | Shield and defensive capacity |
| Water | Score multiplier |
| Forest | Propulsion gauge recovery |
| Rock | HP recovery, repair, warmth |
| Black Hole | Special advanced route, optional normal crew exclusion |

The five normal crew-bearing planet types should each appear at most 7 times in a full finite course:

```text
Wind   max 7
Iron   max 7
Water  max 7
Forest max 7
Rock   max 7
```

With 5 normal types, the maximum normal planet count is:

```text
5 types * 7 = 35 planets
```

This cap controls run length, bounds crew growth, and keeps the final course finite.

## 2. Planet Course Generation

Use a shuffle bag rather than unconstrained random selection.

Example bag:

```python
planet_type_bag = [
    "wind", "wind", "wind", "wind", "wind", "wind", "wind",
    "iron", "iron", "iron", "iron", "iron", "iron", "iron",
    "water", "water", "water", "water", "water", "water", "water",
    "forest", "forest", "forest", "forest", "forest", "forest", "forest",
    "rock", "rock", "rock", "rock", "rock", "rock", "rock",
]
```

Shuffle the bag and place planets in that order.

Recommended constraints:

- Do not place the same planet type 3 times in a row.
- Include at least one Forest or Rock planet early.
- Avoid an early course with no recovery route.
- Keep at least one Iron or Rock planet for the late course.
- Avoid clustering too many Water planets at the start.

Future course generation should accept a debug seed:

```python
course_seed = 12345
```

The same seed should produce the same course so balance issues can be reproduced.

Future mode split:

- Normal mode: 20 planets, 4 appearances per normal planet type.
- Hard mode: 35 planets, 7 appearances per normal planet type.
- Both modes keep the same reward, supply, crew, final goal, and result-screen rules.

## 3. Supply Ship Spawn Condition

A supply ship is reserved when the player completes 3 laps around a planet.

```text
complete lap 3 on a planet
reserve a supply ship for that planet type
ready the ship in a gap 2 or 3 planets later
keep it waiting in SUPPLY ZONE lanes until collected
```

Example:

```text
complete lap 3 on a Rock Planet
reserve Rock Supply Ship
ready Rock Supply Ship 2 or 3 planet gaps later
show Rock Supply Ship in SUPPLY ZONE until collected
```

Do not make the supply ship available immediately after lap 3. Delayed readiness avoids crowding the orbit area, creates anticipation, and gives interplanet travel a clear purpose.

The supply ship should appear in a slightly wider planet gap when possible. Once ready, it should remain available in the current or next SUPPLY ZONE until its cargo is collected.

First visual behavior:

- Enters from offscreen.
- Crosses the screen horizontally.
- Acts as an event source and cargo dropper.
- Ship collision damage is not required in the first supply-ship implementation.

## 4. Supply Ship Repeat Rule

The same planet can reserve supply ships at 3-lap milestones:

```text
lap 3 -> reserve supply ship
lap 6 -> reserve supply ship
lap 9 -> reserve supply ship
```

This should not continue forever. Each planet type has at most 7 supply-ship chances, matching the crew growth sequence.

Initial implementation rule:

- Cap supply ship spawn chances per planet type at 7.
- After 7 chances, do not spawn more supply ships for that type.
- Alternatively, later versions may allow non-crew reward ships after tier 7, but the first implementation should keep the cap simple.

## 5. Waiting Supply Ships

Ready supply ships wait in SUPPLY ZONE instead of crossing once and disappearing.

- Each ready reservation produces one waiting supply ship.
- Waiting ships are arranged horizontally by planet type.
- If multiple ready ships share a planet type, they may stack vertically within that type lane.
- The reservation remains `spawned` until the cargo is collected.
- Collecting cargo changes the reservation to `collected` and advances that planet type's crew success tier.

Example:

```text
Wind, Rock, and Rock reservations are ready
SUPPLY ZONE shows one Wind ship and two Rock ships
player collects Wind cargo
two Rock ships continue waiting in later SUPPLY ZONE passes
```

This makes earned crew opportunities reliable in DEMO and normal play while still requiring the player to fly through the supply zone to collect cargo.

## 6. Supply Ship Reservation Data

Suggested data shape:

```python
@dataclass
class SupplyShipReservation:
    reservation_id: int
    planet_type: str
    source_planet_id: int
    source_lap_count: int
    target_gap_index: int
    status: str  # "reserved", "spawned", "collected", "missed"
```

Fields:

- `source_lap_count`: the lap milestone that called the ship, such as `3`, `6`, or `9`.
- `target_gap_index`: the future planet gap where the ship should appear, generally `current_planet_index + 2` or `current_planet_index + 3`.
- `status`: reservation lifecycle state.

Reservation statuses:

| Status | Meaning |
| --- | --- |
| `reserved` | Scheduled but not yet spawned |
| `spawned` | Ready and waiting in SUPPLY ZONE |
| `collected` | Cargo was collected |
| `missed` | Legacy/moving event opportunity was missed |

## 7. Supply Cargo

Collecting supply cargo should grant:

- score
- propulsion gauge recovery
- crew for the corresponding planet type
- one success tier for that planet type

Provisional constants:

```python
SUPPLY_CARGO_SCORE = 100
SUPPLY_CARGO_FUEL_RATIO = 0.15
```

Cargo behavior:

```text
score += 100
fuel += max_fuel * 0.15
clamp fuel to max fuel
```

Difference from normal supply items:

| Object | Reward |
| --- | --- |
| Normal supply item | Score and propulsion recovery only; implemented in GRC006 |
| Supply ship cargo | Score, propulsion recovery, and crew join |

Normal supply items should not add crew.

## 8. Crew Growth Sequence

Crew joins grow by planet type, based on successful supply cargo collections.

```python
CREW_JOIN_SEQUENCE = [1, 2, 4, 8, 16, 32, 64]
```

Join table:

| Success count for planet type | Join count |
| --- | --- |
| 1 | 1 |
| 2 | 2 |
| 3 | 4 |
| 4 | 8 |
| 5 | 16 |
| 6 | 32 |
| 7 | 64 |

Implementation should use the tier before increment:

```python
tier = supply_success_tier_by_type[planet_type]
join_count = CREW_JOIN_SEQUENCE[tier]

crew_count_by_type[planet_type] += join_count
supply_success_tier_by_type[planet_type] += 1
```

Tier cap:

```text
tier 0 -> 1 crew
tier 1 -> 2 crew
tier 2 -> 4 crew
tier 3 -> 8 crew
tier 4 -> 16 crew
tier 5 -> 32 crew
tier 6 -> 64 crew
tier 7 -> no more crew joins
```

## 9. Maximum Crew Count

Maximum joined crew per normal planet type:

```text
1 + 2 + 4 + 8 + 16 + 32 + 64 = 127
```

Maximum joined crew for five normal types:

```text
127 * 5 = 635
```

The protagonist crew member exists from the start:

```python
joined_crew_count = sum(crew_count_by_type.values())
total_crew_count = 1 + joined_crew_count
```

For scoring, use joined crew only at first:

```python
crew_bonus = joined_crew_count * CREW_SCORE_VALUE
```

For result display, include the protagonist:

```python
display_crew_count = 1 + joined_crew_count
```

## 10. Crew State Data

Suggested dictionaries:

```python
crew_count_by_type = {
    "wind": 0,
    "iron": 0,
    "water": 0,
    "forest": 0,
    "rock": 0,
}

supply_success_tier_by_type = {
    "wind": 0,
    "iron": 0,
    "water": 0,
    "forest": 0,
    "rock": 0,
}

supply_ship_spawn_count_by_type = {
    "wind": 0,
    "iron": 0,
    "water": 0,
    "forest": 0,
    "rock": 0,
}
```

Caps:

```python
MAX_SUPPLY_TIERS_PER_TYPE = 7
MAX_PLANET_APPEARANCES_PER_TYPE = 7
```

## 11. In-Run Crew UI

Do not draw every crew member during gameplay. The max of 635 joined crew is too high for normal play UI.

Use representative crew plus a count:

```text
[Hero][Wind][Iron][Water][Forest][Rock] +128
```

Display principles:

- Lower-left or lower-right screen area.
- Keep central play action clear.
- Show Hero plus one representative per joined planet type.
- Show `+N` for overflow.
- Reuse the resident registry and `32x32` sprite source.

GRC005A moved cut-ins to mid-screen side panels, which preserves the lower screen for future crew UI.

## 12. Journey Progress UI

Because Gravity Courier is becoming a finite journey, the player should always understand how far they are from the goal.

GRC009 should add a compact journey progress display during gameplay.

Suggested display:

```text
GOAL
####------
PLANET 12/35
```

Purpose:

- Show that the course has a finite end.
- Make the player feel "almost there" near the final section.
- Reduce uncertainty about how long the run continues.
- Support final-goal tension before the result screen.

Required first implementation:

- Show current course progress as `PLANET current/35`.
- Show a compact progress bar toward the final goal.
- Keep it readable at `393x852`.
- Do not cover the top-left score/speed HUD.
- Do not cover the top-right demo button or HP/shield/assist HUD.
- Do not cover side cut-ins.

Recommended placement:

- Near the upper-right HUD area if it can fit cleanly.
- Otherwise near the upper middle, below the top HUD.
- Keep it compact; this is navigational context, not a large modal.

Progress definition:

- `total_planets = 35` for the first full course.
- `current_planet_index` can be the nearest upcoming planet, last reached planet, or current course progress marker.
- Prefer a stable, monotonic progress value so the display does not flicker while the rocket moves around one planet.
- First implementation may use the highest reached planet index based on course order.

Supply hint extension:

If a supply ship reservation has targeted a future gap, the progress display may show a small hint:

```text
NEXT SUPPLY
```

or:

```text
SUPPLY NEXT GAP
```

This hint should remain small. It should create anticipation without turning the progress UI into a route map.

Do not implement in GRC009:

- Full minimap.
- Full route map UI.
- Detailed list of every future planet.
- Supply ship management screen.

## 13. Final Goal

Add a final goal to make the game a finite journey. The provisional theme is an Earth-like destination.

Flow:

```text
travel through planets
collect crew
survive hazards
reach Earth-like goal
show result screen
```

Initial full-course placement:

```text
35 normal planets
final goal section
Earth-like goal
```

Short demo builds may place a temporary goal after planet 10 to 15.

Goal arrival:

```python
distance(rocket.position, goal.position) <= goal.radius
```

On arrival, transition to result screen.

## 14. Final Score

Basic formula:

```python
final_score = run_score + crew_bonus + survival_bonus
```

First implementation may use:

```python
final_score = run_score + crew_bonus
```

Crew bonus:

```python
CREW_SCORE_VALUE = 100
crew_bonus = joined_crew_count * CREW_SCORE_VALUE
```

Maximum normal crew bonus:

```text
635 * 100 = 63500
```

The protagonist is not included in crew bonus because they are present from the start.

## 15. Result Evaluation

Display:

- `FINAL SCORE`
- `RUN SCORE`
- `CREW BONUS`
- `CREW COUNT`
- `LAPS`
- `SUPPLY SHIPS COLLECTED`
- `HP LEFT`
- `FUEL LEFT`
- `RANK`

Initial rank can use simple score thresholds:

```text
S
A
B
C
D
```

Future rank inputs may include crew count, arrival time, HP left, fuel left, and supply collection rate.

## 16. Result Crew Display

The result screen should draw as much of the crew as possible.

Density stages:

| Joined crew count | Display style |
| --- | --- |
| 1-50 | Draw as many `32x32` characters as possible |
| 51-200 | Use denser or `16x16`-style display |
| 201+ | Use `8x8` crowd display and type-based rows |

For large groups, separate rows by planet type:

```text
Wind crew row
Iron crew row
Water crew row
Forest crew row
Rock crew row
```

This shows which planet routes contributed most to the crew.

## 17. Result Crew Jump Animation

The result crew should not stand still. They should jump with staggered timing.

Suggested phase:

```python
jump_phase = (frame_count + crew_index * 7) % JUMP_CYCLE
phase_offset = crew_index * 7 + type_index * 13
```

Suggested vertical motion:

```python
jump_y = -abs(math.sin(phase)) * jump_height
```

A triangle wave is also acceptable and cheaper to compute.

Avoid synchronized jumping. Staggering is required so the result screen feels like a lively crowd.

## 18. HP And Shield Meaning

With a final goal, HP and shield become finite-journey resources:

```text
HP / SHIELD = safety margin to reach the goal
```

The defensive planet roles remain distinct:

| Planet | Role |
| --- | --- |
| Iron | Prevent damage with shield, armor, defensive capacity |
| Rock | Restore lost HP |
| Forest | Restore propulsion gauge for avoidance and re-acceleration |

## 19. Crossing Meteor Swarms

Crossing meteor swarms are a future hazard, distinct from floating asteroids.

| Hazard | Role |
| --- | --- |
| Floating asteroid | Static or slow obstacle for route planning |
| Crossing rocket | Moving obstacle for timing |
| Crossing meteor swarm | Dangerous section testing durability, avoidance, and route choice |

Recommended placement:

- after supply zones
- before the final goal
- on high-score routes
- in sections that make Iron, Rock, and Forest valuable

Design principles:

- warning indicator
- avoidable gaps
- predictable travel direction
- HP/shield model prevents unfair instant loss

## 20. Full Game Flow

```text
start run
approach planet
complete planet laps
score and cut-in each lap
lap 2 triggers planet reward
lap 3 reserves supply ship
Transfer Boost away from planet
2-3 planet gaps later, supply ship waits in SUPPLY ZONE
collect cargo
gain score, propulsion recovery, and crew
crew join count doubles by type success tier
cross obstacles and meteor swarms
watch journey progress approach GOAL
reach final goal
calculate final score and crew count
show result screen
crew jumps and celebrates
```

## 21. Roadmap Reflection

### GRC006

Implement interplanet objects:

- floating asteroids
- crossing rockets
- normal supply items

Do not implement:

- supply ships
- crew growth
- final goal
- result screen
- crossing meteor swarms

### GRC007

Implement supply ships and crew growth:

- reserve supply ships on lap 3 milestones
- ready ships 2 or 3 planet gaps later
- keep ready ships waiting in SUPPLY ZONE until collected
- collect supply cargo
- add planet-type crew
- use `[1, 2, 4, 8, 16, 32, 64]`
- add representative in-run crew UI

GRC007 first implementation:
- Lap 3 and later multiples of 3 reserve supply ships for the source planet type.
- The 2-3 planet-gap delay is approximated by counting Transfer Boost exits.
- Odd reservation IDs use a 2-gap delay and even reservation IDs use a 3-gap delay.
- Ready supply ships wait in SUPPLY ZONE lanes by planet type and carry collectible cargo.
- The ship itself is not a damaging hazard in the first implementation.
- Cargo grants `+100` score, restores 15% max fuel, and joins planet-type crew.
- Normal supply items still do not add crew.
- Waiting cargo remains available until collected and does not advance the crew success tier until collection.
- In-run crew UI is compact and does not render every joined crew member.

### GRC008

Implement or tune course generation and hazard pacing:

- max 7 appearances per normal planet type
- shuffle-bag course generation
- wider supply-ship gaps
- crossing meteor swarms
- durability and recovery balance

GRC008 first implementation:
- Generates a seeded finite course with 35 normal planets.
- Each normal planet type appears exactly 7 times.
- Prevents 3 same-type planets in a row.
- Ensures the first 5 planets include Forest or Rock.
- Adds gap metadata between adjacent planets.
- Marks supply ship target gaps when reservations are created.
- Adds warning-based crossing meteor swarms to selected gaps.
- Adds deterministic difficulty helper functions.
- Does not add the final Earth-like goal or result screen.

### GRC009

Implement final goal and result screen:

- Earth-like goal
- Journey Progress UI with `PLANET current/35` and a compact goal progress bar
- Optional small `NEXT SUPPLY` or `SUPPLY NEXT GAP` hint when supply gap data is available
- goal arrival detection
- final score
- crew bonus
- result screen
- crowd crew rendering
- staggered jump celebration
- rank display

GRC009 first implementation:

- Final goal is separate from normal planets.
- Final goal does not apply gravity, lap counts, planet rewards, or supply-ship source behavior.
- Result state is separate from crash/lost state.
- Final score uses `run_score + crew_bonus`.
- Crew bonus uses joined crew only.
- Result crew display switches density by crew count.

### GRC009A

Add developer result-screen test helper:

- DEBUG/DEMO-only `GOAL TEST` button
- crew presets `12`, `50`, `51`, `200`, `201`, `635`
- safe pre-goal placement
- normal goal collision into result state

## 22. Fixed Decisions

1. Normal mode uses 4 appearances per normal planet type.
2. Hard mode uses 7 appearances per normal planet type.
3. Planet order should use shuffle-bag generation.
4. Supply ships are reserved by completing lap 3 milestones.
5. Supply ships become ready later, not immediately.
6. Supply ships become ready after a 2 or 3 gap delay and then wait in SUPPLY ZONE.
7. Supply ships match the source planet type.
8. Waiting supply cargo does not advance the crew success tier until collected.
9. A waiting supply event is not consumed by ordinary misses.
10. Crew join counts use `[1, 2, 4, 8, 16, 32, 64]`.
11. Maximum joined crew per normal planet type is 127.
12. Maximum joined crew across the five normal planet types is 635.
13. In-run crew UI shows representative crew plus a count, not every crew member.
14. Result screen should draw the crew count as actual visible crew or crowd marks.
15. Large crews use smaller, denser crowd rendering.
16. Result crew members jump with staggered timing.
17. The game should have a final Earth-like goal.
18. Final evaluation should include score and crew count.
19. HP and shield are resources for surviving to the final goal.
20. Crossing meteor swarms should later reinforce HP/shield value.
21. GRC009 should include a compact Journey Progress UI because the finite course needs visible distance-to-goal feedback.
22. Journey Progress should show course progress such as `PLANET 12/35` and a compact bar toward `GOAL`.
23. Journey Progress may show small supply anticipation hints, but it should not become a full route map.

## 23. Tunable Values

These values are provisional and should be tuned through playtesting:

```python
SUPPLY_CARGO_SCORE = 100
SUPPLY_CARGO_FUEL_RATIO = 0.15
CREW_SCORE_VALUE = 100
SUPPLY_SHIP_GAP_OFFSET = 2 or 3
NORMAL_PLANET_APPEARANCES_PER_TYPE = 4
HARD_PLANET_APPEARANCES_PER_TYPE = 7
MAX_SUPPLY_TIERS_PER_TYPE = 7
```

`CREW_SCORE_VALUE` especially should be balanced against normal lap scoring so both swing-by skill and crew collection matter.
