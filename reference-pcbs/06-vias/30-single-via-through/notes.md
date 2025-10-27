# 30 - Single Via Through

## Purpose
Single through-hole via connecting top and bottom copper layers. Tests basic via creation, size, and layer connectivity.

## KiCAD Creation Steps
1. Open KiCAD PCB Editor
2. File → New Project
3. Create board outline (100mm x 80mm)
4. Place single via:
   - Position: (50mm, 40mm) - center of board
   - Size (diameter): 0.8mm
   - Drill: 0.4mm
   - Type: Through-hole (connects all copper layers)
   - Net: unassigned (or create net "Signal")
5. Save as `project.kicad_pcb`

## File Contents
- Board outline
- 1 through-hole via
- Position: (50, 40)
- Size: 0.8mm diameter
- Drill: 0.4mm
- Connects: F.Cu to B.Cu (through all layers)

## Key S-expression Elements
- `(via ...)`
- `(at 50 40)`
- `(size 0.8)`
- `(drill 0.4)`
- `(layers "F.Cu" "B.Cu")` or all layers
- `(net ...)` (if assigned)

## Expected Parser Behavior
- Should parse via with position
- Should extract size (diameter)
- Should extract drill diameter
- Should identify connected layers
- Should handle net assignment

## Expected Formatter Behavior
- Should preserve exact position
- Should maintain size and drill dimensions
- Should preserve layer connectivity
- Should format dimensions with proper precision

## Round-Trip Requirements
- ✅ Should be byte-identical after round-trip
- Position and dimensions must be exact

## Testing Checklist
- [ ] Load with `kpa.load_pcb()`
- [ ] Verify `len(pcb.vias) == 1`
- [ ] Verify position == (50, 40)
- [ ] Verify size == 0.8mm
- [ ] Verify drill == 0.4mm
- [ ] Verify connects F.Cu and B.Cu
- [ ] Save and reload
- [ ] Verify round-trip identical

## Manufacturing Notes
- **JLCPCB Compatible**: Yes
- **Via size**: 0.8mm (finished hole)
- **Drill size**: 0.4mm
- **JLCPCB minimum via**: 0.3mm drill
- **Annular ring**: (0.8 - 0.4) / 2 = 0.2mm per side
- **Type**: Through-hole

## Related References
- Compare with `31-multiple-vias-through` (multiple vias)
- Compare with `32-via-blind` (blind via)
- Compare with `33-via-buried` (buried via)
- Build on with `36-simple-circuit-2-resistors` (connect layers)

## Known Issues
- Via may or may not have explicit layer list
- Through vias connect all copper layers by default

## Example Code

```python
import kicad_pcb_api as kpa

# Load PCB with via
pcb = kpa.load_pcb('reference-pcbs/06-vias/30-single-via-through/project.kicad_pcb')

# Verify via
assert len(pcb.vias) == 1

via = pcb.vias[0]
assert via.x == 50.0
assert via.y == 40.0
assert via.size == 0.8
assert via.drill == 0.4

# Verify it's a through via
# Through vias connect all copper layers
assert via.is_through_via()  # Helper method

print('✅ Single via reference validated')
```

## Visual Reference

```
Top View (F.Cu):
     ___
    /   \    ← Via pad (0.8mm diameter)
   |  O  |   ← Drill hole (0.4mm)
    \___/

Side View:
F.Cu  ═══╪═══  ← Top copper
          │
Core      │     ← Board core
          │
B.Cu  ═══╪═══  ← Bottom copper
```
