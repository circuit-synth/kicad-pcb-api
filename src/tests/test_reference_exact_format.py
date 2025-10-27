"""
Test exact format preservation for reference PCB files.

These tests verify that our parser/formatter preserves the exact KiCAD format
by comparing generated files against manually-created reference files.
This ensures byte-level compatibility with KiCAD's native output.
"""

import pytest
from pathlib import Path
import difflib
import kicad_pcb_api as kpa


# Get reference directory
REFERENCE_DIR = Path(__file__).parent.parent.parent / "reference-pcbs"


# Phase 1 references (essential - must work perfectly)
PHASE_1_REFS = [
    "01-basic-structure/01-blank-pcb/project.kicad_pcb",
    "01-basic-structure/05-edge-cuts-rectangle/project.kicad_pcb",
    "04-components/16-single-resistor-0603/project.kicad_pcb",
    "05-routing/24-single-trace-straight/project.kicad_pcb",
    "06-vias/30-single-via-through/project.kicad_pcb",
    "02-zones/09-copper-pour-simple/project.kicad_pcb",
]


# Phase 2 references (important features)
PHASE_2_REFS = [
    "06-vias/32-via-blind/project.kicad_pcb",
    "06-vias/33-via-buried/project.kicad_pcb",
    "08-advanced/54-graphics-text/project.kicad_pcb",
    "08-advanced/55-graphics-textbox/project.kicad_pcb",
    "08-advanced/57-graphics-polygon/project.kicad_pcb",
    "08-advanced/58-graphics-circle/project.kicad_pcb",
    "08-advanced/60-different-layers/project.kicad_pcb",
    "08-advanced/44-board-with-dimensions/project.kicad_pcb",
    "02-zones/61-ruled-area/project.kicad_pcb",
]


class TestExactFormatPreservation:
    """Test that load→save preserves exact KiCAD format."""

    @pytest.mark.parametrize("reference_file", PHASE_1_REFS)
    def test_phase1_exact_format(self, reference_file, tmp_path):
        """Test Phase 1 references for exact format preservation."""

        original_path = REFERENCE_DIR / reference_file

        # Skip if file doesn't exist
        if not original_path.exists():
            pytest.skip(f"Reference file not created yet: {reference_file}")

        # Load original
        pcb = kpa.load_pcb(original_path)

        # Save to temp file
        temp_path = tmp_path / "test_output.kicad_pcb"
        pcb.save(temp_path)

        # Read both files as text
        with open(original_path, 'r') as f:
            original_content = f.read()

        with open(temp_path, 'r') as f:
            generated_content = f.read()

        # Compare line by line for better error messages
        original_lines = original_content.splitlines(keepends=True)
        generated_lines = generated_content.splitlines(keepends=True)

        # Generate diff if not identical
        if original_content != generated_content:
            diff = list(difflib.unified_diff(
                original_lines,
                generated_lines,
                fromfile='original',
                tofile='generated',
                lineterm=''
            ))

            # Show first 50 lines of diff
            diff_text = '\n'.join(diff[:50])
            if len(diff) > 50:
                diff_text += f"\n... ({len(diff) - 50} more lines)"

            pytest.fail(
                f"\n\n❌ Format mismatch in {reference_file}\n"
                f"Diff (first 50 lines):\n{diff_text}\n\n"
                f"Original length: {len(original_content)} bytes\n"
                f"Generated length: {len(generated_content)} bytes"
            )

    @pytest.mark.parametrize("reference_file", PHASE_2_REFS)
    def test_phase2_exact_format(self, reference_file, tmp_path):
        """Test Phase 2 references for exact format preservation."""

        original_path = REFERENCE_DIR / reference_file

        # Skip if file doesn't exist
        if not original_path.exists():
            pytest.skip(f"Reference file not created yet: {reference_file}")

        # Load original
        pcb = kpa.load_pcb(original_path)

        # Save to temp file
        temp_path = tmp_path / "test_output.kicad_pcb"
        pcb.save(temp_path)

        # Read both files as text
        with open(original_path, 'r') as f:
            original_content = f.read()

        with open(temp_path, 'r') as f:
            generated_content = f.read()

        # Compare line by line
        if original_content != generated_content:
            original_lines = original_content.splitlines(keepends=True)
            generated_lines = generated_content.splitlines(keepends=True)

            diff = list(difflib.unified_diff(
                original_lines,
                generated_lines,
                fromfile='original',
                tofile='generated',
                lineterm=''
            ))

            diff_text = '\n'.join(diff[:50])
            if len(diff) > 50:
                diff_text += f"\n... ({len(diff) - 50} more lines)"

            pytest.fail(
                f"\n\n❌ Format mismatch in {reference_file}\n"
                f"Diff (first 50 lines):\n{diff_text}"
            )


