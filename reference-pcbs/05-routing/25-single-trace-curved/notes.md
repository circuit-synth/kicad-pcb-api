# 25 - Single Trace Curved

## Purpose
Curved trace made of multiple angled segments. Tests complex routing geometry.

## KiCAD Creation Steps
1. Open KiCAD PCB Editor
2. File → New Project
3. Draw board outline
4. Select F.Cu layer
5. Route trace with multiple angles to create curve
6. Width: 0.25mm
7. Save as `project.kicad_pcb`

## File Contents
- Board outline (100mm x 100mm)
- Curved trace on F.Cu (4 segments)
- Width: 0.25mm
- Net: Signal
- Approximate S-curve shape

## Key S-expression Elements
- `(segment ...)` (multiple)
- `(start ...) (end ...)`
- `(width 0.25)`
- `(layer "F.Cu")`
- `(net ...)`

## Expected Parser Behavior
- Should parse all segments
- Should preserve exact coordinates
- Should maintain segment connectivity
- Should capture net assignment

## Expected Formatter Behavior
- Should preserve segment order
- Should maintain exact coordinates
- Should preserve width and layer

## Round-Trip Requirements
- ✅ Should be byte-identical
- All segment coordinates exact

## Manufacturing Notes
- **JLCPCB Compatible**: Yes
- **Trace width**: 0.25mm
- **Layer**: Front copper
- **Segments**: 4

## Related References
- Compare with `24-single-trace-straight` (straight trace)
- See `26-two-traces-parallel` for parallel routing
- See `27-differential-pair` for differential pairs

## Known Issues
- KiCAD uses line segments, not true curves
- Multiple segments approximate curve
