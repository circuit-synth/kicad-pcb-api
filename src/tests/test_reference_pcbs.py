"""
Tests for reference PCB files.

These tests verify that our parser/formatter can correctly handle
reference KiCAD PCB files created manually in KiCAD.
"""

import pytest
from pathlib import Path
import kicad_pcb_api as kpa


# Get reference directory
REFERENCE_DIR = Path(__file__).parent.parent.parent / "reference-pcbs"


# Phase 1 references (essential - must work)
PHASE_1_REFS = [
    "01-basic-structure/01-blank-pcb/project.kicad_pcb",
    "01-basic-structure/05-edge-cuts-rectangle/project.kicad_pcb",
    "04-components/16-single-resistor-0603/project.kicad_pcb",
    "05-routing/24-single-trace-straight/project.kicad_pcb",
    "06-vias/30-single-via-through/project.kicad_pcb",
    "02-zones/09-copper-pour-simple/project.kicad_pcb",
]


# Phase 2 references (important)
PHASE_2_REFS = [
    "01-basic-structure/02-blank-pcb-4layer/project.kicad_pcb",
    "07-circuits/36-simple-circuit-2-resistors/project.kicad_pcb",
    "06-vias/32-via-blind/project.kicad_pcb",
    "06-vias/33-via-buried/project.kicad_pcb",
    "03-silkscreen/12-silkscreen-top-text/project.kicad_pcb",
]


class TestPhase1RoundTrip:
    """Test Phase 1 references for round-trip fidelity."""

    @pytest.mark.parametrize("reference_file", PHASE_1_REFS)
    def test_round_trip_fidelity(self, reference_file, tmp_path):
        """Test that load→save→load preserves PCB data."""

        original_path = REFERENCE_DIR / reference_file

        # Skip if file doesn't exist yet
        if not original_path.exists():
            pytest.skip(f"Reference file not created yet: {reference_file}")

        # Load original
        pcb = kpa.load_pcb(original_path)

        # Save to temp
        temp_path = tmp_path / "roundtrip.kicad_pcb"
        pcb.save(temp_path)

        # Load saved version
        pcb2 = kpa.load_pcb(temp_path)

        # Compare element counts (semantic comparison)
        # TODO: Use to_dict() once implemented
        assert len(pcb.footprints) == len(pcb2.footprints), \
            f"Footprint count mismatch in {reference_file}"
        assert len(pcb.tracks) == len(pcb2.tracks), \
            f"Track count mismatch in {reference_file}"
        assert len(pcb.vias) == len(pcb2.vias), \
            f"Via count mismatch in {reference_file}"


class TestBlankPCB:
    """Tests specific to 01-blank-pcb reference."""

    def test_blank_pcb_properties(self):
        """Test that blank PCB has expected properties."""

        reference_path = REFERENCE_DIR / "01-basic-structure/01-blank-pcb/project.kicad_pcb"

        if not reference_path.exists():
            pytest.skip("Reference file not created yet")

        pcb = kpa.load_pcb(reference_path)

        # Blank PCB should have no components
        assert len(pcb.footprints) == 0, "Blank PCB should have no footprints"

        # Should have no tracks
        assert len(pcb.tracks) == 0, "Blank PCB should have no tracks"

        # Should have no vias
        assert len(pcb.vias) == 0, "Blank PCB should have no vias"


class TestEdgeCutsRectangle:
    """Tests specific to 05-edge-cuts-rectangle reference."""

    def test_board_outline_exists(self):
        """Test that board outline is present and correct."""

        reference_path = REFERENCE_DIR / "01-basic-structure/05-edge-cuts-rectangle/project.kicad_pcb"

        if not reference_path.exists():
            pytest.skip("Reference file not created yet")

        pcb = kpa.load_pcb(reference_path)

        # Should have board outline graphics on Edge.Cuts layer
        # TODO: Add board outline access once implemented
        # For now, just verify it loads without error
        assert pcb is not None


class TestSingleResistor:
    """Tests specific to 16-single-resistor-0603 reference."""

    def test_single_resistor_properties(self):
        """Test that resistor has expected properties."""

        reference_path = REFERENCE_DIR / "04-components/16-single-resistor-0603/project.kicad_pcb"

        if not reference_path.exists():
            pytest.skip("Reference file not created yet")

        pcb = kpa.load_pcb(reference_path)

        # Should have exactly 1 footprint
        assert len(pcb.footprints) == 1, "Should have exactly 1 resistor"

        # Get the resistor
        r1 = pcb.footprints.get_by_reference("R1")
        assert r1 is not None, "Resistor R1 should exist"
        assert r1.value == "10k", "Resistor value should be 10k"

        # Verify library ID
        expected_lib_id = "Resistor_SMD:R_0603_1608Metric"
        # Handle both library:name and just name formats
        assert expected_lib_id in r1.library_id or "R_0603" in r1.library_id

        # Verify position (center of 100x80 board)
        assert r1.x == 50.0, "X position should be 50mm"
        assert r1.y == 40.0, "Y position should be 40mm"

        # Verify rotation
        assert r1.rotation == 0.0, "Rotation should be 0°"

        # Should have 2 pads
        assert len(r1.pads) == 2, "0603 resistor should have 2 pads"


