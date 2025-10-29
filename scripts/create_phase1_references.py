#!/usr/bin/env python3
"""
Create Phase 1 priority reference PCBs programmatically.

This script creates 13 new reference PCBs for kicad-pcb-api testing.
"""

from pathlib import Path

# Base directory
REFERENCE_DIR = Path(__file__).parent.parent / "reference-pcbs"
NOTES_TEMPLATE = Path(__file__).parent.parent / "reference-pcbs" / "NOTES_TEMPLATE.md"


def create_directory(path: Path):
    """Create directory if it doesn't exist."""
    path.mkdir(parents=True, exist_ok=True)
    print(f"✓ Created directory: {path}")


def write_notes(path: Path, content: str):
    """Write notes.md file."""
    with open(path, "w") as f:
        f.write(content)
    print(f"✓ Created notes: {path}")


def create_10_copper_pour_polygon():
    """Create 10-copper-pour-polygon: Polygon-shaped copper pour."""
    print("\n📦 Creating 10-copper-pour-polygon...")

    ref_dir = REFERENCE_DIR / "02-zones" / "10-copper-pour-polygon"
    create_directory(ref_dir)

    # Since creating actual zones programmatically is complex,
    # we'll create a minimal PCB that can be edited in KiCAD
    # For now, create a blank PCB as a placeholder
    pcb_content = """(kicad_pcb (version 20241229) (generator "pcbnew") (generator_version "9.0")
	(general
		(thickness 1.6)
	)
	(paper "A4")
	(layers
		(0 "F.Cu" signal)
		(2 "B.Cu" signal)
		(25 "Edge.Cuts" user)
	)
	(setup
		(pad_to_mask_clearance 0)
	)
	(net 0 "")
	(net 1 "GND")
	(gr_rect
		(start 50 50)
		(end 150 150)
		(stroke (width 0.05) (type solid))
		(fill none)
		(layer "Edge.Cuts")
		(uuid "a2038340-83af-4064-824c-f4571468d80e")
	)
	(zone
		(net 1)
		(net_name "GND")
		(layer "F.Cu")
		(uuid "b3038340-83af-4064-824c-f4571468d80f")
		(hatch edge 0.5)
		(connect_pads (clearance 0.5))
		(min_thickness 0.25)
		(filled_areas_thickness no)
		(fill yes (thermal_gap 0.5) (thermal_bridge_width 0.5))
		(polygon
			(pts
				(xy 60 60)
				(xy 90 60)
				(xy 105 75)
				(xy 105 120)
				(xy 60 120)
			)
		)
	)
	(embedded_fonts no)
)
"""

    pcb_path = ref_dir / "project.kicad_pcb"
    with open(pcb_path, "w") as f:
        f.write(pcb_content)

    notes = """# 10 - Copper Pour Polygon

## Purpose
Polygon-shaped copper pour on F.Cu layer. Tests zone with non-rectangular boundary.

## KiCAD Creation Steps
1. Open KiCAD PCB Editor
2. File → New Project
3. Draw board outline
4. Select F.Cu layer
5. Add zone with polygon boundary (not rectangle)
6. Fill zone
7. Save as `project.kicad_pcb`

## File Contents
- Board outline (100mm x 100mm)
- Polygon-shaped copper zone on F.Cu
- Net: GND
- Fill type: Solid

## Key S-expression Elements
- `(zone ...)`
- `(net ...)`
- `(polygon (pts ...))`
- `(fill yes ...)`
- `(layer "F.Cu")`

## Expected Parser Behavior
- Should parse zone definition
- Should extract polygon points
- Should identify fill parameters
- Should preserve net assignment

## Expected Formatter Behavior
- Should preserve exact polygon coordinates
- Should maintain fill settings
- Should preserve zone properties

## Round-Trip Requirements
- ✅ Should be semantically identical
- Polygon points must be exact
- Fill parameters preserved

## Manufacturing Notes
- **JLCPCB Compatible**: Yes
- **Minimum copper spacing**: 0.127mm
- **Layer count**: 2

## Related References
- Compare with `09-copper-pour-simple` (rectangular zone)
- See `11-keepout-zone-simple` for keepout zones

## Known Issues
- None
"""

    write_notes(ref_dir / "notes.md", notes)
    print(f"✅ Created 10-copper-pour-polygon at {ref_dir}")


