"""
Comprehensive tests for DRCManager.

Tests all DRC checks including clearance, connectivity, design rules,
geometry, and layer violations.
"""

import pytest
import math
from pathlib import Path
import sys

# Import directly to avoid circular import issues
sys.path.insert(0, str(Path(__file__).parent.parent))

from kicad_pcb_api.core.types import Point, Footprint, Track, Via, Pad, Line, Layer
from kicad_pcb_api.managers.drc import DRCManager, ValidationIssue


class MockBoard:
    """Mock PCBBoard for testing."""

    def __init__(self):
        self.pcb_data = {
            "footprints": [],
            "tracks": [],
            "vias": [],
            "graphics": [],
        }


@pytest.fixture
def mock_board():
    """Create a mock board for testing."""
    return MockBoard()


@pytest.fixture
def drc_manager(mock_board):
    """Create DRC manager with mock board."""
    return DRCManager(mock_board)


# ========== Design Rule Tests ==========


class TestTrackWidthChecks:
    """Test track width validation."""

    def test_track_below_minimum(self, mock_board, drc_manager):
        """Test detection of tracks below minimum width."""
        # Add track with width below minimum
        mock_board.pcb_data["tracks"] = [
            Track(
                start=Point(0, 0),
                end=Point(10, 0),
                width=0.1,  # Below default 0.127mm
                layer="F.Cu",
                net=1,
                net_name="GND",
                uuid="track1",
            )
        ]

        issues = drc_manager.check_track_widths(min_width=0.127)

        assert len(issues) == 1
        assert issues[0].code == "DRC_TRACK_WIDTH_MIN"
        assert issues[0].level == "error"
        assert "0.100mm" in issues[0].message
        assert issues[0].element1_uuid == "track1"

    def test_track_above_maximum(self, mock_board, drc_manager):
        """Test detection of tracks above maximum width."""
        mock_board.pcb_data["tracks"] = [
            Track(
                start=Point(0, 0),
                end=Point(10, 0),
                width=12.0,  # Above default 10mm
                layer="F.Cu",
                net=1,
                uuid="track1",
            )
        ]

        issues = drc_manager.check_track_widths(max_width=10.0)

        assert len(issues) == 1
        assert issues[0].code == "DRC_TRACK_WIDTH_MAX"
        assert issues[0].level == "warning"
        assert "12.000mm" in issues[0].message

    def test_track_within_limits(self, mock_board, drc_manager):
        """Test that tracks within limits pass."""
        mock_board.pcb_data["tracks"] = [
            Track(
                start=Point(0, 0),
                end=Point(10, 0),
                width=0.5,  # Within limits
                layer="F.Cu",
                net=1,
                uuid="track1",
            )
        ]

        issues = drc_manager.check_track_widths(min_width=0.127, max_width=10.0)

        assert len(issues) == 0


class TestViaSizeChecks:
    """Test via size validation."""

    def test_via_size_below_minimum(self, mock_board, drc_manager):
        """Test detection of vias below minimum size."""
        mock_board.pcb_data["vias"] = [
            Via(
                position=Point(50, 50),
                size=0.3,  # Below 0.4mm default
                drill=0.2,
                layers=["F.Cu", "B.Cu"],
                net=1,
                uuid="via1",
            )
        ]

        issues = drc_manager.check_via_sizes(min_size=0.4)

        assert len(issues) == 1
        assert issues[0].code == "DRC_VIA_SIZE"
        assert issues[0].level == "error"

    def test_via_drill_below_minimum(self, mock_board, drc_manager):
        """Test detection of via drill below minimum."""
        mock_board.pcb_data["vias"] = [
            Via(
                position=Point(50, 50),
                size=0.6,
                drill=0.15,  # Below 0.2mm default
                layers=["F.Cu", "B.Cu"],
                net=1,
                uuid="via1",
            )
        ]

        issues = drc_manager.check_via_sizes(min_drill=0.2)

        assert len(issues) == 1
        assert issues[0].code == "DRC_VIA_DRILL"
        assert issues[0].level == "error"

    def test_via_drill_larger_than_size(self, mock_board, drc_manager):
        """Test detection of via drill larger than pad size."""
        mock_board.pcb_data["vias"] = [
            Via(
                position=Point(50, 50),
                size=0.5,
                drill=0.6,  # Larger than size
                layers=["F.Cu", "B.Cu"],
                net=1,
                uuid="via1",
            )
        ]

        issues = drc_manager.check_via_sizes()

        assert len(issues) == 1
        assert issues[0].code == "DRC_VIA_DRILL_SIZE"
        assert issues[0].level == "error"
        assert "must be smaller than pad size" in issues[0].message


