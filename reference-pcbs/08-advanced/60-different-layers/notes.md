# 60 - Different Layers

## Purpose
Demonstrates various PCB elements placed on different layers (copper, silkscreen, mask, fab, user). This tests layer parsing, multi-layer handling, and layer-specific rendering.

## KiCAD Creation Steps
1. Copy blank template to this directory: `cp -r ../../_templates/blank-template/* .`
2. Rename files: `mv blank.kicad_pcb project.kicad_pcb && mv blank.kicad_pro project.kicad_pro && mv blank.kicad_sch project.kicad_sch && mv blank.kicad_prl project.kicad_prl`
3. Open in KiCAD: `open project.kicad_pcb`
4. Add text on multiple layers:
   - Text "F.Cu" at (30, 30) on F.Cu layer (copper)
   - Text "B.Cu" at (30, 45) on B.Cu layer (copper)
   - Text "F.SilkS" at (30, 60) on F.SilkS layer (silkscreen)
   - Text "F.Mask" at (30, 75) on F.Mask layer (soldermask)
   - Text "F.Fab" at (70, 30) on F.Fab layer (fabrication)
   - Text "Dwgs.User" at (70, 45) on Dwgs.User layer (drawings)
   - Text "Cmts.User" at (70, 60) on Cmts.User layer (comments)
   - Text "Eco1.User" at (70, 75) on Eco1.User layer (user layer 1)
5. Add one shape on Edge.Cuts layer:
   - Rectangle outline (board edge)
6. Save

## File Contents
- **Board**: 100×80mm rectangle
- **Elements**: 8 text elements + 1 edge cuts shape
- **Layers Tested**:
  - F.Cu (front copper)
  - B.Cu (back copper)
  - F.SilkS (front silkscreen)
  - F.Mask (front soldermask)
  - F.Fab (front fabrication)
  - Dwgs.User (drawings)
  - Cmts.User (comments)
  - Eco1.User (user eco 1)
  - Edge.Cuts (board outline)

## Key S-expression Elements
- `(gr_text "..." ... (layer "..."))` - Text on specific layer
- `(gr_rect ... (layer "..."))` - Shape on specific layer
- `(layers ...)` - Board layer stackup definition

## Expected Parser Behavior
- Parse layer names correctly for all standard layers
- Handle user-defined layers (Eco, User)
- Preserve layer assignment for each element
- Validate layer names against board stackup

## Expected Formatter Behavior
- Write elements with correct layer designations
- Maintain layer names exactly as defined
- Group elements by type (not by layer)

## Round-Trip Requirements
- Should be semantically identical after round-trip
- All layer assignments must be preserved
- Element positions must match
- Layer names must match exactly

## Manufacturing Notes
- JLCPCB compatible: Depends on layer
  - F.Cu, B.Cu: Yes (copper layers)
  - F.SilkS, B.SilkS: Yes (silkscreen)
  - F.Mask, B.Mask: Yes (soldermask openings)
  - F.Fab, B.Fab: Yes (fabrication drawings, not printed)
  - User layers: No (documentation only)
- Each layer has specific manufacturing purpose
- User/documentation layers ignored during fabrication

## Related References
- `54-graphics-text` - Text element basics
- `57-graphics-polygon` - Graphics shapes
- `12-silkscreen-top-text` - Silkscreen layer

## Known Issues
- None yet
- Layer naming conventions may vary by KiCAD version
