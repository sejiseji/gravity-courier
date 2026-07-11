# Interplanet Objects Spec

Interplanet space should eventually contain objects that make travel between planets active, readable, and score-relevant. The design must remain lightweight and `393x852` portrait-first.

## Crossing Rocket

Role:
- Moving obstacle.

Behavior:
- Enters from screen edge.
- Crosses the interplanet path in a mostly straight line.
- Challenges timing and reaction.
- GRC006 first implementation uses deterministic crossing rocket lanes with a warning timer before the rocket becomes dangerous.

Gameplay purpose:
- Makes empty travel space more active.
- Forces the player to watch timing, not only trajectory.

## Floating Asteroid

Role:
- Static or slowly drifting obstacle.

Behavior:
- Placed in interplanet space.
- Blocks simple paths.
- Encourages route planning.
- GRC006 first implementation uses a small deterministic set of static or slowly drifting asteroids.
- Collision uses shield before HP and respects damage cooldown.

Gameplay purpose:
- Crossing rockets test timing.
- Asteroids test positioning.

## Supply Item

Role:
- Collectible reward.

Reward:
- Score.
- Boost/fuel recovery.
- No crew in GRC006.

Gameplay purpose:
- Creates risk/reward choices between planets.

GRC006 first implementation:
- Normal supply items grant `+75` score.
- Normal supply items restore 15% max fuel.
- They disappear after collection and cannot be collected repeatedly.
- They are distinct from GRC007 supply ship cargo, which can add crew.

## Supply Ship

Role:
- Special moving opportunity after the player reaches high excitement/lap state.

Activation:
- Completing lap 3 around a planet reserves a supply ship for that planet type.
- Additional 3-lap milestones on the same planet, such as lap 6 and lap 9, can reserve additional ships.
- The ship should not appear immediately. It should spawn in a gap 2 or 3 planets later.

Behavior:
- Crosses the screen.
- May release supply cargo.
- Cargo can be collected for rewards.

Rewards:
- Score.
- Boost parameter recovery.
- Crew addition.

Important:
- The supply ship itself may later be dangerous to collide with, but first implementation can treat it as an event/cargo source.
- The cargo is the main collectible reward.
- Missing the cargo consumes that spawn event but does not advance the crew success tier.

## Crossing Meteor Swarm

Role:
- Dangerous moving hazard section for durability, avoidance, and route choice.

Behavior:
- A group of meteor objects crosses the screen in a predictable direction.
- The swarm should have warning feedback and avoidable gaps.
- It should be distinct from a single floating asteroid.

Gameplay purpose:
- Makes Iron, Rock, and Forest strategically meaningful before dangerous sections.
- Tests HP/shield, propulsion recovery, and route planning.

Implementation boundary:
- Do not implement crossing meteor swarms in GRC006.
- GRC008 implements the first deterministic crossing meteor swarm system.

GRC008 first implementation:
- Selected course gaps have crossing meteor swarms.
- A warning appears before meteors become dangerous.
- Each swarm contains multiple small moving meteors.
- Meteors use shield/HP damage rules.
- Patterns are deterministic by gap index.
- Swarms are meant to reinforce HP/shield value without becoming unavoidable walls.

## Implementation Boundaries

GRC006 implements basic floating asteroids, crossing rockets, normal supply items, collision/collection logic, and scoring/recovery rewards.

GRC007 should implement supply ship reservations, delayed supply ship spawns, supply cargo collection rewards, crew addition, and lower-corner representative crew display.

GRC007 first implementation does this with a Transfer Boost delay approximation: each Transfer Boost exit counts as one future planet gap. Supply ship cargo adds crew, but normal GRC006 supply items remain score/fuel only.

GRC008 adds real course gap metadata. Supply ship reservations now mark a future gap when one exists, and spawned ships use that gap center for placement. Transfer Boost exits still drive the countdown timing for now.

See `SUPPLY_CREW_GOAL_RESULT_SPEC.md` for the full supply ship, crew growth, final goal, and result-screen plan.
