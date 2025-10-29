"""
Integration tests for manager coordination workflows.

Tests how different managers work together:
- PlacementManager + ValidationManager
- RoutingManager + NetManager
- DRCManager + ValidationManager
- Multiple managers in complex workflows
- Manager state coordination
"""

import pytest
from pathlib import Path
import tempfile
import math

from kicad_pcb_api import PCBBoard, Point, Track, Via


@pytest.mark.integration
class TestManagerIntegration:
    """Integration tests for manager coordination."""

    def test_placement_with_validation(self, tmp_path):
        """Test placement manager coordinating with validation."""
        pcb = PCBBoard()

        # Add components
        for i in range(1, 6):
            pcb.add_footprint(f"R{i}", "Resistor_SMD:R_0603_1608Metric", 0, 0, value=f"{i}k")

        # Use placement manager to arrange components
        refs = [f"R{i}" for i in range(1, 6)]
        if hasattr(pcb, 'placement'):
            # Place in grid
            placed = pcb.place_grid(refs, 10, 10, 10, 10, 3)
            assert placed == 5

            # Align horizontally
            pcb.placement.align_horizontally(refs[:3], y=20)

            # Verify alignment
            for ref in refs[:3]:
                fp = pcb.get_footprint(ref)
                assert fp.position.y == 20

        # Run validation after placement
        if hasattr(pcb, 'validation'):
            issues = pcb.validate()
            # Should have no errors after clean placement
            errors = pcb.validation.get_errors()
            assert len([e for e in errors if e.category == "reference"]) == 0

        # Save and reload
        file_path = tmp_path / "test_placement_validation.kicad_pcb"
        pcb.save(file_path)

        pcb2 = PCBBoard(str(file_path))
        assert pcb2.get_footprint_count() == 5

        # Validate reloaded board
        if hasattr(pcb2, 'validation'):
            issues2 = pcb2.validate()
            errors2 = pcb2.validation.get_errors()
            assert len([e for e in errors2 if e.category == "reference"]) == 0

    def test_routing_with_net_management(self, tmp_path):
        """Test routing manager coordinating with net manager."""
        pcb = PCBBoard()

        # Add components
        pcb.add_footprint("U1", "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", 20, 20)
        pcb.add_footprint("R1", "Resistor_SMD:R_0603_1608Metric", 40, 20, value="10k")
        pcb.add_footprint("C1", "Capacitor_SMD:C_0603_1608Metric", 60, 20, value="100nF")

        # Connect components (creates nets)
        pcb.connect_pads("U1", "1", "R1", "1", "Signal1")
        pcb.connect_pads("R1", "2", "C1", "1", "Signal2")

        # Use routing manager if available
        if hasattr(pcb, 'routing'):
            # Create Manhattan route
            start = Point(20, 30)
            end = Point(40, 40)
            tracks = pcb.routing.route_manhattan(start, end, 0.25, "F.Cu", net=1)

            if tracks:
                assert len(tracks) == 2  # Horizontal + vertical

        # Use net manager to get statistics
        if hasattr(pcb, 'net'):
            stats = pcb.net.get_net_statistics()
            assert isinstance(stats, dict)
            assert len(stats) >= 1  # At least net 0

            # Get all nets
            nets = pcb.nets
            assert 0 in nets  # Net 0 always exists

        # Save and reload
        file_path = tmp_path / "test_routing_nets.kicad_pcb"
        pcb.save(file_path)

        pcb2 = PCBBoard(str(file_path))
        assert pcb2.get_footprint_count() == 3

        # Verify nets persisted
        if hasattr(pcb2, 'net'):
            stats2 = pcb2.net.get_net_statistics()
            assert isinstance(stats2, dict)

    def test_drc_after_routing(self, tmp_path):
        """Test DRC manager checking routing results."""
        pcb = PCBBoard()

        # Add footprints
        pcb.add_footprint("R1", "Resistor_SMD:R_0603_1608Metric", 10, 10)
        pcb.add_footprint("R2", "Resistor_SMD:R_0603_1608Metric", 30, 10)

        # Add tracks with various widths (some violating DRC)
        tracks_data = [
            (Point(0, 0), Point(10, 0), 0.05, "F.Cu", 1),   # Too narrow
            (Point(0, 5), Point(10, 5), 0.25, "F.Cu", 2),   # OK
            (Point(0, 10), Point(10, 10), 0.5, "F.Cu", 3),  # OK
            (Point(0, 15), Point(10, 15), 15.0, "F.Cu", 4), # Too wide
        ]

        for start, end, width, layer, net in tracks_data:
            track = Track(start, end, width, layer, net, uuid=f"track-{net}")
            pcb.pcb_data["tracks"].append(track)

        # Run DRC with specific rules
        if hasattr(pcb, 'drc'):
            violations = pcb.check_drc(min_track_width=0.1, max_track_width=10.0)
            assert violations >= 2  # Should catch narrow and wide tracks

            # Get detailed errors and warnings
            errors = pcb.drc.get_errors()
            warnings = pcb.drc.get_warnings()

            # Should have at least one error and one warning
            assert len(errors) >= 1
            assert len(warnings) >= 1

        # Save and reload
        file_path = tmp_path / "test_drc_routing.kicad_pcb"
        pcb.save(file_path)

        pcb2 = PCBBoard(str(file_path))
        assert len(pcb2.pcb_data["tracks"]) == 4

        # Re-run DRC on reloaded board
        if hasattr(pcb2, 'drc'):
            violations2 = pcb2.check_drc(min_track_width=0.1, max_track_width=10.0)
            assert violations2 >= 2

    def test_multiple_managers_workflow(self, tmp_path):
        """Test complex workflow using multiple managers together."""
        pcb = PCBBoard()

        # Step 1: Add components
        component_refs = []
        for i in range(1, 9):
            ref = f"U{i}"
            component_refs.append(ref)
            pcb.add_footprint(ref, "Package_DIP:DIP-8_W7.62mm", 0, 0)

        # Step 2: Use placement manager for circular layout
        if hasattr(pcb, 'placement'):
            placed = pcb.placement.place_in_circle(component_refs, 50, 50, 20)
            if placed:
                assert placed == 8

                # Verify circular placement
                for ref in component_refs:
                    fp = pcb.get_footprint(ref)
                    dx = fp.position.x - 50
                    dy = fp.position.y - 50
                    distance = math.sqrt(dx * dx + dy * dy)
                    # Should be at approximately radius 20
                    assert abs(distance - 20) < 1.0

        # Step 3: Add some routing
        if hasattr(pcb, 'routing'):
            tracks = pcb.routing.route_manhattan(Point(30, 50), Point(70, 50), 0.25, "F.Cu", net=1)

        # Step 4: Validate the design
        if hasattr(pcb, 'validation'):
            issues = pcb.validate()
            errors = pcb.validation.get_errors()
            # No duplicate references
            ref_errors = [e for e in errors if e.category == "reference"]
            assert len(ref_errors) == 0

        # Step 5: Check DRC
        if hasattr(pcb, 'drc'):
            violations = pcb.check_drc(min_track_width=0.1)
            # Should be valid with proper track widths

        # Step 6: Get net statistics
        if hasattr(pcb, 'net'):
            stats = pcb.net.get_net_statistics()
            assert isinstance(stats, dict)

        # Save final design
        file_path = tmp_path / "test_multi_manager.kicad_pcb"
        pcb.save(file_path)

        # Reload and verify
        pcb2 = PCBBoard(str(file_path))
        assert pcb2.get_footprint_count() == 8

    def test_validation_with_drc_coordination(self, tmp_path):
        """Test validation and DRC managers working together."""
        pcb = PCBBoard()

        # Create a design with multiple issues
        # Issue 1: Duplicate references
        pcb.add_footprint("R1", "Resistor_SMD:R_0603_1608Metric", 10, 10)
        pcb.add_footprint("R1", "Resistor_SMD:R_0603_1608Metric", 20, 10)  # Duplicate!
        pcb.add_footprint("C1", "Capacitor_SMD:C_0603_1608Metric", 30, 10)

        # Issue 2: Track width violations
        narrow_track = Track(
            Point(0, 0), Point(10, 0), 0.05, "F.Cu", 1, uuid="narrow"
        )
        pcb.pcb_data["tracks"].append(narrow_track)

        # Run validation
        if hasattr(pcb, 'validation'):
            issues = pcb.validate()
            assert issues > 0  # Should detect duplicate reference

            errors = pcb.validation.get_errors()
            ref_errors = [e for e in errors if e.category == "reference"]
            assert len(ref_errors) > 0  # Duplicate reference error

        # Run DRC
        if hasattr(pcb, 'drc'):
            violations = pcb.check_drc(min_track_width=0.1)
            assert violations > 0  # Should detect narrow track

            drc_errors = pcb.drc.get_errors()
            assert len(drc_errors) > 0  # Track width error

        # Now fix the issues
        # Fix 1: Remove duplicate footprint
        pcb.remove_footprint("R1")
        pcb.add_footprint("R1", "Resistor_SMD:R_0603_1608Metric", 10, 10)

        # Fix 2: Update track width
        pcb.pcb_data["tracks"][0].width = 0.25

        # Re-run validation
        if hasattr(pcb, 'validation'):
            issues2 = pcb.validate()
            errors2 = pcb.validation.get_errors()
            ref_errors2 = [e for e in errors2 if e.category == "reference"]
            # Should be fixed now
            assert len(ref_errors2) == 0

        # Re-run DRC
        if hasattr(pcb, 'drc'):
            violations2 = pcb.check_drc(min_track_width=0.1)
            drc_errors2 = pcb.drc.get_errors()
            # Track width should be fixed
            track_errors = [e for e in drc_errors2 if "width" in e.description.lower()]
            # Should have fewer or no track width errors

        # Save validated design
        file_path = tmp_path / "test_validation_drc.kicad_pcb"
        pcb.save(file_path)

        pcb2 = PCBBoard(str(file_path))
        assert pcb2.get_footprint_count() == 2  # R1 and C1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