def create_11_keepout_zone_simple():
    """Create 11-keepout-zone-simple: Basic keepout zone."""
    print("Creating 11-keepout-zone-simple...")

    ref_dir = REFERENCE_DIR / "02-zones" / "11-keepout-zone-simple"
    create_directory(ref_dir)

    pcb_content = """(kicad_pcb (version 20241229) (generator "pcbnew") (generator_version "9.0")
	(general
		(thickness 1.6)
	)
	(paper "A4")
	(layers
		(0 "F.Cu" signal)
		(2 "B.Cu" signal)
		(25 "Edge.Cuts" user)
	)
	(setup
		(pad_to_mask_clearance 0)
	)
	(net 0 "")
	(gr_rect
		(start 50 50)
		(end 150 150)
		(stroke (width 0.05) (type solid))
		(fill none)
		(layer "Edge.Cuts")
		(uuid "a2038340-83af-4064-824c-f4571468d80e")
	)
	(zone
		(net 0)
		(net_name "")
		(layer "F.Cu")
		(uuid "c4038340-83af-4064-824c-f4571468d80g")
		(name "Keepout1")
		(hatch edge 0.5)
		(connect_pads (clearance 0))
		(min_thickness 0.25)
		(filled_areas_thickness no)
		(keepout (tracks allowed) (vias not_allowed) (pads allowed) (copperpour not_allowed) (footprints allowed))
		(fill (thermal_gap 0.5) (thermal_bridge_width 0.5))
		(polygon
			(pts
				(xy 80 80)
				(xy 120 80)
				(xy 120 120)
				(xy 80 120)
			)
		)
	)
	(embedded_fonts no)
)
"""

    pcb_path = ref_dir / "project.kicad_pcb"
    with open(pcb_path, "w") as f:
        f.write(pcb_content)

    notes = """# 11 - Keepout Zone Simple

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
"""

    write_notes(ref_dir / "notes.md", notes)
    print(f"Created 11-keepout-zone-simple at {ref_dir}")


def create_14_silkscreen_text_simple():
    """Create 14-silkscreen-text-simple: Basic silkscreen text."""
    print("Creating 14-silkscreen-text-simple...")

    ref_dir = REFERENCE_DIR / "03-silkscreen" / "14-silkscreen-text-simple"
    create_directory(ref_dir)

    pcb_content = """(kicad_pcb (version 20241229) (generator "pcbnew") (generator_version "9.0")
	(general
		(thickness 1.6)
	)
	(paper "A4")
	(layers
		(0 "F.Cu" signal)
		(2 "B.Cu" signal)
		(5 "F.SilkS" user "F.Silkscreen")
		(25 "Edge.Cuts" user)
	)
	(setup
		(pad_to_mask_clearance 0)
	)
	(net 0 "")
	(gr_rect
		(start 50 50)
		(end 150 150)
		(stroke (width 0.05) (type solid))
		(fill none)
		(layer "Edge.Cuts")
		(uuid "a2038340-83af-4064-824c-f4571468d80e")
	)
	(gr_text "KiCAD PCB API"
		(at 100 100 0)
		(layer "F.SilkS")
		(uuid "d5038340-83af-4064-824c-f4571468d80h")
		(effects
			(font
				(size 2 2)
				(thickness 0.3)
			)
			(justify left bottom)
		)
	)
	(embedded_fonts no)
)
"""

    pcb_path = ref_dir / "project.kicad_pcb"
    with open(pcb_path, "w") as f:
        f.write(pcb_content)

    notes = """# 14 - Silkscreen Text Simple

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
"""

    write_notes(ref_dir / "notes.md", notes)
    print(f"Created 14-silkscreen-text-simple at {ref_dir}")


def create_15_silkscreen_logo_simple():
    """Create 15-silkscreen-logo-simple: Simple silkscreen graphic."""
    print("Creating 15-silkscreen-logo-simple...")

    ref_dir = REFERENCE_DIR / "03-silkscreen" / "15-silkscreen-logo-simple"
    create_directory(ref_dir)

    pcb_content = """(kicad_pcb (version 20241229) (generator "pcbnew") (generator_version "9.0")
	(general
		(thickness 1.6)
	)
	(paper "A4")
	(layers
		(0 "F.Cu" signal)
		(2 "B.Cu" signal)
		(5 "F.SilkS" user "F.Silkscreen")
		(25 "Edge.Cuts" user)
	)
	(setup
		(pad_to_mask_clearance 0)
	)
	(net 0 "")
	(gr_rect
		(start 50 50)
		(end 150 150)
		(stroke (width 0.05) (type solid))
		(fill none)
		(layer "Edge.Cuts")
		(uuid "a2038340-83af-4064-824c-f4571468d80e")
	)
	(gr_circle
		(center 100 100)
		(end 110 100)
		(stroke (width 0.2) (type solid))
		(fill none)
		(layer "F.SilkS")
		(uuid "e6038340-83af-4064-824c-f4571468d80i")
	)
	(gr_line
		(start 90 100)
		(end 110 100)
		(stroke (width 0.2) (type solid))
		(layer "F.SilkS")
		(uuid "f7038340-83af-4064-824c-f4571468d80j")
	)
	(gr_line
		(start 100 90)
		(end 100 110)
		(stroke (width 0.2) (type solid))
		(layer "F.SilkS")
		(uuid "g8038340-83af-4064-824c-f4571468d80k")
	)
	(embedded_fonts no)
)
"""

    pcb_path = ref_dir / "project.kicad_pcb"
    with open(pcb_path, "w") as f:
        f.write(pcb_content)

    notes = """# 15 - Silkscreen Logo Simple

## Purpose
Simple graphic (circle with crosshairs) on front silkscreen. Tests silkscreen graphics rendering.

## KiCAD Creation Steps
1. Open KiCAD PCB Editor
2. File → New Project
3. Draw board outline
4. Select F.SilkS layer
5. Draw circle (radius 10mm)
6. Draw horizontal and vertical lines through center
7. Save as `project.kicad_pcb`

## File Contents
- Board outline (100mm x 100mm)
- Circle on F.SilkS (radius: 10mm)
- Crosshair lines
- Line width: 0.2mm

## Key S-expression Elements
- `(gr_circle ...)`
- `(gr_line ...)`
- `(layer "F.SilkS")`
- `(stroke (width ...) (type ...))`

## Expected Parser Behavior
- Should parse circle and line graphics
- Should extract geometry (center, radius, endpoints)
- Should capture stroke properties

## Expected Formatter Behavior
- Should preserve exact coordinates
- Should maintain stroke settings
- Should preserve layer assignment

## Round-Trip Requirements
- ✅ Should be byte-identical
- Geometry preserved exactly

## Manufacturing Notes
- **JLCPCB Compatible**: Yes
- **Minimum line width**: 0.15mm recommended
- **Layer**: Front silkscreen

## Related References
- See `14-silkscreen-text-simple` for text
- Compare with `57-graphics-polygon` for filled shapes

## Known Issues
- None
"""

    write_notes(ref_dir / "notes.md", notes)
    print(f"Created 15-silkscreen-logo-simple at {ref_dir}")


