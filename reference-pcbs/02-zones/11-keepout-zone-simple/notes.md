# 11 - Keepout Zone Simple

## Purpose
Basic keepout zone that prevents copper pour in a specific area. Tests keepout zone definition.

## KiCAD Creation Steps
1. Open KiCAD PCB Editor
2. File → New Project
3. Draw board outline
4. Add → Zone → Keepout Area
5. Select F.Cu layer
6. Configure keepout settings (no copper pour, no vias)
7. Draw rectangle
8. Save as `project.kicad_pcb`

## File Contents
- Board outline (100mm x 100mm)
- Rectangular keepout zone on F.Cu (40mm x 40mm)
- No copper pour or vias allowed in zone

## Key S-expression Elements
- `(zone ...)`
- `(keepout ...)`
- `(tracks allowed/not_allowed)`
- `(vias not_allowed)`
- `(copperpour not_allowed)`

## Expected Parser Behavior
- Should parse keepout zone
- Should extract keepout restrictions
- Should identify affected layers

## Expected Formatter Behavior
- Should preserve keepout settings
- Should maintain zone boundaries

## Round-Trip Requirements
- ✅ Should be byte-identical
- Keepout settings preserved exactly

## Manufacturing Notes
- **JLCPCB Compatible**: Yes
- **Purpose**: Define restricted areas
- **Layer count**: 2

## Related References
- Compare with `10-copper-pour-polygon` (filled zone)
- See `09-copper-pour-simple` for basic zones

## Known Issues
- None