class TestHoleSizeChecks:
    """Test hole size validation."""

    def test_hole_below_minimum(self, mock_board, drc_manager):
        """Test detection of holes below minimum size."""
        footprint = Footprint(
            library="Resistor_SMD",
            name="R_0603_1608Metric",
            position=Point(100, 100),
            reference="R1",
            uuid="fp1",
        )

        footprint.pads = [
            Pad(
                number="1",
                type="thru_hole",
                shape="circle",
                position=Point(0, 0),
                size=(1.0, 1.0),
                drill=0.15,  # Below 0.2mm default
                uuid="pad1",
            )
        ]

        mock_board.pcb_data["footprints"] = [footprint]

        issues = drc_manager.check_hole_sizes(min_hole=0.2)

        assert len(issues) == 1
        assert issues[0].code == "DRC_HOLE_SIZE"
        assert issues[0].level == "error"
        assert "R1" in issues[0].message
        assert "pad 1" in issues[0].message


# ========== Clearance Tests ==========


class TestClearanceChecks:
    """Test clearance validation."""

    def test_track_to_track_clearance_violation(self, mock_board, drc_manager):
        """Test detection of track-to-track clearance violations."""
        mock_board.pcb_data["tracks"] = [
            Track(
                start=Point(0, 0),
                end=Point(10, 0),
                width=0.2,
                layer="F.Cu",
                net=1,
                net_name="GND",
                uuid="track1",
            ),
            Track(
                start=Point(0, 0.25),  # Too close
                end=Point(10, 0.25),
                width=0.2,
                layer="F.Cu",
                net=2,
                net_name="VCC",
                uuid="track2",
            ),
        ]

        issues = drc_manager.check_track_to_track_clearance(min_clearance=0.127)

        assert len(issues) == 1
        assert issues[0].code == "DRC_CLEARANCE_TRACK_TRACK"
        assert issues[0].level == "error"
        assert issues[0].element1_uuid == "track1"
        assert issues[0].element2_uuid == "track2"

    def test_track_to_track_same_net_no_violation(self, mock_board, drc_manager):
        """Test that tracks on same net don't trigger violations."""
        mock_board.pcb_data["tracks"] = [
            Track(
                start=Point(0, 0),
                end=Point(10, 0),
                width=0.2,
                layer="F.Cu",
                net=1,
                uuid="track1",
            ),
            Track(
                start=Point(0, 0.1),  # Close but same net
                end=Point(10, 0.1),
                width=0.2,
                layer="F.Cu",
                net=1,  # Same net
                uuid="track2",
            ),
        ]

        issues = drc_manager.check_track_to_track_clearance(min_clearance=0.127)

        assert len(issues) == 0

    def test_pad_to_pad_clearance_violation(self, mock_board, drc_manager):
        """Test detection of pad-to-pad clearance violations."""
        fp1 = Footprint(
            library="Resistor_SMD",
            name="R_0603_1608Metric",
            position=Point(100, 100),
            reference="R1",
            uuid="fp1",
        )
        fp1.pads = [
            Pad(
                number="1",
                type="smd",
                shape="rect",
                position=Point(0, 0),
                size=(0.8, 0.9),
                layers=["F.Cu"],
                net=1,
                net_name="GND",
                uuid="pad1",
            )
        ]

        fp2 = Footprint(
            library="Resistor_SMD",
            name="R_0603_1608Metric",
            position=Point(100.9, 100),  # Very close
            reference="R2",
            uuid="fp2",
        )
        fp2.pads = [
            Pad(
                number="1",
                type="smd",
                shape="rect",
                position=Point(0, 0),
                size=(0.8, 0.9),
                layers=["F.Cu"],
                net=2,
                net_name="VCC",
                uuid="pad2",
            )
        ]

        mock_board.pcb_data["footprints"] = [fp1, fp2]

        issues = drc_manager.check_pad_to_pad_clearance(min_clearance=0.127)

        assert len(issues) == 1
        assert issues[0].code == "DRC_CLEARANCE_PAD_PAD"
        assert issues[0].level == "error"
        assert "R1.1" in issues[0].message
        assert "R2.1" in issues[0].message


# ========== Connectivity Tests ==========


