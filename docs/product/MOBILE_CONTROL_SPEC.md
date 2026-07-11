# Mobile Control Spec

## Purpose

GRC010 should make Gravity Courier feel natural on a `393x852` portrait touch screen.

The target feel is not button pressing. The player should feel like they are guiding the rocket path with a finger while the trajectory preview stays visible as core play information.

## Fixed Direction

- Trajectory preview is always enabled during gameplay.
- Do not expose an in-game touch toggle for trajectory preview.
- Horizontal touch drag controls continuous rocket rotation.
- Horizontal sensitivity should be relatively high so the rocket can enter orbit even at high speed.
- Maximum angular response must be clamped so the rocket cannot suddenly reverse uncontrollably.
- Upward swipe triggers gentle forward acceleration over a short duration.
- Downward swipe triggers gentle braking or reverse thrust over a short duration.
- Vertical swipe input must not apply a large instantaneous velocity impulse.
- Touch input should be converted into a shared `ControlIntent` model.
- Keyboard controls must remain supported.
- Swipe detection uses screen-space coordinates and must not depend on camera zoom.

## Touch Mapping

| Input | Effect |
| --- | --- |
| Horizontal drag | High-sensitivity continuous rotation |
| Up swipe | Gentle forward thrust pulse |
| Down swipe | Gentle braking / reverse-thrust pulse |
| Trajectory preview | Always visible |
| Tap | Reserved for future pause, cut-in advance, or special action |

## Horizontal Drag Steering

Horizontal drag should build angular velocity instead of instantly overwriting the rocket angle.

Suggested model:

```python
rotate_input = drag_dx / width
angular_velocity += rotate_input * effective_turn_sensitivity
angular_velocity = clamp(
    angular_velocity,
    -max_turn_rate,
    max_turn_rate,
)
```

This keeps a small amount of rocket-like inertia while making touch steering responsive.

Directly applying `angle += drag_dx * sensitivity` is acceptable only as an early prototype shortcut. The preferred GRC010 direction is a clamped angular-velocity model.

## High-Speed Turn Assist

As speed rises, turning should not become so weak that orbit entry becomes impractical.

Suggested model:

```python
speed_ratio = min(rocket.speed / HIGH_SPEED_REFERENCE, 1.0)
effective_turn_sensitivity = (
    BASE_TOUCH_TURN_SENSITIVITY
    * (1.0 + speed_ratio * HIGH_SPEED_TURN_ASSIST)
)
```

Provisional tuning:

- `BASE_TOUCH_TURN_SENSITIVITY = 0.0045`
- `HIGH_SPEED_TURN_ASSIST = 0.45`

This gives at most about `1.45x` steering assistance at high speed. Keep the maximum assist in the `1.3x` to `1.5x` range unless playtesting proves a stronger value is needed.

## Vertical Swipe Pulses

Up and down swipes should create short-lived thrust states rather than instant speed changes.

Suggested data:

```python
@dataclass
class ThrustPulse:
    remaining_frames: int = 0
    strength: float = 0.0
```

Suggested first values:

- Up swipe: `remaining_frames = 18`, `strength = 0.35`
- Down swipe: `remaining_frames = 18`, `strength = 0.25`

Each frame:

```python
if thrust_pulse.remaining_frames > 0:
    rocket.apply_thrust(thrust_pulse.strength)
    thrust_pulse.remaining_frames -= 1
```

Down swipe should use the same idea for braking or reverse thrust. It should feel like a smooth correction, not a one-frame impulse.

## Trajectory Preview

Trajectory preview is basic play information for Gravity Courier.

Mobile gameplay should treat it as always-on:

```python
TRAJECTORY_PREVIEW_ALWAYS_ON = True
```

Do not require a tap or button to reveal it during play. Avoid an in-game toggle because it creates ambiguity between tap, swipe, and accidental preview state changes.

Future settings may adjust preview density or length, but moment-to-moment gameplay should not ask the player to manage preview visibility.

## Preview Density Tuning

If the preview is always visible, high speed can make dots visually crowded.

Suggested model:

```python
dot_interval = int(
    clamp(
        BASE_DOT_INTERVAL + rocket.speed * 0.5,
        4,
        10,
    )
)
```

Alternative:

- Keep the predicted time window roughly stable.
- Reduce sample density as speed rises.

The goal is for the preview to remain readable at high speed without becoming a solid noisy line.

## ControlIntent Model

GRC010 should avoid wiring touch input directly into gameplay logic.

Minimum future implementation:

```python
@dataclass
class ControlIntent:
    rotate: float = 0.0
    thrust: float = 0.0
    brake: float = 0.0
```

Recommended shared model:

```python
@dataclass
class ControlIntent:
    rotate_axis: float = 0.0
    thrust_axis: float = 0.0
    brake_axis: float = 0.0
    thrust_pulse: float = 0.0
    brake_pulse: float = 0.0
    debug_toggle_requested: bool = False
    restart_requested: bool = False
```

Keyboard and touch should both produce `ControlIntent`.

This keeps desktop controls testable and lets the future iPhone wrapper use the same gameplay control path.

## Implementation Notes

Keyboard adapter:

- Left/Right produce `rotate`.
- Up produces `thrust`.
- Down produces `brake`.
- Existing debug/restart/demo shortcuts may remain separate or become explicit intent flags.

Touch adapter:

- Horizontal drag produces responsive `rotate`.
- Rotation uses mild high-speed turn assist.
- Maximum angular response is clamped.
- Upward swipe produces a short-duration gentle acceleration pulse.
- Downward swipe produces a short-duration gentle braking or reverse-thrust pulse.
- Vertical swipe input must not apply a large instantaneous velocity impulse.

Trajectory:

- Mobile trajectory preview remains always on.
- Do not expose an in-game trajectory toggle on mobile.
- Desktop debug compatibility may remain, but Normal mobile controls should not require it.

Coordinates:

- Gesture recognition must use screen-space coordinates.
- Camera zoom must not change swipe interpretation.

## Non-Goals For GRC010

- Do not add an iOS wrapper.
- Do not add gesture-dependent trajectory preview toggling.
- Do not remove keyboard support.
- Do not require camera zoom to detect swipes.
- Do not add a new special action unless a later task explicitly defines one.
