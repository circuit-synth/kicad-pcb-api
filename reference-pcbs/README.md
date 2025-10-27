# KiCAD PCB Reference Files

This directory contains reference KiCAD PCB files for testing, validation, and documentation of kicad-pcb-api. Each reference file demonstrates a specific PCB feature or element in isolation.

## Purpose

These reference files serve multiple purposes:

1. **Round-trip Fidelity Testing** - Ensure parser/formatter preserves every detail
2. **Regression Testing** - Catch breaking changes in KiCAD format or our library
3. **Feature Validation** - Verify we handle all PCB elements correctly
4. **Documentation** - Show exactly what output should look like
5. **Debugging** - Compare our generated files against KiCAD's native output
6. **Integration Testing** - Validate circuit-synth → kicad-pcb-api conversion

## Organization

References are organized by category and numbered for easy reference:

```
reference-pcbs/
├── 01-basic-structure/     # Empty PCBs, basic board setup
├── 02-zones/               # Copper pours, keepout zones
├── 03-silkscreen/          # Silkscreen text and graphics
├── 04-components/          # Footprints and components
├── 05-routing/             # Traces and routing
├── 06-vias/                # Through, blind, buried vias
├── 07-circuits/            # Complete circuits
├── 08-advanced/            # Advanced features
└── 09-edge-cases/          # Edge cases and unusual configurations
```

## Phase 1: Essential References (Priority ⭐⭐⭐)

These 6 references cover 90% of common PCB use cases:

| # | Name | Category | Purpose | Status |
|---|------|----------|---------|--------|
| 01 | `01-blank-pcb` | Basic Structure | Empty 2-layer PCB | 📋 TODO |
| 05 | `05-edge-cuts-rectangle` | Basic Structure | Simple rectangular board outline | 📋 TODO |
| 16 | `16-single-resistor-0603` | Components | Basic SMD component (0603) | 📋 TODO |
| 24 | `24-single-trace-straight` | Routing | Single straight trace | 📋 TODO |
| 30 | `30-single-via-through` | Vias | Through-hole via | 📋 TODO |
| 09 | `09-copper-pour-simple` | Zones | Simple ground plane pour | 📋 TODO |

**Start here!** These references provide the foundation for all testing.

## Phase 2: Important References (Priority ⭐⭐)

Expand testing to multi-layer and more complex features:

| # | Name | Category | Purpose | Status |
|---|------|----------|---------|--------|
| 02 | `02-blank-pcb-4layer` | Basic Structure | 4-layer PCB stackup | 📋 TODO |
| 36 | `36-simple-circuit-2-resistors` | Circuits | Complete circuit with nets | 📋 TODO |
| 32 | `32-via-blind` | Vias | Blind via (top to inner) | 📋 TODO |
| 33 | `33-via-buried` | Vias | Buried via (inner to inner) | 📋 TODO |
| 12 | `12-silkscreen-top-text` | Silkscreen | Silkscreen text | 📋 TODO |

## Phase 3: Comprehensive References (Priority ⭐)

Complete coverage of all features and edge cases:

### Basic Structure
- `01-blank-pcb` - Empty PCB (2 layers, default stackup) ⭐⭐⭐
- `02-blank-pcb-4layer` - Empty PCB (4 layers) ⭐⭐
- `03-blank-pcb-6layer` - Empty PCB (6 layers for complex designs)
- `04-pcb-with-title-block` - PCB with title block filled out

### Board Outline & Zones
- `05-edge-cuts-rectangle` - Simple rectangular board outline ⭐⭐⭐
- `06-edge-cuts-rounded` - Board with rounded corners
- `07-edge-cuts-complex` - Complex board shape (cutouts, curves)
- `08-keepout-zone` - Keepout zone on copper layer
- `09-copper-pour-simple` - Simple copper fill/pour (ground plane) ⭐⭐⭐
- `10-copper-pour-with-thermal` - Copper pour with thermal reliefs
- `11-copper-pour-multiple-nets` - Multiple pours (VCC, GND, etc.)

### Silkscreen & Graphics
- `12-silkscreen-top-text` - Text on top silkscreen ⭐⭐
- `13-silkscreen-bottom-text` - Text on bottom silkscreen
- `14-silkscreen-graphics` - Lines, circles, arcs on silkscreen
- `15-silkscreen-logo` - Logo/image on silkscreen (if supported)

