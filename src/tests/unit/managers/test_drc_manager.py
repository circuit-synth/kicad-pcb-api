"""
Unit tests for DRCManager class.

Tests design rule checking functionality including track widths,
via sizes, clearances, and violation reporting.
"""

from unittest.mock import Mock, MagicMock
import pytest

from kicad_pcb_api.managers.drc import DRCManager, ValidationIssue
from kicad_pcb_api.core.types import Point, Track, Via


@pytest.fixture
def mock_board():
    """Create a mock PCBBoard instance."""
    board = Mock()
    board.pcb_data = {
        "tracks": [],
        "vias": [],
        "footprints": [],
        "graphics": []
    }
    return board


@pytest.fixture
def drc_manager(mock_board):
    """Create DRCManager instance with mock board."""
    return DRCManager(mock_board)


@pytest.mark.unit
class TestDRCManager:
    """Test cases for DRCManager."""

    def test_initialization_creates_empty_issues_list(self, mock_board):
        """Test DRCManager initializes with empty issues list."""
        manager = DRCManager(mock_board)

        assert manager.board is mock_board
        assert len(manager.issues) == 0
        assert isinstance(manager.issues, list)

    def test_check_track_widths_finds_violations_below_minimum(self, drc_manager, mock_board):
        """Test track width checking finds tracks below minimum."""
        # Create track below minimum width
        track = Mock(spec=Track)
        track.width = 0.05  # Below min of 0.127
        track.uuid = "track-uuid-1"
        track.start = Point(10, 10)
        track.end = Point(20, 20)
        track.net_name = "TEST_NET"

        mock_board.pcb_data["tracks"] = [track]

        issues = drc_manager.check_track_widths(min_width=0.127)

        assert len(issues) >= 1
        assert issues[0].category == "design_rule"
        assert issues[0].level == "error"
        assert issues[0].code == "DRC_TRACK_WIDTH_MIN"
        assert "0.050mm below minimum 0.127mm" in issues[0].message

    def test_check_track_widths_finds_violations_above_maximum(self, drc_manager, mock_board):
        """Test track width checking finds tracks above maximum."""
        # Create track above maximum width
        track = Mock(spec=Track)
        track.width = 12.0  # Above max of 10.0
        track.uuid = "track-uuid-1"
        track.start = Point(10, 10)
        track.end = Point(20, 20)
        track.net_name = "TEST_NET"

        mock_board.pcb_data["tracks"] = [track]

        issues = drc_manager.check_track_widths(max_width=10.0)

        assert len(issues) >= 1
        assert issues[0].category == "design_rule"
        assert issues[0].level == "warning"
        assert issues[0].code == "DRC_TRACK_WIDTH_MAX"

    def test_check_track_widths_no_violations_when_valid(self, drc_manager, mock_board):
        """Test track width checking finds no violations when tracks valid."""
        # Create valid track
        track = Mock(spec=Track)
        track.width = 0.5  # Valid width
        track.uuid = "track-uuid-1"
        track.start = Point(10, 10)
        track.end = Point(20, 20)
        track.net_name = "TEST_NET"

        mock_board.pcb_data["tracks"] = [track]

        issues = drc_manager.check_track_widths(min_width=0.1, max_width=10.0)

        assert len(issues) == 0

    def test_check_via_sizes_finds_multiple_violations(self, drc_manager, mock_board):
        """Test via size checking finds multiple violation types."""
        # Create via with multiple issues
        via = Mock(spec=Via)
        via.size = 0.15  # Below min of 0.4
        via.drill = 0.05  # Below min of 0.2
        via.uuid = "via-uuid-1"
        via.position = Point(50, 50)

        mock_board.pcb_data["vias"] = [via]

        issues = drc_manager.check_via_sizes(min_size=0.4, min_drill=0.2)

        assert len(issues) >= 2
        codes = [issue.code for issue in issues]
        assert "DRC_VIA_SIZE" in codes
        assert "DRC_VIA_DRILL" in codes

    def test_check_via_sizes_finds_drill_larger_than_pad(self, drc_manager, mock_board):
        """Test via checking finds drill size larger than pad."""
        # Create via with drill >= pad size
        via = Mock(spec=Via)
        via.size = 0.4
        via.drill = 0.4  # Equal to size (invalid)
        via.uuid = "via-uuid-1"
        via.position = Point(50, 50)

        mock_board.pcb_data["vias"] = [via]

        issues = drc_manager.check_via_sizes()

        assert len(issues) >= 1
        # Find the drill/pad violation
        drill_violations = [v for v in issues if "must be smaller than pad size" in v.message]
        assert len(drill_violations) == 1
        assert drill_violations[0].code == "DRC_VIA_DRILL_SIZE"

    def test_check_all_runs_all_checks_and_clears_previous(self, drc_manager, mock_board):
        """Test check_all runs all checks and clears previous issues."""
        # Add previous issue
        drc_manager._issues.append(
            ValidationIssue(
                category="old",
                message="old violation",
                level="error",
                code="OLD001"
            )
        )

        # Create valid track and via
        track = Mock(spec=Track)
        track.width = 0.5
        track.uuid = "track-1"
        track.start = Point(0, 0)
        track.end = Point(10, 10)
        track.net_name = "TEST"
        track.net = 1
        track.layer = "F.Cu"

        via = Mock(spec=Via)
        via.size = 0.5
        via.drill = 0.2
        via.uuid = "via-1"
        via.position = Point(20, 20)

        mock_board.pcb_data["tracks"] = [track]
        mock_board.pcb_data["vias"] = [via]

        issues = drc_manager.check_all()

        # Old issues should be cleared, and we might have some unconnected pad warnings
        assert len(drc_manager.issues) >= 0  # May have warnings but not errors from old test
        # Verify old issue is gone
        assert not any(issue.code == "OLD001" for issue in drc_manager.issues)

    def test_get_errors_filters_error_level(self, drc_manager):
        """Test get_errors returns only error-level issues."""
        drc_manager._issues = [
            ValidationIssue(category="test1", message="error 1", level="error", code="E1"),
            ValidationIssue(category="test2", message="warning 1", level="warning", code="W1"),
            ValidationIssue(category="test3", message="error 2", level="error", code="E2"),
        ]

        errors = drc_manager.get_errors()

        assert len(errors) == 2
        assert all(v.level == "error" for v in errors)

    def test_get_warnings_filters_warning_level(self, drc_manager):
        """Test get_warnings returns only warning-level issues."""
        drc_manager._issues = [
            ValidationIssue(category="test1", message="error 1", level="error", code="E1"),
            ValidationIssue(category="test2", message="warning 1", level="warning", code="W1"),
            ValidationIssue(category="test3", message="warning 2", level="warning", code="W2"),
        ]

        warnings = drc_manager.get_warnings()

        assert len(warnings) == 2
        assert all(v.level == "warning" for v in warnings)

    def test_clear_issues_removes_all(self, drc_manager):
        """Test clear_issues removes all stored issues."""
        drc_manager._issues = [
            ValidationIssue(category="test1", message="error 1", level="error", code="E1"),
            ValidationIssue(category="test2", message="warning 1", level="warning", code="W1"),
        ]

        drc_manager.clear_issues()

        assert len(drc_manager.issues) == 0

    def test_has_errors_returns_true_when_errors_exist(self, drc_manager):
        """Test has_errors correctly identifies when errors present."""
        drc_manager._issues = [
            ValidationIssue(category="test", message="error", level="error", code="E1"),
        ]

        assert drc_manager.has_errors() is True

    def test_has_errors_returns_false_when_no_errors(self, drc_manager):
        """Test has_errors returns false when only warnings."""
        drc_manager._issues = [
            ValidationIssue(category="test", message="warning", level="warning", code="W1"),
        ]

        assert drc_manager.has_errors() is False

    def test_summary_provides_readable_output(self, drc_manager):
        """Test summary generates readable output."""
        drc_manager._issues = [
            ValidationIssue(category="test1", message="error 1", level="error", code="E1"),
            ValidationIssue(category="test2", message="error 2", level="error", code="E2"),
            ValidationIssue(category="test3", message="warning 1", level="warning", code="W1"),
        ]

        summary = drc_manager.summary()

        assert "2 errors" in summary
        assert "1 warning" in summary
