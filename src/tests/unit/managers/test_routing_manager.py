"""
Unit tests for RoutingManager class.

Tests routing operations including track creation, Manhattan routing,
length statistics, and track optimization.
"""

from unittest.mock import Mock, MagicMock, patch
import pytest

from kicad_pcb_api.managers.routing import RoutingManager
from kicad_pcb_api.core.types import Point, Track


@pytest.fixture
def mock_board():
    """Create a mock PCBBoard instance."""
    board = Mock()
    board.tracks = Mock()
    board.tracks.add = Mock()
    board.tracks.__iter__ = Mock(return_value=iter([]))
    return board


@pytest.fixture
def routing_manager(mock_board):
    """Create RoutingManager instance with mock board."""
    return RoutingManager(mock_board)


@pytest.mark.unit
class TestRoutingManager:
    """Test cases for RoutingManager."""

    def test_initialization_with_board_reference(self, mock_board):
        """Test RoutingManager initializes with board reference."""
        manager = RoutingManager(mock_board)

        assert manager.board is mock_board

    @patch('uuid.uuid4')
    def test_add_track_creates_track_with_parameters(self, mock_uuid, routing_manager, mock_board):
        """Test add_track creates track with correct parameters."""
        mock_uuid.return_value = "test-uuid-1"

        start = Point(10, 20)
        end = Point(30, 40)
        uuid_result = routing_manager.add_track(
            start=start,
            end=end,
            width=0.5,
            layer="F.Cu",
            net=5,
            net_name="GND"
        )

        assert uuid_result == "test-uuid-1"
        mock_board.tracks.add.assert_called_once()

        # Check the track that was added
        added_track = mock_board.tracks.add.call_args[0][0]
        assert added_track.start == start
        assert added_track.end == end
        assert added_track.width == 0.5
        assert added_track.layer == "F.Cu"
        assert added_track.net == 5
        assert added_track.net_name == "GND"

    def test_add_track_works_without_net_info(self, routing_manager, mock_board):
        """Test add_track works without net information."""
        uuid_result = routing_manager.add_track(
            start=Point(0, 0),
            end=Point(10, 10),
            width=0.3,
            layer="B.Cu"
        )

        assert uuid_result is not None
        mock_board.tracks.add.assert_called_once()

    @patch('uuid.uuid4')
    def test_route_manhattan_creates_horizontal_then_vertical(self, mock_uuid, routing_manager, mock_board):
        """Test route_manhattan creates horizontal then vertical segments."""
        mock_uuid.side_effect = ["uuid-1", "uuid-2"]

        start = Point(10, 10)
        end = Point(30, 40)
        uuids = routing_manager.route_manhattan(
            start=start,
            end=end,
            width=0.5,
            layer="F.Cu",
            net=3
        )

        assert len(uuids) == 2
        assert uuids == ["uuid-1", "uuid-2"]
        assert mock_board.tracks.add.call_count == 2

        # Check first segment (horizontal)
        track1 = mock_board.tracks.add.call_args_list[0][0][0]
        assert track1.start == Point(10, 10)
        assert track1.end == Point(30, 10)  # Same Y, different X

        # Check second segment (vertical)
        track2 = mock_board.tracks.add.call_args_list[1][0][0]
        assert track2.start == Point(30, 10)
        assert track2.end == Point(30, 40)  # Same X, different Y

    @patch('uuid.uuid4')
    def test_route_manhattan_skips_segment_when_no_movement_needed(self, mock_uuid, routing_manager, mock_board):
        """Test route_manhattan skips segments when no movement needed."""
        mock_uuid.side_effect = ["uuid-1"]

        # Only horizontal movement
        start = Point(10, 20)
        end = Point(50, 20)
        uuids = routing_manager.route_manhattan(
            start=start,
            end=end,
            width=0.5,
            layer="F.Cu"
        )

        assert len(uuids) == 1
        assert mock_board.tracks.add.call_count == 1

    def test_get_total_track_length_by_net_calculates_correctly(self, routing_manager, mock_board):
        """Test get_total_track_length_by_net calculates total correctly."""
        # Create mock tracks with length property
        track1 = Mock()
        track1.net = 5
        track1.length = 10.0

        track2 = Mock()
        track2.net = 5
        track2.length = 15.0

        track3 = Mock()
        track3.net = 3
        track3.length = 20.0

        mock_board.tracks.__iter__ = Mock(return_value=iter([track1, track2, track3]))

        length = routing_manager.get_total_track_length_by_net(5)

        assert length == 25.0

    def test_get_length_statistics_by_net_groups_and_calculates(self, routing_manager, mock_board):
        """Test get_length_statistics_by_net groups by net and calculates stats."""
        track1 = Mock()
        track1.net = 1
        track1.length = 10.0

        track2 = Mock()
        track2.net = 1
        track2.length = 20.0

        track3 = Mock()
        track3.net = 2
        track3.length = 15.0

        track4 = Mock()
        track4.net = None
        track4.length = 5.0

        mock_board.tracks.__iter__ = Mock(return_value=iter([track1, track2, track3, track4]))

        stats = routing_manager.get_length_statistics_by_net()

        assert 1 in stats
        assert stats[1]["total_length"] == 30.0
        assert stats[1]["track_count"] == 2
        assert stats[1]["average_length"] == 15.0
        assert stats[1]["min_length"] == 10.0
        assert stats[1]["max_length"] == 20.0

        assert 2 in stats
        assert stats[2]["total_length"] == 15.0
        assert stats[2]["track_count"] == 1

        # Track with None net should not be in stats
        assert None not in stats

    def test_find_stubs_identifies_short_tracks(self, routing_manager, mock_board):
        """Test find_stubs identifies tracks shorter than threshold."""
        track1 = Mock()
        track1.uuid = "stub-1"
        track1.length = 0.05

        track2 = Mock()
        track2.uuid = "normal-1"
        track2.length = 5.0

        track3 = Mock()
        track3.uuid = "stub-2"
        track3.length = 0.08

        mock_board.tracks.__iter__ = Mock(return_value=iter([track1, track2, track3]))

        stubs = routing_manager.find_stubs(min_stub_length=0.1)

        assert len(stubs) == 2
        assert "stub-1" in stubs
        assert "stub-2" in stubs
        assert "normal-1" not in stubs

    def test_optimize_track_order_sorts_by_layer_and_net(self, routing_manager, mock_board):
        """Test optimize_track_order sorts tracks by layer and net."""
        # Create mock tracks
        track1 = Mock()
        track1.data = Mock(layer="B.Cu", net=3)

        track2 = Mock()
        track2.data = Mock(layer="F.Cu", net=1)

        track3 = Mock()
        track3.data = Mock(layer="F.Cu", net=2)

        track4 = Mock()
        track4.data = Mock(layer="F.Cu", net=None)

        tracks = [track1, track2, track3, track4]
        mock_board.tracks.__iter__ = Mock(return_value=iter(tracks))
        mock_board.tracks._items = []
        mock_board.tracks._dirty_indexes = False

        routing_manager.optimize_track_order()

        # Verify sorting was applied
        assert mock_board.tracks._dirty_indexes is True
        assert len(mock_board.tracks._items) == 4

    def test_get_length_statistics_handles_empty_board(self, routing_manager, mock_board):
        """Test get_length_statistics_by_net handles board with no tracks."""
        mock_board.tracks.__iter__ = Mock(return_value=iter([]))

        stats = routing_manager.get_length_statistics_by_net()

        assert isinstance(stats, dict)
        assert len(stats) == 0

    def test_route_manhattan_preserves_net_information(self, routing_manager, mock_board):
        """Test route_manhattan preserves net information in both segments."""
        uuids = routing_manager.route_manhattan(
            start=Point(0, 0),
            end=Point(10, 20),
            width=0.5,
            layer="F.Cu",
            net=7,
            net_name="SIGNAL"
        )

        assert mock_board.tracks.add.call_count == 2

        # Check both tracks have the same net info
        track1 = mock_board.tracks.add.call_args_list[0][0][0]
        track2 = mock_board.tracks.add.call_args_list[1][0][0]

        assert track1.net == 7
        assert track1.net_name == "SIGNAL"
        assert track2.net == 7
        assert track2.net_name == "SIGNAL"
