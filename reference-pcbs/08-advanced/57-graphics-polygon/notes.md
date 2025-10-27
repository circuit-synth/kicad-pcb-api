# 57 - Graphics Polygon

## Purpose
Demonstrates a drawn polygon shape on the PCB. This tests polygon parsing, vertex handling, and filled/unfilled shapes.

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

## Manufacturing Notes
- JLCPCB compatible: Yes
- On silkscreen: printed in silkscreen ink
- On copper: becomes copper pour/shape
- Minimum width: 0.15mm (silkscreen), 0.1mm (copper)

## Related References
- `58-graphics-circle` - Circle shape
- `14-silkscreen-graphics` - Silkscreen graphics
- `60-different-layers` - Elements on different layers
