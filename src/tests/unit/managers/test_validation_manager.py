"""
Unit tests for ValidationManager class.

Tests board-level validation including reference checking,
net validation, placement validation, and layer validation.
"""

from unittest.mock import Mock
import pytest

from kicad_pcb_api.managers.validation import ValidationManager, ValidationIssue
from kicad_pcb_api.core.types import Point


@pytest.fixture
def mock_board():
    """Create a mock PCBBoard instance."""
    board = Mock()
    board.pcb_data = {
        "footprints": [],
        "tracks": [],
        "vias": []
    }
    return board


@pytest.fixture
def validation_manager(mock_board):
    """Create ValidationManager instance with mock board."""
    return ValidationManager(mock_board)


@pytest.mark.unit
class TestValidationManager:
    """Test cases for ValidationManager."""

    def test_initialization_creates_empty_issues_list(self, mock_board):
        """Test ValidationManager initializes with empty issues list."""
        manager = ValidationManager(mock_board)

        assert manager.board is mock_board
        assert len(manager.issues) == 0
        assert isinstance(manager.issues, list)

    def test_validate_references_finds_duplicate_references(self, validation_manager, mock_board):
        """Test validate_references finds duplicate component references."""
        footprint1 = Mock()
        footprint1.reference = "R1"
        footprint1.uuid = "uuid-1"

        footprint2 = Mock()
        footprint2.reference = "R1"  # Duplicate
        footprint2.uuid = "uuid-2"

        mock_board.pcb_data["footprints"] = [footprint1, footprint2]

        issues = validation_manager.validate_references()

        assert issues == 1
        assert len(validation_manager.issues) == 1
        assert validation_manager.issues[0].category == "reference"
        assert validation_manager.issues[0].severity == "error"
        assert "Duplicate reference: R1" in validation_manager.issues[0].description

    def test_validate_references_finds_missing_references(self, validation_manager, mock_board):
        """Test validate_references finds footprints with no reference."""
        footprint = Mock()
        footprint.reference = ""  # Missing reference
        footprint.uuid = "uuid-1"

        mock_board.pcb_data["footprints"] = [footprint]

        issues = validation_manager.validate_references()

        assert issues == 1
        assert len(validation_manager.issues) == 1
        assert validation_manager.issues[0].category == "reference"
        assert "no reference designator" in validation_manager.issues[0].description

    def test_validate_references_passes_with_unique_references(self, validation_manager, mock_board):
        """Test validate_references passes when all references unique."""
        footprint1 = Mock()
        footprint1.reference = "R1"
        footprint1.uuid = "uuid-1"

        footprint2 = Mock()
        footprint2.reference = "C1"
        footprint2.uuid = "uuid-2"

        mock_board.pcb_data["footprints"] = [footprint1, footprint2]

        issues = validation_manager.validate_references()

        assert issues == 0
        assert len(validation_manager.issues) == 0

    def test_validate_nets_finds_inconsistent_net_names(self, validation_manager, mock_board):
        """Test validate_nets finds inconsistent net names for same net number."""
        footprint1 = Mock()
        pad1 = Mock()
        pad1.net = 5
        pad1.net_name = "VCC"
        footprint1.pads = [pad1]

        footprint2 = Mock()
        pad2 = Mock()
        pad2.net = 5
        pad2.net_name = "VDD"  # Different name for same net
        footprint2.pads = [pad2]

        mock_board.pcb_data["footprints"] = [footprint1, footprint2]

        issues = validation_manager.validate_nets()

        assert issues == 1
        assert len(validation_manager.issues) == 1
        assert validation_manager.issues[0].category == "net"
        assert validation_manager.issues[0].severity == "warning"
        assert "inconsistent names" in validation_manager.issues[0].description

    def test_validate_nets_passes_with_consistent_names(self, validation_manager, mock_board):
        """Test validate_nets passes when net names consistent."""
        footprint1 = Mock()
        pad1 = Mock()
        pad1.net = 5
        pad1.net_name = "GND"
        footprint1.pads = [pad1]

        footprint2 = Mock()
        pad2 = Mock()
        pad2.net = 5
        pad2.net_name = "GND"  # Same name
        footprint2.pads = [pad2]

        mock_board.pcb_data["footprints"] = [footprint1, footprint2]

        issues = validation_manager.validate_nets()

        assert issues == 0

    def test_validate_placement_finds_overlapping_components(self, validation_manager, mock_board):
        """Test validate_placement finds components at same position."""
        footprint1 = Mock()
        footprint1.reference = "R1"
        footprint1.position = Point(50.0, 100.0)
        footprint1.uuid = "uuid-1"

        footprint2 = Mock()
        footprint2.reference = "C1"
        footprint2.position = Point(50.0, 100.0)  # Same position
        footprint2.uuid = "uuid-2"

        mock_board.pcb_data["footprints"] = [footprint1, footprint2]

        issues = validation_manager.validate_placement()

        assert issues == 1
        assert len(validation_manager.issues) == 1
        assert validation_manager.issues[0].category == "placement"
        assert "same position" in validation_manager.issues[0].description

    def test_validate_placement_passes_with_different_positions(self, validation_manager, mock_board):
        """Test validate_placement passes when components at different positions."""
        footprint1 = Mock()
        footprint1.reference = "R1"
        footprint1.position = Point(50.0, 100.0)

        footprint2 = Mock()
        footprint2.reference = "C1"
        footprint2.position = Point(60.0, 110.0)

        mock_board.pcb_data["footprints"] = [footprint1, footprint2]

        issues = validation_manager.validate_placement()

        assert issues == 0

    def test_validate_layers_finds_tracks_on_non_copper(self, validation_manager, mock_board):
        """Test validate_layers finds tracks on non-copper layers."""
        track = Mock()
        track.layer = "F.SilkS"  # Not a copper layer
        track.uuid = "track-uuid-1"

        mock_board.pcb_data["tracks"] = [track]

        issues = validation_manager.validate_layers()

        assert issues == 1
        assert len(validation_manager.issues) == 1
        assert validation_manager.issues[0].category == "layer"
        assert validation_manager.issues[0].severity == "error"
        assert "non-copper layer" in validation_manager.issues[0].description

    def test_validate_layers_finds_vias_with_invalid_spans(self, validation_manager, mock_board):
        """Test validate_layers finds vias with invalid layer spans."""
        via = Mock()
        via.layers = ["F.Cu"]  # Only one layer (need at least 2)
        via.uuid = "via-uuid-1"

        mock_board.pcb_data["vias"] = [via]

        issues = validation_manager.validate_layers()

        assert issues == 1
        assert len(validation_manager.issues) == 1
        assert validation_manager.issues[0].category == "layer"
        assert "must span at least 2 layers" in validation_manager.issues[0].description

    def test_validate_all_runs_all_checks_and_clears_previous(self, validation_manager, mock_board):
        """Test validate_all runs all checks and clears previous issues."""
        # Add previous issue
        validation_manager._issues.append(
            ValidationIssue(severity="error", category="old", description="old issue")
        )

        # Create valid board
        footprint = Mock()
        footprint.reference = "R1"
        footprint.position = Point(50, 50)
        footprint.pads = []

        mock_board.pcb_data["footprints"] = [footprint]
        mock_board.pcb_data["tracks"] = []
        mock_board.pcb_data["vias"] = []

        issues = validation_manager.validate_all()

        # Should have no issues (valid board) and old issues cleared
        assert issues == 0
        assert len(validation_manager.issues) == 0

    def test_get_errors_filters_error_severity(self, validation_manager):
        """Test get_errors returns only error-level issues."""
        validation_manager._issues = [
            ValidationIssue(severity="error", category="test1", description="error 1"),
            ValidationIssue(severity="warning", category="test2", description="warning 1"),
            ValidationIssue(severity="error", category="test3", description="error 2"),
            ValidationIssue(severity="info", category="test4", description="info 1"),
        ]

        errors = validation_manager.get_errors()

        assert len(errors) == 2
        assert all(i.severity == "error" for i in errors)

    def test_get_warnings_filters_warning_severity(self, validation_manager):
        """Test get_warnings returns only warning-level issues."""
        validation_manager._issues = [
            ValidationIssue(severity="error", category="test1", description="error 1"),
            ValidationIssue(severity="warning", category="test2", description="warning 1"),
            ValidationIssue(severity="warning", category="test3", description="warning 2"),
        ]

        warnings = validation_manager.get_warnings()

        assert len(warnings) == 2
        assert all(i.severity == "warning" for i in warnings)

    def test_clear_issues_removes_all(self, validation_manager):
        """Test clear_issues removes all stored issues."""
        validation_manager._issues = [
            ValidationIssue(severity="error", category="test1", description="error 1"),
            ValidationIssue(severity="warning", category="test2", description="warning 1"),
        ]

        validation_manager.clear_issues()

        assert len(validation_manager.issues) == 0