class TestConnectivityChecks:
    """Test connectivity validation."""

    def test_unconnected_pad_detection(self, mock_board, drc_manager):
        """Test detection of unconnected pads."""
        footprint = Footprint(
            library="Resistor_SMD",
            name="R_0603_1608Metric",
            position=Point(100, 100),
            reference="R1",
            uuid="fp1",
        )
        footprint.pads = [
            Pad(
                number="1",
                type="smd",
                shape="rect",
                position=Point(0, 0),
                size=(0.8, 0.9),
                layers=["F.Cu"],
                net=None,  # Unconnected
                uuid="pad1",
            )
        ]

        mock_board.pcb_data["footprints"] = [footprint]

        issues = drc_manager.check_unconnected_pads()

        assert len(issues) == 1
        assert issues[0].code == "DRC_UNCONNECTED_PAD"
        assert issues[0].level == "warning"
        assert "R1 pin 1" in issues[0].message

    def test_floating_net_detection(self, mock_board, drc_manager):
        """Test detection of floating nets (only one connection)."""
        footprint = Footprint(
            library="Resistor_SMD",
            name="R_0603_1608Metric",
            position=Point(100, 100),
            reference="R1",
            uuid="fp1",
        )
        footprint.pads = [
            Pad(
                number="1",
                type="smd",
                shape="rect",
                position=Point(0, 0),
                size=(0.8, 0.9),
                layers=["F.Cu"],
                net=42,  # Unique net with only one pad
                net_name="FLOATING",
                uuid="pad1",
            )
        ]

        mock_board.pcb_data["footprints"] = [footprint]

        issues = drc_manager.check_floating_nets()

        assert len(issues) == 1
        assert issues[0].code == "DRC_FLOATING_NET"
        assert issues[0].level == "warning"
        assert "FLOATING" in issues[0].message

    def test_net_without_routing(self, mock_board, drc_manager):
        """Test detection of nets with multiple pads but no routing."""
        fp1 = Footprint(
            library="Resistor_SMD",
            name="R_0603_1608Metric",
            position=Point(100, 100),
            reference="R1",
            uuid="fp1",
        )
        fp1.pads = [
            Pad(
                number="1",
                type="smd",
                shape="rect",
                position=Point(0, 0),
                size=(0.8, 0.9),
                net=1,
                net_name="SIGNAL",
            )
        ]

        fp2 = Footprint(
            library="Resistor_SMD",
            name="R_0603_1608Metric",
            position=Point(110, 100),
            reference="R2",
            uuid="fp2",
        )
        fp2.pads = [
            Pad(
                number="1",
                type="smd",
                shape="rect",
                position=Point(0, 0),
                size=(0.8, 0.9),
                net=1,
                net_name="SIGNAL",
            )
        ]

        mock_board.pcb_data["footprints"] = [fp1, fp2]
        # No tracks - should trigger violation

        issues = drc_manager.check_net_connectivity()

        assert len(issues) == 1
        assert issues[0].code == "DRC_NET_NO_ROUTING"
        assert issues[0].level == "error"
        assert "SIGNAL" in issues[0].message


# ========== Geometry Tests ==========


