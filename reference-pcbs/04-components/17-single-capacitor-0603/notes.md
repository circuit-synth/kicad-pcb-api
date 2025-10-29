# 17 - Single Capacitor 0603

## Purpose
Single 0603 SMD capacitor footprint. Tests basic SMD component placement.

## KiCAD Creation Steps
1. Open KiCAD PCB Editor
2. File → New Project
3. Draw board outline
4. Add → Footprint
5. Select Capacitor_SMD:C_0603_1608Metric
6. Place at (100, 100)
7. Set reference: C1
8. Set value: 100nF
9. Save as `project.kicad_pcb`

## File Contents
- Board outline (100mm x 100mm)
- Single 0603 capacitor
- Reference: C1
- Value: 100nF
- Position: (100, 100)

## Key S-expression Elements
- `(footprint "Capacitor_SMD:C_0603_1608Metric")`
- `(at 100 100 0)`
- `(fp_text reference "C1")`
- `(fp_text value "100nF")`
- `(pad "1" smd ...)`
- `(pad "2" smd ...)`

## Expected Parser Behavior
- Should parse footprint
- Should extract pads (2)
- Should capture position and rotation
- Should preserve reference and value

## Expected Formatter Behavior
- Should preserve footprint library name
- Should maintain pad properties
- Should preserve position exactly

## Round-Trip Requirements
- ✅ Should be byte-identical
- All footprint properties preserved

## Manufacturing Notes
- **JLCPCB Compatible**: Yes
- **Package**: 0603 (1.6mm x 0.8mm)
- **Pads**: 2 SMD
- **Layer**: Top

## Related References
- Compare with `16-single-resistor-0603` (resistor)
- See `18-two-resistors-series` for multiple components
- See `19-resistor-capacitor-rc` for RC circuit

## Known Issues
- Requires KiCAD footprint library
- Create manually in KiCAD
