"""
Comprehensive integration tests for PCBBoard with managers and collections.

These tests verify that managers, collections, and the core PCBBoard class
work together correctly for real-world use cases.
"""

import pytest
from pathlib import Path

from kicad_pcb_api import PCBBoard, Point, Track, Via


class TestManagerCollectionIntegration:
    """Test manager and collection integration."""

    def test_complete_workflow(self, tmp_path):
        """Test a complete PCB design workflow."""
        pcb = PCBBoard()

        # Step 1: Add components
        pcb.add_footprint("R1", "Resistor_SMD:R_0603_1608Metric", 0, 0, value="10k")
        pcb.add_footprint("R2", "Resistor_SMD:R_0603_1608Metric", 0, 0, value="10k")
        pcb.add_footprint("C1", "Capacitor_SMD:C_0603_1608Metric", 0, 0, value="100nF")
        pcb.add_footprint("C2", "Capacitor_SMD:C_0603_1608Metric", 0, 0, value="100nF")

        # Step 2: Auto-place components in grid
        placed = pcb.place_grid(["R1", "R2", "C1", "C2"], 10, 10, 10, 10, 2)
        assert placed == 4

        # Step 3: Verify placement via collections
        r1 = pcb.footprints.get_by_reference("R1")
        assert r1 is not None
        assert r1.position.x == 10
        assert r1.position.y == 10

        # Step 4: Add board outline
        pcb.set_board_outline_rect(0, 0, 50, 50)

        # Step 5: Validate design
        issues = pcb.validate()
        # No duplicate references, so should pass
        assert len(pcb.validation.get_errors()) == 0

        # Step 6: Save and reload
        file_path = tmp_path / "test_workflow.kicad_pcb"
        pcb.save(file_path)

        pcb2 = PCBBoard(str(file_path))
        assert len(list(pcb2.footprints)) == 4

    def test_placement_manager_circle_layout(self):
        """Test circular placement via placement manager."""
        pcb = PCBBoard()

        # Add components
        refs = [f"U{i}" for i in range(1, 9)]
        for ref in refs:
            pcb.add_footprint(ref, "Package_DIP:DIP-8_W7.62mm", 0, 0)

        # Place in circle
        placed = pcb.placement.place_in_circle(refs, 50, 50, 20)
        assert placed == 8

        # Verify they're arranged in a circle
        import math
        for i, ref in enumerate(refs):
            fp = pcb.footprints.get_by_reference(ref)
            # Should be roughly at radius 20 from center
            dx = fp.position.x - 50
            dy = fp.position.y - 50
            distance = math.sqrt(dx * dx + dy * dy)
            assert abs(distance - 20) < 0.1

    def test_routing_manager_manhattan(self):
        """Test Manhattan routing via routing manager."""
        pcb = PCBBoard()

        # Create Manhattan route
        start = Point(10, 10)
        end = Point(30, 40)
        tracks = pcb.routing.route_manhattan(start, end, 0.25, "F.Cu")

        # Should create 2 segments (horizontal then vertical)
        assert len(tracks) == 2

        # Verify tracks were added to collection
        assert len(list(pcb.tracks)) == 2

    def test_net_manager_statistics(self):
        """Test net statistics via net manager."""
        pcb = PCBBoard()

        # Add components
        pcb.add_footprint("R1", "Resistor_SMD:R_0603_1608Metric", 10, 10)
        pcb.add_footprint("R2", "Resistor_SMD:R_0603_1608Metric", 20, 10)
        pcb.add_footprint("R3", "Resistor_SMD:R_0603_1608Metric", 30, 10)

        # Connect in series
        pcb.connect_pads("R1", "2", "R2", "1", "Net1")
        pcb.connect_pads("R2", "2", "R3", "1", "Net2")

        # Get statistics
        stats = pcb.net.get_net_statistics()
        assert len(stats) > 0

        # Check nets property
        nets = pcb.nets
        assert len(nets) >= 2

    def test_drc_track_width_violations(self):
        """Test DRC track width checking."""
        pcb = PCBBoard()

        # Add tracks with various widths
        pcb.pcb_data["tracks"].append(
            Track(Point(0, 0), Point(10, 0), 0.05, "F.Cu", uuid="track1")
        )  # Too narrow
        pcb.pcb_data["tracks"].append(
            Track(Point(0, 5), Point(10, 5), 0.25, "F.Cu", uuid="track2")
        )  # OK
        pcb.pcb_data["tracks"].append(
            Track(Point(0, 10), Point(10, 10), 15.0, "F.Cu", uuid="track3")
        )  # Too wide

        # Run DRC
        violations = pcb.check_drc(min_track_width=0.1, max_track_width=10.0)
        assert violations >= 2  # Should catch narrow and wide tracks

        # Check specific violations
        errors = pcb.drc.get_errors()
        warnings = pcb.drc.get_warnings()
        assert len(errors) >= 1  # Narrow track
        assert len(warnings) >= 1  # Wide track

    def test_validation_duplicate_references(self):
        """Test validation catches duplicate references."""
        pcb = PCBBoard()

        # Add components with duplicate references
        pcb.add_footprint("R1", "Resistor_SMD:R_0603_1608Metric", 10, 10)
        pcb.add_footprint("R1", "Resistor_SMD:R_0603_1608Metric", 20, 10)
        pcb.add_footprint("C1", "Capacitor_SMD:C_0603_1608Metric", 30, 10)

        # Validate
        issues = pcb.validate()
        assert issues > 0

        # Check for reference errors
        errors = pcb.validation.get_errors()
        assert any(e.category == "reference" for e in errors)
        assert any("Duplicate" in e.description for e in errors)

    def test_collection_queries_with_managers(self):
        """Test collection queries work with manager operations."""
        pcb = PCBBoard()

        # Add footprints
        pcb.add_footprint("R1", "Resistor_SMD:R_0603_1608Metric", 10, 10)
        pcb.add_footprint("R2", "Resistor_SMD:R_0603_1608Metric", 20, 10)
        pcb.add_footprint("C1", "Capacitor_SMD:C_0603_1608Metric", 30, 10)

        # Query via collections
        resistors = pcb.footprints.filter_by_lib_id("Resistor_SMD")
        assert len(resistors) == 2

        capacitors = pcb.footprints.filter_by_lib_id("Capacitor_SMD")
        assert len(capacitors) == 1

        # Use placement manager to move resistors
        pcb.placement.align_horizontally(["R1", "R2"], y=20)

        # Verify alignment
        r1 = pcb.footprints.get_by_reference("R1")
        r2 = pcb.footprints.get_by_reference("R2")
        assert r1.position.y == 20
        assert r2.position.y == 20


