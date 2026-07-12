# Sprite Asset Plan

## Purpose

Gravity Courier should eventually replace primitive resident and rocket visuals with Pyxel resource-backed sprites while keeping primitive fallback support.

Do not create a fake `.pyxres` file. The real resource file should be authored in Pyxel Editor by the developer.
The first real Hero sprite and five initial resident idle sprites are now in the reserved resource.

Reserved resource:

```text
prototypes/gravity_courier/assets/gravity_courier.pyxres
```

Primitive fallback remains mandatory.

Current completed assets:

| Asset | Image bank | u | v | Size | Transparent color |
| --- | ---: | ---: | ---: | --- | ---: |
| Hero idle | 0 | 0 | 0 | `32x32` | 14 |
| Wind idle | 0 | 0 | 32 | `32x32` | 14 |
| Iron idle | 0 | 0 | 64 | `32x32` | 14 |
| Water idle | 0 | 0 | 96 | `32x32` | 14 |
| Forest idle | 0 | 0 | 128 | `32x32` | 14 |
| Rock idle | 0 | 0 | 160 | `32x32` | 14 |

Hero cheer/result temporarily fall back to the idle-style primitive until dedicated cells are authored.
Resident cheer stages are not marked ready yet; they fall back to primitive portraits until dedicated
cheer-stage cells are authored.

## Resident Sprite Standard

Resident and crew characters use:

| Field | Value |
| --- | --- |
| Source size | `32x32` |
| Format | Pyxel Editor `.pyxres` |
| Cut-in display | 3x, `96x96` |
| Gameplay crew UI | 1x |
| Newly joined/highlighted crew | 2x |

## Required Resident Sprites

Five normal resident types:

- Wind
- Iron
- Water
- Forest
- Rock

Required states per resident:

- idle
- cheer stage 1
- cheer stage 2
- cheer stage 3

Total:

```text
5 residents x 4 states = 20 sprites
```

## Hero Sprites

Minimum Hero set:

- hero idle
- hero cheer
- hero result / celebration

Total Hero sprites:

```text
3
```

## Initial Asset Count

Minimum planned total:

```text
20 resident sprites + 3 Hero sprites = 23 sprites
```

Optional future join-expression state:

```text
5 residents x 5 states + 3 Hero states = 28 sprites
```

Do not require the optional set initially.

## Atlas Proposal

Use `32x32` cells.

Rows:

| Row | Character |
| --- | --- |
| 0 | Hero |
| 1 | Wind |
| 2 | Iron |
| 3 | Water |
| 4 | Forest |
| 5 | Rock |

Columns:

| Column | Resident state |
| --- | --- |
| 0 | idle |
| 1 | cheer 1 |
| 2 | cheer 2 |
| 3 | cheer 3 |

Hero row:

| Column | Hero state |
| --- | --- |
| 0 | idle |
| 1 | cheer, fallback until authored |
| 2 | result, fallback until authored |
| 3 | reserved |

## Current Readiness Matrix

`load_resident_resources()` loads the `.pyxres` once, but individual sprites are activated through
per-state readiness so unfinished cells do not silently appear as finished art.

Hero:

| State | Status |
| --- | --- |
| idle | ready |
| cheer | fallback until authored |
| result | fallback until authored |

Residents:

| Type | idle | cheer1 | cheer2 | cheer3 |
| --- | --- | --- | --- | --- |
| Wind | ready | fallback | fallback | fallback |
| Iron | ready | fallback | fallback | fallback |
| Water | ready | fallback | fallback | fallback |
| Forest | ready | fallback | fallback | fallback |
| Rock | ready | fallback | fallback | fallback |

## Rocket Sprite Plan

Rocket source sprite:

```text
32x32
```

Minimum states:

- rocket idle
- rocket thrust
- rocket damage

Shield should remain a primitive overlay instead of requiring a separate full sprite.

Preferred initial rotation solution:

```text
one source orientation rendered with rotation
```

Fallback if rotation support proves unsuitable:

```text
8 directions x idle/thrust = 16 sprites
```

Do not adopt the 16-sprite fallback unless necessary.

## Display Sizes

| Use | Source | Scale | Display |
| --- | --- | --- | --- |
| Resident cut-in | `32x32` | 3x | `96x96` |
| Gameplay crew UI | `32x32` | 1x | `32x32` |
| Crew join highlight | `32x32` | 2x | `64x64` |
| Rocket gameplay | `32x32` | 1x | `32x32` |

## Validation Direction

Future sprite integration should validate:

- `.pyxres` exists before loading.
- Missing resource falls back to primitives.
- Atlas coordinates match resident registry.
- Rocket fallback remains available if sprite loading fails.
