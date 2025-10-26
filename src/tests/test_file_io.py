"""
Tests for PCB file I/O operations.

Tests loading, saving, and round-trip preservation of PCB files.
"""

import os
import tempfile
from pathlib import Path

import pytest

from kicad_pcb_api.core.pcb_board import PCBBoard


class TestPCBLoading:
    """Tests for loading PCB files."""

    def test_load_nonexistent_file(self):
        """Test loading a file that doesn't exist."""
        pcb = PCBBoard()
        with pytest.raises(FileNotFoundError, match="PCB file not found"):
            pcb.load("nonexistent_file.kicad_pcb")

    def test_load_invalid_extension(self):
        """Test loading a file with wrong extension."""
        pcb = PCBBoard()
        with pytest.raises(ValueError, match="Invalid file extension"):
            pcb.load("test_file.txt")

    def test_load_directory(self, tmp_path):
        """Test loading a directory instead of a file."""
        # Create a directory with .kicad_pcb name (which is invalid)
        test_dir = tmp_path / "test.kicad_pcb"
        test_dir.mkdir()

        pcb = PCBBoard()
        with pytest.raises(ValueError, match="Path is not a file"):
            pcb.load(test_dir)

    def test_load_empty_pcb(self, tmp_path):
        """Test loading an empty PCB file."""
        # Create a minimal valid PCB file
        test_file = tmp_path / "empty.kicad_pcb"
        test_file.write_text(
            '(kicad_pcb (version 20241229) (generator "pcbnew") '
            '(generator_version "9.0") '
            '(general (thickness 1.6)) '
            '(paper "A4") '
            '(layers) '
            '(net 0 ""))'
        )

        pcb = PCBBoard()
        pcb.load(test_file)

        assert pcb.filepath == test_file
        assert not pcb.is_modified
        assert pcb.get_footprint_count() == 0

    def test_load_with_footprints(self, tmp_path):
        """Test loading a PCB with footprints."""
        # Create a PCB file with a footprint
        test_file = tmp_path / "with_footprint.kicad_pcb"
        test_file.write_text(
            '(kicad_pcb (version 20241229) (generator "pcbnew") '
            '(generator_version "9.0") '
            '(general (thickness 1.6)) '
            '(paper "A4") '
            '(layers) '
            '(net 0 "") '
            '(footprint "Resistor_SMD:R_0603_1608Metric" '
            '(layer "F.Cu") '
            '(uuid "12345678-1234-1234-1234-123456789abc") '
            '(at 50 50 0) '
            '(property "Reference" "R1" (at 0 0 0) (layer "F.SilkS") '
            '(uuid "87654321-1234-1234-1234-123456789abc") '
            '(effects (font (size 1 1) (thickness 0.15)))) '
            '(property "Value" "10k" (at 0 0 0) (layer "F.Fab") '
            '(uuid "87654321-1234-1234-1234-123456789abd") '
            '(effects (font (size 1 1) (thickness 0.15))))))'
        )

        pcb = PCBBoard()
        pcb.load(test_file)

        assert pcb.get_footprint_count() == 1
        assert not pcb.is_modified

        fp = pcb.get_footprint("R1")
        assert fp is not None
        assert fp.reference == "R1"
        assert fp.value == "10k"


