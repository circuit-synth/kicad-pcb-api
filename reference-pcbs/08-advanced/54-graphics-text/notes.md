# 54 - Graphics Text

## Purpose
Demonstrates a text element on the PCB (not silkscreen). This tests PCB text parsing, formatting, and layer handling.

## KiCAD Creation Steps
1. Copy blank template to this directory: `cp -r ../../_templates/blank-template/* .`
2. Rename files: `mv blank.kicad_pcb project.kicad_pcb && mv blank.kicad_pro project.kicad_pro && mv blank.kicad_sch project.kicad_sch && mv blank.kicad_prl project.kicad_prl`
3. Open in KiCAD: `open project.kicad_pcb`
4. Place → Add Text (or press T)
5. Click at position (50, 40)
6. Enter text: "KICAD-PCB-API"
7. In text properties:
   - Layer: F.Cu (copper layer text)
   - Font size: 2mm height
   - Thickness: 0.3mm
   - Justification: Center
8. Save

## File Contents
- **Board**: 100×80mm rectangle
- **Text**: "KICAD-PCB-API" on F.Cu layer
- **Position**: (50.0, 40.0)
- **Font**: 2mm height, 0.3mm thickness

## Key S-expression Elements
- `(gr_text "..." ...)` - Graphics text element
- `(at x y rotation)` - Position and rotation
- `(layer "...")` - Layer designation
- `(effects (font (size ...) (thickness ...)))` - Font properties
- `(justify ...)` - Text alignment

## Expected Parser Behavior
- Parse text content as string
- Correctly identify layer
- Preserve font properties (size, thickness)
- Parse position and rotation

## Expected Formatter Behavior
- Write text with correct S-expression format
- Escape special characters if needed
- Maintain all font properties
- Preserve layer assignment

## Round-Trip Requirements
- Should be semantically identical after round-trip
- Text content must match exactly
- Position, rotation, layer must match
- Font properties must be preserved

## Manufacturing Notes
- JLCPCB compatible: Yes
- Text on copper layers becomes actual copper
- Minimum stroke width: 0.15mm
- Text on silkscreen layers is screen-printed

## Related References
- `12-silkscreen-top-text` - Silkscreen text
- `55-graphics-textbox` - Text box element
- `60-different-layers` - Elements on different layers

## Known Issues
- None yet
