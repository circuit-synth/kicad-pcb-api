"""
Demonstration of PCBParser and PCBFormatter usage.

This example shows how to:
1. Parse a KiCad PCB file
2. Inspect the parsed data
3. Modify the data
4. Write it back to a file
"""

from pathlib import Path
import tempfile

from kicad_pcb_api.core.pcb_parser import PCBParser
from kicad_pcb_api.core.types import Footprint, Net, Point, Property


def main():
    """Demonstrate parser/formatter functionality."""
    parser = PCBParser()

    # Example 1: Parse a minimal PCB from string
    print("Example 1: Parse a minimal PCB\n" + "=" * 50)
    minimal_pcb = """(kicad_pcb (version 20241229) (generator pcbnew)
  (general
    (thickness 1.6)
  )
  (paper "A4")
  (layers
    (0 "F.Cu" signal)
    (31 "B.Cu" signal)
  )
  (net 0 "")
  (net 1 "GND")
  (net 2 "VCC")

  (footprint "Resistor_SMD:R_0603_1608Metric" (layer "F.Cu")
    (uuid "test-uuid-1")
    (at 100 50)
    (property "Reference" "R1"
      (at 0 -1.5 0)
      (layer "F.SilkS")
      (uuid "ref-uuid")
      (effects (font (size 1.0 1.0) (thickness 0.15)))
    )
    (property "Value" "10k"
      (at 0 1.5 0)
      (layer "F.Fab")
      (uuid "val-uuid")
      (effects (font (size 1.0 1.0) (thickness 0.15)))
    )
    (pad "1" smd rect (at -0.875 0) (size 1.05 0.95) (layers "F.Cu" "F.Paste" "F.Mask")
      (net 1 "GND")
      (uuid "pad1-uuid")
    )
    (pad "2" smd rect (at 0.875 0) (size 1.05 0.95) (layers "F.Cu" "F.Paste" "F.Mask")
      (net 2 "VCC")
      (uuid "pad2-uuid")
    )
    (embedded_fonts no)
  )
  (embedded_fonts no)
)"""

    # Parse the PCB
    pcb_data = parser.parse_string(minimal_pcb)

    # Inspect parsed data
    print(f"Version: {pcb_data['version']}")
    print(f"Generator: {pcb_data['generator']}")
    print(f"Number of layers: {len(pcb_data['layers'])}")
    print(f"Number of nets: {len(pcb_data['nets'])}")
    print(f"Number of footprints: {len(pcb_data['footprints'])}")

    # Inspect the footprint
    if pcb_data['footprints']:
        fp = pcb_data['footprints'][0]
        print(f"\nFootprint details:")
        print(f"  Reference: {fp.reference}")
        print(f"  Value: {fp.value}")
        print(f"  Library: {fp.get_library_id()}")
        print(f"  Position: ({fp.position.x}, {fp.position.y})")
        print(f"  Number of pads: {len(fp.pads)}")

    # Example 2: Programmatically create PCB data
    print("\n\nExample 2: Create PCB programmatically\n" + "=" * 50)

    # Create minimal PCB structure
    new_pcb_data = {
        "version": 20241229,
        "generator": "kicad-pcb-api",
        "generator_version": "1.0.0",
        "general": {"thickness": 1.6, "legacy_teardrops": False},
        "paper": "A4",
        "layers": [
            {"number": 0, "canonical_name": "F.Cu", "type": "signal"},
            {"number": 31, "canonical_name": "B.Cu", "type": "signal"},
        ],
        "nets": [
            Net(0, ""),
            Net(1, "GND"),
            Net(2, "VCC"),
        ],
        "footprints": [
            Footprint(
                library="Capacitor_SMD",
                name="C_0603_1608Metric",
                position=Point(120, 60),
                rotation=0,
                layer="F.Cu",
                reference="C1",
                value="100nF",
                uuid="cap-uuid-1",
                properties=[
                    Property(
                        name="Reference",
                        value="C1",
                        position=Point(0, -1.5),
                        layer="F.SilkS",
                        uuid="cap-ref-uuid"
                    ),
                    Property(
                        name="Value",
                        value="100nF",
                        position=Point(0, 1.5),
                        layer="F.Fab",
                        uuid="cap-val-uuid"
                    ),
                ],
            )
        ],
        "vias": [],
        "tracks": [],
        "zones": [],
        "embedded_fonts": False,
    }

    # Convert to S-expression string
    output = parser.dumps(new_pcb_data)
    print("Generated PCB (first 500 chars):")
    print(output[:500] + "...")

    # Example 3: Round-trip test (parse and write)
    print("\n\nExample 3: Round-trip test\n" + "=" * 50)

    # Parse the original
    pcb1 = parser.parse_string(minimal_pcb)

    # Write to string
    pcb_str = parser.dumps(pcb1)

    # Parse again
    pcb2 = parser.parse_string(pcb_str)

    # Compare
    print(f"Original footprints: {len(pcb1['footprints'])}")
    print(f"After round-trip: {len(pcb2['footprints'])}")
    print(f"Match: {len(pcb1['footprints']) == len(pcb2['footprints'])}")

    if pcb1['footprints'] and pcb2['footprints']:
        fp1 = pcb1['footprints'][0]
        fp2 = pcb2['footprints'][0]
        print(f"\nFootprint comparison:")
        print(f"  Reference match: {fp1.reference == fp2.reference}")
        print(f"  Value match: {fp1.value == fp2.value}")
        print(f"  Position match: {fp1.position.x == fp2.position.x and fp1.position.y == fp2.position.y}")
        print(f"  Pad count match: {len(fp1.pads) == len(fp2.pads)}")

    # Example 4: File operations
    print("\n\nExample 4: File operations\n" + "=" * 50)

    with tempfile.NamedTemporaryFile(suffix=".kicad_pcb", delete=False, mode='w') as tmp:
        tmp_path = Path(tmp.name)

    try:
        # Write to file
        parser.write_file(new_pcb_data, tmp_path)
        print(f"Written to: {tmp_path}")
        print(f"File size: {tmp_path.stat().st_size} bytes")

        # Read back
        loaded_pcb = parser.parse_file(tmp_path)
        print(f"Loaded footprints: {len(loaded_pcb['footprints'])}")

        if loaded_pcb['footprints']:
            fp = loaded_pcb['footprints'][0]
            print(f"  First footprint: {fp.reference} ({fp.value})")

    finally:
        # Clean up
        if tmp_path.exists():
            tmp_path.unlink()
            print(f"Cleaned up temporary file")

    print("\n" + "=" * 50)
    print("Demo complete!")


if __name__ == "__main__":
    main()
