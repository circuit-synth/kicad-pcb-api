"""
Unit tests for NetManager class.

Tests net management operations including net queries,
statistics, and net name management.
"""

from unittest.mock import Mock
import pytest

from kicad_pcb_api.managers.net import NetManager
from kicad_pcb_api.core.types import Point, Pad


@pytest.fixture
def mock_board():
    """Create a mock PCBBoard instance."""
    board = Mock()
    board.pcb_data = {
        "nets": [],
        "tracks": [],
        "vias": [],
        "footprints": []
    }
    return board


@pytest.fixture
def net_manager(mock_board):
    """Create NetManager instance with mock board."""
    return NetManager(mock_board)


@pytest.mark.unit
class TestNetManager:
    """Test cases for NetManager."""

    def test_initialization_with_board_reference(self, mock_board):
        """Test NetManager initializes with board reference."""
        manager = NetManager(mock_board)

        assert manager.board is mock_board

    def test_get_all_nets_returns_unique_nets(self, net_manager, mock_board):
        """Test get_all_nets returns unique net numbers from all sources."""
        # Create mock footprint with pads
        footprint = Mock()
        pad1 = Mock(spec=Pad)
        pad1.net = 1
        pad2 = Mock(spec=Pad)
        pad2.net = 2
        footprint.pads = [pad1, pad2]

        # Create mock tracks
        track1 = Mock()
        track1.net = 1  # Same as pad1
        track2 = Mock()
        track2.net = 3  # New net

        # Create mock via
        via = Mock()
        via.net = 4

        mock_board.pcb_data["footprints"] = [footprint]
        mock_board.pcb_data["tracks"] = [track1, track2]
        mock_board.pcb_data["vias"] = [via]

        nets = net_manager.get_all_nets()

        assert len(nets) == 4
        assert nets == {1, 2, 3, 4}

    def test_get_all_nets_excludes_none_nets(self, net_manager, mock_board):
        """Test get_all_nets excludes None net values."""
        footprint = Mock()
        pad1 = Mock(spec=Pad)
        pad1.net = 1
        pad2 = Mock(spec=Pad)
        pad2.net = None  # Unconnected pad
        footprint.pads = [pad1, pad2]

        mock_board.pcb_data["footprints"] = [footprint]

        nets = net_manager.get_all_nets()

        assert len(nets) == 1
        assert nets == {1}
        assert None not in nets

    def test_get_net_name_finds_from_pads(self, net_manager, mock_board):
        """Test get_net_name finds net name from footprint pads."""
        footprint = Mock()
        pad = Mock(spec=Pad)
        pad.net = 5
        pad.net_name = "VCC"
        footprint.pads = [pad]

        mock_board.pcb_data["footprints"] = [footprint]

        name = net_manager.get_net_name(5)

        assert name == "VCC"

    def test_get_net_name_returns_none_when_not_found(self, net_manager, mock_board):
        """Test get_net_name returns None when net doesn't exist."""
        name = net_manager.get_net_name(999)

        assert name is None

    def test_get_net_statistics_calculates_comprehensive_data(self, net_manager, mock_board):
        """Test get_net_statistics calculates all statistics correctly."""
        # Create footprint with pads on net 1
        footprint = Mock()
        pad1 = Mock(spec=Pad)
        pad1.net = 1
        pad1.net_name = "GND"
        pad2 = Mock(spec=Pad)
        pad2.net = 1
        pad2.net_name = "GND"
        footprint.pads = [pad1, pad2]

        # Create tracks on net 1
        track1 = Mock()
        track1.net = 1
        track1.start = Point(0, 0)
        track1.end = Point(3, 4)  # Length = 5
        track2 = Mock()
        track2.net = 1
        track2.start = Point(10, 10)
        track2.end = Point(13, 14)  # Length = 5

        # Create via on net 1
        via = Mock()
        via.net = 1

        mock_board.pcb_data["footprints"] = [footprint]
        mock_board.pcb_data["tracks"] = [track1, track2]
        mock_board.pcb_data["vias"] = [via]

        stats = net_manager.get_net_statistics()

        assert 1 in stats
        assert stats[1]["name"] == "GND"
        assert stats[1]["track_count"] == 2
        assert stats[1]["via_count"] == 1
        assert stats[1]["pad_count"] == 2
        assert stats[1]["total_track_length"] == 10.0  # 5 + 5

    def test_find_unconnected_pads_identifies_net_zero(self, net_manager, mock_board):
        """Test find_unconnected_pads identifies pads with net 0 or None."""
        footprint1 = Mock()
        footprint1.reference = "R1"
        pad1 = Mock(spec=Pad)
        pad1.net = 0
        pad1.number = "1"
        footprint1.pads = [pad1]

        footprint2 = Mock()
        footprint2.reference = "C1"
        pad2 = Mock(spec=Pad)
        pad2.net = None
        pad2.number = "2"
        footprint2.pads = [pad2]

        footprint3 = Mock()
        footprint3.reference = "R2"
        pad3 = Mock(spec=Pad)
        pad3.net = 5  # Connected
        pad3.number = "1"
        footprint3.pads = [pad3]

        mock_board.pcb_data["footprints"] = [footprint1, footprint2, footprint3]

        unconnected = net_manager.find_unconnected_pads()

        assert len(unconnected) == 2
        assert ("R1", "1") in unconnected
        assert ("C1", "2") in unconnected
        assert ("R2", "1") not in unconnected

    def test_rename_net_updates_all_elements(self, net_manager, mock_board):
        """Test rename_net updates net_name on all connected elements."""
        # Create footprint with pad
        footprint = Mock()
        pad = Mock(spec=Pad)
        pad.net = 10
        pad.net_name = "OLD_NAME"
        footprint.pads = [pad]

        # Create track
        track = Mock()
        track.net = 10
        track.net_name = "OLD_NAME"

        # Create via
        via = Mock()
        via.net = 10
        via.net_name = "OLD_NAME"

        mock_board.pcb_data["footprints"] = [footprint]
        mock_board.pcb_data["tracks"] = [track]
        mock_board.pcb_data["vias"] = [via]

        count = net_manager.rename_net(10, "NEW_NAME")

        assert count == 3
        assert pad.net_name == "NEW_NAME"
        assert track.net_name == "NEW_NAME"
        assert via.net_name == "NEW_NAME"

    def test_rename_net_returns_zero_when_net_not_found(self, net_manager, mock_board):
        """Test rename_net returns 0 when net doesn't exist."""
        count = net_manager.rename_net(999, "NONEXISTENT")

        assert count == 0

    def test_get_net_statistics_handles_empty_board(self, net_manager, mock_board):
        """Test get_net_statistics handles board with no nets."""
        stats = net_manager.get_net_statistics()

        assert isinstance(stats, dict)
        assert len(stats) == 0
