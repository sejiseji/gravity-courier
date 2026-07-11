# Score And Lap Spec

This spec defines the first score-driven form of Gravity Courier. The design target is a readable `393x852` portrait Pyxel arcade game, not strict orbital simulation.

## Core Score Loop

1. Rocket enters a planet gravity well.
2. Rocket circles around the planet while staying inside that gravity well.
3. Signed angular progress reaches the lap completion threshold.
4. Lap completion increments that planet's local lap count.
5. Lap completion adds score, cheer feedback, and a resident cut-in.
6. Lap 2 activates that planet's special reward once.
7. After one or more completed laps in the current visit, leaving the gravity well triggers Transfer Boost.

## Lap Count Definition

Use "lap count" as the number of completed angular laps around the same planet. GRC005A changed the implementation so lap count no longer waits for gravity-well exit.

Recommended first implementation:
- First completed orbit lap on a planet: lap 1.
- Second completed orbit lap on the same planet: lap 2.
- Third and later completed orbit laps: lap 3+.

Display rules:
- Show the current lap count large on or near the planet.
- Use `3+` for lap count 3 and beyond if display space is limited.
- Internally keep the exact count for score calculation.

The lap display should be legible at `393x852` and should not cover the rocket, core trajectory preview, or central play action.

GRC005A implementation:
- Track the active orbit planet while the rocket is inside a gravity well.
- Accumulate signed wrapped angular delta from the planet center to the rocket.
- Do not sum absolute angle delta, because back-and-forth jitter should not create laps.
- `LAP_COMPLETION_RADIANS = math.tau * 0.90` for the first arcade-tuned implementation.
- Completed laps can occur without leaving the gravity well.
- Transfer Boost is an exit event after at least one completed lap in the current visit.

## Score Formula

Use this provisional formula:

```text
base_assist_score = 100
score_gain = base_assist_score * lap_multiplier * planet_bonus_multiplier
```

Suggested provisional lap multiplier:

| Lap | Multiplier |
| --- | --- |
| 1 | x1.0 |
| 2 | x1.5 |
| 3 | x2.0 |
| 4+ | x2.0 + 0.25 * (lap - 3) |

This formula is provisional and should be tuned after playtesting. Keep the function simple enough to explain through the HUD, lap display, and feedback text.

GRC004 water bonus behavior:
- Water Planet grants 3 future assist score bonus uses when its lap 2 reward activates.
- While water bonus uses remain, `planet_bonus_multiplier = 1.25`.
- The water bonus applies starting with future assist scoring events; it does not retroactively modify the same lap 2 assist that granted the reward.
- Score gain uses the existing rounded scoring helper. Example: lap 2 with x1.25 is `round(100 * 1.5 * 1.25) = 188`.

## Risk And Reward

- More laps give more score.
- More laps make the rocket faster.
- Faster movement makes the next escape, next planet approach, and obstacle avoidance harder.
- The player should feel tempted to attempt one more lap, but not forced.

The intended decision is:

```text
lap 1: success, score, and a clear invitation to try one more
lap 2: stronger scoring and planet reward activation
lap 3+: high-score/high-risk territory
```

## Implementation Boundaries

GRC003 should implement score, lap count, lap display, score HUD, and simple 3-stage cheer text feedback. It should not implement planet-type rewards, full cut-ins, crew, supply ships, or procedural generation.

GRC004 implements planet-type rewards and HP/shield damage. It should not implement full cut-ins, crew, supply ships, interplanet obstacles, or procedural generation.

GRC005A fixes the lap event flow and Transfer Boost clarity. It does not add interplanet obstacles, supply ships, crew UI, procedural generation, or final art.