### Components/Footprints
- `16-single-resistor-0603` - Single 0603 resistor (SMD) ⭐⭐⭐
- `17-single-resistor-through-hole` - Single through-hole resistor
- `18-single-capacitor-0603` - Single 0603 capacitor
- `19-single-ic-smd` - Single SMD IC (e.g., SOIC-8)
- `20-single-ic-qfp` - Single QFP package IC
- `21-single-ic-bga` - Single BGA package (complex)
- `22-connector-through-hole` - Through-hole connector
- `23-multiple-components` - Mix of components (R, C, IC)

### Routing/Traces
- `24-single-trace-straight` - Single straight trace (top layer) ⭐⭐⭐
- `25-single-trace-curved` - Single curved/angled trace
- `26-trace-with-width-change` - Trace with width changes
- `27-differential-pair` - Differential pair routing
- `28-trace-on-bottom-layer` - Trace on bottom layer
- `29-trace-on-inner-layer` - Trace on inner layer (4-layer board)

### Vias
- `30-single-via-through` - Single through-hole via ⭐⭐⭐
- `31-multiple-vias-through` - Multiple through vias
- `32-via-blind` - Blind via (top to inner layer) ⭐⭐
- `33-via-buried` - Buried via (inner to inner layer) ⭐⭐
- `34-via-micro` - Micro via (if needed for HDI)
- `35-via-in-pad` - Via-in-pad configuration

### Nets & Connections
- `36-simple-circuit-2-resistors` - 2 resistors connected by trace ⭐⭐
- `37-simple-circuit-rc-filter` - RC filter circuit
- `38-power-distribution` - VCC/GND distribution with pours
- `39-multiple-nets` - Multiple named nets

### Advanced Features
- `40-teardrops` - Teardrops on pads/vias
- `41-filled-zones-priority` - Zone priority/ordering
- `42-board-with-mounting-holes` - Mounting holes (NPTH)
- `43-board-with-slots` - Slots in board
- `44-board-with-dimensions` - Dimension annotations
- `45-mixed-technology` - SMD + through-hole components
- `46-high-speed-routing` - Controlled impedance traces
- `47-flex-pcb` - Flexible PCB (if supported)

### Edge Cases
- `48-pad-shapes-various` - Different pad shapes (round, square, oval)
- `49-custom-pad-shape` - Custom pad shape
- `50-footprint-rotated` - Rotated footprints (various angles)
- `51-negative-coordinates` - Components at negative coordinates
- `52-very-small-geometry` - Very small traces/gaps (manufacturing limits)
- `53-very-large-board` - Large board dimensions

## Directory Structure

Each reference follows this structure:

```
16-single-resistor-0603/
├── project.kicad_pcb          # The actual PCB file ⭐ REQUIRED
├── project.kicad_pro          # Project file (optional but recommended)
├── project.kicad_sch          # Schematic (optional, for complete circuits)
├── screenshot.png             # Visual reference (optional)
├── notes.md                   # Documentation ⭐ REQUIRED
└── expected_output.json       # Expected parsed output (optional)
```

### Required Files

**`project.kicad_pcb`** - The reference PCB file
- Created manually in KiCAD
- Should be the simplest possible example of the feature
- No extra elements unless necessary

**`notes.md`** - Documentation for this reference
- See template below
- Describes what this tests
- Lists creation steps
- Documents expected behavior

### Optional Files

**`project.kicad_pro`** - KiCAD project file
- Useful for opening in KiCAD
- Contains board settings

**`screenshot.png`** - Visual reference
- Screenshot from KiCAD's 3D viewer or PCB editor
- Helps quickly identify what the reference demonstrates

**`expected_output.json`** - Expected parsed structure
- JSON representation of what our parser should produce
- Useful for automated testing

## Creating a New Reference

### 1. Create in KiCAD

1. Open KiCAD PCB Editor
2. Create the absolute simplest example of the feature
3. Use standard/common values (e.g., R1, 10k, 0603)
4. Save to appropriate category directory

### 2. Add Documentation

Create `notes.md` from the template (see below).

### 3. (Optional) Add Screenshot

1. In KiCAD, take screenshot of PCB editor
2. Or use 3D viewer for visual reference
3. Save as `screenshot.png`

### 4. Test Round-Trip

```bash
# Test that our library can load and save without changes
cd ../../
source .venv/bin/activate
python -c "
import kicad_pcb_api as kpa
pcb = kpa.load_pcb('reference-pcbs/04-components/16-single-resistor-0603/project.kicad_pcb')
pcb.save('reference-pcbs/04-components/16-single-resistor-0603/project-roundtrip.kicad_pcb')
print('✅ Round-trip test passed')
"
```

