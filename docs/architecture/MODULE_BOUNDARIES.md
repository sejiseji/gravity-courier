# Module Boundaries

```text
constants.py
  screen size, tuning constants, colors, profile name

entities.py
  Vec2, Rocket, Planet, simple data structures

physics.py
  gravity acceleration, integration helpers

trajectory.py
  future trajectory simulation without mutating real rocket

scoring.py
  gravity assist detection and score-related pure logic

camera.py
  camera state and world/screen transform

app.py
  Pyxel app loop, input, update, draw

main.py
  small launcher only
```
