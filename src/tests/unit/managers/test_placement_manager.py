"""
Unit tests for PlacementManager class.

Tests component placement operations including grid placement,
circular placement, alignment, and distribution.
"""

from unittest.mock import Mock, MagicMock
import pytest
import math

from kicad_pcb_api.managers.placement import PlacementManager
from kicad_pcb_api.core.types import Point


@pytest.fixture
def mock_board():
    """Create a mock PCBBoard instance."""
    board = Mock()
    board.footprints = Mock()
    return board


@pytest.fixture
def placement_manager(mock_board):
    """Create PlacementManager instance with mock board."""
    return PlacementManager(mock_board)


@pytest.fixture
def mock_footprint():
    """Create a mock footprint."""
    footprint = Mock()
    footprint.position = Point(0, 0)
    footprint.rotation = 0
    return footprint


@pytest.mark.unit
class TestPlacementManager:
    """Test cases for PlacementManager."""

    def test_initialization_with_board_reference(self, mock_board):
        """Test PlacementManager initializes with board reference."""
        manager = PlacementManager(mock_board)

        assert manager.board is mock_board

    def test_place_in_grid_arranges_components_correctly(self, placement_manager, mock_board):
        """Test place_in_grid arranges components in grid pattern."""
        # Create mock footprints
        footprints = {}
        for i in range(6):
            fp = Mock()
            fp.position = Point(0, 0)
            footprints[f"R{i+1}"] = fp

        mock_board.footprints.get_by_reference = lambda ref: footprints.get(ref)

        references = ["R1", "R2", "R3", "R4", "R5", "R6"]
        count = placement_manager.place_in_grid(
            references=references,
            start_x=10.0,
            start_y=20.0,
            spacing_x=5.0,
            spacing_y=10.0,
            columns=3
        )

        assert count == 6
        # Check first row
        assert footprints["R1"].position == Point(10.0, 20.0)
        assert footprints["R2"].position == Point(15.0, 20.0)
        assert footprints["R3"].position == Point(20.0, 20.0)
        # Check second row
        assert footprints["R4"].position == Point(10.0, 30.0)
        assert footprints["R5"].position == Point(15.0, 30.0)
        assert footprints["R6"].position == Point(20.0, 30.0)

    def test_place_in_grid_skips_missing_footprints(self, placement_manager, mock_board):
        """Test place_in_grid skips missing footprints and continues."""
        footprints = {"R1": Mock(), "R3": Mock()}
        for fp in footprints.values():
            fp.position = Point(0, 0)

        mock_board.footprints.get_by_reference = lambda ref: footprints.get(ref)

        references = ["R1", "R2", "R3"]  # R2 doesn't exist
        count = placement_manager.place_in_grid(
            references=references,
            start_x=0.0,
            start_y=0.0,
            spacing_x=5.0,
            spacing_y=5.0,
            columns=3
        )

        assert count == 2  # Only R1 and R3 placed

    def test_place_in_circle_arranges_components_in_circle(self, placement_manager, mock_board):
        """Test place_in_circle arranges components in circular pattern."""
        # Create mock footprints
        footprints = {}
        for i in range(4):
            fp = Mock()
            fp.position = Point(0, 0)
            fp.rotation = 0
            footprints[f"R{i+1}"] = fp

        mock_board.footprints.get_by_reference = lambda ref: footprints.get(ref)

        references = ["R1", "R2", "R3", "R4"]
        count = placement_manager.place_in_circle(
            references=references,
            center_x=50.0,
            center_y=50.0,
            radius=10.0
        )

        assert count == 4
        # Check that components are roughly at correct positions
        # R1 at 0 degrees
        assert abs(footprints["R1"].position.x - 60.0) < 0.01
        assert abs(footprints["R1"].position.y - 50.0) < 0.01
        # R3 at 180 degrees
        assert abs(footprints["R3"].position.x - 40.0) < 0.01
        assert abs(footprints["R3"].position.y - 50.0) < 0.01

    def test_place_in_circle_returns_zero_for_empty_list(self, placement_manager):
        """Test place_in_circle returns 0 for empty references list."""
        count = placement_manager.place_in_circle(
            references=[],
            center_x=0.0,
            center_y=0.0,
            radius=10.0
        )

        assert count == 0

    def test_align_horizontally_sets_same_y_coordinate(self, placement_manager, mock_board):
        """Test align_horizontally sets same Y coordinate for all components."""
        footprints = {
            "R1": Mock(position=Point(10, 20)),
            "R2": Mock(position=Point(30, 25)),
            "R3": Mock(position=Point(50, 15))
        }

        mock_board.footprints.get_by_reference = lambda ref: footprints.get(ref)

        references = ["R1", "R2", "R3"]
        count = placement_manager.align_horizontally(references, y=100.0)

        assert count == 3
        assert footprints["R1"].position.y == 100.0
        assert footprints["R2"].position.y == 100.0
        assert footprints["R3"].position.y == 100.0
        # X coordinates should remain unchanged
        assert footprints["R1"].position.x == 10
        assert footprints["R2"].position.x == 30
        assert footprints["R3"].position.x == 50

    def test_align_horizontally_uses_first_component_when_y_none(self, placement_manager, mock_board):
        """Test align_horizontally uses first component's Y when y is None."""
        footprints = {
            "R1": Mock(position=Point(10, 77)),
            "R2": Mock(position=Point(30, 25)),
        }

        mock_board.footprints.get_by_reference = lambda ref: footprints.get(ref)

        references = ["R1", "R2"]
        count = placement_manager.align_horizontally(references, y=None)

        assert count == 2
        assert footprints["R1"].position.y == 77
        assert footprints["R2"].position.y == 77

    def test_align_vertically_sets_same_x_coordinate(self, placement_manager, mock_board):
        """Test align_vertically sets same X coordinate for all components."""
        footprints = {
            "R1": Mock(position=Point(10, 20)),
            "R2": Mock(position=Point(30, 25)),
            "R3": Mock(position=Point(50, 15))
        }

        mock_board.footprints.get_by_reference = lambda ref: footprints.get(ref)

        references = ["R1", "R2", "R3"]
        count = placement_manager.align_vertically(references, x=200.0)

        assert count == 3
        assert footprints["R1"].position.x == 200.0
        assert footprints["R2"].position.x == 200.0
        assert footprints["R3"].position.x == 200.0
        # Y coordinates should remain unchanged
        assert footprints["R1"].position.y == 20
        assert footprints["R2"].position.y == 25
        assert footprints["R3"].position.y == 15

    def test_distribute_horizontally_spaces_evenly(self, placement_manager, mock_board):
        """Test distribute_horizontally spaces components evenly."""
        footprints = {
            "R1": Mock(position=Point(0, 50)),
            "R2": Mock(position=Point(0, 50)),
            "R3": Mock(position=Point(0, 50)),
        }

        mock_board.footprints.get_by_reference = lambda ref: footprints.get(ref)

        references = ["R1", "R2", "R3"]
        count = placement_manager.distribute_horizontally(
            references=references,
            start_x=0.0,
            end_x=100.0
        )

        assert count == 3
        assert footprints["R1"].position.x == 0.0
        assert footprints["R2"].position.x == 50.0
        assert footprints["R3"].position.x == 100.0
        # Y coordinates should remain unchanged
        assert all(fp.position.y == 50 for fp in footprints.values())

    def test_distribute_vertically_spaces_evenly(self, placement_manager, mock_board):
        """Test distribute_vertically spaces components evenly."""
        footprints = {
            "R1": Mock(position=Point(25, 0)),
            "R2": Mock(position=Point(25, 0)),
            "R3": Mock(position=Point(25, 0)),
            "R4": Mock(position=Point(25, 0)),
        }

        mock_board.footprints.get_by_reference = lambda ref: footprints.get(ref)

        references = ["R1", "R2", "R3", "R4"]
        count = placement_manager.distribute_vertically(
            references=references,
            start_y=0.0,
            end_y=60.0
        )

        assert count == 4
        assert footprints["R1"].position.y == 0.0
        assert footprints["R2"].position.y == 20.0
        assert footprints["R3"].position.y == 40.0
        assert footprints["R4"].position.y == 60.0
        # X coordinates should remain unchanged
        assert all(fp.position.x == 25 for fp in footprints.values())

    def test_distribute_returns_zero_for_less_than_two_components(self, placement_manager, mock_board):
        """Test distribute operations return 0 for < 2 components."""
        footprints = {"R1": Mock(position=Point(0, 0))}
        mock_board.footprints.get_by_reference = lambda ref: footprints.get(ref)

        count_h = placement_manager.distribute_horizontally(["R1"], 0.0, 100.0)
        count_v = placement_manager.distribute_vertically(["R1"], 0.0, 100.0)

        assert count_h == 0
        assert count_v == 0
