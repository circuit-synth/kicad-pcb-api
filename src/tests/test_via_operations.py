"""
Integration tests for via operation workflows.

Tests end-to-end via manipulation including:
- Adding vias at specific locations
- Connecting layers with vias
- Different via types (through-hole, blind, buried)
- Via size and drill specifications
- Net assignment and layer spans
"""

import pytest
from pathlib import Path
import tempfile

from kicad_pcb_api import PCBBoard, Point, Via


@pytest.mark.integration
class TestViaOperations:
    """Integration tests for via workflows."""

    def test_add_simple_via_workflow(self, tmp_path):
        """Test adding a simple through-hole via."""
        pcb = PCBBoard()

        # Add footprints on different layers (conceptually)
        pcb.add_footprint("R1", "Resistor_SMD:R_0603_1608Metric", 20, 20, value="10k")
        pcb.add_footprint("R2", "Resistor_SMD:R_0603_1608Metric", 20, 40, value="10k")

        # Add via to connect layers
        via = Via(
            position=Point(20, 30),
            size=0.8,
            drill=0.4,
            layers=["F.Cu", "B.Cu"],
            net=1,
            uuid="via-1"
        )
        pcb.pcb_data["vias"].append(via)

        # Verify via was added
        assert len(pcb.pcb_data["vias"]) == 1
        assert pcb.pcb_data["vias"][0].size == 0.8
        assert pcb.pcb_data["vias"][0].drill == 0.4
        assert "F.Cu" in pcb.pcb_data["vias"][0].layers
        assert "B.Cu" in pcb.pcb_data["vias"][0].layers

        # Save and reload
        file_path = tmp_path / "test_simple_via.kicad_pcb"
        pcb.save(file_path)

        pcb2 = PCBBoard(str(file_path))
        assert len(pcb2.pcb_data["vias"]) == 1
        via_loaded = pcb2.pcb_data["vias"][0]
        assert via_loaded.size == 0.8
        assert via_loaded.drill == 0.4
        assert via_loaded.position.x == 20
        assert via_loaded.position.y == 30

    def test_multiple_vias_connecting_layers(self, tmp_path):
        """Test multiple vias for layer transitions."""
        pcb = PCBBoard()

        # Add components
        pcb.add_footprint("U1", "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", 50, 50)

        # Create via array for power distribution
        via_positions = [
            (40, 40), (60, 40),
            (40, 50), (60, 50),
            (40, 60), (60, 60),
        ]

        for i, (x, y) in enumerate(via_positions):
            via = Via(
                position=Point(x, y),
                size=0.6,
                drill=0.3,
                layers=["F.Cu", "B.Cu"],
                net=1,  # GND net
                uuid=f"via-gnd-{i}"
            )
            pcb.pcb_data["vias"].append(via)

        # Verify vias
        assert len(pcb.pcb_data["vias"]) == 6

        # All vias should be on the same net (GND)
        nets = [v.net for v in pcb.pcb_data["vias"]]
        assert all(net == 1 for net in nets)

        # Save and reload
        file_path = tmp_path / "test_via_array.kicad_pcb"
        pcb.save(file_path)

        pcb2 = PCBBoard(str(file_path))
        assert len(pcb2.pcb_data["vias"]) == 6

        # Verify all vias still on same net
        nets2 = [v.net for v in pcb2.pcb_data["vias"]]
        assert all(net == 1 for net in nets2)

    def test_via_types_and_layer_spans(self, tmp_path):
        """Test different via types with various layer spans."""
        pcb = PCBBoard()

        # Through-hole via (F.Cu to B.Cu)
        via_through = Via(
            position=Point(10, 10),
            size=0.8,
            drill=0.4,
            layers=["F.Cu", "B.Cu"],
            net=1,
            uuid="via-through"
        )

        # Micro via (smaller size)
        via_micro = Via(
            position=Point(20, 10),
            size=0.4,
            drill=0.2,
            layers=["F.Cu", "In1.Cu"],
            net=2,
            uuid="via-micro"
        )

        # Standard via for inner layers
        via_inner = Via(
            position=Point(30, 10),
            size=0.6,
            drill=0.3,
            layers=["In1.Cu", "In2.Cu"],
            net=3,
            uuid="via-inner"
        )

        pcb.pcb_data["vias"].append(via_through)
        pcb.pcb_data["vias"].append(via_micro)
        pcb.pcb_data["vias"].append(via_inner)

        # Verify different sizes
        assert len(pcb.pcb_data["vias"]) == 3
        sizes = [v.size for v in pcb.pcb_data["vias"]]
        assert 0.4 in sizes  # Micro via
        assert 0.8 in sizes  # Through-hole via

        # Verify different layer spans
        assert "B.Cu" in pcb.pcb_data["vias"][0].layers
        assert "In1.Cu" in pcb.pcb_data["vias"][1].layers
        assert "In2.Cu" in pcb.pcb_data["vias"][2].layers

        # Save and reload
        file_path = tmp_path / "test_via_types.kicad_pcb"
        pcb.save(file_path)

        pcb2 = PCBBoard(str(file_path))
        assert len(pcb2.pcb_data["vias"]) == 3

        # Verify properties persisted
        sizes2 = [v.size for v in pcb2.pcb_data["vias"]]
        assert 0.4 in sizes2
        assert 0.8 in sizes2

    def test_via_size_and_drill_specifications(self, tmp_path):
        """Test vias with various size and drill specifications."""
        pcb = PCBBoard()

        # Different via specifications for different purposes
        via_specs = [
            # (position, size, drill, net, description)
            (Point(10, 10), 0.4, 0.2, 1, "micro"),    # Micro via
            (Point(20, 10), 0.6, 0.3, 2, "standard"),  # Standard via
            (Point(30, 10), 0.8, 0.4, 3, "normal"),    # Normal via
            (Point(40, 10), 1.2, 0.8, 4, "power"),     # Power via
            (Point(50, 10), 1.6, 1.0, 5, "large"),     # Large via
        ]

        for pos, size, drill, net, desc in via_specs:
            via = Via(
                position=pos,
                size=size,
                drill=drill,
                layers=["F.Cu", "B.Cu"],
                net=net,
                uuid=f"via-{desc}"
            )
            pcb.pcb_data["vias"].append(via)

        # Verify specifications
        assert len(pcb.pcb_data["vias"]) == 5

        # Check size range
        sizes = [v.size for v in pcb.pcb_data["vias"]]
        assert min(sizes) == 0.4  # Smallest
        assert max(sizes) == 1.6  # Largest

        # Check drill sizes
        drills = [v.drill for v in pcb.pcb_data["vias"]]
        assert min(drills) == 0.2
        assert max(drills) == 1.0

        # Verify drill is always smaller than via size
        for via in pcb.pcb_data["vias"]:
            assert via.drill < via.size

        # Save and reload
        file_path = tmp_path / "test_via_specs.kicad_pcb"
        pcb.save(file_path)

        pcb2 = PCBBoard(str(file_path))
        assert len(pcb2.pcb_data["vias"]) == 5

        # Verify specs persisted correctly
        for via in pcb2.pcb_data["vias"]:
            assert via.drill < via.size
            assert via.size >= 0.4
            assert via.size <= 1.6

    def test_via_net_assignment_with_tracks(self, tmp_path):
        """Test vias with net assignment coordinated with tracks."""
        pcb = PCBBoard()

        # Add footprints
        pcb.add_footprint("U1", "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", 20, 20)
        pcb.add_footprint("U2", "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", 20, 60)

        # Add via to transition layers
        via = Via(
            position=Point(20, 40),
            size=0.8,
            drill=0.4,
            layers=["F.Cu", "B.Cu"],
            net=1,
            uuid="via-transition"
        )
        pcb.pcb_data["vias"].append(via)

        # Add tracks on different layers connecting to via
        from kicad_pcb_api import Track

        # Track on front layer
        track_front = Track(
            start=Point(20, 20),
            end=Point(20, 40),
            width=0.25,
            layer="F.Cu",
            net=1,
            uuid="track-front"
        )

        # Track on back layer
        track_back = Track(
            start=Point(20, 40),
            end=Point(20, 60),
            width=0.25,
            layer="B.Cu",
            net=1,
            uuid="track-back"
        )

        pcb.pcb_data["tracks"].append(track_front)
        pcb.pcb_data["tracks"].append(track_back)

        # Verify all elements on same net
        assert pcb.pcb_data["vias"][0].net == 1
        assert pcb.pcb_data["tracks"][0].net == 1
        assert pcb.pcb_data["tracks"][1].net == 1

        # Verify via connects the layers
        assert "F.Cu" in pcb.pcb_data["vias"][0].layers
        assert "B.Cu" in pcb.pcb_data["vias"][0].layers
        assert pcb.pcb_data["tracks"][0].layer == "F.Cu"
        assert pcb.pcb_data["tracks"][1].layer == "B.Cu"

        # Save and reload
        file_path = tmp_path / "test_via_with_tracks.kicad_pcb"
        pcb.save(file_path)

        pcb2 = PCBBoard(str(file_path))
        assert len(pcb2.pcb_data["vias"]) == 1
        assert len(pcb2.pcb_data["tracks"]) == 2

        # Verify net consistency after reload
        assert pcb2.pcb_data["vias"][0].net == 1
        assert pcb2.pcb_data["tracks"][0].net == 1
        assert pcb2.pcb_data["tracks"][1].net == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
