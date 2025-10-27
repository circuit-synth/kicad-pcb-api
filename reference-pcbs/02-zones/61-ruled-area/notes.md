# 61 - Ruled Area

## Purpose
Demonstrates a ruled/hatched copper area (zone with hatched fill instead of solid). This tests zone fill style parsing and hatched pattern handling.

## File Contents
- **Board**: 100×80mm rectangle
- **Zone**: Hatched copper area on F.Cu
- **Outline**: 60×40mm rectangle
- **Pattern**: 1.0mm pitch, 0.5mm width hatching

## Key S-expression Elements
- `(zone ...)` - Zone element
- `(fill_mode hatched)` - Fill mode (not solid)
- `(hatch_thickness ...)` - Hatch line width
- `(hatch_gap ...)` - Spacing between hatch lines
- `(polygon ...)` - Zone outline

## Manufacturing Notes
- JLCPCB compatible: Yes
- Hatched zones use less copper than solid
- Better for thermal management and flexible PCBs

## Related References
- `09-copper-pour-simple` - Simple solid copper pour
