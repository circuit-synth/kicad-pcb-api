# 09 - Copper Pour Simple

## Purpose
Simple rectangular copper pour/fill on top layer for ground plane. Tests zone creation, polygon definition, and fill settings.

## KiCAD Creation Steps
1. Open KiCAD PCB Editor
2. File → New Project
3. Create board outline (100mm x 80mm)
4. Create net "GND" (or use net 0)
5. Add zone/copper pour:
   - Layer: F.Cu
   - Net: GND
   - Outline: Rectangle slightly inside board edge (5mm margin)
     - Coordinates: (5, 5) to (95, 75)
   - Clearance: 0.5mm
   - Min width: 0.25mm
   - Fill type: Solid
   - Priority: 0
6. Fill zones (Tools → Fill All Zones or press 'B')
7. Save as `project.kicad_pcb`

## File Contents
- Board outline (100mm x 80mm)
- 1 filled zone on F.Cu
- Net: GND
- Polygon outline defining zone area
- Fill segments (after zone is filled)
- Clearance settings
- Thermal relief settings (if pads present)

## Key S-expression Elements
- `(zone ...)`
- `(net ...)` - assigned to GND
- `(layer "F.Cu")`
- `(polygon ...)` - zone outline
- `(pts ...)` - polygon points
- `(filled_polygon ...)` - fill result
- `(hatch ...)` - hatch settings
- `(connect_pads ...)` - pad connection settings
- `(min_thickness ...)`
- `(keepout ...)` - keepout settings

## Expected Parser Behavior
- Should parse zone with all properties
- Should extract polygon outline points
- Should parse fill settings
- Should handle filled polygon segments
- Should identify net assignment

## Expected Formatter Behavior
- Should preserve zone outline exactly
- Should maintain fill settings
- Should preserve filled polygon data
- Should maintain net assignment

## Round-Trip Requirements
- ⚠️ Semantic equivalence only
- Fill polygon may be regenerated differently
- Outline must be identical
- Settings must be preserved

## Testing Checklist
- [ ] Load with `kpa.load_pcb()`
- [ ] Verify zone exists
- [ ] Verify net == "GND" or net number
- [ ] Verify layer == F.Cu
- [ ] Verify polygon has 4 corners
- [ ] Verify clearance settings
- [ ] Save and reload
- [ ] Verify zone outline preserved

## Manufacturing Notes
- **JLCPCB Compatible**: Yes
- **Pour area**: ~90mm x 70mm
- **Clearance**: 0.5mm from tracks
- **Min width**: 0.25mm
- **Purpose**: Ground plane for return path

## Related References
- Compare with `10-copper-pour-with-thermal` (thermal reliefs)
- Compare with `11-copper-pour-multiple-nets` (VCC + GND)
- Compare with `08-keepout-zone` (keepout vs pour)

## Known Issues
- Fill polygon may change between saves (copper fill algorithm)
- Outline and settings should be preserved exactly
- Filled segments may differ but should be functionally equivalent

## Example Code

```python
import kicad_pcb_api as kpa

# Load PCB with copper pour
pcb = kpa.load_pcb('reference-pcbs/02-zones/09-copper-pour-simple/project.kicad_pcb')

# Verify zone exists
zones = pcb.zones  # Or however zones are accessed
assert len(zones) > 0

gnd_zone = zones[0]
assert gnd_zone.layer == 'F.Cu'
# Verify net is GND
# assert gnd_zone.net_name == 'GND' or gnd_zone.net == 0

# Verify polygon outline
assert len(gnd_zone.polygon) == 4  # Rectangle has 4 corners

print('✅ Copper pour reference validated')
```

## Visual Reference

```
Top View (F.Cu):
┌─────────────────────────────┐
│  Board Edge                 │
│  ┌─────────────────────┐    │
│  │█████████████████████│    │  ← Copper pour (GND)
│  │█████████████████████│    │
│  │█████████████████████│    │
│  │█████████████████████│    │
│  └─────────────────────┘    │
│     5mm margin              │
└─────────────────────────────┘
```

## S-expression Sample

```lisp
(zone
  (net 0)
  (net_name "GND")
  (layer "F.Cu")
  (hatch edge 0.5)
  (connect_pads (clearance 0.5))
  (min_thickness 0.25)
  (filled_areas_thickness no)
  (keepout (tracks not_allowed) (vias not_allowed) (pads not_allowed) (copperpour allowed) (footprints allowed))
  (fill yes (thermal_gap 0.5) (thermal_bridge_width 0.5))
  (polygon
    (pts
      (xy 5 5)
      (xy 95 5)
      (xy 95 75)
      (xy 5 75)
    )
  )
  ; Filled polygon data follows
)
```
