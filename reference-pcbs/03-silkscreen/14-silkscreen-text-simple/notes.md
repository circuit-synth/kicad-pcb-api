# 14 - Silkscreen Text Simple

## Purpose
Basic text on front silkscreen layer. Tests silkscreen text rendering.

## KiCAD Creation Steps
1. Open KiCAD PCB Editor
2. File → New Project
3. Draw board outline
4. Select F.SilkS layer
5. Add → Text
6. Type "KiCAD PCB API"
7. Set size: 2mm x 2mm, thickness: 0.3mm
8. Save as `project.kicad_pcb`

## File Contents
- Board outline (100mm x 100mm)
- Text "KiCAD PCB API" on F.SilkS
- Position: (100, 100)
- Font size: 2mm x 2mm

## Key S-expression Elements
- `(gr_text ...)`
- `(layer "F.SilkS")`
- `(effects (font ...) (justify ...))`
- `(at x y rotation)`

## Expected Parser Behavior
- Should parse text element
- Should extract text content
- Should capture font properties
- Should preserve position and rotation

## Expected Formatter Behavior
- Should preserve exact text formatting
- Should maintain layer assignment
- Should preserve justification

## Round-Trip Requirements
- ✅ Should be byte-identical
- Text properties preserved exactly

## Manufacturing Notes
- **JLCPCB Compatible**: Yes
- **Minimum text size**: 1mm height recommended
- **Layer**: Front silkscreen

## Related References
- See `15-silkscreen-logo-simple` for graphics
- Compare with `54-graphics-text` for PCB layer text

## Known Issues
- None