def create_17_single_capacitor_0603():
    """Create 17-single-capacitor-0603: SMD capacitor."""
    print("Creating 17-single-capacitor-0603...")

    ref_dir = REFERENCE_DIR / "04-components" / "17-single-capacitor-0603"
    create_directory(ref_dir)

    # This would require actual footprint library integration
    # For now, create a minimal structure
    notes = """# 17 - Single Capacitor 0603

## Purpose
Single 0603 SMD capacitor footprint. Tests basic SMD component placement.

## KiCAD Creation Steps
1. Open KiCAD PCB Editor
2. File → New Project
3. Draw board outline
4. Add → Footprint
5. Select Capacitor_SMD:C_0603_1608Metric
6. Place at (100, 100)
7. Set reference: C1
8. Set value: 100nF
9. Save as `project.kicad_pcb`

## File Contents
- Board outline (100mm x 100mm)
- Single 0603 capacitor
- Reference: C1
- Value: 100nF
- Position: (100, 100)

## Key S-expression Elements
- `(footprint "Capacitor_SMD:C_0603_1608Metric")`
- `(at 100 100 0)`
- `(fp_text reference "C1")`
- `(fp_text value "100nF")`
- `(pad "1" smd ...)`
- `(pad "2" smd ...)`

## Expected Parser Behavior
- Should parse footprint
- Should extract pads (2)
- Should capture position and rotation
- Should preserve reference and value

## Expected Formatter Behavior
- Should preserve footprint library name
- Should maintain pad properties
- Should preserve position exactly

## Round-Trip Requirements
- ✅ Should be byte-identical
- All footprint properties preserved

## Manufacturing Notes
- **JLCPCB Compatible**: Yes
- **Package**: 0603 (1.6mm x 0.8mm)
- **Pads**: 2 SMD
- **Layer**: Top

## Related References
- Compare with `16-single-resistor-0603` (resistor)
- See `18-two-resistors-series` for multiple components
- See `19-resistor-capacitor-rc` for RC circuit

## Known Issues
- Requires KiCAD footprint library
- Create manually in KiCAD
"""

    write_notes(ref_dir / "notes.md", notes)
    print("17-single-capacitor-0603: Create manually in KiCAD (requires footprint library)")


