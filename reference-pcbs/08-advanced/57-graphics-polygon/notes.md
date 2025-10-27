# 57 - Graphics Polygon

## Purpose
Demonstrates a drawn polygon shape on the PCB. This tests polygon parsing, vertex handling, and filled/unfilled shapes.

## KiCAD Creation Steps
1. Copy blank template to this directory: `cp -r ../../_templates/blank-template/* .`
2. Rename files: `mv blank.kicad_pcb project.kicad_pcb && mv blank.kicad_pro project.kicad_pro && mv blank.kicad_sch project.kicad_sch && mv blank.kicad_prl project.kicad_prl`
3. Open in KiCAD: `open project.kicad_pcb`
4. Draw → Polygon (or press Ctrl+Shift+P)
5. Draw pentagon with vertices:
   - (50, 25) - top point
   - (65, 40) - right upper
   - (60, 55) - right lower
   - (40, 55) - left lower
   - (35, 40) - left upper
   - Click on first point to close
6. In polygon properties:
   - Layer: F.SilkS (silkscreen)
   - Width: 0.15mm
   - Fill: Yes
7. Save

## File Contents
- **Board**: 100×80mm rectangle
- **Polygon**: Pentagon shape on F.SilkS
- **Vertices**: 5 points forming closed polygon
- **Fill**: Filled polygon

## Key S-expression Elements
- `(gr_poly ...)` - Graphics polygon element
- `(pts (xy x1 y1) (xy x2 y2) ...)` - Vertex list
- `(layer "...")` - Layer designation
- `(stroke (width ...) (type ...))` - Outline properties
- `(fill solid/none)` - Fill type

## Expected Parser Behavior
- Parse all polygon vertices in order
- Identify closed vs open polygons
- Parse fill type (solid/none)
- Preserve stroke properties

## Expected Formatter Behavior
- Write polygon with correct S-expression format
- Maintain vertex ordering
- Preserve fill settings
- Write stroke properties

## Round-Trip Requirements
- Should be semantically identical after round-trip
- All vertices must match exactly
- Vertex order must be preserved
- Fill type must match

## Manufacturing Notes
- JLCPCB compatible: Yes
- On silkscreen: printed in silkscreen ink
- On copper: becomes copper pour/shape
- Minimum width: 0.15mm (silkscreen), 0.1mm (copper)

## Related References
- `58-graphics-circle` - Circle shape
- `14-silkscreen-graphics` - Silkscreen graphics
- `60-different-layers` - Elements on different layers

## Known Issues
- None yet
