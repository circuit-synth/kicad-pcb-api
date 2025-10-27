# 32 - Blind Via

## Purpose
Demonstrates a blind via that connects the top layer (F.Cu) to an inner layer (In1.Cu or In2.Cu). This tests multi-layer board support and blind via parsing/formatting.

## KiCAD Creation Steps
1. Copy blank template to this directory: `cp -r ../../_templates/blank-template/* .`
2. Rename files: `mv blank.kicad_pcb project.kicad_pcb && mv blank.kicad_pro project.kicad_pro && mv blank.kicad_sch project.kicad_sch && mv blank.kicad_prl project.kicad_prl`
3. Open in KiCAD: `open project.kicad_pcb`
4. File → Board Setup → Board Stackup → Change to 4 layers
5. Place → Drill and Place Via (or press Ctrl+Shift+V)
6. In via properties:
   - Position: Center of board (50, 40)
   - Size: 0.6mm
   - Drill: 0.3mm
   - Via Type: **Blind/Buried**
   - Layer Pair: **F.Cu → In1.Cu** (top to first inner layer)
7. Save

## File Contents
- **Board**: 100×80mm rectangle, 4-layer stackup
- **Via**: 1 blind via from F.Cu to In1.Cu
- **Position**: (50.0, 40.0)
- **Dimensions**: 0.6mm size, 0.3mm drill

## Key S-expression Elements
- `(via blind ...)` - Blind via designation
- `(layers "F.Cu" "In1.Cu")` - Layer pair specification
- `(size ...)` - Via diameter
- `(drill ...)` - Drill diameter

## Expected Parser Behavior
- Parse via as blind type (not through-hole)
- Correctly identify layer pair (F.Cu to In1.Cu)
- Preserve all dimensions exactly

## Expected Formatter Behavior
- Write blind via with correct S-expression format
- Maintain layer pair ordering
- Include all required via parameters

## Round-Trip Requirements
- Should be semantically identical after round-trip
- Via type (blind) must be preserved
- Layer pair must match exactly
- Position and dimensions must match

## Manufacturing Notes
- JLCPCB compatible: Yes (4-layer boards support blind vias)
- Minimum via size: 0.3mm (JLCPCB standard)
- Requires 4+ layer board
- More expensive than through-hole vias

## Related References
- `30-single-via-through` - Basic through-hole via
- `33-via-buried` - Buried via (inner to inner)
- `02-blank-pcb-4layer` - 4-layer board setup

## Known Issues
- None yet
