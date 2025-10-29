"""
Integration tests for complete end-to-end PCB design workflows.

Tests realistic PCB design scenarios from start to finish:
- Create new PCB from scratch
- Add and place components
- Route connections
- Add copper pours
- Validate and check DRC
- Save and reload
"""

import pytest
from pathlib import Path
import tempfile
import math

from kicad_pcb_api import PCBBoard, Point, Track, Via, Zone


@pytest.mark.integration
class TestCompleteWorkflow:
    """Integration tests for complete PCB design workflows."""

    def test_simple_led_circuit_workflow(self, tmp_path):
        """Test complete workflow: Simple LED circuit with resistor."""
        # Step 1: Create new PCB
        pcb = PCBBoard()
        assert pcb.get_footprint_count() == 0

        # Step 2: Add components
        led = pcb.add_footprint(
            "D1",
            "LED_SMD:LED_0805_2012Metric",
            50, 50,
            value="RED"
        )
        resistor = pcb.add_footprint(
            "R1",
            "Resistor_SMD:R_0603_1608Metric",
            40, 50,
            value="330"
        )
        connector = pcb.add_footprint(
            "J1",
            "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical",
            30, 50,
            value="POWER"
        )

        assert pcb.get_footprint_count() == 3

        # Step 3: Position components
        led.position = Point(50, 50)
        resistor.position = Point(40, 50)
        connector.position = Point(25, 50)

        # Step 4: Add routing between components
        # Connect J1 to R1
        track1 = Track(
            Point(25, 50), Point(40, 50),
            0.5, "F.Cu", 1, uuid="track-1"
        )
        # Connect R1 to D1
        track2 = Track(
            Point(40, 50), Point(50, 50),
            0.5, "F.Cu", 1, uuid="track-2"
        )
        pcb.pcb_data["tracks"].append(track1)
        pcb.pcb_data["tracks"].append(track2)

        # Step 5: Add ground track
        track3 = Track(
            Point(25, 55), Point(50, 55),
            0.5, "F.Cu", 2, uuid="track-gnd"
        )
        pcb.pcb_data["tracks"].append(track3)

        # Step 6: Set board outline
        pcb.set_board_outline_rect(0, 0, 80, 80)

        # Step 7: Validate design
        if hasattr(pcb, 'validation'):
            issues = pcb.validate()
            errors = pcb.validation.get_errors()
            # Should have no critical errors
            assert len([e for e in errors if e.category == "reference"]) == 0

        # Step 8: Save PCB
        file_path = tmp_path / "led_circuit.kicad_pcb"
        pcb.save(file_path)
        assert file_path.exists()

        # Step 9: Reload and verify
        pcb2 = PCBBoard(str(file_path))
        assert pcb2.get_footprint_count() == 3
        assert len(pcb2.pcb_data["tracks"]) == 3

        # Verify components
        assert pcb2.get_footprint("D1") is not None
        assert pcb2.get_footprint("R1") is not None
        assert pcb2.get_footprint("J1") is not None

    def test_power_supply_circuit_workflow(self, tmp_path):
        """Test complete workflow: Power supply with regulator and capacitors."""
        # Create PCB
        pcb = PCBBoard()

        # Add power supply components
        reg = pcb.add_footprint(
            "U1",
            "Package_TO_SOT_SMD:SOT-23",
            50, 50,
            value="LM1117-3.3"
        )
        cin = pcb.add_footprint(
            "C1",
            "Capacitor_SMD:C_1206_3216Metric",
            35, 50,
            value="10uF"
        )
        cout = pcb.add_footprint(
            "C2",
            "Capacitor_SMD:C_0603_1608Metric",
            65, 50,
            value="10uF"
        )
        cout2 = pcb.add_footprint(
            "C3",
            "Capacitor_SMD:C_0603_1608Metric",
            65, 55,
            value="100nF"
        )

        # Add connectors
        vin_conn = pcb.add_footprint(
            "J1",
            "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical",
            20, 50,
            value="VIN"
        )
        vout_conn = pcb.add_footprint(
            "J2",
            "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical",
            80, 50,
            value="VOUT"
        )

        assert pcb.get_footprint_count() == 6

        # Add power traces (wider for power)
        power_tracks = [
            Track(Point(20, 50), Point(35, 50), 0.8, "F.Cu", 1, uuid="vin-cin"),
            Track(Point(35, 50), Point(50, 50), 0.8, "F.Cu", 1, uuid="cin-reg"),
            Track(Point(50, 50), Point(65, 50), 0.8, "F.Cu", 2, uuid="reg-cout"),
            Track(Point(65, 50), Point(80, 50), 0.8, "F.Cu", 2, uuid="cout-vout"),
        ]
        for track in power_tracks:
            pcb.pcb_data["tracks"].append(track)

        # Add ground plane zone
        gnd_zone = Zone(
            net=3,  # GND net
            layer="B.Cu",
            polygon=[
                Point(10, 40),
                Point(90, 40),
                Point(90, 70),
                Point(10, 70),
            ],
            priority=0,
            clearance=0.5,
            min_thickness=0.25,
            uuid="zone-gnd"
        )
        pcb.pcb_data["zones"].append(gnd_zone)

        # Add vias for ground connections
        via_positions = [(35, 55), (50, 55), (65, 60)]
        for i, (x, y) in enumerate(via_positions):
            via = Via(
                Point(x, y), 0.8, 0.4, ["F.Cu", "B.Cu"], 3, uuid=f"via-gnd-{i}"
            )
            pcb.pcb_data["vias"].append(via)

        # Set board outline
        pcb.set_board_outline_rect(0, 0, 100, 80)

        # Validate
        if hasattr(pcb, 'validation'):
            issues = pcb.validate()
            # Check for major issues
            errors = pcb.validation.get_errors()
            critical_errors = [e for e in errors if e.category in ["reference", "net"]]
            assert len(critical_errors) == 0

        # Check DRC
        if hasattr(pcb, 'drc'):
            violations = pcb.check_drc(min_track_width=0.1)
            # Power traces should pass minimum width

        # Save and reload
        file_path = tmp_path / "power_supply.kicad_pcb"
        pcb.save(file_path)

        pcb2 = PCBBoard(str(file_path))
        assert pcb2.get_footprint_count() == 6
        assert len(pcb2.pcb_data["tracks"]) == 4
        assert len(pcb2.pcb_data["vias"]) == 3
        assert len(pcb2.pcb_data["zones"]) == 1

    def test_sensor_array_workflow(self, tmp_path):
        """Test complete workflow: Sensor array with uniform placement."""
        pcb = PCBBoard()

        # Add sensor array
        sensor_refs = []
        for i in range(1, 9):
            ref = f"U{i}"
            sensor_refs.append(ref)
            pcb.add_footprint(
                ref,
                "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm",
                0, 0,
                value="LM75"
            )

        # Add pull-up resistors for I2C
        pcb.add_footprint("R1", "Resistor_SMD:R_0603_1608Metric", 0, 0, value="4.7k")
        pcb.add_footprint("R2", "Resistor_SMD:R_0603_1608Metric", 0, 0, value="4.7k")

        assert pcb.get_footprint_count() == 10

        # Use placement manager for grid layout
        if hasattr(pcb, 'placement'):
            # Place sensors in 2x4 grid
            placed = pcb.place_grid(sensor_refs, 20, 20, 15, 15, 4)
            if placed:
                assert placed == 8

            # Place resistors
            r1 = pcb.get_footprint("R1")
            r2 = pcb.get_footprint("R2")
            r1.position = Point(10, 10)
            r2.position = Point(15, 10)

        # Create I2C bus traces
        # SDA line
        sda_track = Track(
            Point(10, 10), Point(80, 10),
            0.25, "F.Cu", 1, uuid="sda-bus"
        )
        # SCL line
        scl_track = Track(
            Point(15, 10), Point(80, 15),
            0.25, "F.Cu", 2, uuid="scl-bus"
        )
        pcb.pcb_data["tracks"].append(sda_track)
        pcb.pcb_data["tracks"].append(scl_track)

        # Add ground plane
        gnd_zone = Zone(
            net=3,
            layer="B.Cu",
            polygon=[
                Point(0, 0),
                Point(100, 0),
                Point(100, 80),
                Point(0, 80),
            ],
            priority=0,
            clearance=0.5,
            min_thickness=0.25,
            uuid="zone-gnd-plane"
        )
        pcb.pcb_data["zones"].append(gnd_zone)

        # Set board outline
        pcb.set_board_outline_rect(0, 0, 100, 80)

        # Validate
        if hasattr(pcb, 'validation'):
            issues = pcb.validate()
            errors = pcb.validation.get_errors()
            # All references should be unique
            ref_errors = [e for e in errors if e.category == "reference"]
            assert len(ref_errors) == 0

        # Save
        file_path = tmp_path / "sensor_array.kicad_pcb"
        pcb.save(file_path)

        pcb2 = PCBBoard(str(file_path))
        assert pcb2.get_footprint_count() == 10
        assert len(pcb2.pcb_data["zones"]) == 1

    def test_multilayer_design_workflow(self, tmp_path):
        """Test complete workflow: Multilayer board with vias."""
        pcb = PCBBoard()

        # Add components
        mcu = pcb.add_footprint(
            "U1",
            "Package_QFP:LQFP-48_7x7mm_P0.5mm",
            50, 50,
            value="STM32"
        )
        crystal = pcb.add_footprint(
            "Y1",
            "Crystal:Crystal_SMD_HC49-SD",
            35, 50,
            value="8MHz"
        )
        caps = []
        for i in range(1, 5):
            cap = pcb.add_footprint(
                f"C{i}",
                "Capacitor_SMD:C_0603_1608Metric",
                40 + i*5, 60,
                value="100nF"
            )
            caps.append(cap)

        assert pcb.get_footprint_count() == 6

        # Add traces on front layer
        track_f1 = Track(Point(35, 50), Point(50, 50), 0.25, "F.Cu", 1, uuid="xtal-mcu")
        pcb.pcb_data["tracks"].append(track_f1)

        # Add via to transition to back layer
        via1 = Via(Point(50, 45), 0.6, 0.3, ["F.Cu", "B.Cu"], 1, uuid="via-1")
        pcb.pcb_data["vias"].append(via1)

        # Add trace on back layer
        track_b1 = Track(Point(50, 45), Point(60, 45), 0.25, "B.Cu", 1, uuid="back-trace")
        pcb.pcb_data["tracks"].append(track_b1)

        # Add power zones on different layers
        # VCC zone on front
        vcc_zone_f = Zone(
            net=2,
            layer="F.Cu",
            polygon=[
                Point(70, 40),
                Point(90, 40),
                Point(90, 70),
                Point(70, 70),
            ],
            priority=5,
            clearance=0.5,
            min_thickness=0.25,
            uuid="zone-vcc-front"
        )

        # GND zone on back (larger, lower priority)
        gnd_zone_b = Zone(
            net=3,
            layer="B.Cu",
            polygon=[
                Point(10, 30),
                Point(90, 30),
                Point(90, 70),
                Point(10, 70),
            ],
            priority=0,
            clearance=0.5,
            min_thickness=0.25,
            uuid="zone-gnd-back"
        )

        pcb.pcb_data["zones"].append(vcc_zone_f)
        pcb.pcb_data["zones"].append(gnd_zone_b)

        # Add power vias
        for x in [45, 55]:
            for y in [45, 55]:
                via = Via(
                    Point(x, y), 0.8, 0.4,
                    ["F.Cu", "B.Cu"], 3,
                    uuid=f"via-gnd-{x}-{y}"
                )
                pcb.pcb_data["vias"].append(via)

        # Set board outline
        pcb.set_board_outline_rect(0, 0, 100, 80)

        # Validate
        if hasattr(pcb, 'validation'):
            issues = pcb.validate()

        # Check DRC
        if hasattr(pcb, 'drc'):
            violations = pcb.check_drc(min_track_width=0.15)

        # Get net statistics
        if hasattr(pcb, 'net'):
            stats = pcb.net.get_net_statistics()
            assert isinstance(stats, dict)

        # Save
        file_path = tmp_path / "multilayer_design.kicad_pcb"
        pcb.save(file_path)

        # Reload and verify
        pcb2 = PCBBoard(str(file_path))
        assert pcb2.get_footprint_count() == 6
        assert len(pcb2.pcb_data["vias"]) == 5  # 1 signal + 4 power
        assert len(pcb2.pcb_data["zones"]) == 2
        assert len(pcb2.pcb_data["tracks"]) == 2

        # Verify zones on correct layers
        zones = pcb2.pcb_data["zones"]
        layers = [z.layer for z in zones]
        assert "F.Cu" in layers
        assert "B.Cu" in layers

    def test_iterative_design_refinement_workflow(self, tmp_path):
        """Test complete workflow: Iterative design with modifications."""
        file_path = tmp_path / "iterative_design.kicad_pcb"

        # Iteration 1: Initial design
        pcb = PCBBoard()
        pcb.add_footprint("R1", "Resistor_SMD:R_0603_1608Metric", 10, 10, value="10k")
        pcb.add_footprint("C1", "Capacitor_SMD:C_0603_1608Metric", 20, 10, value="100nF")
        pcb.set_board_outline_rect(0, 0, 50, 50)
        pcb.save(file_path)

        # Iteration 2: Add more components
        pcb2 = PCBBoard(str(file_path))
        assert pcb2.get_footprint_count() == 2

        pcb2.add_footprint("R2", "Resistor_SMD:R_0603_1608Metric", 30, 10, value="10k")
        pcb2.add_footprint("U1", "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", 20, 25, value="LM358")

        # Add routing
        track1 = Track(Point(10, 10), Point(20, 10), 0.25, "F.Cu", 1, uuid="r1-c1")
        track2 = Track(Point(20, 10), Point(30, 10), 0.25, "F.Cu", 1, uuid="c1-r2")
        pcb2.pcb_data["tracks"].append(track1)
        pcb2.pcb_data["tracks"].append(track2)

        pcb2.save(file_path)

        # Iteration 3: Add ground plane and validate
        pcb3 = PCBBoard(str(file_path))
        assert pcb3.get_footprint_count() == 4
        assert len(pcb3.pcb_data["tracks"]) == 2

        # Add ground zone
        gnd_zone = Zone(
            net=2,
            layer="B.Cu",
            polygon=[
                Point(0, 0),
                Point(50, 0),
                Point(50, 50),
                Point(0, 50),
            ],
            priority=0,
            clearance=0.5,
            min_thickness=0.25,
            uuid="zone-gnd-final"
        )
        pcb3.pcb_data["zones"].append(gnd_zone)

        # Final validation
        if hasattr(pcb3, 'validation'):
            issues = pcb3.validate()
            errors = pcb3.validation.get_errors()
            # Should have no reference errors
            ref_errors = [e for e in errors if e.category == "reference"]
            assert len(ref_errors) == 0

        # Increase board size
        pcb3.set_board_outline_rect(0, 0, 70, 70)

        pcb3.save(file_path)

        # Final verification
        pcb_final = PCBBoard(str(file_path))
        assert pcb_final.get_footprint_count() == 4
        assert len(pcb_final.pcb_data["tracks"]) == 2
        assert len(pcb_final.pcb_data["zones"]) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
