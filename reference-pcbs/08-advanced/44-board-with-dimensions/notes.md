# 44 - Board with Dimensions

## Purpose
Demonstrates dimension annotations on the PCB (orthogonal and aligned dimensions). This tests dimension parsing, leader line handling, and measurement display.

## KiCAD Creation Steps
1. Copy blank template to this directory: `cp -r ../../_templates/blank-template/* .`
2. Rename files: `mv blank.kicad_pcb project.kicad_pcb && mv blank.kicad_pro project.kicad_pro && mv blank.kicad_sch project.kicad_sch && mv blank.kicad_prl project.kicad_prl`
3. Open in KiCAD: `open project.kicad_pcb`
4. Draw → Dimension (or press Ctrl+Shift+D)
5. Add horizontal dimension:
   - Click start point at edge of board (50, 50)
   - Click end point at (150, 50)
   - Click to place dimension line at (100, 45)
   - Result: "100.00 mm" dimension
6. Add vertical dimension:
   - Click start point at (150, 50)
   - Click end point at (150, 150)
   - Click to place dimension line at (155, 100)
   - Result: "100.00 mm" dimension
7. In dimension properties:
   - Layer: Dwgs.User (drawings layer)
   - Text size: 1.5mm
   - Arrow size: 1.0mm
   - Extension offset: 2mm
8. Save

## File Contents
- **Board**: 100×80mm rectangle
- **Dimensions**: 2 orthogonal dimensions (horizontal + vertical)
- **Layer**: Dwgs.User
- **Measurements**: Auto-calculated from geometry

## Key S-expression Elements
- `(dimension ...)` - Dimension element
- `(type aligned/orthogonal/...)` - Dimension type
- `(start x y)` - Measurement start point
- `(end x y)` - Measurement end point
- `(height ...)` - Distance from measured line to dimension line
- `(gr_text "..." ...)` - Dimension text (auto-generated)
- `(format ...)` - Units and precision
- `(layer "...")` - Layer designation

## Expected Parser Behavior
- Parse dimension type (aligned, orthogonal, etc.)
- Extract start/end points and height
- Parse text formatting options
- Calculate measurement value from geometry
- Preserve arrow and extension line properties

## Expected Formatter Behavior
- Write dimension with correct S-expression format
- Maintain all geometry precisely
- Preserve text formatting
- Write arrow and extension properties

## Round-Trip Requirements
- Should be semantically identical after round-trip
- Start/end points must match exactly
- Dimension type must be preserved
- Text formatting must match

## Manufacturing Notes
- JLCPCB compatible: N/A (dimensions are documentation only)
- Typically placed on Dwgs.User or Cmts.User layer
- Not printed on final PCB
- Useful for assembly documentation and drawings

## Related References
- `54-graphics-text` - Text element
- `57-graphics-polygon` - Graphics shapes
- `60-different-layers` - Elements on different layers

## Known Issues
- None yet
- Dimension format may vary by KiCAD version
