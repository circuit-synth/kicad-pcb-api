# 58 - Graphics Circle

## Purpose
Demonstrates a drawn circle shape on the PCB. This tests circle parsing, center/radius handling, and filled/unfilled shapes.

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

## Manufacturing Notes
- JLCPCB compatible: Yes
- On silkscreen: printed in silkscreen ink
- On copper: becomes copper shape
- Minimum width: 0.15mm (silkscreen), 0.1mm (copper)

## Related References
- `57-graphics-polygon` - Polygon shape
- `14-silkscreen-graphics` - Silkscreen graphics
