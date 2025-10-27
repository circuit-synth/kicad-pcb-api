# 33 - Buried Via

## Purpose
Demonstrates a buried via that connects two inner layers (In1.Cu to In2.Cu). This tests advanced multi-layer board support and buried via parsing/formatting.

## KiCAD Creation Steps
1. Copy blank template to this directory: `cp -r ../../_templates/blank-template/* .`
2. Rename files: `mv blank.kicad_pcb project.kicad_pcb && mv blank.kicad_pro project.kicad_pro && mv blank.kicad_sch project.kicad_sch && mv blank.kicad_prl project.kicad_prl`
3. Open in KiCAD: `open project.kicad_pcb`
4. File → Board Setup → Board Stackup → Change to 4 layers
5. Place → Drill and Place Via (or press Ctrl+Shift+V)
6. In via properties:
   - Position: Center of board (50, 40)
   - Size: 0.5mm
   - Drill: 0.25mm
   - Via Type: **Blind/Buried**
   - Layer Pair: **In1.Cu → In2.Cu** (first inner to second inner)
7. Save

## File Contents
- **Board**: 100×80mm rectangle, 4-layer stackup
- **Via**: 1 buried via from In1.Cu to In2.Cu
- **Position**: (50.0, 40.0)
- **Dimensions**: 0.5mm size, 0.25mm drill

## Key S-expression Elements
- `(via blind ...)` - Buried vias also use "blind" designation
- `(layers "In1.Cu" "In2.Cu")` - Inner layer pair specification
- `(size ...)` - Via diameter
- `(drill ...)` - Drill diameter

## Expected Parser Behavior
- Parse via as buried type (inner-to-inner)
- Correctly identify both layers are internal
- Preserve all dimensions exactly

## Expected Formatter Behavior
- Write buried via with correct S-expression format
- Maintain layer pair ordering
- Include all required via parameters

## Round-Trip Requirements
- Should be semantically identical after round-trip
- Via type (buried) must be preserved
- Layer pair must match exactly (both inner layers)
- Position and dimensions must match

## Manufacturing Notes
- JLCPCB compatible: Yes (4-layer boards support buried vias)
- Minimum via size: 0.3mm (JLCPCB standard)
- Requires 4+ layer board
- Most expensive via type (sequential lamination)
- Used in high-density HDI designs

## Related References
- `30-single-via-through` - Basic through-hole via
- `32-via-blind` - Blind via (top to inner)
- `02-blank-pcb-4layer` - 4-layer board setup

## Known Issues
- None yet