class TestGeometryChecks:
    """Test geometry validation."""

    def test_missing_board_outline(self, mock_board, drc_manager):
        """Test detection of missing board outline."""
        # Empty graphics - no edge cuts
        mock_board.pcb_data["graphics"] = []

        issues = drc_manager.check_board_outline()

        assert len(issues) == 1
        assert issues[0].code == "DRC_NO_BOARD_OUTLINE"
        assert issues[0].level == "error"

    def test_board_outline_with_edge_cuts(self, mock_board, drc_manager):
        """Test that board outline is detected when present."""
        mock_board.pcb_data["graphics"] = [
            Line(
                start=Point(0, 0),
                end=Point(100, 0),
                layer="Edge.Cuts",
                width=0.1,
            ),
            Line(
                start=Point(100, 0),
                end=Point(100, 100),
                layer="Edge.Cuts",
                width=0.1,
            ),
        ]

        issues = drc_manager.check_board_outline()

        # Should not have "no outline" error
        no_outline_errors = [i for i in issues if i.code == "DRC_NO_BOARD_OUTLINE"]
        assert len(no_outline_errors) == 0

    def test_overlapping_footprints(self, mock_board, drc_manager):
        """Test detection of overlapping footprints."""
        fp1 = Footprint(
            library="Resistor_SMD",
            name="R_0603_1608Metric",
            position=Point(100, 100),
            layer="F.Cu",
            reference="R1",
            uuid="fp1",
        )

        fp2 = Footprint(
            library="Resistor_SMD",
            name="R_0603_1608Metric",
            position=Point(102, 100),  # Too close (< 5mm default)
            layer="F.Cu",
            reference="R2",
            uuid="fp2",
        )

        mock_board.pcb_data["footprints"] = [fp1, fp2]

        issues = drc_manager.check_overlapping_footprints()

        assert len(issues) == 1
        assert issues[0].code == "DRC_FOOTPRINT_SPACING"
        assert issues[0].level == "warning"
        assert "R1" in issues[0].message
        assert "R2" in issues[0].message

    def test_courtyard_collision(self, mock_board, drc_manager):
        """Test detection of courtyard collisions."""
        # Create footprints with courtyards
        fp1 = Footprint(
            library="Resistor_SMD",
            name="R_0603_1608Metric",
            position=Point(100, 100),
            layer="F.Cu",
            reference="R1",
            uuid="fp1",
        )
        # Add courtyard lines
        fp1.lines = [
            Line(start=Point(-1, -1), end=Point(1, -1), layer="F.CrtYd", width=0.05),
            Line(start=Point(1, -1), end=Point(1, 1), layer="F.CrtYd", width=0.05),
            Line(start=Point(1, 1), end=Point(-1, 1), layer="F.CrtYd", width=0.05),
            Line(start=Point(-1, 1), end=Point(-1, -1), layer="F.CrtYd", width=0.05),
        ]

        fp2 = Footprint(
            library="Resistor_SMD",
            name="R_0603_1608Metric",
            position=Point(101.5, 100),  # Overlapping courtyard
            layer="F.Cu",
            reference="R2",
            uuid="fp2",
        )
        fp2.lines = [
            Line(start=Point(-1, -1), end=Point(1, -1), layer="F.CrtYd", width=0.05),
            Line(start=Point(1, -1), end=Point(1, 1), layer="F.CrtYd", width=0.05),
            Line(start=Point(1, 1), end=Point(-1, 1), layer="F.CrtYd", width=0.05),
            Line(start=Point(-1, 1), end=Point(-1, -1), layer="F.CrtYd", width=0.05),
        ]

        mock_board.pcb_data["footprints"] = [fp1, fp2]

        issues = drc_manager.check_courtyard_collisions()

        assert len(issues) == 1
        assert issues[0].code == "DRC_COURTYARD_COLLISION"
        assert issues[0].level == "error"


# ========== Layer Tests ==========


class TestLayerChecks:
    """Test layer validation."""

    def test_track_on_invalid_layer(self, mock_board, drc_manager):
        """Test detection of tracks on invalid layers."""
        mock_board.pcb_data["tracks"] = [
            Track(
                start=Point(0, 0),
                end=Point(10, 0),
                width=0.2,
                layer="Dwgs.User",  # Invalid for copper
                net=1,
                uuid="track1",
            )
        ]

        issues = drc_manager.check_invalid_layers()

        assert len(issues) == 1
        assert issues[0].code == "DRC_INVALID_LAYER"
        assert issues[0].level == "error"
        assert "Dwgs.User" in issues[0].message

    def test_footprint_on_invalid_layer(self, mock_board, drc_manager):
        """Test detection of footprints on invalid layers."""
        footprint = Footprint(
            library="Resistor_SMD",
            name="R_0603_1608Metric",
            position=Point(100, 100),
            layer="Cmts.User",  # Invalid for footprint
            reference="R1",
            uuid="fp1",
        )

        mock_board.pcb_data["footprints"] = [footprint]

        issues = drc_manager.check_invalid_layers()

        assert len(issues) == 1
        assert issues[0].code == "DRC_INVALID_LAYER"
        assert issues[0].level == "error"

    def test_through_hole_without_proper_layers(self, mock_board, drc_manager):
        """Test detection of through-hole pads without proper layer coverage."""
        footprint = Footprint(
            library="Resistor_THT",
            name="R_Axial_DIN0207",
            position=Point(100, 100),
            reference="R1",
            uuid="fp1",
        )
        footprint.pads = [
            Pad(
                number="1",
                type="thru_hole",
                shape="circle",
                position=Point(0, 0),
                size=(1.6, 1.6),
                drill=0.8,
                layers=["F.Cu"],  # Missing B.Cu
                uuid="pad1",
            )
        ]

        mock_board.pcb_data["footprints"] = [footprint]

        issues = drc_manager.check_through_hole_violations()

        assert len(issues) == 1
        assert issues[0].code == "DRC_TH_LAYER_COVERAGE"
        assert issues[0].level == "error"
        assert "R1.1" in issues[0].message

    def test_through_hole_marked_as_smd(self, mock_board, drc_manager):
        """Test detection of through-hole components marked as SMD."""
        footprint = Footprint(
            library="Resistor_THT",
            name="R_Axial_DIN0207",
            position=Point(100, 100),
            reference="R1",
            attr="smd",  # Wrong attribute
            uuid="fp1",
        )
        footprint.pads = [
            Pad(
                number="1",
                type="thru_hole",
                shape="circle",
                position=Point(0, 0),
                size=(1.6, 1.6),
                drill=0.8,
                layers=["*.Cu"],
            )
        ]

        mock_board.pcb_data["footprints"] = [footprint]

        issues = drc_manager.check_through_hole_violations()

        assert len(issues) == 1
        assert issues[0].code == "DRC_TH_ATTRIBUTE"
        assert issues[0].level == "warning"