def create_18_two_resistors_series():
    """Create 18-two-resistors-series: Two resistors connected."""
    print("Creating 18-two-resistors-series...")

    ref_dir = REFERENCE_DIR / "04-components" / "18-two-resistors-series"
    create_directory(ref_dir)

    notes = """# 18 - Two Resistors Series

## Purpose
Two 0603 resistors connected in series. Tests multiple components and basic routing.

## KiCAD Creation Steps
1. Open KiCAD PCB Editor
2. File → New Project
3. Draw board outline
4. Add R1: Resistor_SMD:R_0603_1608Metric at (80, 100)
5. Add R2: Resistor_SMD:R_0603_1608Metric at (120, 100)
6. Set values: R1=10k, R2=10k
7. Route trace between R1 pad 2 and R2 pad 1
8. Save as `project.kicad_pcb`

## File Contents
- Board outline (100mm x 100mm)
- Two 0603 resistors
- R1 at (80, 100), value: 10k
- R2 at (120, 100), value: 10k
- Single trace connecting them
- Net: Signal

## Key S-expression Elements
- `(footprint "Resistor_SMD:R_0603_1608Metric")` (x2)
- `(fp_text reference ...)` (R1, R2)
- `(fp_text value ...)` (10k, 10k)
- `(segment ...)` for trace
- `(net ...)` definitions

## Expected Parser Behavior
- Should parse two footprints
- Should extract net connections
- Should capture trace routing
- Should preserve component values

## Expected Formatter Behavior
- Should preserve footprint order
- Should maintain net assignments
- Should preserve trace properties

## Round-Trip Requirements
- ✅ Should be byte-identical
- Component relationships preserved

## Manufacturing Notes
- **JLCPCB Compatible**: Yes
- **Components**: 2x 0603 resistors
- **Trace width**: 0.25mm typical
- **Layer**: Top

## Related References
- Build on `16-single-resistor-0603`
- See `19-resistor-capacitor-rc` for RC circuit
- See `24-single-trace-straight` for routing

## Known Issues
- Requires KiCAD footprint library
- Create manually in KiCAD
"""

    write_notes(ref_dir / "notes.md", notes)
    print("18-two-resistors-series: Create manually in KiCAD (requires footprint library)")


def create_19_resistor_capacitor_rc():
    """Create 19-resistor-capacitor-rc: RC network."""
    print("Creating 19-resistor-capacitor-rc...")

    ref_dir = REFERENCE_DIR / "04-components" / "19-resistor-capacitor-rc"
    create_directory(ref_dir)

    notes = """# 19 - Resistor Capacitor RC

## Purpose
Basic RC filter circuit with resistor and capacitor. Tests mixed component types and circuit layout.

## KiCAD Creation Steps
1. Open KiCAD PCB Editor
2. File → New Project
3. Draw board outline
4. Add R1: Resistor_SMD:R_0603_1608Metric at (80, 100)
5. Add C1: Capacitor_SMD:C_0603_1608Metric at (120, 100)
6. Set values: R1=10k, C1=100nF
7. Route trace between R1 pad 2 and C1 pad 1
8. Add ground connection for C1 pad 2
9. Save as `project.kicad_pcb`

## File Contents
- Board outline (100mm x 100mm)
- R1: 0603 resistor, 10k
- C1: 0603 capacitor, 100nF
- Traces connecting components
- Nets: Signal, GND

## Key S-expression Elements
- `(footprint "Resistor_SMD:R_0603_1608Metric")`
- `(footprint "Capacitor_SMD:C_0603_1608Metric")`
- `(segment ...)` for traces
- `(net ...)` definitions (Signal, GND)

## Expected Parser Behavior
- Should parse both component types
- Should extract net connections
- Should capture circuit topology
- Should preserve values

## Expected Formatter Behavior
- Should preserve component order
- Should maintain net assignments
- Should preserve routing

## Round-Trip Requirements
- ✅ Should be byte-identical
- Circuit integrity preserved

## Manufacturing Notes
- **JLCPCB Compatible**: Yes
- **Components**: 1x resistor, 1x capacitor
- **Cutoff frequency**: ~15.9 Hz (10k, 100nF)
- **Layer**: Top

## Related References
- Build on `16-single-resistor-0603` and `17-single-capacitor-0603`
- See `18-two-resistors-series` for series connection
- See `36-simple-circuit-2-resistors` for complete circuits

## Known Issues
- Requires KiCAD footprint library
- Create manually in KiCAD
"""

    write_notes(ref_dir / "notes.md", notes)
    print("19-resistor-capacitor-rc: Create manually in KiCAD (requires footprint library)")


def create_20_single_ic_soic8():
    """Create 20-single-ic-soic8: Simple IC footprint."""
    print("Creating 20-single-ic-soic8...")

    ref_dir = REFERENCE_DIR / "04-components" / "20-single-ic-soic8"
    create_directory(ref_dir)

    notes = """# 20 - Single IC SOIC8

## Purpose
Single SOIC-8 IC footprint. Tests multi-pin SMD component.

## KiCAD Creation Steps
1. Open KiCAD PCB Editor
2. File → New Project
3. Draw board outline
4. Add → Footprint
5. Select Package_SO:SOIC-8_3.9x4.9mm_P1.27mm
6. Place at (100, 100)
7. Set reference: U1
8. Set value: LM358
9. Save as `project.kicad_pcb`

## File Contents
- Board outline (100mm x 100mm)
- Single SOIC-8 footprint
- Reference: U1
- Value: LM358 (dual op-amp)
- Position: (100, 100)
- 8 SMD pads

## Key S-expression Elements
- `(footprint "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm")`
- `(at 100 100 0)`
- `(fp_text reference "U1")`
- `(fp_text value "LM358")`
- `(pad "1" smd ...)` through `(pad "8" smd ...)`

## Expected Parser Behavior
- Should parse IC footprint
- Should extract all 8 pads
- Should capture position and rotation
- Should preserve reference and value

## Expected Formatter Behavior
- Should preserve footprint library name
- Should maintain all pad properties
- Should preserve position exactly

## Round-Trip Requirements
- ✅ Should be byte-identical
- All IC properties preserved

## Manufacturing Notes
- **JLCPCB Compatible**: Yes
- **Package**: SOIC-8 (3.9mm x 4.9mm)
- **Pitch**: 1.27mm
- **Pads**: 8 SMD
- **Layer**: Top

## Related References
- Compare with `16-single-resistor-0603` (2-pad SMD)
- See `19-single-ic-qfp` for QFP packages
- See `20-single-ic-bga` for BGA packages

## Known Issues
- Requires KiCAD footprint library
- Create manually in KiCAD
"""

    write_notes(ref_dir / "notes.md", notes)
    print("20-single-ic-soic8: Create manually in KiCAD (requires footprint library)")


