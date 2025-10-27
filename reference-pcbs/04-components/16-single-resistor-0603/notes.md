# 16 - Single Resistor 0603

## Purpose
Single 0603 SMD resistor placed on PCB. Tests basic SMD component placement, pad generation, and silkscreen.

## KiCAD Creation Steps
1. Open KiCAD PCB Editor
2. File → New Project
3. Create board outline (100mm x 80mm rectangle on Edge.Cuts)
4. Place footprint:
   - Library: `Resistor_SMD`
   - Footprint: `R_0603_1608Metric`
   - Reference: R1
   - Value: 10k
   - Position: (50mm, 40mm) - center of board
   - Rotation: 0°
   - Layer: F.Cu
5. Save as `project.kicad_pcb`

## File Contents
- Board outline (100mm x 80mm)
- 1 footprint (R_0603_1608Metric)
- 2 pads (pad 1, pad 2)
- Silkscreen reference text "R1"
- Silkscreen value text "10k"
- Courtyard outline
- Fab layer outline

## Key S-expression Elements
- `(footprint "Resistor_SMD:R_0603_1608Metric" ...)`
- `(layer "F.Cu")`
- `(at 50 40 0)`
- `(pad "1" smd ...)`
- `(pad "2" smd ...)`
- `(fp_text reference "R1" ...)`
- `(fp_text value "10k" ...)`
- `(fp_line ...)` for courtyard

## Expected Parser Behavior
- Should parse footprint with all properties
- Should extract reference, value, position, rotation
- Should parse all pads with layers, size, position
- Should parse footprint text (reference, value)
- Should parse courtyard and fab layer graphics

## Expected Formatter Behavior
- Should preserve exact pad positions and sizes
- Should maintain layer assignments
- Should preserve footprint library ID
- Should maintain text properties (size, position)

## Round-Trip Requirements
- ✅ Should be byte-identical after round-trip
- Pad positions must be exact (micrometers)
- Layer stack must be preserved

## Testing Checklist
- [ ] Load with `kpa.load_pcb()`
- [ ] Verify `len(pcb.footprints) == 1`
- [ ] Verify reference == "R1"
- [ ] Verify value == "10k"
- [ ] Verify position == (50, 40)
- [ ] Verify 2 pads
- [ ] Verify pads on F.Cu layer
- [ ] Save and reload
- [ ] Verify round-trip identical

## Manufacturing Notes
- **JLCPCB Compatible**: Yes
- **Package**: 0603 (1.6mm x 0.8mm)
- **Pad size**: ~0.9mm x 0.8mm
- **Layer**: Top (F.Cu)
- **Assembly**: SMT

## Related References
- Compare with `17-single-resistor-through-hole` (THT vs SMD)
- Build on this with `36-simple-circuit-2-resistors` (add connections)
- Compare with `18-single-capacitor-0603` (different component, same package)

## Known Issues
None expected - standard 0603 footprint.

## Example Code

```python
import kicad_pcb_api as kpa

# Load PCB with resistor
pcb = kpa.load_pcb('reference-pcbs/04-components/16-single-resistor-0603/project.kicad_pcb')

# Verify component
assert len(pcb.footprints) == 1

r1 = pcb.footprints.get_by_reference('R1')
assert r1 is not None
assert r1.value == '10k'
assert r1.library_id == 'Resistor_SMD:R_0603_1608Metric'
assert r1.x == 50.0
assert r1.y == 40.0
assert r1.rotation == 0.0

# Verify pads
assert len(r1.pads) == 2
assert 'F.Cu' in r1.pads[0].layers

print('✅ Single resistor reference validated')
```