class TestSingleTrace:
    """Tests specific to 24-single-trace-straight reference."""

    def test_single_trace_properties(self):
        """Test that trace has expected properties."""

        reference_path = REFERENCE_DIR / "05-routing/24-single-trace-straight/project.kicad_pcb"

        if not reference_path.exists():
            pytest.skip("Reference file not created yet")

        pcb = kpa.load_pcb(reference_path)

        # Should have exactly 1 track
        assert len(pcb.tracks) == 1, "Should have exactly 1 track"

        track = list(pcb.tracks)[0]

        # Verify coordinates
        assert track.start.x == 20.0, "Track start X should be 20mm"
        assert track.start.y == 40.0, "Track start Y should be 40mm"
        assert track.end.x == 80.0, "Track end X should be 80mm"
        assert track.end.y == 40.0, "Track end Y should be 40mm"

        # Verify width
        assert track.width == 0.25, "Track width should be 0.25mm"

        # Verify layer
        assert track.layer == "F.Cu", "Track should be on F.Cu layer"


class TestSingleVia:
    """Tests specific to 30-single-via-through reference."""

    def test_single_via_properties(self):
        """Test that via has expected properties."""

        reference_path = REFERENCE_DIR / "06-vias/30-single-via-through/project.kicad_pcb"

        if not reference_path.exists():
            pytest.skip("Reference file not created yet")

        pcb = kpa.load_pcb(reference_path)

        # Should have exactly 1 via
        assert len(pcb.vias) == 1, "Should have exactly 1 via"

        via = list(pcb.vias)[0]

        # Verify position (center of board)
        assert via.x == 50.0, "Via X should be 50mm"
        assert via.y == 40.0, "Via Y should be 40mm"

        # Verify dimensions
        assert via.size == 0.8, "Via size should be 0.8mm"
        assert via.drill == 0.4, "Via drill should be 0.4mm"


class TestCopperPour:
    """Tests specific to 09-copper-pour-simple reference."""

    def test_copper_pour_properties(self):
        """Test that copper pour has expected properties."""

        reference_path = REFERENCE_DIR / "02-zones/09-copper-pour-simple/project.kicad_pcb"

        if not reference_path.exists():
            pytest.skip("Reference file not created yet")

        pcb = kpa.load_pcb(reference_path)

        # Should have at least 1 zone
        # TODO: Add zone access once implemented
        # For now, just verify it loads without error
        assert pcb is not None


# ============================================================================
# Phase 2 Tests (run when those references are created)
# ============================================================================

class TestPhase2RoundTrip:
    """Test Phase 2 references for round-trip fidelity."""

    @pytest.mark.parametrize("reference_file", PHASE_2_REFS)
    def test_round_trip_fidelity(self, reference_file, tmp_path):
        """Test that load→save→load preserves PCB data."""

        original_path = REFERENCE_DIR / reference_file

        # Skip if file doesn't exist yet
        if not original_path.exists():
            pytest.skip(f"Reference file not created yet: {reference_file}")

        # Load original
        pcb = kpa.load_pcb(original_path)

        # Save to temp
        temp_path = tmp_path / "roundtrip.kicad_pcb"
        pcb.save(temp_path)

        # Load saved version
        pcb2 = kpa.load_pcb(temp_path)

        # Compare element counts
        assert len(pcb.footprints) == len(pcb2.footprints), \
            f"Footprint count mismatch in {reference_file}"
        assert len(pcb.tracks) == len(pcb2.tracks), \
            f"Track count mismatch in {reference_file}"
        assert len(pcb.vias) == len(pcb2.vias), \
            f"Via count mismatch in {reference_file}"


# ============================================================================
# Utility Tests
# ============================================================================

class TestReferenceStructure:
    """Test that reference directory structure is correct."""

    def test_phase1_directories_exist(self):
        """Test that all Phase 1 directories exist."""

        expected_dirs = [
            "01-basic-structure/01-blank-pcb",
            "01-basic-structure/05-edge-cuts-rectangle",
            "04-components/16-single-resistor-0603",
            "05-routing/24-single-trace-straight",
            "06-vias/30-single-via-through",
            "02-zones/09-copper-pour-simple",
        ]

        for dir_path in expected_dirs:
            full_path = REFERENCE_DIR / dir_path
            assert full_path.exists(), f"Reference directory should exist: {dir_path}"
            assert full_path.is_dir(), f"Should be a directory: {dir_path}"

    def test_notes_files_exist(self):
        """Test that all Phase 1 notes.md files exist."""

        expected_notes = [
            "01-basic-structure/01-blank-pcb/notes.md",
            "01-basic-structure/05-edge-cuts-rectangle/notes.md",
            "04-components/16-single-resistor-0603/notes.md",
            "05-routing/24-single-trace-straight/notes.md",
            "06-vias/30-single-via-through/notes.md",
            "02-zones/09-copper-pour-simple/notes.md",
        ]

        for notes_path in expected_notes:
            full_path = REFERENCE_DIR / notes_path
            assert full_path.exists(), f"Notes file should exist: {notes_path}"
            assert full_path.is_file(), f"Should be a file: {notes_path}"
