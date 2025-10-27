# 44 - Board with Dimensions

## Purpose
Demonstrates dimension annotations on the PCB (orthogonal and aligned dimensions). This tests dimension parsing, leader line handling, and measurement display.

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

## Manufacturing Notes
- JLCPCB compatible: N/A (dimensions are documentation only)
- Typically placed on Dwgs.User or Cmts.User layer
- Not printed on final PCB

## Related References
- `54-graphics-text` - Text element
- `60-different-layers` - Elements on different layers
