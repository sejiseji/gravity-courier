# Result Test Helper Spec

## Purpose

Provide a developer-only shortcut for testing final-goal entry and result-screen crew-density modes.

This tool should make it easy to verify result layouts without manually playing a full run.

## Button

Add a bottom-right development button.

Suggested label:

```text
GOAL TEST
```

Display condition:

```text
DEMO ON or DEBUG ON
```

Do not show during normal release gameplay.

## Activation

Click/touch hit detection should use pure screen-space rectangle helpers.

Keyboard fallback may also be added if useful.

## Test Behavior

On activation:

1. Assign a result-test crew preset.
2. Assign test score.
3. Assign HP/shield/fuel test values.
4. Place the rocket shortly before the final goal.
5. Set a safe low forward velocity toward the goal.
6. Allow normal goal collision to trigger the result state.

Do not call the result screen directly if normal goal entry can be tested.

## Crew Presets

Use deterministic boundary-focused presets:

```python
RESULT_TEST_CREW_PRESETS = (
    12,
    50,
    51,
    200,
    201,
    635,
)
```

These values test:

- Normal display mode.
- Normal/dense boundary.
- Dense mode.
- Dense/crowd boundary.
- Crowd mode.
- Maximum planned crew count.

## Distribution By Type

Distribute preset crew deterministically among the five types.

Suggested method:

- Divide the preset count equally by type.
- Assign the remainder in stable type order: Wind, Iron, Water, Forest, Rock.

Do not use uncontrolled randomness for boundary testing.

An optional separate random mode may be added later.

## Safety

- Test run must not write high scores.
- Test state should be visibly marked as debug/demo.
- Restart returns to standard initial state.
- Feature should be easy to disable in release builds.

## Non-Goals

- Do not add release-facing cheats.
- Do not bypass goal collision if normal pre-goal placement can test it.
- Do not make result layout depend on random crew distributions.
