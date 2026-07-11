# Game Mode Spec

## Purpose

Gravity Courier should support two primary play modes after the first final-goal implementation:

- Normal mode for shorter spare-time runs.
- Hard mode for the longer score-attack route.

Both modes preserve the same core game loop: orbit, score, planet rewards, supply ships, crew growth, hazards, final goal, and result evaluation.

## Normal Mode

Normal mode is the standard first-play experience.

Purpose:

- Designed for short spare-time play sessions.
- Reaches the final goal sooner.
- Still exposes the full core loop.
- Keeps the journey readable on `393x852`.

Initial specification:

| Field | Value |
| --- | --- |
| Mode ID | `normal` |
| Planet count | 20 |
| Planet appearances per normal type | 4 |
| Normal planet types | Wind, Iron, Water, Forest, Rock |
| Expected distribution | 5 types x 4 = 20 planets |

Recommended initial difficulty:

- Hazard multiplier: `1.0`
- Meteor frequency: standard
- Crossing rocket frequency: standard
- Rank thresholds: normal thresholds

Normal mode should use the same crew join sequence as all other modes:

```python
CREW_JOIN_SEQUENCE = (1, 2, 4, 8, 16, 32, 64)
```

Do not create a separate simplified crew sequence for Normal mode initially. Higher crew tiers may remain rare and should reward aggressive repeated-lap play.

## Hard Mode

Hard mode preserves the current 35-planet structure.

Purpose:

- Longer score-attack route.
- Intended for experienced players.
- Keeps the current full-length course as a challenge mode.

Initial specification:

| Field | Value |
| --- | --- |
| Mode ID | `hard` |
| Planet count | 35 |
| Planet appearances per normal type | 7 |
| Normal planet types | Wind, Iron, Water, Forest, Rock |
| Expected distribution | 5 types x 7 = 35 planets |

Recommended initial difficulty:

- Hazard multiplier: `1.25`
- Meteor frequency: increased
- Crossing rocket frequency: increased
- Rank thresholds: higher than Normal

## Shared Rules

Normal and Hard should share:

- Planet reward rules.
- Crew join sequence.
- Lap milestones.
- Supply ship behavior.
- Control model.
- Result-screen structure.
- Final goal rules.

Avoid mode-specific rule fragmentation unless playtesting proves it is necessary.

## Course Generation

The course generator should accept a mode configuration.

Suggested model:

```python
@dataclass(frozen=True)
class GameModeConfig:
    mode_id: str
    planet_appearances_per_type: int
    hazard_multiplier: float
    meteor_frequency_multiplier: float
    rank_thresholds: tuple[int, int, int, int]
```

Suggested constants:

```python
NORMAL_PLANET_APPEARANCES_PER_TYPE = 4
HARD_PLANET_APPEARANCES_PER_TYPE = 7
```

Both modes should remain seeded and deterministic when using the same mode and seed.

## Result Summary

The selected mode should appear in the result summary.

Examples:

```text
MODE NORMAL
MODE HARD
```

Rank thresholds may differ by mode, but the result-screen structure should stay the same.

## Non-Goals

- Do not add separate planet reward formulas per mode unless playtesting requires it.
- Do not simplify the crew sequence for Normal mode.
- Do not remove Hard mode's 35-planet route.
- Do not make mode generation non-deterministic.
