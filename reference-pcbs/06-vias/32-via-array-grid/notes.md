# 32 - Via Array Grid

## Purpose
3x3 grid of vias for ground stitching. Tests multiple via handling and array patterns.

## KiCAD Creation Steps
1. Open KiCAD PCB Editor
2. File → New Project
3. Draw board outline
4. Add vias in 3x3 grid pattern
5. Spacing: 15mm horizontal and vertical
6. All vias: 0.8mm size, 0.4mm drill
7. Net: GND
8. Save as `project.kicad_pcb`

## File Contents
- Board outline (100mm x 100mm)
- 9 through vias in 3x3 grid
- Spacing: 15mm x 15mm
- All vias: 0.8mm/0.4mm
- Net: GND
- Center at (100, 100)

## Key S-expression Elements
- `(via ...)` (x9)
- `(at x y)` positions in grid
- `(size 0.8)`
- `(drill 0.4)`
- `(layers "F.Cu" "B.Cu")`
- `(net 1)` (GND)

## Expected Parser Behavior
- Should parse all 9 vias
- Should preserve exact positions
- Should maintain grid pattern
- Should capture common properties

## Expected Formatter Behavior
- Should preserve via order
- Should maintain exact positions
- Should preserve all properties

## Round-Trip Requirements
- ✅ Should be byte-identical
- All via positions exact

## Manufacturing Notes
- **JLCPCB Compatible**: Yes
- **Purpose**: Ground stitching
- **Via count**: 9
- **Grid**: 3x3, 15mm spacing
- **Via size**: 0.8mm/0.4mm

## Related References
- Build on `30-single-via-through`
- See `31-multiple-vias-through` for random placement
- Compare with thermal vias for power dissipation

## Known Issues
- None
