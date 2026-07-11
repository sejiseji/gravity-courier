# Physics Model

Gravity Courier plans to use a lightweight, readable 2D physics model:

- 2D position and velocity.
- Per-planet gravity acceleration.
- Softening to avoid singularities.
- Semi-implicit Euler integration.
- Substeps for stability when needed.
- Gameplay feel over physical realism.

Constants are intentionally not finalized in GRC000.
