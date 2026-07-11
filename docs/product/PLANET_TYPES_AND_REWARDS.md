# Planet Types And Rewards

Every planet type should offer a meaningful benefit when used well. Avoid creating planets that feel only like obstacles.

The fixed layout target remains `393x852` portrait-first. Planet visuals and reward feedback must stay readable in a narrow vertical playfield.

## Reward Activation Rule

A planet's special reward activates after 2 successful swing-bys around that same planet.

Reason:
- 1 success is too automatic.
- 3 successes may slow down game progression too much.
- 2 successes creates a clear "one more lap for the bonus" decision.

Recommended decision structure:

```text
lap 1: score and cheer
lap 2: score, stronger cheer, and planet reward
lap 3+: score scaling and high-risk routing
```

GRC004/GRC005A implementation rule:
- Rewards trigger once per planet per run.
- Rewards are claimed from the same lap completion flow that increments lap count.
- Lap 1 does not trigger the planet reward.
- Lap 2 triggers the planet reward if it has not already been claimed.
- Lap 3+ does not retrigger the same planet's reward.

## Wind Planet

Theme:
- Wind.
- Clouds.
- Birds.
- Flowing cloth.
- Air currents.

Reward:
- After 2 successful swing-bys, swing-by acceleration effect becomes stronger.

GRC004 implementation:
- Set that planet's `gravity_multiplier` to `1.25`.
- The multiplier affects normal gravity acceleration.
- Trajectory preview uses the same planet objects, so the preview stays consistent with boosted gravity.
- Feedback text: `WIND BOOST!`.

Gameplay role:
- High acceleration.
- High speed.
- Exciting but risky.

## Iron Planet

Theme:
- Metal.
- Robots.
- Machinery.
- Rivets.
- Industrial residents.

Reward:
- After 2 successful swing-bys around the Iron Planet, rocket defensive capacity is improved.

GRC004 implementation:
- Gain 1 shield point.
- Clamp to max shield.
- Feedback text: `SHIELD +1`.

Gameplay role:
- Defensive route.
- Good before obstacle-heavy sections.
- Prevention/armor/shield route.

## Water Planet

Theme:
- Ocean.
- Jellyfish-like residents.
- Bubbles.
- Flowing water.

Reward:
- After 2 successful swing-bys, score gain receives a bonus multiplier.

GRC004 implementation:
- Grant 3 future assist score bonus uses.
- While uses remain, assist scoring uses `planet_bonus_multiplier = 1.25`.
- Uses decrement when an assist score is awarded.
- The lap 2 assist that grants the Water reward is not retroactively multiplied.
- Feedback text: `SCORE BONUS x1.25`.

Gameplay role:
- High-score route.
- Strategic scoring setup.

## Forest Planet

Theme:
- Trees.
- Leaves.
- Spores.
- Spirits.
- Small forest creatures.

Reward:
- After 2 successful swing-bys around the Forest Planet, recover the propulsion gauge.

First implementation:
- If the current code uses `fuel`, treat `fuel` as the propulsion/boost gauge for now.
- Recover 25% of max gauge.
- Clamp recovery to the maximum gauge value.
- Feedback text: `FUEL +25%`.

Gameplay role:
- Recovery route.
- Extends the run.
- Lets the player attempt more risky swing-by chains.
- Good for extending runs.

## Rock Planet

Theme:
- Stone.
- Minerals.
- Cave residents.
- Sturdy rock-like characters.

Reward:
- After 2 successful swing-bys around the Rock Planet, recover rocket HP.

GRC004 implementation:
- Recover 1 HP.
- Clamp recovery to max HP.
- Feedback text: `HP +1`.

Character note:
- The rock resident may be loosely inspired by friendly rock-like sci-fi companion characters, but must be original.
- Do not directly copy named characters, designs, dialogue, or protected expression from existing works.

Gameplay role:
- Healing route.
- Helps recover from mistakes.
- Feels reliable, protective, and warm.

## Iron / Rock Distinction

- Iron Planet improves defensive capacity.
- Rock Planet restores lost health.
- Iron = prevention / armor / shield.
- Rock = healing / repair / recovery.

Do not mix these roles in later implementation. Iron should make the rocket harder to break; Rock should help the rocket recover after it has already been hurt.

## Black Hole / Strong Gravity Object

Theme:
- Dark gravity well.
- Lensing.
- Dangerous high-energy route.

Reward:
- Extremely strong acceleration and high score potential.

Risk:
- Too close means crash/loss.
- It should feel high-risk high-reward.
- It may not have normal residents or crew.

Gameplay role:
- Advanced route.
- Score/speed spike.

## GRC004 Implementation Boundary

GRC004 adds initial planet type definitions, simple visual distinctions, and the 2-lap reward activation rule for normal planet types. It does not add full resident art, supply ships, crew, interplanet obstacles, or advanced procedural generation.
