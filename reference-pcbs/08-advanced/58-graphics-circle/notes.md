# 58 - Graphics Circle

## Purpose
Demonstrates a drawn circle shape on the PCB. This tests circle parsing, center/radius handling, and filled/unfilled shapes.

## KiCAD Creation Steps
1. Copy blank template to this directory: `cp -r ../../_templates/blank-template/* .`
2. Rename files: `mv blank.kicad_pcb project.kicad_pcb && mv blank.kicad_pro project.kicad_pro && mv blank.kicad_sch project.kicad_sch && mv blank.kicad_prl project.kicad_prl`
3. Open in KiCAD: `open project.kicad_pcb`
4. Draw → Circle (or press Ctrl+Shift+C)
5. Click center point at (50, 40)
6. Click edge point at (65, 40) - creates 15mm radius circle
7. In circle properties:
   - Layer: F.SilkS (silkscreen)
   - Width: 0.2mm
   - Fill: None (outline only)
8. Save

## File Contents
- **Board**: 100×80mm rectangle
- **Circle**: Unfilled circle on F.SilkS
- **Center**: (50.0, 40.0)
- **Radius**: ~15mm
- **Outline**: 0.2mm width

## Key S-expression Elements
- `(gr_circle ...)` - Graphics circle element
- `(center x y)` - Circle center point
- `(end x y)` - Point on circle edge (defines radius)
- `(layer "...")` - Layer designation
- `(stroke (width ...) (type ...))` - Outline properties
- `(fill none/solid)` - Fill type

## Expected Parser Behavior
- Parse center and radius (from center/end points)
- Calculate radius from center and end coordinates
- Parse fill type (solid/none)
- Preserve stroke properties

## Expected Formatter Behavior
- Write circle with correct S-expression format
- Maintain center position exactly
- Preserve radius (via end point)
- Write fill and stroke properties

## Round-Trip Requirements
- Should be semantically identical after round-trip
- Center position must match exactly
- Radius must match (end point preservation)
- Fill type must match

## Manufacturing Notes
- JLCPCB compatible: Yes
- On silkscreen: printed in silkscreen ink
- On copper: becomes copper shape
- Minimum width: 0.15mm (silkscreen), 0.1mm (copper)
- Filled circles create solid copper areas

## Related References
- `57-graphics-polygon` - Polygon shape
- `14-silkscreen-graphics` - Silkscreen graphics
- `60-different-layers` - Elements on different layers

## Known Issues
- None yet
