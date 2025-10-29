# 19 - Resistor Capacitor RC

## Purpose
Basic RC filter circuit with resistor and capacitor. Tests mixed component types and circuit layout.

## KiCAD Creation Steps
1. Open KiCAD PCB Editor
2. File → New Project
3. Draw board outline
4. Add R1: Resistor_SMD:R_0603_1608Metric at (80, 100)
5. Add C1: Capacitor_SMD:C_0603_1608Metric at (120, 100)
6. Set values: R1=10k, C1=100nF
7. Route trace between R1 pad 2 and C1 pad 1
8. Add ground connection for C1 pad 2
9. Save as `project.kicad_pcb`

## File Contents
- Board outline (100mm x 100mm)
- R1: 0603 resistor, 10k
- C1: 0603 capacitor, 100nF
- Traces connecting components
- Nets: Signal, GND

## Key S-expression Elements
- `(footprint "Resistor_SMD:R_0603_1608Metric")`
- `(footprint "Capacitor_SMD:C_0603_1608Metric")`
- `(segment ...)` for traces
- `(net ...)` definitions (Signal, GND)

## Expected Parser Behavior
- Should parse both component types
- Should extract net connections
- Should capture circuit topology
- Should preserve values

## Expected Formatter Behavior
- Should preserve component order
- Should maintain net assignments
- Should preserve routing

## Round-Trip Requirements
- ✅ Should be byte-identical
- Circuit integrity preserved

## Manufacturing Notes
- **JLCPCB Compatible**: Yes
- **Components**: 1x resistor, 1x capacitor
- **Cutoff frequency**: ~15.9 Hz (10k, 100nF)
- **Layer**: Top

## Related References
- Build on `16-single-resistor-0603` and `17-single-capacitor-0603`
- See `18-two-resistors-series` for series connection
- See `36-simple-circuit-2-resistors` for complete circuits

## Known Issues
- Requires KiCAD footprint library
- Create manually in KiCAD