class TestPCBSaving:
    """Tests for saving PCB files."""

    def test_save_without_filepath(self):
        """Test saving without specifying a filepath and no previous path."""
        pcb = PCBBoard()
        with pytest.raises(ValueError, match="No filepath specified"):
            pcb.save()

    def test_save_with_invalid_extension(self, tmp_path):
        """Test saving with wrong file extension."""
        pcb = PCBBoard()
        with pytest.raises(ValueError, match="Invalid file extension"):
            pcb.save(tmp_path / "test.txt")

    def test_save_new_pcb(self, tmp_path):
        """Test saving a newly created PCB."""
        test_file = tmp_path / "new_board.kicad_pcb"

        pcb = PCBBoard()
        pcb.add_footprint("R1", "Resistor_SMD:R_0603_1608Metric", 50, 50, value="10k")

        assert pcb.is_modified

        pcb.save(test_file)

        assert test_file.exists()
        assert pcb.filepath == test_file
        assert not pcb.is_modified

    def test_save_without_path_after_load(self, tmp_path):
        """Test saving without path argument after loading."""
        test_file = tmp_path / "test.kicad_pcb"

        # Create initial file
        pcb = PCBBoard()
        pcb.save(test_file)

        # Load and modify
        pcb2 = PCBBoard()
        pcb2.load(test_file)
        pcb2.add_footprint("R1", "Resistor_SMD:R_0603_1608Metric", 50, 50)

        assert pcb2.is_modified

        # Save without path (should use loaded path)
        pcb2.save()

        assert not pcb2.is_modified

    def test_save_to_different_path(self, tmp_path):
        """Test saving to a different path than loaded from."""
        file1 = tmp_path / "original.kicad_pcb"
        file2 = tmp_path / "copy.kicad_pcb"

        # Create and save
        pcb = PCBBoard()
        pcb.add_footprint("R1", "Resistor_SMD:R_0603_1608Metric", 50, 50)
        pcb.save(file1)

        # Save to different path
        pcb.save(file2)

        assert file1.exists()
        assert file2.exists()
        assert pcb.filepath == file2  # Path updated to last save


class TestRoundTrip:
    """Tests for round-trip file preservation."""

    def test_simple_round_trip(self, tmp_path):
        """Test that load -> save preserves file content."""
        file1 = tmp_path / "original.kicad_pcb"
        file2 = tmp_path / "roundtrip.kicad_pcb"

        # Create original
        pcb1 = PCBBoard()
        pcb1.add_footprint("R1", "Resistor_SMD:R_0603_1608Metric", 50, 50, value="10k")
        pcb1.add_footprint("R2", "Resistor_SMD:R_0603_1608Metric", 60, 60, value="20k")
        pcb1.save(file1)

        # Load and save
        pcb2 = PCBBoard()
        pcb2.load(file1)
        pcb2.save(file2)

        # Load both and compare
        pcb_orig = PCBBoard()
        pcb_orig.load(file1)

        pcb_roundtrip = PCBBoard()
        pcb_roundtrip.load(file2)

        # Compare footprint counts
        assert pcb_orig.get_footprint_count() == pcb_roundtrip.get_footprint_count()

        # Compare footprints
        for ref in ["R1", "R2"]:
            fp_orig = pcb_orig.get_footprint(ref)
            fp_roundtrip = pcb_roundtrip.get_footprint(ref)

            assert fp_orig is not None
            assert fp_roundtrip is not None
            assert fp_orig.reference == fp_roundtrip.reference
            assert fp_orig.value == fp_roundtrip.value
            assert fp_orig.position.x == fp_roundtrip.position.x
            assert fp_orig.position.y == fp_roundtrip.position.y

    def test_round_trip_with_modification(self, tmp_path):
        """Test round-trip with modifications."""
        test_file = tmp_path / "test.kicad_pcb"

        # Create and save
        pcb1 = PCBBoard()
        pcb1.add_footprint("R1", "Resistor_SMD:R_0603_1608Metric", 50, 50, value="10k")
        pcb1.save(test_file)

        # Load, modify, and save
        pcb2 = PCBBoard()
        pcb2.load(test_file)
        pcb2.add_footprint("R2", "Resistor_SMD:R_0603_1608Metric", 60, 60, value="20k")
        pcb2.save()

        # Load again and verify
        pcb3 = PCBBoard()
        pcb3.load(test_file)

        assert pcb3.get_footprint_count() == 2
        assert pcb3.get_footprint("R1") is not None
        assert pcb3.get_footprint("R2") is not None


