"""
Comprehensive tests for PCBParser class.
"""

import pytest
import tempfile
from pathlib import Path

from kicad_pcb_api.core.pcb_parser import PCBParser
from kicad_pcb_api.core.types import (
    Footprint,
    Line,
    Net,
    Pad,
    Point,
    Property,
    Rectangle,
    Track,
    Via,
    Zone,
)


@pytest.fixture
def parser():
    """Provide a PCBParser instance."""
    return PCBParser()


def test_parser_initialization(parser):
    """Test parser initializes with correct defaults."""
    assert parser.version == 20241229
    assert parser.generator == "pcbnew"
    assert parser.generator_version == "9.0"


def test_parse_minimal_pcb(parser):
    """Test parsing a minimal PCB file."""
    minimal_pcb = """(kicad_pcb (version 20241229) (generator pcbnew)
  (general
    (thickness 1.6)
  )
  (paper "A4")
  (layers
    (0 "F.Cu" signal)
    (31 "B.Cu" signal)
  )
  (net 0 "")
)"""

    pcb_data = parser.parse_string(minimal_pcb)

    assert pcb_data["version"] == 20241229
    assert pcb_data["generator"] == "pcbnew"
    assert pcb_data["paper"] == "A4"
    assert len(pcb_data["layers"]) == 2
    assert len(pcb_data["nets"]) == 1
    assert pcb_data["nets"][0].number == 0
    assert pcb_data["nets"][0].name == ""


def test_parse_pcb_with_footprint(parser):
    """Test parsing a PCB with a footprint."""
    pcb_content = """(kicad_pcb (version 20241229) (generator pcbnew)
  (general (thickness 1.6))
  (paper "A4")
  (layers
    (0 "F.Cu" signal)
  )
  (net 0 "")
  (net 1 "GND")

  (footprint "Resistor_SMD:R_0603_1608Metric" (layer "F.Cu")
    (uuid "12345678-1234-1234-1234-123456789abc")
    (at 100 50 90)
    (property "Reference" "R1"
      (at 0 -1.43 90)
      (layer "F.SilkS")
      (uuid "uuid-ref")
      (effects (font (size 1 1) (thickness 0.15)))
    )
    (property "Value" "10k"
      (at 0 1.43 90)
      (layer "F.Fab")
      (uuid "uuid-val")
      (effects (font (size 1 1) (thickness 0.15)))
    )
    (attr smd)
    (fp_line (start -0.8 -0.4) (end 0.8 -0.4)
      (stroke (width 0.1) (type solid))
      (layer "F.Fab")
      (uuid "uuid-line")
    )
    (pad "1" smd rect (at -0.875 0 90) (size 1.05 0.95) (layers "F.Cu" "F.Paste" "F.Mask")
      (net 1 "GND")
      (uuid "uuid-pad1")
    )
    (pad "2" smd rect (at 0.875 0 90) (size 1.05 0.95) (layers "F.Cu" "F.Paste" "F.Mask")
      (net 0 "")
      (uuid "uuid-pad2")
    )
  )
)"""

    pcb_data = parser.parse_string(pcb_content)

    assert len(pcb_data["footprints"]) == 1

    footprint = pcb_data["footprints"][0]
    assert footprint.library == "Resistor_SMD"
    assert footprint.name == "R_0603_1608Metric"
    assert footprint.reference == "R1"
    assert footprint.value == "10k"
    assert footprint.position.x == 100
    assert footprint.position.y == 50
    assert footprint.rotation == 90
    assert footprint.layer == "F.Cu"
    assert footprint.attr == "smd"

    # Check properties
    assert len(footprint.properties) == 2
    ref_prop = footprint.get_property("Reference")
    assert ref_prop is not None
    assert ref_prop.value == "R1"

    # Check graphical elements
    assert len(footprint.lines) == 1
    line = footprint.lines[0]
    assert line.start.x == -0.8
    assert line.start.y == -0.4
    assert line.end.x == 0.8
    assert line.end.y == -0.4

    # Check pads
    assert len(footprint.pads) == 2
    pad1 = footprint.pads[0]
    assert pad1.number == "1"
    assert pad1.type == "smd"
    assert pad1.shape == "rect"
    assert pad1.net == 1
    assert pad1.net_name == "GND"
    assert pad1.size == (1.05, 0.95)


def test_parse_track(parser):
    """Test parsing a track (segment)."""
    pcb_content = """(kicad_pcb (version 20241229) (generator pcbnew)
  (general (thickness 1.6))
  (paper "A4")
  (layers (0 "F.Cu" signal))
  (net 0 "")
  (net 1 "Signal")

  (segment (start 10 20) (end 30 40) (width 0.25) (layer "F.Cu") (net 1)
    (uuid "track-uuid")
  )
)"""

    pcb_data = parser.parse_string(pcb_content)

    assert len(pcb_data["tracks"]) == 1
    track = pcb_data["tracks"][0]
    assert track.start.x == 10
    assert track.start.y == 20
    assert track.end.x == 30
    assert track.end.y == 40
    assert track.width == 0.25
    assert track.layer == "F.Cu"
    assert track.net == 1


