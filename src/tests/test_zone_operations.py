"""
Integration tests for zone/copper pour operation workflows.

Tests end-to-end zone manipulation including:
- Creating zones (copper pours)
- Setting zone properties (clearance, priority, etc.)
- Zone fill configuration
- Net assignment for zones
- Multiple zone coordination
"""

import pytest
from pathlib import Path
import tempfile

from kicad_pcb_api import PCBBoard, Point, Zone


@pytest.mark.integration
class TestZoneOperations:
    """Integration tests for zone/copper pour workflows."""

    def test_create_simple_zone_workflow(self, tmp_path):
        """Test creating a simple copper pour zone."""
        pcb = PCBBoard()

        # Add a footprint that the zone might connect to
        pcb.add_footprint("U1", "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", 50, 50)

        # Create a rectangular zone around the component
        zone_points = [
            Point(30, 30),
            Point(70, 30),
            Point(70, 70),
            Point(30, 70),
        ]

        zone = Zone(
            net=1,
            layer="F.Cu",
            polygon=zone_points,
            priority=0,
            clearance=0.5,
            min_thickness=0.25,
            uuid="zone-1"
        )
        pcb.pcb_data["zones"].append(zone)

        # Verify zone was added
        assert len(pcb.pcb_data["zones"]) == 1
        assert pcb.pcb_data["zones"][0].net == 1
        assert pcb.pcb_data["zones"][0].layer == "F.Cu"
        assert len(pcb.pcb_data["zones"][0].polygon) == 4

        # Save and reload
        file_path = tmp_path / "test_simple_zone.kicad_pcb"
        pcb.save(file_path)

        pcb2 = PCBBoard(str(file_path))
        assert len(pcb2.pcb_data["zones"]) == 1
        zone_loaded = pcb2.pcb_data["zones"][0]
        assert zone_loaded.net == 1
        assert zone_loaded.layer == "F.Cu"
        assert len(zone_loaded.polygon) == 4

    def test_zone_properties_configuration(self, tmp_path):
        """Test setting various zone properties."""
        pcb = PCBBoard()

        # Create zone with specific properties
        zone_points = [
            Point(10, 10),
            Point(40, 10),
            Point(40, 40),
            Point(10, 40),
        ]

        zone = Zone(
            net=1,
            layer="F.Cu",
            polygon=zone_points,
            priority=5,
            clearance=0.5,
            min_thickness=0.254,
            filled_areas_thickness=True,
            fill_type="solid",
            hatch_thickness=0.5,
            hatch_gap=0.5,
            uuid="zone-configured"
        )
        pcb.pcb_data["zones"].append(zone)

        # Verify properties
        assert pcb.pcb_data["zones"][0].priority == 5
        assert pcb.pcb_data["zones"][0].clearance == 0.5
        assert pcb.pcb_data["zones"][0].min_thickness == 0.254

        # Test thermal relief properties if supported
        if hasattr(zone, 'thermal_gap'):
            zone.thermal_gap = 0.5
            zone.thermal_bridge_width = 0.5

        # Save and reload
        file_path = tmp_path / "test_zone_properties.kicad_pcb"
        pcb.save(file_path)

        pcb2 = PCBBoard(str(file_path))
        assert len(pcb2.pcb_data["zones"]) == 1
        zone_loaded = pcb2.pcb_data["zones"][0]
        assert zone_loaded.priority == 5
        assert zone_loaded.clearance == 0.5
        assert zone_loaded.min_thickness == 0.254

    def test_zone_priorities_and_overlap(self, tmp_path):
        """Test multiple zones with different priorities."""
        pcb = PCBBoard()

        # Create ground plane (low priority)
        gnd_zone_points = [
            Point(0, 0),
            Point(100, 0),
            Point(100, 100),
            Point(0, 100),
        ]
        gnd_zone = Zone(
            net=1,  # GND
            layer="F.Cu",
            polygon=gnd_zone_points,
            priority=0,
            clearance=0.5,
            min_thickness=0.25,
            uuid="zone-gnd"
        )

        # Create power zone (higher priority, smaller area)
        pwr_zone_points = [
            Point(20, 20),
            Point(50, 20),
            Point(50, 50),
            Point(20, 50),
        ]
        pwr_zone = Zone(
            net=2,  # VCC
            layer="F.Cu",
            polygon=pwr_zone_points,
            priority=10,  # Higher priority
            clearance=0.5,
            min_thickness=0.25,
            uuid="zone-pwr"
        )

        # Create signal zone (medium priority)
        sig_zone_points = [
            Point(60, 60),
            Point(90, 60),
            Point(90, 90),
            Point(60, 90),
        ]
        sig_zone = Zone(
            net=3,  # Signal net
            layer="F.Cu",
            polygon=sig_zone_points,
            priority=5,
            clearance=0.3,
            min_thickness=0.25,
            uuid="zone-sig"
        )

        pcb.pcb_data["zones"].append(gnd_zone)
        pcb.pcb_data["zones"].append(pwr_zone)
        pcb.pcb_data["zones"].append(sig_zone)

        # Verify priorities
        assert len(pcb.pcb_data["zones"]) == 3
        priorities = [z.priority for z in pcb.pcb_data["zones"]]
        assert 0 in priorities   # GND
        assert 10 in priorities  # VCC (highest)
        assert 5 in priorities   # Signal

        # Verify different nets
        nets = [z.net for z in pcb.pcb_data["zones"]]
        assert len(set(nets)) == 3  # Three different nets

        # Save and reload
        file_path = tmp_path / "test_zone_priorities.kicad_pcb"
        pcb.save(file_path)

        pcb2 = PCBBoard(str(file_path))
        assert len(pcb2.pcb_data["zones"]) == 3

        # Verify priorities persisted
        priorities2 = [z.priority for z in pcb2.pcb_data["zones"]]
        assert 0 in priorities2
        assert 10 in priorities2
        assert 5 in priorities2

    def test_zone_net_assignment(self, tmp_path):
        """Test zone net assignment for power distribution."""
        pcb = PCBBoard()

        # Add power components
        pcb.add_footprint("U1", "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", 50, 50)
        pcb.add_footprint("C1", "Capacitor_SMD:C_0603_1608Metric", 40, 50, value="10uF")
        pcb.add_footprint("C2", "Capacitor_SMD:C_0603_1608Metric", 60, 50, value="100nF")

        # Create GND zone on front layer
        gnd_zone_front = Zone(
            net=1,  # GND
            layer="F.Cu",
            polygon=[
                Point(20, 20),
                Point(80, 20),
                Point(80, 80),
                Point(20, 80),
            ],
            priority=0,
            clearance=0.5,
            min_thickness=0.25,
            uuid="zone-gnd-front"
        )

        # Create VCC zone on back layer
        vcc_zone_back = Zone(
            net=2,  # VCC
            layer="B.Cu",
            polygon=[
                Point(20, 20),
                Point(80, 20),
                Point(80, 80),
                Point(20, 80),
            ],
            priority=0,
            clearance=0.5,
            min_thickness=0.25,
            uuid="zone-vcc-back"
        )

        pcb.pcb_data["zones"].append(gnd_zone_front)
        pcb.pcb_data["zones"].append(vcc_zone_back)

        # Verify net assignments
        assert len(pcb.pcb_data["zones"]) == 2
        assert pcb.pcb_data["zones"][0].net == 1  # GND
        assert pcb.pcb_data["zones"][1].net == 2  # VCC

        # Verify layer assignments
        assert pcb.pcb_data["zones"][0].layer == "F.Cu"
        assert pcb.pcb_data["zones"][1].layer == "B.Cu"

        # Save and reload
        file_path = tmp_path / "test_zone_nets.kicad_pcb"
        pcb.save(file_path)

        pcb2 = PCBBoard(str(file_path))
        assert len(pcb2.pcb_data["zones"]) == 2

        # Verify nets persisted
        nets = [z.net for z in pcb2.pcb_data["zones"]]
        assert 1 in nets
        assert 2 in nets

    def test_complex_zone_polygon_shapes(self, tmp_path):
        """Test zones with complex polygon shapes."""
        pcb = PCBBoard()

        # Create L-shaped zone
        l_shaped_points = [
            Point(10, 10),
            Point(40, 10),
            Point(40, 30),
            Point(30, 30),
            Point(30, 40),
            Point(10, 40),
        ]
        l_zone = Zone(
            net=1,
            layer="F.Cu",
            polygon=l_shaped_points,
            priority=0,
            clearance=0.5,
            min_thickness=0.25,
            uuid="zone-l-shape"
        )

        # Create octagonal zone
        import math
        center_x, center_y, radius = 70, 30, 15
        octagon_points = []
        for i in range(8):
            angle = i * math.pi / 4
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            octagon_points.append(Point(x, y))

        octagon_zone = Zone(
            net=2,
            layer="F.Cu",
            polygon=octagon_points,
            priority=0,
            clearance=0.5,
            min_thickness=0.25,
            uuid="zone-octagon"
        )

        # Create triangular zone
        triangle_points = [
            Point(50, 60),
            Point(70, 90),
            Point(30, 90),
        ]
        triangle_zone = Zone(
            net=3,
            layer="F.Cu",
            polygon=triangle_points,
            priority=0,
            clearance=0.5,
            min_thickness=0.25,
            uuid="zone-triangle"
        )

        pcb.pcb_data["zones"].append(l_zone)
        pcb.pcb_data["zones"].append(octagon_zone)
        pcb.pcb_data["zones"].append(triangle_zone)

        # Verify different polygon vertex counts
        assert len(pcb.pcb_data["zones"]) == 3
        assert len(pcb.pcb_data["zones"][0].polygon) == 6  # L-shape
        assert len(pcb.pcb_data["zones"][1].polygon) == 8  # Octagon
        assert len(pcb.pcb_data["zones"][2].polygon) == 3  # Triangle

        # Save and reload
        file_path = tmp_path / "test_zone_shapes.kicad_pcb"
        pcb.save(file_path)

        pcb2 = PCBBoard(str(file_path))
        assert len(pcb2.pcb_data["zones"]) == 3

        # Verify polygon counts persisted
        assert len(pcb2.pcb_data["zones"][0].polygon) == 6
        assert len(pcb2.pcb_data["zones"][1].polygon) == 8
        assert len(pcb2.pcb_data["zones"][2].polygon) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