class TestModificationTracking:
    """Tests for modification tracking."""

    def test_new_pcb_not_modified(self):
        """Test that a new PCB is not marked as modified."""
        pcb = PCBBoard()
        assert not pcb.is_modified

    def test_loaded_pcb_not_modified(self, tmp_path):
        """Test that a loaded PCB is not marked as modified."""
        test_file = tmp_path / "test.kicad_pcb"

        # Create file
        pcb1 = PCBBoard()
        pcb1.save(test_file)

        # Load it
        pcb2 = PCBBoard()
        pcb2.load(test_file)

        assert not pcb2.is_modified

    def test_adding_footprint_marks_modified(self):
        """Test that adding a footprint marks PCB as modified."""
        pcb = PCBBoard()
        assert not pcb.is_modified

        pcb.add_footprint("R1", "Resistor_SMD:R_0603_1608Metric", 50, 50)

        assert pcb.is_modified

    def test_save_clears_modified(self, tmp_path):
        """Test that saving clears the modified flag."""
        test_file = tmp_path / "test.kicad_pcb"

        pcb = PCBBoard()
        pcb.add_footprint("R1", "Resistor_SMD:R_0603_1608Metric", 50, 50)

        assert pcb.is_modified

        pcb.save(test_file)

        assert not pcb.is_modified

    def test_reset_modified(self):
        """Test manually resetting modified flag."""
        pcb = PCBBoard()
        pcb.add_footprint("R1", "Resistor_SMD:R_0603_1608Metric", 50, 50)

        assert pcb.is_modified

        pcb.reset_modified()

        assert not pcb.is_modified


class TestFileProperties:
    """Tests for file-related properties."""

    def test_filepath_property_none(self):
        """Test filepath property on new PCB."""
        pcb = PCBBoard()
        assert pcb.filepath is None

    def test_filepath_property_after_load(self, tmp_path):
        """Test filepath property after loading."""
        test_file = tmp_path / "test.kicad_pcb"

        # Create file
        pcb1 = PCBBoard()
        pcb1.save(test_file)

        # Load it
        pcb2 = PCBBoard()
        pcb2.load(test_file)

        assert pcb2.filepath == test_file

    def test_filepath_property_after_save(self, tmp_path):
        """Test filepath property after saving."""
        test_file = tmp_path / "test.kicad_pcb"

        pcb = PCBBoard()
        assert pcb.filepath is None

        pcb.save(test_file)

        assert pcb.filepath == test_file


class TestErrorHandling:
    """Tests for error handling."""

    def test_load_malformed_file(self, tmp_path):
        """Test loading a malformed PCB file."""
        test_file = tmp_path / "malformed.kicad_pcb"
        test_file.write_text("This is not valid S-expression data")

        pcb = PCBBoard()
        with pytest.raises(Exception):  # Will raise parsing error
            pcb.load(test_file)

    def test_save_to_readonly_location(self, tmp_path):
        """Test saving to a read-only location."""
        # Create a read-only directory
        readonly_dir = tmp_path / "readonly"
        readonly_dir.mkdir()
        test_file = readonly_dir / "test.kicad_pcb"

        # Make directory read-only
        readonly_dir.chmod(0o444)

        pcb = PCBBoard()

        # This should raise PermissionError
        # Note: This might not work on all systems/filesystems
        try:
            with pytest.raises(PermissionError):
                pcb.save(test_file)
        finally:
            # Restore permissions for cleanup
            readonly_dir.chmod(0o755)

    def test_load_from_constructor(self, tmp_path):
        """Test loading from constructor."""
        test_file = tmp_path / "test.kicad_pcb"

        # Create file
        pcb1 = PCBBoard()
        pcb1.add_footprint("R1", "Resistor_SMD:R_0603_1608Metric", 50, 50)
        pcb1.save(test_file)

        # Load via constructor
        pcb2 = PCBBoard(test_file)

        assert pcb2.get_footprint_count() == 1
        assert pcb2.filepath == test_file
        assert not pcb2.is_modified