def test_parse_via(parser):
    """Test parsing a via."""
    pcb_content = """(kicad_pcb (version 20241229) (generator pcbnew)
  (general (thickness 1.6))
  (paper "A4")
  (layers
    (0 "F.Cu" signal)
    (31 "B.Cu" signal)
  )
  (net 0 "")
  (net 1 "Signal")

  (via (at 50 50) (size 0.8) (drill 0.4) (layers "F.Cu" "B.Cu") (net 1)
    (uuid "via-uuid")
  )
)"""

    pcb_data = parser.parse_string(pcb_content)

    assert len(pcb_data["vias"]) == 1
    via = pcb_data["vias"][0]
    assert via.position.x == 50
    assert via.position.y == 50
    assert via.size == 0.8
    assert via.drill == 0.4
    assert "F.Cu" in via.layers
    assert "B.Cu" in via.layers
    assert via.net == 1


def test_parse_graphics(parser):
    """Test parsing graphics items (lines, rectangles)."""
    pcb_content = """(kicad_pcb (version 20241229) (generator pcbnew)
  (general (thickness 1.6))
  (paper "A4")
  (layers (0 "F.Cu" signal))
  (net 0 "")

  (gr_line (start 0 0) (end 100 0)
    (stroke (width 0.15) (type solid))
    (layer "Edge.Cuts")
    (uuid "line-uuid")
  )

  (gr_rect (start 10 10) (end 90 50)
    (stroke (width 0.1) (type default))
    (fill no)
    (layer "Dwgs.User")
    (uuid "rect-uuid")
  )
)"""

    pcb_data = parser.parse_string(pcb_content)

    assert "graphics" in pcb_data
    assert len(pcb_data["graphics"]) == 2

    # Check line
    line = pcb_data["graphics"][0]
    assert isinstance(line, Line)
    assert line.start.x == 0
    assert line.start.y == 0
    assert line.end.x == 100
    assert line.end.y == 0
    assert line.width == 0.15
    assert line.layer == "Edge.Cuts"

    # Check rectangle
    rect = pcb_data["graphics"][1]
    assert isinstance(rect, Rectangle)
    assert rect.start.x == 10
    assert rect.start.y == 10
    assert rect.end.x == 90
    assert rect.end.y == 50
    assert rect.fill is False


def test_parse_zone(parser):
    """Test parsing a zone (copper pour)."""
    pcb_content = """(kicad_pcb (version 20241229) (generator pcbnew)
  (general (thickness 1.6))
  (paper "A4")
  (layers (0 "F.Cu" signal))
  (net 0 "")
  (net 1 "GND")

  (zone (net 1) (net_name "GND") (layer "F.Cu")
    (uuid "zone-uuid")
    (hatch edge 0.5)
    (connect_pads (clearance 0.5))
    (min_thickness 0.25)
    (filled_areas_thickness yes)
    (fill
      (thermal_gap 0.5)
      (thermal_bridge_width 0.5)
    )
    (polygon
      (pts
        (xy 10 10)
        (xy 90 10)
        (xy 90 50)
        (xy 10 50)
      )
    )
  )
)"""

    pcb_data = parser.parse_string(pcb_content)

    assert len(pcb_data["zones"]) == 1
    zone = pcb_data["zones"][0]
    assert zone.net == 1
    assert zone.net_name == "GND"
    assert zone.layer == "F.Cu"
    assert zone.thermal_relief_gap == 0.5
    assert zone.thermal_relief_bridge == 0.5
    assert zone.min_thickness == 0.25
    assert zone.filled is True
    assert len(zone.polygon) == 4


def test_parse_invalid_format(parser):
    """Test parsing invalid PCB format raises error."""
    invalid_content = "(not_a_pcb)"

    with pytest.raises(ValueError, match="Invalid KiCad PCB format"):
        parser.parse_string(invalid_content)


def test_parse_file_not_found(parser):
    """Test parsing non-existent file raises error."""
    with pytest.raises(FileNotFoundError):
        parser.parse_file("/nonexistent/file.kicad_pcb")


def test_parse_reference_pcb_files(parser):
    """Test parsing actual reference PCB files."""
    # Find reference PCB files
    ref_dir = Path(__file__).parent.parent.parent / "reference-implementations" / "pykicad" / "tests"
    minimal_pcb = ref_dir / "minimal_pcb.kicad_pcb"

    if minimal_pcb.exists():
        pcb_data = parser.parse_file(minimal_pcb)

        # Should have nets and modules
        assert len(pcb_data["nets"]) > 0
        assert len(pcb_data["footprints"]) > 0


