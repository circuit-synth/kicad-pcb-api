# 15 - Silkscreen Logo Simple

## Purpose
Simple graphic (circle with crosshairs) on front silkscreen. Tests silkscreen graphics rendering.

## KiCAD Creation Steps
1. Open KiCAD PCB Editor
2. File → New Project
3. Draw board outline
4. Select F.SilkS layer
5. Draw circle (radius 10mm)
6. Draw horizontal and vertical lines through center
7. Save as `project.kicad_pcb`

## File Contents
- Board outline (100mm x 100mm)
- Circle on F.SilkS (radius: 10mm)
- Crosshair lines
- Line width: 0.2mm

## Key S-expression Elements
- `(gr_circle ...)`
- `(gr_line ...)`
- `(layer "F.SilkS")`
- `(stroke (width ...) (type ...))`

## Expected Parser Behavior
- Should parse circle and line graphics
- Should extract geometry (center, radius, endpoints)
- Should capture stroke properties

## Expected Formatter Behavior
- Should preserve exact coordinates
- Should maintain stroke settings
- Should preserve layer assignment

## Round-Trip Requirements
- ✅ Should be byte-identical
- Geometry preserved exactly

## Manufacturing Notes
- **JLCPCB Compatible**: Yes
- **Minimum line width**: 0.15mm recommended
- **Layer**: Front silkscreen

## Related References
- See `14-silkscreen-text-simple` for text
- Compare with `57-graphics-polygon` for filled shapes

## Known Issues
- None
