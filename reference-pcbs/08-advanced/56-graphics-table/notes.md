# 56 - Graphics Table

## Purpose
Demonstrates a table element on the PCB. This tests table parsing, cell structure, and grid layout handling.

## KiCAD Creation Steps
1. Copy blank template to this directory: `cp -r ../../_templates/blank-template/* .`
2. Rename files: `mv blank.kicad_pcb project.kicad_pcb && mv blank.kicad_pro project.kicad_pro && mv blank.kicad_sch project.kicad_sch && mv blank.kicad_prl project.kicad_prl`
3. Open in KiCAD: `open project.kicad_pcb`
4. Place → Add Table
5. Draw table area from (20, 20) to (80, 60)
6. Configure table:
   - Rows: 3
   - Columns: 2
   - Layer: Dwgs.User (drawings layer)
7. Fill in table:
   - Row 1: "Component" | "Value"
   - Row 2: "R1" | "10k"
   - Row 3: "C1" | "100nF"
8. In table properties:
   - Border width: 0.15mm
   - Cell padding: 1mm
9. Save

## File Contents
- **Board**: 100×80mm rectangle
- **Table**: 3×2 table with component data
- **Position**: (20, 20) to (80, 60)
- **Layer**: Dwgs.User

## Key S-expression Elements
- `(table ...)` - Table element
- `(column_widths ...)` - Column width specifications
- `(row_heights ...)` - Row height specifications
- `(cells ...)` - Cell content and properties
- `(border ...)` - Border styling
- `(layer "...")` - Layer designation

## Expected Parser Behavior
- Parse table structure (rows × columns)
- Extract all cell contents
- Parse column widths and row heights
- Preserve border properties

## Expected Formatter Behavior
- Write table with correct S-expression format
- Maintain grid structure
- Preserve cell contents
- Write border properties

## Round-Trip Requirements
- Should be semantically identical after round-trip
- Table dimensions (rows/columns) must match
- All cell contents must be preserved
- Border and styling must match

## Manufacturing Notes
- JLCPCB compatible: Depends on layer
- Typically used on documentation layers
- Not printed unless on silkscreen/fab layer
- Useful for BOM, revision history, notes

## Related References
- `54-graphics-text` - Simple text element
- `55-graphics-textbox` - Text box element
- `04-pcb-with-title-block` - Title block with table

## Known Issues
- None yet
- Table support may vary by KiCAD version
