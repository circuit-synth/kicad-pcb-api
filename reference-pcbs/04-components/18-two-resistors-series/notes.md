# 18 - Two Resistors Series

## Purpose
Two 0603 resistors connected in series. Tests multiple components and basic routing.

## KiCAD Creation Steps
1. Open KiCAD PCB Editor
2. File → New Project
3. Draw board outline
4. Add R1: Resistor_SMD:R_0603_1608Metric at (80, 100)
5. Add R2: Resistor_SMD:R_0603_1608Metric at (120, 100)
6. Set values: R1=10k, R2=10k
7. Route trace between R1 pad 2 and R2 pad 1
8. Save as `project.kicad_pcb`

## File Contents
- Board outline (100mm x 100mm)
- Two 0603 resistors
- R1 at (80, 100), value: 10k
- R2 at (120, 100), value: 10k
- Single trace connecting them
- Net: Signal

## Key S-expression Elements
- `(footprint "Resistor_SMD:R_0603_1608Metric")` (x2)
- `(fp_text reference ...)` (R1, R2)
- `(fp_text value ...)` (10k, 10k)
- `(segment ...)` for trace
- `(net ...)` definitions

## Expected Parser Behavior
- Should parse two footprints
- Should extract net connections
- Should capture trace routing
- Should preserve component values

## Expected Formatter Behavior
- Should preserve footprint order
- Should maintain net assignments
- Should preserve trace properties

## Round-Trip Requirements
- ✅ Should be byte-identical
- Component relationships preserved

## Manufacturing Notes
- **JLCPCB Compatible**: Yes
- **Components**: 2x 0603 resistors
- **Trace width**: 0.25mm typical
- **Layer**: Top

## Related References
- Build on `16-single-resistor-0603`
- See `19-resistor-capacitor-rc` for RC circuit
- See `24-single-trace-straight` for routing

## Known Issues
- Requires KiCAD footprint library
- Create manually in KiCAD
