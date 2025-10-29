# 20 - Single IC SOIC8

## Purpose
Single SOIC-8 IC footprint. Tests multi-pin SMD component.

## KiCAD Creation Steps
1. Open KiCAD PCB Editor
2. File → New Project
3. Draw board outline
4. Add → Footprint
5. Select Package_SO:SOIC-8_3.9x4.9mm_P1.27mm
6. Place at (100, 100)
7. Set reference: U1
8. Set value: LM358
9. Save as `project.kicad_pcb`

## File Contents
- Board outline (100mm x 100mm)
- Single SOIC-8 footprint
- Reference: U1
- Value: LM358 (dual op-amp)
- Position: (100, 100)
- 8 SMD pads

## Key S-expression Elements
- `(footprint "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm")`
- `(at 100 100 0)`
- `(fp_text reference "U1")`
- `(fp_text value "LM358")`
- `(pad "1" smd ...)` through `(pad "8" smd ...)`

## Expected Parser Behavior
- Should parse IC footprint
- Should extract all 8 pads
- Should capture position and rotation
- Should preserve reference and value

## Expected Formatter Behavior
- Should preserve footprint library name
- Should maintain all pad properties
- Should preserve position exactly

## Round-Trip Requirements
- ✅ Should be byte-identical
- All IC properties preserved

## Manufacturing Notes
- **JLCPCB Compatible**: Yes
- **Package**: SOIC-8 (3.9mm x 4.9mm)
- **Pitch**: 1.27mm
- **Pads**: 8 SMD
- **Layer**: Top

## Related References
- Compare with `16-single-resistor-0603` (2-pad SMD)
- See `19-single-ic-qfp` for QFP packages
- See `20-single-ic-bga` for BGA packages

## Known Issues
- Requires KiCAD footprint library
- Create manually in KiCAD
