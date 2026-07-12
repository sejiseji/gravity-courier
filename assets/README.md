# Gravity Courier Assets

Reserved Pyxel resource path:

```text
prototypes/gravity_courier/assets/gravity_courier.pyxres
```

`gravity_courier.pyxres` now contains the first completed Hero sprite and the first
idle sprites for the five normal residents.

Resident and future crew sprites should use `32x32` cells in image bank 0:

- row 0, `v=0`: Hero
- row 1, `v=32`: Wind resident
- row 2, `v=64`: Iron resident
- row 3, `v=96`: Water resident
- row 4, `v=128`: Forest resident
- row 5, `v=160`: Rock resident

Current authored column:

- `u=0`: idle

Future resident expression columns:

- `u=32`: cheer stage 1
- `u=64`: cheer stage 2
- `u=96`: cheer stage 3

Hero currently uses only `(u=0, v=0, 32x32)` and reuses that sprite for all Hero appearances.
Residents currently use each row's `(u=0, 32x32)` cell for all cheer stages until
dedicated cheer-stage cells are authored.
The transparent color key is palette index `14`.

The game must keep working without this resource file by using primitive fallback portraits.
Loading the resource enables Hero and the five initial resident sprites.