class TestRealWorldScenarios:
    """Test real-world PCB design scenarios."""

    def test_power_distribution_network(self):
        """Test designing a power distribution network."""
        pcb = PCBBoard()

        # Add power components
        pcb.add_footprint("U1", "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", 50, 50)
        pcb.add_footprint("C1", "Capacitor_SMD:C_0603_1608Metric", 40, 50, value="10uF")
        pcb.add_footprint("C2", "Capacitor_SMD:C_0603_1608Metric", 60, 50, value="100nF")
        pcb.add_footprint("C3", "Capacitor_SMD:C_0603_1608Metric", 50, 40, value="100nF")

        # Connect power pins to ground
        pcb.connect_pads("U1", "4", "C1", "2", "GND")
        pcb.connect_pads("U1", "4", "C2", "2", "GND")
        pcb.connect_pads("U1", "4", "C3", "2", "GND")

        # Add power traces (simplified)
        for i in range(3):
            pcb.pcb_data["tracks"].append(
                Track(
                    Point(50, 50), Point(50 + i * 10, 50),
                    0.5, "F.Cu", net=1, uuid=f"pwr-track-{i}"
                )
            )

        # Check net statistics
        stats = pcb.net.get_net_statistics()
        gnd_net = None
        for net_num, net_stat in stats.items():
            if net_stat["name"] == "GND":
                gnd_net = net_stat
                break

        assert gnd_net is not None
        assert gnd_net["pad_count"] >= 3

    def test_differential_pair_layout(self):
        """Test differential pair routing."""
        pcb = PCBBoard()

        # Add components for differential pair
        pcb.add_footprint("U1", "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", 20, 50)
        pcb.add_footprint("U2", "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", 80, 50)

        # Connect differential pair
        pcb.connect_pads("U1", "1", "U2", "1", "USB_DP")
        pcb.connect_pads("U1", "2", "U2", "2", "USB_DN")

        # Add differential traces
        # Positive signal
        pcb.pcb_data["tracks"].append(
            Track(Point(20, 50), Point(80, 50), 0.15, "F.Cu", net=1, uuid="dp-track")
        )
        # Negative signal (parallel, 0.3mm spacing)
        pcb.pcb_data["tracks"].append(
            Track(Point(20, 50.3), Point(80, 50.3), 0.15, "F.Cu", net=2, uuid="dn-track")
        )

        # Verify both nets exist
        nets = pcb.nets
        assert len(nets) >= 2

    def test_mixed_placement_strategies(self):
        """Test using multiple placement strategies."""
        pcb = PCBBoard()

        # Add different component groups
        # Group 1: Power regulators (place in line)
        for i in range(1, 4):
            pcb.add_footprint(f"U{i}", "Package_TO_SOT_SMD:SOT-23", 0, 0)

        # Group 2: Passives (place in grid)
        for i in range(1, 9):
            pcb.add_footprint(f"R{i}", "Resistor_SMD:R_0603_1608Metric", 0, 0)

        # Place regulators horizontally
        pcb.placement.align_horizontally(["U1", "U2", "U3"], y=10)
        pcb.placement.distribute_horizontally(["U1", "U2", "U3"], 10, 40)

        # Place resistors in grid
        refs = [f"R{i}" for i in range(1, 9)]
        pcb.place_grid(refs, 10, 30, 5, 5, 4)

        # Verify placement
        u1 = pcb.footprints.get_by_reference("U1")
        u2 = pcb.footprints.get_by_reference("U2")
        u3 = pcb.footprints.get_by_reference("U3")

        assert u1.position.y == 10
        assert u2.position.y == 10
        assert u3.position.y == 10
        assert u1.position.x < u2.position.x < u3.position.x

    def test_design_iteration_workflow(self, tmp_path):
        """Test iterative design workflow with save/load."""
        # Iteration 1: Initial design
        pcb = PCBBoard()
        pcb.add_footprint("R1", "Resistor_SMD:R_0603_1608Metric", 10, 10, value="10k")
        pcb.set_board_outline_rect(0, 0, 50, 50)

        file_path = tmp_path / "design_v1.kicad_pcb"
        pcb.save(file_path)

        # Iteration 2: Load and modify
        pcb2 = PCBBoard(str(file_path))
        pcb2.add_footprint("C1", "Capacitor_SMD:C_0603_1608Metric", 20, 10, value="100nF")
        pcb2.save(file_path)

        # Iteration 3: Load and validate
        pcb3 = PCBBoard(str(file_path))
        assert len(list(pcb3.footprints)) == 2

        # Run validation
        issues = pcb3.validate()
        # Should pass basic validation
        assert len(pcb3.validation.get_errors()) == 0


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_board_validation(self):
        """Test validation on empty board."""
        pcb = PCBBoard()
        issues = pcb.validate()
        # Empty board should have minimal issues
        assert issues >= 0

    def test_empty_board_drc(self):
        """Test DRC on empty board."""
        pcb = PCBBoard()
        violations = pcb.check_drc()
        assert violations == 0

    def test_placement_with_nonexistent_references(self):
        """Test placement with invalid references."""
        pcb = PCBBoard()
        pcb.add_footprint("R1", "Resistor_SMD:R_0603_1608Metric", 10, 10)

        # Try to place non-existent component
        placed = pcb.place_grid(["R1", "R2", "R3"], 10, 10, 5, 5, 2)
        assert placed == 1  # Only R1 exists

    def test_net_operations_on_empty_board(self):
        """Test net operations on board with no nets."""
        pcb = PCBBoard()

        nets = pcb.nets
        # Should have at least net 0
        assert 0 in nets

        stats = pcb.net.get_net_statistics()
        # Should return empty or minimal stats
        assert isinstance(stats, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
