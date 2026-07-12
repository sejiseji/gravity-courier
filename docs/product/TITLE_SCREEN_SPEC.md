# Title Screen Spec

## Purpose

Gravity Courier needs a small start screen once final goal/result flow and course modes exist.

The title screen should introduce the journey, allow mode selection, and expose DEMO without becoming a full tutorial.

## Game States

Introduce or formalize:

```python
STATE_TITLE = "title"
STATE_PLAYING = "playing"
STATE_CRASHED = "crashed"
STATE_RESULT = "result"
```

Existing crash/lost handling may be adapted into this state model when the title screen is implemented.

## Minimum Title Screen

Display:

```text
GRAVITY COURIER
START
MODE: NORMAL
DEMO
```

Optional small description:

```text
ORBIT. GATHER. RETURN.
```

## Mode Selection

Available modes:

```text
NORMAL - 20 PLANETS
HARD   - 35 PLANETS
```

Touch:

- Tap mode selector.
- Tap START.
- Tap DEMO.

Keyboard:

- Left/Right: change mode.
- Z or Enter: start.
- M: toggle DEMO.

## Mobile Communication

Show concise controls:

```text
DRAG: TURN
SWIPE UP/DOWN: SPEED
TRAJECTORY: ALWAYS ON
```

Do not overload the title screen with a full tutorial.

## Start Behavior

Starting a run should:

- Generate course for selected mode.
- Reset score/crew/rewards/objects.
- Preserve mode selection.
- Enter playing state.
- Start gameplay BGM if sound is enabled.

## DEMO Behavior

The existing DEMO button and M key remain valid.

Title-screen DEMO entry should use the same underlying demo-mode state.

Avoid duplicate demo implementations.

## Dependencies

If course modes are not implemented yet, GRC009F must precede the final title-screen mode selector.

## Non-Goals

- Do not add a large tutorial.
- Do not implement settings menus in the first title-screen pass.
- Do not add iOS wrapper behavior here.

## Implemented Notes

GRC010A adds the first title-screen pass:

- `STATE_TITLE` is used when launching through `run()`.
- `GravityCourierApp()` still builds a playable state for existing unit tests and internal helpers.
- Title buttons cover START, MODE, DEMO, and SOUND.
- Left/Right changes the selected mode without rebuilding the active course until START/DEMO.
- Z, Enter, and START begin the selected course.
- M and DEMO begin a demo run using the same underlying demo mode as gameplay.
- S and SOUND toggle audio state.
- Title screen uses layered BGM with low accompaniment and high music-box harmony.
- Re-enabling sound on the title screen resumes title audio, not gameplay BGM.
