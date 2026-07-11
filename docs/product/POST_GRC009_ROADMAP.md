# Post-GRC009 Roadmap

## Purpose

This roadmap defines the recommended polish and implementation order after GRC009 makes Gravity Courier completable with a final goal and result screen.

## GRC009: Implement Final Goal And Result Screen

Scope:

- Earth-like final goal.
- Goal reach state.
- Final score.
- Crew bonus.
- Rank.
- Result screen.
- Crew density modes.
- Staggered celebration.

## GRC009A: Add Result-Screen Test Helper

Scope:

- Bottom-right `GOAL TEST` button.
- DEBUG/DEMO-only visibility.
- Crew presets: `12`, `50`, `51`, `200`, `201`, `635`.
- Score/resource test state.
- Teleport to safe pre-goal position.
- Normal result transition verification.

## GRC009F: Add Normal And Hard Course Modes

Status: implemented.

Scope:

- Normal: 20 planets, 4 per type.
- Hard: 35 planets, 7 per type.
- Shared rules.
- Mode-specific difficulty/rank tuning.
- Selected mode carried into result summary.

Normal is currently the default course. `N` toggles Normal/Hard until the title screen owns mode selection.

## GRC009B: Add Orbit Focus Presentation

Scope:

- Focus strength.
- Gradual camera zoom.
- Midpoint focus.
- Concentration lines.
- Cut-in attenuation.
- Transfer Boost release.

Do not add screen shake.

## GRC009C: Add Off-Course Recovery Helper

Scope:

- Next course planet selection.
- Off-course detection.
- Screen-edge arrow.
- Distance display.
- Safe HUD placement.

## GRC009D: Enrich Procedural Planet Visuals

Scope:

- Shared planet render architecture.
- Type-specific surface patterns.
- Lightweight atmospheric animation.
- Maintain collision/render separation.

## GRC009E: Integrate Resident And Rocket Sprite Assets

Scope:

- `.pyxres` resource integration.
- 23-sprite minimum resident/Hero atlas.
- 3-state rocket minimum.
- Primitive fallback retained.
- Atlas documentation and validation.

This task may wait until the developer has created the sprites in Pyxel Editor.

## GRC010: Implement Mobile Touch Controls

Scope:

- `ControlIntent`.
- Keyboard adapter.
- Touch adapter.
- Horizontal drag steering.
- High-speed turn assist.
- Vertical acceleration/braking swipes.
- Trajectory always on for mobile.
- Touch debug overlay if needed.

## GRC010A: Implement Title Screen And Mode Selection

Scope:

- Title state.
- START.
- Normal/Hard selection.
- DEMO.
- Concise control guidance.
- Touch and keyboard navigation.

If course modes are not yet implemented, GRC009F must precede this task.

## GRC011: Polish And Release-Candidate Prototype

Scope:

- Manual playtest tuning.
- UI hierarchy.
- Final feedback polish.
- Route duration tuning.
- Sound plan or implementation.
- Retry flow.
- Release/debug feature separation.
- Public prototype readiness.

## Recommended Dependency Order

```text
GRC009
  final goal/result
      ↓
GRC009A
  result test helper
      ↓
GRC009F
  Normal/Hard modes
      ↓
GRC009B
  orbit focus presentation
      ↓
GRC009C
  off-course helper
      ↓
GRC009D
  planet visuals
      ↓
GRC009E
  sprite integration when assets are ready
      ↓
GRC010
  mobile touch controls
      ↓
GRC010A
  title screen/mode selection
      ↓
GRC011
  polish/release candidate
```

GRC009E may move later if sprite assets are not ready.
