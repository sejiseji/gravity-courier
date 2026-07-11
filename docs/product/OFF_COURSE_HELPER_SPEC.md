# Off-Course Helper Spec

## Purpose

When the rocket travels far away from the intended course, show a helper that points toward the next meaningful planet.

The helper should guide the player back to the route without controlling the rocket.

## Target Selection

Do not point to the geometrically nearest planet without course context.

Preferred target:

```text
the next uncompleted or next expected planet in course order
```

Suggested state:

```python
next_course_planet_index
```

Fallback behavior:

- If no explicit next index exists, select the nearest future planet by course index.
- Never select a completed planet behind the player unless no future planet exists.
- If the final goal is the next target, point to the final goal instead of a planet.

## Activation Conditions

The helper should normally be hidden.

Show it when one or more conditions are met:

- Target planet is outside the visible screen.
- Rocket distance from the expected route exceeds a threshold.
- Rocket has not reduced distance to the next planet for a configured duration.
- Rocket is moving strongly away from the next planet.

Suggested provisional constants:

```python
OFF_COURSE_DISTANCE_THRESHOLD = 600.0
OFF_COURSE_STALL_FRAMES = 180
OFF_COURSE_MARGIN = 24
```

Exact values remain tuning targets.

## Display

Show:

- Screen-edge arrow.
- `NEXT`.
- Optional distance value.

Example:

```text
NEXT 840
<arrow>
```

The indicator should sit inside a safe screen margin.

Use the vector from screen center to the target planet and intersect it with the screen-safe rectangle.

Suggested helper:

```python
def edge_indicator_position(
    target_screen_x: float,
    target_screen_y: float,
    width: int,
    height: int,
    margin: int,
) -> tuple[int, int]:
    ...
```

## Placement Restrictions

- Do not cover the top-right DEMO button.
- Do not cover HP/shield/assist HUD.
- Do not cover the top-left score/speed HUD.
- Do not cover side cut-ins.
- Stay within the `393x852` safe screen area.

## Gameplay Restrictions

- Helper does not alter physics.
- Helper does not consume fuel.
- Helper does not teleport the rocket.
- Helper should disappear once the player returns near the route.
- Helper should remain compatible with camera zoom.

## Debugging

Debug HUD may show:

- Current next course planet index.
- Off-course active true/false.
- Distance to target.
- Stall frame count.
- Current helper target type: planet or final goal.
