# 24 - Single Trace Straight

## Purpose
Single straight trace on top copper layer. Tests basic track/trace creation, width, and layer assignment.

## KiCAD Creation Steps
1. Open KiCAD PCB Editor
2. File → New Project
3. Create board outline (100mm x 80mm)
4. Select F.Cu layer
5. Route single straight trace:
   - Start: (20mm, 40mm)
   - End: (80mm, 40mm)
   - Width: 0.25mm (standard signal trace)
   - Layer: F.Cu
   - Net: unassigned (or create net "Signal")
6. Save as `project.kicad_pcb`

## File Contents
- Board outline
- 1 track/trace on F.Cu
- Start point: (20, 40)
- End point: (80, 40)
- Width: 0.25mm
- Length: 60mm
- Layer: F.Cu

## Key S-expression Elements
- `(segment ...)`
- `(start 20 40)`
- `(end 80 40)`
- `(width 0.25)`
- `(layer "F.Cu")`
- `(net ...)` (if assigned)

## Expected Parser Behavior
- Should parse track with start/end coordinates
- Should extract width
- Should identify layer
- Should handle net assignment (if present)

## Expected Formatter Behavior
- Should preserve exact start/end coordinates
- Should maintain width precision
- Should preserve layer assignment
- Should format coordinates consistently

## Round-Trip Requirements
- ✅ Should be byte-identical after round-trip
- Coordinate precision critical (micrometers)

## Testing Checklist
- [ ] Load with `kpa.load_pcb()`
- [ ] Verify `len(pcb.tracks) == 1`
- [ ] Verify start == (20, 40)
- [ ] Verify end == (80, 40)
- [ ] Verify width == 0.25
- [ ] Verify layer == F.Cu
- [ ] Calculate length == 60mm
- [ ] Save and reload
- [ ] Verify round-trip identical

## Manufacturing Notes
- **JLCPCB Compatible**: Yes
- **Trace width**: 0.25mm (well above minimum)
- **JLCPCB minimum**: 0.127mm
- **Layer**: Top copper (F.Cu)

## Related References
- Compare with `25-single-trace-curved` (angled trace)
- Compare with `26-trace-with-width-change` (varying width)
- Compare with `28-trace-on-bottom-layer` (different layer)
- Build on this with `36-simple-circuit-2-resistors` (connect components)

## Known Issues
None expected - simplest routing case.

## Example Code

```python
import kicad_pcb_api as kpa

# Load PCB with trace
pcb = kpa.load_pcb('reference-pcbs/05-routing/24-single-trace-straight/project.kicad_pcb')

# Verify track
assert len(pcb.tracks) == 1

track = pcb.tracks[0]
assert track.start.x == 20.0
assert track.start.y == 40.0
assert track.end.x == 80.0
assert track.end.y == 40.0
assert track.width == 0.25
assert track.layer == 'F.Cu'

# Calculate length
import math
length = math.sqrt((track.end.x - track.start.x)**2 + (track.end.y - track.start.y)**2)
assert abs(length - 60.0) < 0.001

print('✅ Single trace reference validated')
```
