# 10 - Copper Pour Polygon

## Purpose
Polygon-shaped copper pour on F.Cu layer. Tests zone with non-rectangular boundary.

## KiCAD Creation Steps
1. Open KiCAD PCB Editor
2. File → New Project
3. Draw board outline
4. Select F.Cu layer
5. Add zone with polygon boundary (not rectangle)
6. Fill zone
7. Save as `project.kicad_pcb`

## File Contents
- Board outline (100mm x 100mm)
- Polygon-shaped copper zone on F.Cu
- Net: GND
- Fill type: Solid

## Key S-expression Elements
- `(zone ...)`
- `(net ...)`
- `(polygon (pts ...))`
- `(fill yes ...)`
- `(layer "F.Cu")`

## Expected Parser Behavior
- Should parse zone definition
- Should extract polygon points
- Should identify fill parameters
- Should preserve net assignment

## Expected Formatter Behavior
- Should preserve exact polygon coordinates
- Should maintain fill settings
- Should preserve zone properties

## Round-Trip Requirements
- ✅ Should be semantically identical
- Polygon points must be exact
- Fill parameters preserved

## Manufacturing Notes
- **JLCPCB Compatible**: Yes
- **Minimum copper spacing**: 0.127mm
- **Layer count**: 2

## Related References
- Compare with `09-copper-pour-simple` (rectangular zone)
- See `11-keepout-zone-simple` for keepout zones

## Known Issues
- None