def create_25_single_trace_curved():
    """Create 25-single-trace-curved: Curved track."""
    print("Creating 25-single-trace-curved...")

    ref_dir = REFERENCE_DIR / "05-routing" / "25-single-trace-curved"
    create_directory(ref_dir)

    # Create PCB with angled trace segments (simulates curve)
    pcb_content = """(kicad_pcb (version 20241229) (generator "pcbnew") (generator_version "9.0")
	(general
		(thickness 1.6)
	)
	(paper "A4")
	(layers
		(0 "F.Cu" signal)
		(2 "B.Cu" signal)
		(25 "Edge.Cuts" user)
	)
	(setup
		(pad_to_mask_clearance 0)
	)
	(net 0 "")
	(net 1 "Signal")
	(gr_rect
		(start 50 50)
		(end 150 150)
		(stroke (width 0.05) (type solid))
		(fill none)
		(layer "Edge.Cuts")
		(uuid "a2038340-83af-4064-824c-f4571468d80e")
	)
	(segment
		(start 70 100)
		(end 85 95)
		(width 0.25)
		(layer "F.Cu")
		(net 1)
		(uuid "h9038340-83af-4064-824c-f4571468d80l")
	)
	(segment
		(start 85 95)
		(end 100 90)
		(width 0.25)
		(layer "F.Cu")
		(net 1)
		(uuid "i0038340-83af-4064-824c-f4571468d80m")
	)
	(segment
		(start 100 90)
		(end 115 90)
		(width 0.25)
		(layer "F.Cu")
		(net 1)
		(uuid "j1038340-83af-4064-824c-f4571468d80n")
	)
	(segment
		(start 115 90)
		(end 130 100)
		(width 0.25)
		(layer "F.Cu")
		(net 1)
		(uuid "k2038340-83af-4064-824c-f4571468d80o")
	)
	(embedded_fonts no)
)
"""

    pcb_path = ref_dir / "project.kicad_pcb"
    with open(pcb_path, "w") as f:
        f.write(pcb_content)

    notes = """# 25 - Single Trace Curved

## Purpose
Curved trace made of multiple angled segments. Tests complex routing geometry.

## KiCAD Creation Steps
1. Open KiCAD PCB Editor
2. File → New Project
3. Draw board outline
4. Select F.Cu layer
5. Route trace with multiple angles to create curve
6. Width: 0.25mm
7. Save as `project.kicad_pcb`

## File Contents
- Board outline (100mm x 100mm)
- Curved trace on F.Cu (4 segments)
- Width: 0.25mm
- Net: Signal
- Approximate S-curve shape

## Key S-expression Elements
- `(segment ...)` (multiple)
- `(start ...) (end ...)`
- `(width 0.25)`
- `(layer "F.Cu")`
- `(net ...)`

## Expected Parser Behavior
- Should parse all segments
- Should preserve exact coordinates
- Should maintain segment connectivity
- Should capture net assignment

## Expected Formatter Behavior
- Should preserve segment order
- Should maintain exact coordinates
- Should preserve width and layer

## Round-Trip Requirements
- ✅ Should be byte-identical
- All segment coordinates exact

## Manufacturing Notes
- **JLCPCB Compatible**: Yes
- **Trace width**: 0.25mm
- **Layer**: Front copper
- **Segments**: 4

## Related References
- Compare with `24-single-trace-straight` (straight trace)
- See `26-two-traces-parallel` for parallel routing
- See `27-differential-pair` for differential pairs

## Known Issues
- KiCAD uses line segments, not true curves
- Multiple segments approximate curve
"""

    write_notes(ref_dir / "notes.md", notes)
    print(f"Created 25-single-trace-curved at {ref_dir}")


