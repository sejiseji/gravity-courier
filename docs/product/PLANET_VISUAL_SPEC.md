# Planet Visual Spec

## Purpose

Replace simple filled-circle planets with richer type-specific procedural visuals.

Do not require image assets. Planet rendering should stay lightweight and readable in the `393x852` portrait layout.

## Shared Layers

Every planet renderer should support:

- Outer silhouette.
- Base fill.
- Surface pattern.
- Atmosphere or outer accents.
- Optional particles.
- Gravity-well outline.
- Type label and lap display.

Suggested architecture:

```python
def draw_planet_base(...): ...
def draw_planet_surface(...): ...
def draw_planet_atmosphere(...): ...
def draw_planet_particles(...): ...
```

Type dispatch:

```python
PLANET_RENDERERS = {
    "wind": draw_wind_planet,
    "iron": draw_iron_planet,
    "water": draw_water_planet,
    "forest": draw_forest_planet,
    "rock": draw_rock_planet,
}
```

## Wind Planet

Visual elements:

- Curved cloud bands.
- Moving flow lines.
- Small wind particles.
- Subtle rotating atmospheric marks.

Gameplay readability:

- Preserve the visible gravity well.
- Do not make flow lines look like trajectory dots.

## Iron Planet

Visual elements:

- Panel seams.
- Rivets.
- Metallic bands.
- Small light points.
- Industrial segmented appearance.

Gameplay readability:

- Keep labels legible against metallic colors.
- Avoid overly dense seams at small radius.

## Water Planet

Visual elements:

- Wave bands.
- Bubbles.
- Bright atmosphere ring.
- Animated highlight or flowing surface stripes.

Gameplay readability:

- Keep bubbles visually distinct from supply items.
- Avoid bright rings that hide lap labels.

## Forest Planet

Visual elements:

- Green land-like clusters.
- Treetop dots.
- Leaf/spore particles.
- Small sprout-like outer details.

Gameplay readability:

- Keep particles sparse.
- Do not let spores resemble hazards.

## Rock Planet

Visual elements:

- Craters.
- Cracks.
- Irregular outer details.
- Tiny orbiting fragments.

Gameplay readability:

- Orbiting fragments are visual only.
- Visual fragments must not imply extra collision unless gameplay adds that explicitly.

## Performance Constraints

- No per-frame expensive procedural noise generation.
- Use deterministic precomputed pattern offsets where possible.
- Keep particle counts small.
- Visual animation should not alter collision radius.
- Trajectory and orbit readability remain more important than decoration.

## Non-Goals

- Do not require external image assets.
- Do not replace resident sprites.
- Do not alter planet reward behavior.
- Do not change collision radius based on decorative shapes.

## Implementation Status

GRC009D implements this as lightweight procedural drawing in `app.py`.

- Planet drawing is split into base, surface, atmosphere, and sparse particle layers.
- `PLANET_RENDERERS` dispatches Wind, Iron, Water, Forest, Rock, and Black Hole to type-specific renderers.
- Animation uses deterministic frame phases and planet indices rather than random per-frame noise.
- Collision radius, gravity wells, rewards, labels, and lap display remain unchanged.