class TestRoundTripStability:
    """Test that multiple round-trips remain stable."""

    @pytest.mark.parametrize("reference_file", PHASE_1_REFS[:3])  # Test first 3 for speed
    def test_multiple_roundtrips(self, reference_file, tmp_path):
        """Test that load→save→load→save produces identical results."""

        original_path = REFERENCE_DIR / reference_file

        if not original_path.exists():
            pytest.skip(f"Reference file not created yet: {reference_file}")

        # First round-trip
        pcb1 = kpa.load_pcb(original_path)
        temp1 = tmp_path / "roundtrip1.kicad_pcb"
        pcb1.save(temp1)

        # Second round-trip
        pcb2 = kpa.load_pcb(temp1)
        temp2 = tmp_path / "roundtrip2.kicad_pcb"
        pcb2.save(temp2)

        # Third round-trip
        pcb3 = kpa.load_pcb(temp2)
        temp3 = tmp_path / "roundtrip3.kicad_pcb"
        pcb3.save(temp3)

        # Read all three generated files
        with open(temp1, 'r') as f:
            content1 = f.read()
        with open(temp2, 'r') as f:
            content2 = f.read()
        with open(temp3, 'r') as f:
            content3 = f.read()

        # All should be identical
        assert content1 == content2, \
            f"First and second round-trip differ for {reference_file}"
        assert content2 == content3, \
            f"Second and third round-trip differ for {reference_file}"


class TestFormatWhitespace:
    """Test that whitespace and indentation are preserved correctly."""

    def test_indentation_consistency(self):
        """Test that indentation is consistent (2 spaces per level)."""

        reference_file = PHASE_1_REFS[0]  # Test blank PCB
        original_path = REFERENCE_DIR / reference_file

        if not original_path.exists():
            pytest.skip(f"Reference file not created yet: {reference_file}")

        with open(original_path, 'r') as f:
            lines = f.readlines()

        # Check that indentation uses 2 spaces
        for i, line in enumerate(lines, 1):
            if line.strip() and not line.startswith(')'):
                # Count leading spaces
                spaces = len(line) - len(line.lstrip(' '))

                # Should be multiple of 2
                if spaces > 0:
                    assert spaces % 2 == 0, \
                        f"Line {i} has {spaces} leading spaces (not multiple of 2): {line.rstrip()}"


class TestSExpressionStructure:
    """Test that S-expression structure is correct."""

    def test_balanced_parentheses(self):
        """Test that all parentheses are balanced."""

        for reference_file in PHASE_1_REFS:
            original_path = REFERENCE_DIR / reference_file

            if not original_path.exists():
                continue

            with open(original_path, 'r') as f:
                content = f.read()

            # Count parentheses
            open_count = content.count('(')
            close_count = content.count(')')

            assert open_count == close_count, \
                f"Unbalanced parentheses in {reference_file}: {open_count} open, {close_count} close"

    def test_no_trailing_whitespace(self):
        """Test that there's no trailing whitespace on lines."""

        for reference_file in PHASE_1_REFS[:2]:  # Test first 2 for speed
            original_path = REFERENCE_DIR / reference_file

            if not original_path.exists():
                continue

            with open(original_path, 'r') as f:
                lines = f.readlines()

            for i, line in enumerate(lines, 1):
                # Check no trailing whitespace (except newline)
                stripped = line.rstrip('\n\r')
                if stripped != stripped.rstrip():
                    pytest.fail(
                        f"Line {i} has trailing whitespace in {reference_file}: {repr(line)}"
                    )


class TestFileEncoding:
    """Test that file encoding is correct."""

    def test_utf8_encoding(self):
        """Test that all files are valid UTF-8."""

        for reference_file in PHASE_1_REFS + PHASE_2_REFS:
            original_path = REFERENCE_DIR / reference_file

            if not original_path.exists():
                continue

            try:
                with open(original_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Try to encode back to UTF-8
                    content.encode('utf-8')
            except UnicodeDecodeError as e:
                pytest.fail(f"File {reference_file} is not valid UTF-8: {e}")
            except UnicodeEncodeError as e:
                pytest.fail(f"File {reference_file} contains invalid UTF-8 characters: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