def test_round_trip_parsing(parser):
    """Test that parsing and writing preserves data."""
    original_content = """(kicad_pcb (version 20241229) (generator pcbnew) (generator_version "9.0")
  (general
    (thickness 1.6)
  )
  (paper "A4")
  (layers
    (0 "F.Cu" signal)
    (31 "B.Cu" signal)
  )
  (net 0 "")
  (net 1 "Signal")

  (footprint "Resistor_SMD:R_0603_1608Metric" (layer "F.Cu")
    (uuid "test-uuid")
    (at 100 50)
    (property "Reference" "R1"
      (at 0 0 0)
      (layer "F.SilkS")
      (uuid "ref-uuid")
      (effects (font (size 1.0 1.0) (thickness 0.15)))
    )
    (property "Value" "10k"
      (at 0 0 0)
      (layer "F.Fab")
      (uuid "val-uuid")
      (effects (font (size 1.0 1.0) (thickness 0.15)))
    )
    (pad "1" smd rect (at 0 0) (size 1.0 1.0) (layers "F.Cu")
      (uuid "pad-uuid")
    )
    (embedded_fonts no)
  )
  (embedded_fonts no)
)"""

    # Parse
    pcb_data = parser.parse_string(original_content)

    # Write back
    output = parser.dumps(pcb_data)

    # Parse again
    pcb_data2 = parser.parse_string(output)

    # Compare key elements
    assert pcb_data["version"] == pcb_data2["version"]
    assert len(pcb_data["nets"]) == len(pcb_data2["nets"])
    assert len(pcb_data["footprints"]) == len(pcb_data2["footprints"])

    # Compare footprint details
    fp1 = pcb_data["footprints"][0]
    fp2 = pcb_data2["footprints"][0]
    assert fp1.reference == fp2.reference
    assert fp1.value == fp2.value
    assert fp1.position.x == fp2.position.x
    assert fp1.position.y == fp2.position.y


def test_write_file(parser):
    """Test writing PCB data to file."""
    pcb_data = {
        "version": 20241229,
        "generator": "pcbnew",
        "generator_version": "9.0",
        "general": {"thickness": 1.6},
        "paper": "A4",
        "layers": [
            {"number": 0, "canonical_name": "F.Cu", "type": "signal"},
            {"number": 31, "canonical_name": "B.Cu", "type": "signal"},
        ],
        "nets": [Net(0, "")],
        "footprints": [],
        "vias": [],
        "tracks": [],
        "zones": [],
        "embedded_fonts": False,
    }

    with tempfile.NamedTemporaryFile(suffix=".kicad_pcb", delete=False) as tmp:
        tmp_path = Path(tmp.name)

        try:
            # Write file
            parser.write_file(pcb_data, tmp_path)

            # Verify file exists
            assert tmp_path.exists()

            # Read and parse
            pcb_data2 = parser.parse_file(tmp_path)

            # Verify content
            assert pcb_data2["version"] == 20241229
            assert len(pcb_data2["nets"]) == 1

        finally:
            # Clean up
            if tmp_path.exists():
                tmp_path.unlink()


def test_parse_pad_with_drill(parser):
    """Test parsing pads with drill specifications."""
    pcb_content = """(kicad_pcb (version 20241229) (generator pcbnew)
  (general (thickness 1.6))
  (paper "A4")
  (layers (0 "F.Cu" signal))
  (net 0 "")

  (footprint "Connector:Pin" (layer "F.Cu")
    (uuid "fp-uuid")
    (at 50 50)
    (property "Reference" "J1"
      (at 0 0 0)
      (layer "F.SilkS")
      (uuid "ref-uuid")
      (effects (font (size 1.0 1.0) (thickness 0.15)))
    )
    (property "Value" "Conn"
      (at 0 0 0)
      (layer "F.Fab")
      (uuid "val-uuid")
      (effects (font (size 1.0 1.0) (thickness 0.15)))
    )
    (pad "1" thru_hole circle (at 0 0) (size 1.7 1.7) (drill 1.0) (layers "*.Cu" "*.Mask")
      (uuid "pad1-uuid")
    )
    (pad "2" thru_hole oval (at 2.54 0) (size 2.0 1.5) (drill oval 1.2 0.8) (layers "*.Cu" "*.Mask")
      (uuid "pad2-uuid")
    )
    (embedded_fonts no)
  )
)"""

    pcb_data = parser.parse_string(pcb_content)

    footprint = pcb_data["footprints"][0]
    assert len(footprint.pads) == 2

    # Circular drill
    pad1 = footprint.pads[0]
    assert pad1.drill == 1.0

    # Oval drill
    pad2 = footprint.pads[1]
    assert isinstance(pad2.drill, dict)
    assert pad2.drill["shape"] == "oval"
    assert pad2.drill["width"] == 1.2
    assert pad2.drill["height"] == 0.8