# ========== Integration Tests ==========


class TestDRCIntegration:
    """Test comprehensive DRC checks."""

    def test_check_all_runs_all_checks(self, mock_board, drc_manager):
        """Test that check_all runs all DRC checks."""
        # Add various violations
        mock_board.pcb_data["tracks"] = [
            Track(
                start=Point(0, 0),
                end=Point(10, 0),
                width=0.1,  # Too narrow
                layer="F.Cu",
                net=1,
                uuid="track1",
            )
        ]

        footprint = Footprint(
            library="Resistor_SMD",
            name="R_0603_1608Metric",
            position=Point(100, 100),
            reference="R1",
            uuid="fp1",
        )
        footprint.pads = [
            Pad(
                number="1",
                type="smd",
                shape="rect",
                position=Point(0, 0),
                size=(0.8, 0.9),
                net=None,  # Unconnected
            )
        ]
        mock_board.pcb_data["footprints"] = [footprint]

        issues = drc_manager.check_all()

        # Should have multiple issues from different categories
        assert len(issues) > 0

        # Check that different categories are represented
        categories = set(issue.category for issue in issues)
        assert "design_rule" in categories
        assert "connectivity" in categories

    def test_summary_generation(self, mock_board, drc_manager):
        """Test DRC summary generation."""
        # Add mix of errors and warnings
        mock_board.pcb_data["tracks"] = [
            Track(
                start=Point(0, 0),
                end=Point(10, 0),
                width=0.1,  # Error
                layer="F.Cu",
                net=1,
                uuid="track1",
            ),
            Track(
                start=Point(0, 10),
                end=Point(10, 10),
                width=12.0,  # Warning
                layer="F.Cu",
                net=2,
                uuid="track2",
            ),
        ]

        drc_manager.check_all()

        summary = drc_manager.summary()
        assert "error" in summary
        assert "warning" in summary

    def test_filter_by_severity(self, mock_board, drc_manager):
        """Test filtering issues by severity level."""
        mock_board.pcb_data["tracks"] = [
            Track(
                start=Point(0, 0),
                end=Point(10, 0),
                width=0.1,  # Error
                layer="F.Cu",
                net=1,
                uuid="track1",
            ),
            Track(
                start=Point(0, 10),
                end=Point(10, 10),
                width=12.0,  # Warning
                layer="F.Cu",
                net=2,
                uuid="track2",
            ),
        ]

        drc_manager.check_all()

        errors = drc_manager.get_errors()
        warnings = drc_manager.get_warnings()

        assert len(errors) > 0
        assert len(warnings) > 0
        assert all(issue.level == "error" for issue in errors)
        assert all(issue.level == "warning" for issue in warnings)

    def test_has_errors(self, mock_board, drc_manager):
        """Test has_errors() method."""
        # No issues initially
        assert not drc_manager.has_errors()

        # Add error
        mock_board.pcb_data["tracks"] = [
            Track(
                start=Point(0, 0),
                end=Point(10, 0),
                width=0.1,  # Error
                layer="F.Cu",
                net=1,
                uuid="track1",
            )
        ]

        drc_manager.check_all()
        assert drc_manager.has_errors()

    def test_clear_issues(self, mock_board, drc_manager):
        """Test clearing issues."""
        mock_board.pcb_data["tracks"] = [
            Track(
                start=Point(0, 0),
                end=Point(10, 0),
                width=0.1,
                layer="F.Cu",
                net=1,
                uuid="track1",
            )
        ]

        drc_manager.check_all()
        assert len(drc_manager.issues) > 0

        drc_manager.clear_issues()
        assert len(drc_manager.issues) == 0