def create_26_two_traces_parallel():
    """Create 26-two-traces-parallel: Parallel routing."""
    print("Creating 26-two-traces-parallel...")

    ref_dir = REFERENCE_DIR / "05-routing" / "26-two-traces-parallel"
    create_directory(ref_dir)

    pcb_content = """(kicad_pcb (version 20241229) (generator "pcbnew") (generator_version "9.0")
	(general
		(thickness 1.6)
	)
	(paper "A4")
	(layers
		(0 "F.Cu" signal)
		(2 "B.Cu" signal)
		(25 "Edge.Cuts" user)
	)
	(setup
		(pad_to_mask_clearance 0)
	)
	(net 0 "")
	(net 1 "Signal1")
	(net 2 "Signal2")
	(gr_rect
		(start 50 50)
		(end 150 150)
		(stroke (width 0.05) (type solid))
		(fill none)
		(layer "Edge.Cuts")
		(uuid "a2038340-83af-4064-824c-f4571468d80e")
	)
	(segment
		(start 70 95)
		(end 130 95)
		(width 0.25)
		(layer "F.Cu")
		(net 1)
		(uuid "l3038340-83af-4064-824c-f4571468d80p")
	)
	(segment
		(start 70 105)
		(end 130 105)
		(width 0.25)
		(layer "F.Cu")
		(net 2)
		(uuid "m4038340-83af-4064-824c-f4571468d80q")
	)
	(embedded_fonts no)
)
"""

    pcb_path = ref_dir / "project.kicad_pcb"
    with open(pcb_path, "w") as f:
        f.write(pcb_content)

    notes = """# 26 - Two Traces Parallel

## Purpose
Two parallel traces with controlled spacing. Tests parallel routing and clearance.

## KiCAD Creation Steps
1. Open KiCAD PCB Editor
2. File → New Project
3. Draw board outline
4. Select F.Cu layer
5. Route first trace horizontally
6. Route second trace parallel (10mm spacing)
7. Width: 0.25mm each
8. Save as `project.kicad_pcb`

## File Contents
- Board outline (100mm x 100mm)
- Two parallel traces on F.Cu
- Width: 0.25mm each
- Spacing: 10mm
- Nets: Signal1, Signal2
- Length: ~60mm each

## Key S-expression Elements
- `(segment ...)` (x2)
- `(net 1)` and `(net 2)`
- `(layer "F.Cu")`
- `(width 0.25)`

## Expected Parser Behavior
- Should parse both traces
- Should identify different nets
- Should preserve spacing
- Should capture parallel relationship

## Expected Formatter Behavior
- Should preserve both traces
- Should maintain net assignments
- Should preserve exact coordinates

## Round-Trip Requirements
- ✅ Should be byte-identical
- Spacing preserved exactly

## Manufacturing Notes
- **JLCPCB Compatible**: Yes
- **Trace width**: 0.25mm
- **Trace spacing**: 10mm (wide)
- **Layer**: Front copper

## Related References
- Build on `24-single-trace-straight`
- Compare with `27-differential-pair` (matched length)
- See `46-high-speed-routing` for controlled impedance

## Known Issues
- None
"""

    write_notes(ref_dir / "notes.md", notes)
    print(f"Created 26-two-traces-parallel at {ref_dir}")


def create_27_multi_layer_routing():
    """Create 27-multi-layer-routing: Traces on different layers."""
    print("Creating 27-multi-layer-routing...")

    ref_dir = REFERENCE_DIR / "05-routing" / "27-multi-layer-routing"
    create_directory(ref_dir)

    pcb_content = """(kicad_pcb (version 20241229) (generator "pcbnew") (generator_version "9.0")
	(general
		(thickness 1.6)
	)
	(paper "A4")
	(layers
		(0 "F.Cu" signal)
		(2 "B.Cu" signal)
		(25 "Edge.Cuts" user)
	)
	(setup
		(pad_to_mask_clearance 0)
	)
	(net 0 "")
	(net 1 "Signal")
	(gr_rect
		(start 50 50)
		(end 150 150)
		(stroke (width 0.05) (type solid))
		(fill none)
		(layer "Edge.Cuts")
		(uuid "a2038340-83af-4064-824c-f4571468d80e")
	)
	(segment
		(start 70 100)
		(end 95 100)
		(width 0.25)
		(layer "F.Cu")
		(net 1)
		(uuid "n5038340-83af-4064-824c-f4571468d80r")
	)
	(via
		(at 95 100)
		(size 0.8)
		(drill 0.4)
		(layers "F.Cu" "B.Cu")
		(net 1)
		(uuid "o6038340-83af-4064-824c-f4571468d80s")
	)
	(segment
		(start 95 100)
		(end 130 100)
		(width 0.25)
		(layer "B.Cu")
		(net 1)
		(uuid "p7038340-83af-4064-824c-f4571468d80t")
	)
	(embedded_fonts no)
)
"""

    pcb_path = ref_dir / "project.kicad_pcb"
    with open(pcb_path, "w") as f:
        f.write(pcb_content)

    notes = """# 27 - Multi Layer Routing

## Purpose
Trace routing across multiple layers using via. Tests layer transitions.

## KiCAD Creation Steps
1. Open KiCAD PCB Editor
2. File → New Project
3. Draw board outline
4. Route trace on F.Cu
5. Add via
6. Continue trace on B.Cu
7. Save as `project.kicad_pcb`

## File Contents
- Board outline (100mm x 100mm)
- Trace segment on F.Cu
- Via at layer transition point
- Trace segment on B.Cu
- Net: Signal
- Via size: 0.8mm, drill: 0.4mm

## Key S-expression Elements
- `(segment ...)` on F.Cu
- `(via ...)`
- `(segment ...)` on B.Cu
- `(layers "F.Cu" "B.Cu")`
- `(net ...)` consistent across elements

## Expected Parser Behavior
- Should parse both layer segments
- Should parse via
- Should maintain net continuity
- Should preserve layer assignments

## Expected Formatter Behavior
- Should preserve layer transitions
- Should maintain via properties
- Should preserve net assignment

## Round-Trip Requirements
- ✅ Should be byte-identical
- Layer continuity preserved

## Manufacturing Notes
- **JLCPCB Compatible**: Yes
- **Layers used**: F.Cu, B.Cu
- **Via**: 0.8mm/0.4mm
- **Layer count**: 2

## Related References
- Build on `24-single-trace-straight`
- See `30-single-via-through` for vias
- Compare with `29-trace-on-inner-layer` for 4-layer

## Known Issues
- None
"""

    write_notes(ref_dir / "notes.md", notes)
    print(f"Created 27-multi-layer-routing at {ref_dir}")


