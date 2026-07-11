# Orbit Focus Presentation Spec

## Implementation Status

Implemented in GRC009B.

- Orbit focus starts after meaningful orbit progress, then grows with current lap progress and completed laps.
- World camera zoom is capped at `1.12`.
- HUD, buttons, cut-ins, and input hit testing remain screen-space and unzoomed.
- Camera follow target blends slightly toward the rocket/planet midpoint.
- Concentration lines are deterministic screen-space lines.
- Resident cut-ins attenuate focus strength.
- Transfer Boost releases focus smoothly.
- Screen shake remains intentionally out of scope.

## Purpose

Active orbiting should feel tense and visually focused.

During a swing-by orbit:

- Subtle concentration lines appear.
- Camera gradually zooms in.
- Camera focus shifts slightly toward the rocket/planet interaction.
- The effect grows with orbit progress and lap count.

This is presentation only. It must not change the Lap Completed or Transfer Boost event model.

## Activation

Do not activate merely on gravity-well entry.

Suggested start:

```text
orbit tracker active
and current-lap angular progress >= 15%
```

Suggested constant:

```python
ORBIT_FOCUS_START_PROGRESS = 0.15
```

## Focus Strength

Suggested formula:

```python
lap_progress_component = current_lap_progress * 0.7
lap_count_component = min(planet_lap_count * 0.15, 0.45)
focus_strength = clamp(
    lap_progress_component + lap_count_component,
    0.0,
    1.0,
)
```

The exact formula may be tuned.

## Camera Zoom

Use restrained zoom to avoid motion sickness.

Suggested zoom by lap stage:

| Lap stage | Maximum zoom |
| --- | --- |
| lap 1 | around 1.06 |
| lap 2 | around 1.09 |
| lap 3+ | around 1.12 |

Never exceed the configured safe maximum without explicit playtest approval.

Suggested constants:

```python
ORBIT_FOCUS_MAX_ZOOM = 1.12
ORBIT_FOCUS_ZOOM_LERP = 0.05
ORBIT_FOCUS_RELEASE_LERP = 0.06
```

World-space objects should use the zoomed world-to-screen transform.

HUD, cut-ins, buttons, and touch coordinates remain screen-space and unzoomed.

## Focus Target

Preferred camera focus target:

```python
focus_target = midpoint(rocket.position, active_planet.position)
```

Blend from the normal camera target toward the focus target.

Suggested maximum blend:

```python
ORBIT_FOCUS_POSITION_BLEND = 0.35
```

## Concentration Lines

Draw screen-space lines from selected screen edges toward the focus center.

Requirements:

- Use fixed or deterministic angles.
- Do not regenerate completely random lines every frame.
- Lines stop before reaching the rocket/planet center.
- Line count increases with focus strength.
- Use 8 to 16 lines at most initially.
- Use a subdued color.
- No flashing or full-screen blinking.

## Cut-in Interaction

When resident cut-in is active:

```python
effective_focus_strength *= 0.45
```

This keeps the cut-in readable.

## Transfer Boost Exit

On Transfer Boost:

- Release orbit zoom smoothly.
- Optionally apply a tiny temporary zoom-out around `0.96`.
- Return to `1.0`.

Do not introduce screen shake in this task.

## Non-Goals

- Do not change orbit physics.
- Do not change lap counting thresholds.
- Do not add screen shake.
- Do not zoom screen-space HUD or touch coordinates.
