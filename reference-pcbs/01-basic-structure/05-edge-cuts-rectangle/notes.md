# 05 - Edge Cuts Rectangle

## Purpose
Simple rectangular board outline (100mm x 80mm) on Edge.Cuts layer. Tests basic board outline definition.

## KiCAD Creation Steps
1. Open KiCAD PCB Editor
2. File → New Project
3. Select Edge.Cuts layer
4. Draw rectangle: 100mm x 80mm (or use dimensions: 0,0 to 100,80)
5. Save as `project.kicad_pcb`

## File Contents
- Basic PCB structure
- Rectangle on Edge.Cuts layer defining board outline
- Coordinates: (0, 0) to (100, 80)
- No components or traces

## Key S-expression Elements
- `(kicad_pcb ...)`
- `(gr_rect ...)` or `(gr_line ...)` for outline
- `(layer "Edge.Cuts")`
- `(start ...) (end ...)`

## Expected Parser Behavior
- Should parse board outline graphics
- Should identify Edge.Cuts layer elements
- Should extract rectangle dimensions
- Should calculate board size

## Expected Formatter Behavior
- Should preserve exact rectangle coordinates
- Should maintain Edge.Cuts layer assignment
- Should use same graphics primitive (rect vs lines)

## Round-Trip Requirements
- ✅ Should be byte-identical after round-trip
- Coordinate precision must be exact

## Testing Checklist
- [ ] Load with `kpa.load_pcb()`
- [ ] Verify board outline exists
- [ ] Verify dimensions: 100mm x 80mm
- [ ] Verify Edge.Cuts layer
- [ ] Save and reload
- [ ] Verify round-trip identical

## Manufacturing Notes
- **JLCPCB Compatible**: Yes
- **Board size**: 100mm x 80mm
- **Layer count**: 2
- **Panelization**: Single board

## Related References
- Builds on `01-blank-pcb` (adds outline)
- Compare with `06-edge-cuts-rounded` (rounded corners)
- Compare with `07-edge-cuts-complex` (complex shapes)

## Known Issues
- KiCAD may use `gr_rect` or four `gr_line` elements
- Both formats should round-trip correctly

## Example Code

```python
import kicad_pcb_api as kpa

# Load PCB with outline
pcb = kpa.load_pcb('reference-pcbs/01-basic-structure/05-edge-cuts-rectangle/project.kicad_pcb')

# Verify board dimensions
# TODO: Add board size check once implemented

# Should have board outline but no components
assert len(pcb.footprints) == 0
assert len(pcb.tracks) == 0

print('✅ Edge cuts rectangle reference validated')
```
