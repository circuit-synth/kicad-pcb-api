# 61 - Ruled Area

## Purpose
Demonstrates a ruled/hatched copper area (zone with hatched fill instead of solid). This tests zone fill style parsing and hatched pattern handling.

## KiCAD Creation Steps
1. Copy blank template to this directory: `cp -r ../../_templates/blank-template/* .`
2. Rename files: `mv blank.kicad_pcb project.kicad_pcb && mv blank.kicad_pro project.kicad_pro && mv blank.kicad_sch project.kicad_sch && mv blank.kicad_prl project.kicad_prl`
3. Open in KiCAD: `open project.kicad_pcb`
4. Place → Zone (or press Ctrl+Shift+Z)
5. Draw zone outline:
   - Start at (20, 20)
   - Continue to (80, 20)
   - Continue to (80, 60)
   - Continue to (20, 60)
   - Close at (20, 20)
6. In zone properties:
   - Net: (No Net)
   - Layer: F.Cu
   - Fill Type: **Hatched** (not solid)
   - Hatch pitch: 1.0mm
   - Hatch width: 0.5mm
   - Hatch smoothing: None
   - Clearance: 0.5mm
   - Min thickness: 0.25mm
7. Fill zone (B to refill)
8. Save

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
- `(hatch_orientation ...)` - Hatch angle
- `(hatch_smoothing_level ...)` - Smoothing value
- `(polygon ...)` - Zone outline
- `(filled_polygon ...)` - Filled hatched pattern

## Expected Parser Behavior
- Parse zone fill mode (hatched vs solid)
- Extract hatch parameters (pitch, width, orientation)
- Parse zone outline polygon
- Handle filled polygon data for hatched pattern
- Preserve all hatch styling

## Expected Formatter Behavior
- Write zone with correct fill mode
- Maintain hatch parameters exactly
- Preserve zone outline
- Write filled polygon data for hatched pattern

## Round-Trip Requirements
- Should be semantically identical after round-trip
- Fill mode must be "hatched" (not solid)
- Hatch parameters must match
- Zone outline must match
- Filled pattern should be regenerated on zone refill

## Manufacturing Notes
- JLCPCB compatible: Yes
- Hatched zones use less copper than solid
- Useful for ground planes with thermal management
- Reduces warping in large copper areas
- Better for flexible PCBs
- Saves copper in large pours

## Related References
- `09-copper-pour-simple` - Simple solid copper pour
- `10-copper-pour-with-thermal` - Copper pour with thermals
- `41-filled-zones-priority` - Zone priority

## Known Issues
- None yet
- Hatch pattern regeneration may vary slightly between fills
