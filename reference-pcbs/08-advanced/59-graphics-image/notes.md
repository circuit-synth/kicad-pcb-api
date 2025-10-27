# 59 - Graphics Image

## Purpose
Demonstrates an embedded image/bitmap on the PCB (logo, artwork). This tests image parsing, bitmap data handling, and layer placement.

## KiCAD Creation Steps
1. Copy blank template to this directory: `cp -r ../../_templates/blank-template/* .`
2. Rename files: `mv blank.kicad_pcb project.kicad_pcb && mv blank.kicad_pro project.kicad_pro && mv blank.kicad_sch project.kicad_sch && mv blank.kicad_prl project.kicad_prl`
3. Open in KiCAD: `open project.kicad_pcb`
4. Place → Add Image
5. Select a small bitmap image (e.g., company logo, 20×20mm max)
6. Click to place at position (50, 40)
7. In image properties:
   - Layer: F.SilkS (silkscreen)
   - Scale: 1.0
   - Position: (50, 40)
8. Save

## File Contents
- **Board**: 100×80mm rectangle
- **Image**: Bitmap embedded in PCB file
- **Position**: (50.0, 40.0)
- **Layer**: F.SilkS
- **Format**: PNG data encoded in S-expression

## Key S-expression Elements
- `(image ...)` - Image element
- `(at x y rotation)` - Position and rotation
- `(scale ...)` - Image scaling factor
- `(layer "...")` - Layer designation
- `(data "..." ...)` - Base64-encoded image data

## Expected Parser Behavior
- Parse image position and rotation
- Extract scale factor
- Parse layer assignment
- Handle base64-encoded bitmap data
- Preserve image data exactly (binary data)

## Expected Formatter Behavior
- Write image with correct S-expression format
- Encode bitmap data properly (base64)
- Maintain position and scale
- Preserve layer assignment

## Round-Trip Requirements
- Should be semantically identical after round-trip
- Image data must be byte-identical
- Position, scale, rotation must match exactly
- Layer must match

## Manufacturing Notes
- JLCPCB compatible: Yes (on silkscreen only)
- Image resolution affects silkscreen quality
- Typical resolution: 800 DPI minimum
- Keep images small (< 50mm) for clarity
- Black and white only on silkscreen
- Not recommended on copper layers

## Related References
- `15-silkscreen-logo` - Logo on silkscreen
- `54-graphics-text` - Text element
- `60-different-layers` - Elements on different layers

## Known Issues
- Large images increase file size significantly
- Some manufacturers may not support complex images
- Image quality depends on silkscreen resolution
