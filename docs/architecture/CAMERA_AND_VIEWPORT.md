# Camera And Viewport

The camera should follow the rocket smoothly while keeping the future path visible.

- Camera follows rocket smoothly.
- Rocket is anchored below center.
- Upper screen space is reserved for upcoming trajectory and planets.

Target anchor:

```python
CAMERA_ANCHOR_X = WIDTH * 0.5
CAMERA_ANCHOR_Y = HEIGHT * 0.72
```