# ========== ValidationIssue Tests ==========


class TestValidationIssue:
    """Test ValidationIssue dataclass."""

    def test_validation_issue_creation(self):
        """Test creating a ValidationIssue."""
        issue = ValidationIssue(
            category="clearance",
            message="Test violation",
            level="error",
            code="TEST001",
            location=Point(50, 50),
            element1_uuid="elem1",
            element2_uuid="elem2",
            net_name="GND",
            suggested_fix="Fix it",
        )

        assert issue.category == "clearance"
        assert issue.message == "Test violation"
        assert issue.level == "error"
        assert issue.code == "TEST001"
        assert issue.location.x == 50
        assert issue.location.y == 50

    def test_validation_issue_string_representation(self):
        """Test ValidationIssue string representation."""
        issue = ValidationIssue(
            category="clearance",
            message="Test violation",
            level="error",
            code="TEST001",
            location=Point(50.123, 50.456),
            suggested_fix="Fix it",
        )

        str_repr = str(issue)
        assert "TEST001" in str_repr
        assert "ERROR" in str_repr
        assert "Test violation" in str_repr
        assert "50.123" in str_repr
        assert "Fix it" in str_repr


# ========== Helper Method Tests ==========


class TestHelperMethods:
    """Test DRC helper methods."""

    def test_point_distance(self, drc_manager):
        """Test point distance calculation."""
        p1 = Point(0, 0)
        p2 = Point(3, 4)

        distance = drc_manager._point_distance(p1, p2)
        assert math.isclose(distance, 5.0)

    def test_pad_on_layer(self, drc_manager):
        """Test pad layer checking."""
        pad_with_wildcard = Pad(
            number="1",
            type="thru_hole",
            shape="circle",
            position=Point(0, 0),
            size=(1.0, 1.0),
            layers=["*.Cu"],
        )

        assert drc_manager._pad_on_layer(pad_with_wildcard, "F.Cu")
        assert drc_manager._pad_on_layer(pad_with_wildcard, "B.Cu")

        pad_specific = Pad(
            number="1",
            type="smd",
            shape="rect",
            position=Point(0, 0),
            size=(0.8, 0.9),
            layers=["F.Cu"],
        )

        assert drc_manager._pad_on_layer(pad_specific, "F.Cu")
        assert not drc_manager._pad_on_layer(pad_specific, "B.Cu")

    def test_pads_share_layer(self, drc_manager):
        """Test pad layer sharing check."""
        pad1 = Pad(
            number="1",
            type="smd",
            shape="rect",
            position=Point(0, 0),
            size=(0.8, 0.9),
            layers=["F.Cu"],
        )

        pad2 = Pad(
            number="2",
            type="smd",
            shape="rect",
            position=Point(0, 0),
            size=(0.8, 0.9),
            layers=["F.Cu"],
        )

        pad3 = Pad(
            number="3",
            type="smd",
            shape="rect",
            position=Point(0, 0),
            size=(0.8, 0.9),
            layers=["B.Cu"],
        )

        assert drc_manager._pads_share_layer(pad1, pad2)
        assert not drc_manager._pads_share_layer(pad1, pad3)

    def test_pad_has_proper_layers(self, drc_manager):
        """Test through-hole pad layer validation."""
        th_pad_good = Pad(
            number="1",
            type="thru_hole",
            shape="circle",
            position=Point(0, 0),
            size=(1.6, 1.6),
            layers=["*.Cu"],
        )

        assert drc_manager._pad_has_proper_layers(th_pad_good)

        th_pad_bad = Pad(
            number="1",
            type="thru_hole",
            shape="circle",
            position=Point(0, 0),
            size=(1.6, 1.6),
            layers=["F.Cu"],  # Missing B.Cu
        )

        assert not drc_manager._pad_has_proper_layers(th_pad_bad)

        smd_pad = Pad(
            number="1",
            type="smd",
            shape="rect",
            position=Point(0, 0),
            size=(0.8, 0.9),
            layers=["F.Cu"],
        )

        # SMD pads always pass this check
        assert drc_manager._pad_has_proper_layers(smd_pad)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
