# 55 - Graphics Text Box

## Purpose
Demonstrates a text box element on the PCB with defined boundaries. This tests text box parsing, multi-line text, and box boundary handling.

## KiCAD Creation Steps
1. Copy blank template to this directory: `cp -r ../../_templates/blank-template/* .`
2. Rename files: `mv blank.kicad_pcb project.kicad_pcb && mv blank.kicad_pro project.kicad_pro && mv blank.kicad_sch project.kicad_sch && mv blank.kicad_prl project.kicad_prl`
3. Open in KiCAD: `open project.kicad_pcb`
4. Place → Add Text Box (or Shift+T)
5. Draw box from (30, 30) to (70, 50)
6. Enter text: "kicad-pcb-api\nPython library\nfor PCB automation"
7. In text box properties:
   - Layer: Cmts.User (comments layer)
   - Font size: 1.5mm height
   - Thickness: 0.2mm
   - Border: Yes, 0.15mm width
8. Save

## File Contents
- **Board**: 100×80mm rectangle
- **Text Box**: Multi-line text with border
- **Bounds**: (30, 30) to (70, 50)
- **Text**: 3 lines about kicad-pcb-api
- **Layer**: Cmts.User

## Key S-expression Elements
- `(gr_text_box "..." ...)` - Graphics text box element
- `(start x y)` - Top-left corner
- `(end x y)` - Bottom-right corner
- `(layer "...")` - Layer designation
- `(effects (font ...))` - Font properties
- `(border yes/no)` - Border visibility
- `(stroke (width ...) (type ...))` - Border properties

## Expected Parser Behavior
- Parse multi-line text correctly (preserve newlines)
- Extract box boundaries (start/end points)
- Parse border properties
- Preserve font settings

## Expected Formatter Behavior
- Write text box with correct S-expression format
- Escape newlines and special characters properly
- Maintain box dimensions
- Preserve border settings

## Round-Trip Requirements
- Should be semantically identical after round-trip
- Multi-line text must be preserved exactly
- Box boundaries must match
- Border properties must match

## Manufacturing Notes
- JLCPCB compatible: Yes (if on non-manufacturing layer)
- Typically used on documentation layers
- Not printed on final PCB unless on silkscreen
- Useful for assembly notes and documentation

## Related References
- `54-graphics-text` - Simple text element
- `56-graphics-table` - Table element
- `60-different-layers` - Elements on different layers

## Known Issues
- None yet
