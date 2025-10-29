# 26 - Two Traces Parallel

## Purpose
Two parallel traces with controlled spacing. Tests parallel routing and clearance.

## KiCAD Creation Steps
1. Open KiCAD PCB Editor
2. File → New Project
3. Draw board outline
4. Select F.Cu layer
5. Route first trace horizontally
6. Route second trace parallel (10mm spacing)
7. Width: 0.25mm each
8. Save as `project.kicad_pcb`

## File Contents
- Board outline (100mm x 100mm)
- Two parallel traces on F.Cu
- Width: 0.25mm each
- Spacing: 10mm
- Nets: Signal1, Signal2
- Length: ~60mm each

## Key S-expression Elements
- `(segment ...)` (x2)
- `(net 1)` and `(net 2)`
- `(layer "F.Cu")`
- `(width 0.25)`

## Expected Parser Behavior
- Should parse both traces
- Should identify different nets
- Should preserve spacing
- Should capture parallel relationship

## Expected Formatter Behavior
- Should preserve both traces
- Should maintain net assignments
- Should preserve exact coordinates

## Round-Trip Requirements
- ✅ Should be byte-identical
- Spacing preserved exactly

## Manufacturing Notes
- **JLCPCB Compatible**: Yes
- **Trace width**: 0.25mm
- **Trace spacing**: 10mm (wide)
- **Layer**: Front copper

## Related References
- Build on `24-single-trace-straight`
- Compare with `27-differential-pair` (matched length)
- See `46-high-speed-routing` for controlled impedance

## Known Issues
- None
