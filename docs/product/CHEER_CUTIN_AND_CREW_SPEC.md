# Cheer Cut-in And Crew Spec

Cheering, cut-ins, and crew growth should make successful swing-bys feel like visible events without crowding the `393x852` portrait playfield.

## Cheer Stages

Cheer reaction has 3 stages.

Stage 1:
- Normal cheers.
- Text examples: `WAA!`, `OOH!`, `YEAH!`.

Stage 2:
- Cheers plus clapping.
- Text examples: `CLAP! CLAP!`, `YEAH!!`.

Stage 3:
- Cheers plus clapping plus whistles.
- Text examples: `WOOO! WHISTLE!`, `WOOO!`, `CLAP!`.

Text note:
- Use explicit `WHISTLE!` wording instead of unclear whistle-sound text for the first implementation because it is easier to understand at a glance.

For Pyxel compatibility, prefer ASCII text in the first implementation. Avoid depending on emoji or custom fonts.

## Stage Mapping

Recommended mapping:

| Lap result | Cheer stage |
| --- | --- |
| lap 1 completed | stage 1 |
| lap 2 completed | stage 2 |
| lap 3+ completed | stage 3 |

After stage 3, reuse the same maximum cheer presentation. Only score numbers continue scaling with exact lap count.

## Cut-in System

All planets should use a shared cut-in framework.

Common behavior:
- Same slide/fade timing.
- Same screen position logic.
- Same duration.
- Same text layout.
- Same entry/exit animation.

Planet-specific data:
- Resident character ID.
- Resident sprite or primitive placeholder.
- Planet theme colors.
- Cheer text set.

GRC005 art direction:
- Resident and future crew characters should be designed as `32x32` Pyxel Editor sprites.
- Use the same `32x32` sprite source for cheer cut-in portraits, future lower-corner crew UI, and future crew join feedback.
- Current cut-in display scale is 3x, resulting in a `96x96` portrait centered in the left area before the divider.
- Keep the portrait inside that left area by using a small inset from the card edge.
- Future crew UI should use the same sprites at 1x for normal slots and possibly 2x for highlighted/newly joined crew.
- If the Pyxel resource file is not available yet, keep a primitive fallback renderer so tests and app startup remain robust.
- Do not add external image assets. A `.pyxres` file authored in Pyxel Editor is allowed for this prototype.

Reserved resource path:

```text
prototypes/gravity_courier/assets/gravity_courier.pyxres
```

First implementation should be resource-backed but fallback-safe. Primitive portraits are a fallback, not the preferred long-term representation.

Current sprite sheet layout in image bank 0:

| Row | v | Character | Columns |
| --- | --- | --- | --- |
| 0 | 0 | Hero | idle ready; cheer/result fallback until authored |
| 1 | 32 | Wind resident | idle ready; cheer stages fallback until authored |
| 2 | 64 | Iron resident | idle ready; cheer stages fallback until authored |
| 3 | 96 | Water resident | idle ready; cheer stages fallback until authored |
| 4 | 128 | Forest resident | idle ready; cheer stages fallback until authored |
| 5 | 160 | Rock resident | idle ready; cheer stages fallback until authored |

Column meaning:
- `u=0`: idle/normal.
- `u=32`: cheer stage 1.
- `u=64`: cheer stage 2.
- `u=96`: cheer stage 3.

Hero source is image bank 0, `(u=0, v=0)`, `32x32`, with palette color `14` as the transparent key. Resident rows use the same transparent key. Runtime readiness is tracked per Hero state and per resident stage, so unfinished cheer/result cells fall back to primitives instead of being treated as finished sprites.

Sprite metadata should live in a resident registry, for example `residents.py`, with:
- `image_bank`.
- `u`.
- `v`.
- `w=32`.
- `h=32`.
- `colkey=14`.
- resident ID.
- display name.
- planet type.
- stage sprite mapping.
- stage cheer line mapping.

Cut-ins should not obscure the rocket during a critical steering moment. GRC005A places cut-ins around the middle of the screen, sliding in from the side opposite the assisting planet. The lower screen is preserved for future crew UI, fuel, and controls.

Current cut-in composition for `393x852`:
- Panel width is `300` px and height is `120` px.
- Place a 3x `96x96` resident portrait centered on the left side of the panel, before the divider.
- Place resident name, `GRAVITY ASSIST!`, lap/score, cheer text, and reward text to the right.
- If the planet is on the left side of the screen, the panel slides in from the right.
- If the planet is on the right side of the screen, the panel slides in from the left.
- Stage 3 is reused for lap 3 and beyond.

## Crew System

The crew display should show the rocket becoming livelier over time.

Initial plan:
- The protagonist crew member is visible from the start.
- New crew members may be added through supply events.
- Crew members are displayed in lower-left or lower-right screen areas.
- The main play action remains near the center and upper screen, so lower corners can be used for crew UI.

Asset-sharing rule:
- Planet resident cut-in characters and crew display characters should use the same character registry.
- This reduces asset duplication.
- It also helps the player understand that a resident they saw earlier has joined the journey.
- The same `32x32` sprite should be used for both cut-ins and future crew UI.

First implementation:
- Crew can be cosmetic only.
- Later, crew may provide small passive bonuses.

Future crew UI limit:
- Show a maximum of roughly 5-6 crew members in the lower corner UI.
- If the roster grows beyond the visible slots, show a compact `+N` count rather than drawing every crew member.

## Resident Character Direction

Wind resident:
- Cloud-like face.
- Flowing hair or cloth.
- Extra wind lines at cheer stage 3.

Iron resident:
- Boxy robot face.
- Rivets and antenna.
- Mechanical clapping arm at cheer stage 2.
- Warning-light-like accent at cheer stage 3.

Water resident:
- Jellyfish-like round face.
- Tentacles and bubbles.
- More bubbles at cheer stage 3.

Forest resident:
- Leaf-like ears.
- Small sprout.
- Leaves at cheer stage 2.
- Flower detail at cheer stage 3.

Rock resident:
- Sturdy uneven body.
- Gentle eyes.
- Small warm mouth.
- Small raised hands at cheer stage 2.
- Rhythm lines or pebble-like accents at cheer stage 3.

Important:
- Rock resident should feel sturdy but kind.
- Keep all character designs original.
- Do not directly copy named characters, protected designs, dialogue, or protected expression from existing works.

## Implementation Boundaries

GRC003 may implement only simple 3-stage cheer text feedback.

GRC005 adds the resource-backed shared cut-in framework, resident registry, `32x32` sprite metadata, primitive fallback renderer, planet-specific resident IDs, visual stage effects, timing, and cooldowns.

GRC005A changes the cut-in trigger from gravity-well exit assist success to completed orbit laps. It also changes placement from lower screen to side slide-in around the middle of the screen.

GRC007 should add supply ship triggers, cargo collection, crew roster, and lower-corner crew UI.
