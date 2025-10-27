# 60 - Different Layers

## Purpose
Demonstrates various PCB elements placed on different layers (copper, silkscreen, mask, fab, user). This tests layer parsing, multi-layer handling, and layer-specific rendering.

## File Contents
- **Board**: 100×80mm rectangle
- **Elements**: 8 text elements on different layers
- **Layers Tested**: F.Cu, B.Cu, F.SilkS, F.Mask, F.Fab, Dwgs.User, Cmts.User, Eco1.User

## Key S-expression Elements
- `(gr_text "..." ... (layer "..."))` - Text on specific layer

## Manufacturing Notes
- JLCPCB compatible: Depends on layer
  - F.Cu, B.Cu: Yes (copper layers)
  - F.SilkS, B.SilkS: Yes (silkscreen)
  - User layers: No (documentation only)

## Related References
- `54-graphics-text` - Text element basics
- `12-silkscreen-top-text` - Silkscreen layer
