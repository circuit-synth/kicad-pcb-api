"""
Integration tests for track routing operation workflows.

Tests end-to-end track manipulation including:
- Adding tracks between points
- Connecting pads with routing
- Multi-segment track creation
- Track width and layer management
- Net assignment and validation
"""

import pytest
from pathlib import Path
import tempfile
import math

from kicad_pcb_api import PCBBoard, Point, Track


@pytest.mark.integration
class TestTrackOperations:
    """Integration tests for track routing workflows."""

    def test_add_simple_track_workflow(self, tmp_path):
        """Test adding a simple track between two points."""
        pcb = PCBBoard()

        # Add two footprints
        pcb.add_footprint("R1", "Resistor_SMD:R_0603_1608Metric", 10, 50, value="10k")
        pcb.add_footprint("R2", "Resistor_SMD:R_0603_1608Metric", 30, 50, value="10k")

        # Create track between them
        start = Point(10, 50)
        end = Point(30, 50)

        # Add track directly to pcb_data
        track = Track(
            start=start,
            end=end,
            width=0.25,
            layer="F.Cu",
            net=1,
            uuid="track-1"
        )
        pcb.pcb_data["tracks"].append(track)

        # Verify track was added
        assert len(pcb.pcb_data["tracks"]) == 1
        assert pcb.pcb_data["tracks"][0].width == 0.25
        assert pcb.pcb_data["tracks"][0].layer == "F.Cu"

        # Save and reload
        file_path = tmp_path / "test_simple_track.kicad_pcb"
        pcb.save(file_path)

        pcb2 = PCBBoard(str(file_path))
        assert len(pcb2.pcb_data["tracks"]) == 1
        track_loaded = pcb2.pcb_data["tracks"][0]
        assert track_loaded.width == 0.25
        assert track_loaded.start.x == 10
        assert track_loaded.end.x == 30

    def test_connect_pads_with_routing(self, tmp_path):
        """Test connecting component pads with tracks."""
        pcb = PCBBoard()

        # Add components
        pcb.add_footprint("U1", "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", 50, 50)
        pcb.add_footprint("R1", "Resistor_SMD:R_0603_1608Metric", 40, 50, value="10k")
        pcb.add_footprint("C1", "Capacitor_SMD:C_0603_1608Metric", 60, 50, value="100nF")

        # Connect pads using the PCBBoard API
        pcb.connect_pads("U1", "1", "R1", "2", "Signal1")
        pcb.connect_pads("U1", "2", "C1", "1", "Signal2")

        # Verify connections were created (check nets)
        nets = pcb.nets
        assert len(nets) >= 2  # At least net 0 and our new nets

        # Save and reload
        file_path = tmp_path / "test_pad_connections.kicad_pcb"
        pcb.save(file_path)

        pcb2 = PCBBoard(str(file_path))
        nets2 = pcb2.nets
        assert len(nets2) >= 2

    def test_multi_segment_track_creation(self, tmp_path):
        """Test creating multi-segment tracks (Manhattan routing)."""
        pcb = PCBBoard()

        # Add footprints at different positions
        pcb.add_footprint("J1", "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical", 10, 10)
        pcb.add_footprint("J2", "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical", 50, 40)

        # Create Manhattan route (horizontal then vertical)
        segment1 = Track(
            start=Point(10, 10),
            end=Point(50, 10),
            width=0.5,
            layer="F.Cu",
            net=1,
            uuid="seg-1"
        )
        segment2 = Track(
            start=Point(50, 10),
            end=Point(50, 40),
            width=0.5,
            layer="F.Cu",
            net=1,
            uuid="seg-2"
        )

        pcb.pcb_data["tracks"].append(segment1)
        pcb.pcb_data["tracks"].append(segment2)

        # Verify segments
        assert len(pcb.pcb_data["tracks"]) == 2
        assert pcb.pcb_data["tracks"][0].end == pcb.pcb_data["tracks"][1].start

        # Use routing manager if available
        if hasattr(pcb, 'routing'):
            # Test Manhattan routing helper
            start = Point(10, 50)
            end = Point(80, 80)
            tracks = pcb.routing.route_manhattan(start, end, 0.25, "F.Cu", net=2)

            if tracks:
                assert len(tracks) == 2  # Horizontal + vertical
                total_tracks = len(pcb.pcb_data["tracks"])
                assert total_tracks == 4  # Previous 2 + new 2

        # Save and reload
        file_path = tmp_path / "test_multi_segment.kicad_pcb"
        pcb.save(file_path)

        pcb2 = PCBBoard(str(file_path))
        assert len(pcb2.pcb_data["tracks"]) >= 2

    def test_track_width_and_layer_management(self, tmp_path):
        """Test tracks with different widths and layers."""
        pcb = PCBBoard()

        # Add tracks with various widths (representing different signal types)
        tracks_config = [
            (Point(10, 10), Point(20, 10), 0.15, "F.Cu", 1),  # Fine signal
            (Point(10, 15), Point(20, 15), 0.25, "F.Cu", 2),  # Standard signal
            (Point(10, 20), Point(20, 20), 0.5, "F.Cu", 3),   # Power trace
            (Point(10, 25), Point(20, 25), 1.0, "F.Cu", 4),   # Heavy power
            (Point(30, 10), Point(40, 10), 0.25, "B.Cu", 5),  # Back layer
        ]

        for i, (start, end, width, layer, net) in enumerate(tracks_config):
            track = Track(
                start=start,
                end=end,
                width=width,
                layer=layer,
                net=net,
                uuid=f"track-{i}"
            )
            pcb.pcb_data["tracks"].append(track)

        # Verify different widths
        assert len(pcb.pcb_data["tracks"]) == 5
        widths = [t.width for t in pcb.pcb_data["tracks"]]
        assert 0.15 in widths
        assert 1.0 in widths

        # Verify different layers
        layers = [t.layer for t in pcb.pcb_data["tracks"]]
        assert "F.Cu" in layers
        assert "B.Cu" in layers

        # Save and reload
        file_path = tmp_path / "test_track_properties.kicad_pcb"
        pcb.save(file_path)

        pcb2 = PCBBoard(str(file_path))
        assert len(pcb2.pcb_data["tracks"]) == 5

        # Verify properties persisted
        widths2 = [t.width for t in pcb2.pcb_data["tracks"]]
        assert 0.15 in widths2
        assert 1.0 in widths2

    def test_track_net_assignment_and_validation(self, tmp_path):
        """Test track net assignment and validation."""
        pcb = PCBBoard()

        # Add footprints
        pcb.add_footprint("R1", "Resistor_SMD:R_0603_1608Metric", 10, 10, value="1k")
        pcb.add_footprint("R2", "Resistor_SMD:R_0603_1608Metric", 20, 10, value="1k")
        pcb.add_footprint("R3", "Resistor_SMD:R_0603_1608Metric", 30, 10, value="1k")

        # Create tracks with different nets
        track1 = Track(
            start=Point(10, 10),
            end=Point(20, 10),
            width=0.25,
            layer="F.Cu",
            net=1,
            uuid="track-net1"
        )
        track2 = Track(
            start=Point(20, 10),
            end=Point(30, 10),
            width=0.25,
            layer="F.Cu",
            net=2,
            uuid="track-net2"
        )
        track3 = Track(
            start=Point(10, 15),
            end=Point(30, 15),
            width=0.25,
            layer="F.Cu",
            net=0,  # Unconnected
            uuid="track-net0"
        )

        pcb.pcb_data["tracks"].append(track1)
        pcb.pcb_data["tracks"].append(track2)
        pcb.pcb_data["tracks"].append(track3)

        # Verify net assignments
        net_numbers = [t.net for t in pcb.pcb_data["tracks"]]
        assert 0 in net_numbers
        assert 1 in net_numbers
        assert 2 in net_numbers

        # Use net manager if available
        if hasattr(pcb, 'net'):
            stats = pcb.net.get_net_statistics()
            assert isinstance(stats, dict)
            assert len(stats) >= 1  # At least net 0

        # Save and reload
        file_path = tmp_path / "test_net_assignment.kicad_pcb"
        pcb.save(file_path)

        pcb2 = PCBBoard(str(file_path))
        assert len(pcb2.pcb_data["tracks"]) == 3

        # Verify nets persisted
        net_numbers2 = [t.net for t in pcb2.pcb_data["tracks"]]
        assert 0 in net_numbers2
        assert 1 in net_numbers2
        assert 2 in net_numbers2

        # Test net statistics on reloaded board
        if hasattr(pcb2, 'net'):
            stats2 = pcb2.net.get_net_statistics()
            assert isinstance(stats2, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
