# 01 - Blank PCB

## Purpose
Empty 2-layer PCB with default settings. Tests basic PCB structure without any components, traces, or zones.

## KiCAD Creation Steps
1. Open KiCAD PCB Editor
2. File → New Project
3. Keep all default settings
4. Do NOT add any elements (no outline, no components)
5. Save as `project.kicad_pcb`

## File Contents
Minimal PCB structure:
- PCB header with version
- Default settings (thickness, layers)
- Layer stackup (F.Cu, B.Cu, F.SilkS, B.SilkS, etc.)
- No board outline
- No components
- No traces
- No zones

## Key S-expression Elements
- `(kicad_pcb (version ...))`
- `(general (thickness ...))`
- `(paper ...)`
- `(layers ...)`
- `(setup ...)`

## Expected Parser Behavior
- Should parse minimal valid PCB file
- Should extract version number
- Should extract layer stackup
- Should handle empty board (no elements)

## Expected Formatter Behavior
- Should write valid minimal PCB file
- Should preserve version number
- Should preserve layer definitions
- Should maintain KiCAD format exactly

## Round-Trip Requirements
- ✅ Should be byte-identical after round-trip
- This is the simplest test case

## Testing Checklist
- [ ] Load with `kpa.load_pcb()`
- [ ] Verify `len(pcb.footprints) == 0`
- [ ] Verify `len(pcb.tracks) == 0`
- [ ] Verify `len(pcb.vias) == 0`
- [ ] Verify layer count == 2
- [ ] Save and reload
- [ ] Verify round-trip identical

## Manufacturing Notes
- **JLCPCB Compatible**: Yes
- **Layer count**: 2
- **Thickness**: 1.6mm (default)

## Related References
- Build on this with `05-edge-cuts-rectangle` (add board outline)
- Compare with `02-blank-pcb-4layer` (different layer count)

## Known Issues
None expected - this is the simplest reference.

## Example Code

```python
import kicad_pcb_api as kpa

# Load blank PCB
pcb = kpa.load_pcb('reference-pcbs/01-basic-structure/01-blank-pcb/project.kicad_pcb')

# Verify empty
assert len(pcb.footprints) == 0
assert len(pcb.tracks) == 0
assert len(pcb.vias) == 0

# Should have 2 copper layers
# TODO: Add layer count check once implemented

print('✅ Blank PCB reference validated')
```