def create_31_single_via_blind():
    """Create 31-single-via-blind: Blind via."""
    print("Creating 31-single-via-blind...")

    # Check if it already exists as 32-via-blind
    existing_path = REFERENCE_DIR / "06-vias" / "32-via-blind"
    if existing_path.exists():
        print("32-via-blind already exists, skipping 31-single-via-blind")
        return

    ref_dir = REFERENCE_DIR / "06-vias" / "31-single-via-blind"
    create_directory(ref_dir)

    notes = """# 31 - Single Via Blind

## Purpose
Single blind via connecting top layer to inner layer. Tests blind via definition.

## KiCAD Creation Steps
1. Open KiCAD PCB Editor
2. File → New Project (4-layer board)
3. Draw board outline
4. Add → Via
5. Set type: Blind (F.Cu to In1.Cu)
6. Size: 0.6mm, Drill: 0.3mm
7. Save as `project.kicad_pcb`

## File Contents
- Board outline (100mm x 100mm)
- 4-layer stackup
- Single blind via
- Layers: F.Cu to In1.Cu
- Size: 0.6mm, drill: 0.3mm
- Net: Signal

## Key S-expression Elements
- `(via ...)`
- `(at x y)`
- `(size 0.6)`
- `(drill 0.3)`
- `(layers "F.Cu" "In1.Cu")`
- `(net ...)`

## Expected Parser Behavior
- Should parse blind via
- Should extract layer pair
- Should preserve size and drill
- Should identify as blind via (not through)

## Expected Formatter Behavior
- Should preserve blind via type
- Should maintain layer pair
- Should preserve dimensions

## Round-Trip Requirements
- ✅ Should be byte-identical
- Layer pair preserved exactly

## Manufacturing Notes
- **JLCPCB Compatible**: Yes (may have additional cost)
- **Via type**: Blind
- **Layers**: F.Cu to In1.Cu
- **Layer count**: 4
- **Size**: 0.6mm/0.3mm

## Related References
- Compare with `30-single-via-through` (through via)
- Compare with `33-via-buried` (buried via)
- See `32-via-blind` if duplicate

## Known Issues
- Requires 4-layer board
- Create manually in KiCAD
"""

    write_notes(ref_dir / "notes.md", notes)
    print("31-single-via-blind: Create manually in KiCAD (requires 4-layer board)")


