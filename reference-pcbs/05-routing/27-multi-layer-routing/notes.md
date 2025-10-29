# 27 - Multi Layer Routing

## Purpose
Trace routing across multiple layers using via. Tests layer transitions.

## KiCAD Creation Steps
1. Open KiCAD PCB Editor
2. File → New Project
3. Draw board outline
4. Route trace on F.Cu
5. Add via
6. Continue trace on B.Cu
7. Save as `project.kicad_pcb`

## File Contents
- Board outline (100mm x 100mm)
- Trace segment on F.Cu
- Via at layer transition point
- Trace segment on B.Cu
- Net: Signal
- Via size: 0.8mm, drill: 0.4mm

## Key S-expression Elements
- `(segment ...)` on F.Cu
- `(via ...)`
- `(segment ...)` on B.Cu
- `(layers "F.Cu" "B.Cu")`
- `(net ...)` consistent across elements

## Expected Parser Behavior
- Should parse both layer segments
- Should parse via
- Should maintain net continuity
- Should preserve layer assignments

## Expected Formatter Behavior
- Should preserve layer transitions
- Should maintain via properties
- Should preserve net assignment

## Round-Trip Requirements
- ✅ Should be byte-identical
- Layer continuity preserved

## Manufacturing Notes
- **JLCPCB Compatible**: Yes
- **Layers used**: F.Cu, B.Cu
- **Via**: 0.8mm/0.4mm
- **Layer count**: 2

## Related References
- Build on `24-single-trace-straight`
- See `30-single-via-through` for vias
- Compare with `29-trace-on-inner-layer` for 4-layer

## Known Issues
- None