### 5. Create Test Case

Add test to `src/tests/test_reference_pcbs.py` (see Testing section below).

## Notes Template

Use this template for each reference's `notes.md`:

```markdown
# [Number] - [Name]

## Purpose
[1-2 sentence description of what this reference demonstrates]

## KiCAD Creation Steps
1. Step 1
2. Step 2
3. ...

## File Contents
List of key elements in the PCB:
- Element 1
- Element 2
- ...

## Key S-expression Elements
S-expression tokens this reference tests:
- `(footprint ...)`
- `(pad ...)`
- ...

## Expected Parser Behavior
- What should be preserved
- What should be validated
- Any special handling needed

## Expected Formatter Behavior
- How it should be written back
- Any formatting requirements

## Round-Trip Requirements
- Should be byte-identical? Or semantically identical?
- Any known variations that are acceptable

## Manufacturing Notes
- JLCPCB compatible? Yes/No
- Minimum trace/space requirements
- Any special manufacturing considerations

## Related References
- Links to related reference files
- What to test next after this one

## Known Issues
- Any known parser/formatter issues
- KiCAD version differences
- Workarounds needed
```

## Testing

### Manual Testing

```bash
# Load and inspect
python -c "
import kicad_pcb_api as kpa
pcb = kpa.load_pcb('reference-pcbs/04-components/16-single-resistor-0603/project.kicad_pcb')
print(f'Footprints: {len(pcb.footprints)}')
print(f'Tracks: {len(pcb.tracks)}')
print(f'Vias: {len(pcb.vias)}')
"

# Test round-trip fidelity
python -c "
import kicad_pcb_api as kpa
original = kpa.load_pcb('reference-pcbs/04-components/16-single-resistor-0603/project.kicad_pcb')
original.save('/tmp/roundtrip.kicad_pcb')
roundtrip = kpa.load_pcb('/tmp/roundtrip.kicad_pcb')
assert original.to_dict() == roundtrip.to_dict()
print('✅ Round-trip test passed')
"
```

### Automated Testing

Test file: `src/tests/test_reference_pcbs.py`

```python
import pytest
from pathlib import Path
import kicad_pcb_api as kpa

REFERENCE_DIR = Path(__file__).parent.parent.parent / "reference-pcbs"

# Phase 1 references (essential)
PHASE_1_REFS = [
    "01-basic-structure/01-blank-pcb/project.kicad_pcb",
    "01-basic-structure/05-edge-cuts-rectangle/project.kicad_pcb",
    "04-components/16-single-resistor-0603/project.kicad_pcb",
    "05-routing/24-single-trace-straight/project.kicad_pcb",
    "06-vias/30-single-via-through/project.kicad_pcb",
    "02-zones/09-copper-pour-simple/project.kicad_pcb",
]

@pytest.mark.parametrize("reference_file", PHASE_1_REFS)
def test_phase1_round_trip(reference_file, tmp_path):
    """Test Phase 1 references for round-trip fidelity."""
    original_path = REFERENCE_DIR / reference_file

    # Skip if file doesn't exist yet
    if not original_path.exists():
        pytest.skip(f"Reference file not created yet: {reference_file}")

    # Load
    pcb = kpa.load_pcb(original_path)

    # Save to temp
    temp_path = tmp_path / "roundtrip.kicad_pcb"
    pcb.save(temp_path)

    # Load again
    pcb2 = kpa.load_pcb(temp_path)

    # Compare
    assert pcb.to_dict() == pcb2.to_dict()
```

Run tests:

```bash
pytest src/tests/test_reference_pcbs.py -v
```

## Workflow Summary

1. **Create in KiCAD** - Make the reference PCB file
2. **Document** - Fill out `notes.md` template
3. **Test** - Verify round-trip works
4. **Add Test** - Add automated test case
5. **Commit** - Commit reference and documentation

## Status Tracking

| Phase | Total | Created | Tested | Status |
|-------|-------|---------|--------|--------|
| Phase 1 | 6 | 0 | 0 | 📋 Not Started |
| Phase 2 | 5 | 0 | 0 | 📋 Not Started |
| Phase 3 | 42 | 0 | 0 | 📋 Not Started |
| **Total** | **53** | **0** | **0** | **0%** |

## Contributing

When creating new references:

1. Follow the directory structure
2. Use the notes template
3. Keep references minimal (one feature at a time)
4. Test round-trip fidelity
5. Add automated tests
6. Update this README with status

## Questions?

See `INTEGRATION.md` for integration guidance or open an issue on GitHub.