def create_32_via_array_grid():
    """Create 32-via-array-grid: Grid of vias."""
    print("Creating 32-via-array-grid...")

    ref_dir = REFERENCE_DIR / "06-vias" / "32-via-array-grid"
    create_directory(ref_dir)

    # Create a 3x3 grid of vias
    pcb_content = """(kicad_pcb (version 20241229) (generator "pcbnew") (generator_version "9.0")
	(general
		(thickness 1.6)
	)
	(paper "A4")
	(layers
		(0 "F.Cu" signal)
		(2 "B.Cu" signal)
		(25 "Edge.Cuts" user)
	)
	(setup
		(pad_to_mask_clearance 0)
	)
	(net 0 "")
	(net 1 "GND")
	(gr_rect
		(start 50 50)
		(end 150 150)
		(stroke (width 0.05) (type solid))
		(fill none)
		(layer "Edge.Cuts")
		(uuid "a2038340-83af-4064-824c-f4571468d80e")
	)
	(via
		(at 85 85)
		(size 0.8)
		(drill 0.4)
		(layers "F.Cu" "B.Cu")
		(net 1)
		(uuid "q8038340-83af-4064-824c-f4571468d80u")
	)
	(via
		(at 100 85)
		(size 0.8)
		(drill 0.4)
		(layers "F.Cu" "B.Cu")
		(net 1)
		(uuid "r9038340-83af-4064-824c-f4571468d80v")
	)
	(via
		(at 115 85)
		(size 0.8)
		(drill 0.4)
		(layers "F.Cu" "B.Cu")
		(net 1)
		(uuid "s0038340-83af-4064-824c-f4571468d80w")
	)
	(via
		(at 85 100)
		(size 0.8)
		(drill 0.4)
		(layers "F.Cu" "B.Cu")
		(net 1)
		(uuid "t1038340-83af-4064-824c-f4571468d80x")
	)
	(via
		(at 100 100)
		(size 0.8)
		(drill 0.4)
		(layers "F.Cu" "B.Cu")
		(net 1)
		(uuid "u2038340-83af-4064-824c-f4571468d80y")
	)
	(via
		(at 115 100)
		(size 0.8)
		(drill 0.4)
		(layers "F.Cu" "B.Cu")
		(net 1)
		(uuid "v3038340-83af-4064-824c-f4571468d80z")
	)
	(via
		(at 85 115)
		(size 0.8)
		(drill 0.4)
		(layers "F.Cu" "B.Cu")
		(net 1)
		(uuid "w4038340-83af-4064-824c-f4571468d810")
	)
	(via
		(at 100 115)
		(size 0.8)
		(drill 0.4)
		(layers "F.Cu" "B.Cu")
		(net 1)
		(uuid "x5038340-83af-4064-824c-f4571468d811")
	)
	(via
		(at 115 115)
		(size 0.8)
		(drill 0.4)
		(layers "F.Cu" "B.Cu")
		(net 1)
		(uuid "y6038340-83af-4064-824c-f4571468d812")
	)
	(embedded_fonts no)
)
"""

    pcb_path = ref_dir / "project.kicad_pcb"
    with open(pcb_path, "w") as f:
        f.write(pcb_content)

    notes = """# 32 - Via Array Grid

## Purpose
3x3 grid of vias for ground stitching. Tests multiple via handling and array patterns.

## KiCAD Creation Steps
1. Open KiCAD PCB Editor
2. File → New Project
3. Draw board outline
4. Add vias in 3x3 grid pattern
5. Spacing: 15mm horizontal and vertical
6. All vias: 0.8mm size, 0.4mm drill
7. Net: GND
8. Save as `project.kicad_pcb`

## File Contents
- Board outline (100mm x 100mm)
- 9 through vias in 3x3 grid
- Spacing: 15mm x 15mm
- All vias: 0.8mm/0.4mm
- Net: GND
- Center at (100, 100)

## Key S-expression Elements
- `(via ...)` (x9)
- `(at x y)` positions in grid
- `(size 0.8)`
- `(drill 0.4)`
- `(layers "F.Cu" "B.Cu")`
- `(net 1)` (GND)

## Expected Parser Behavior
- Should parse all 9 vias
- Should preserve exact positions
- Should maintain grid pattern
- Should capture common properties

## Expected Formatter Behavior
- Should preserve via order
- Should maintain exact positions
- Should preserve all properties

## Round-Trip Requirements
- ✅ Should be byte-identical
- All via positions exact

## Manufacturing Notes
- **JLCPCB Compatible**: Yes
- **Purpose**: Ground stitching
- **Via count**: 9
- **Grid**: 3x3, 15mm spacing
- **Via size**: 0.8mm/0.4mm

## Related References
- Build on `30-single-via-through`
- See `31-multiple-vias-through` for random placement
- Compare with thermal vias for power dissipation

## Known Issues
- None
"""

    write_notes(ref_dir / "notes.md", notes)
    print(f"Created 32-via-array-grid at {ref_dir}")


def main():
    """Main entry point."""
    print("Starting Phase 1 reference PCB creation...")

    # Create all references
    create_10_copper_pour_polygon()
    create_11_keepout_zone_simple()
    create_14_silkscreen_text_simple()
    create_15_silkscreen_logo_simple()
    create_17_single_capacitor_0603()
    create_18_two_resistors_series()
    create_19_resistor_capacitor_rc()
    create_20_single_ic_soic8()
    create_25_single_trace_curved()
    create_26_two_traces_parallel()
    create_27_multi_layer_routing()
    create_31_single_via_blind()
    create_32_via_array_grid()

    print("✅ Phase 1 reference PCB creation complete!")
    print("Note: Some references require manual creation in KiCAD (see warnings above)")
    print("Next steps:")
    print("1. Open references marked for manual creation in KiCAD")
    print("2. Create the PCB files following the notes.md instructions")
    print("3. Run validation: ./reference-pcbs/create_reference.sh validate-all")
    print("4. Commit the changes to git")


if __name__ == "__main__":
    main()
