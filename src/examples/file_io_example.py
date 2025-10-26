"""
Example demonstrating file I/O operations with the PCB API.

This example shows how to:
- Create a new PCB and save it
- Load an existing PCB file
- Modify a PCB and save changes
- Track modifications
- Handle file operations safely
"""

from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from kicad_pcb_api.core.pcb_board import PCBBoard


def example_create_and_save():
    """Example: Create a new PCB and save it."""
    print("=== Example 1: Create and Save ===\n")

    # Create a new PCB
    pcb = PCBBoard()
    print(f"Created new PCB. Modified: {pcb.is_modified}")

    # Add some components
    pcb.add_footprint("R1", "Resistor_SMD:R_0603_1608Metric", 50, 50, value="10k")
    pcb.add_footprint("R2", "Resistor_SMD:R_0603_1608Metric", 60, 50, value="20k")
    print(f"Added 2 resistors. Modified: {pcb.is_modified}")

    # Save to file
    output_file = Path("/tmp/example_pcb.kicad_pcb")
    pcb.save(output_file)
    print(f"Saved to {output_file}. Modified: {pcb.is_modified}")
    print(f"Filepath: {pcb.filepath}\n")


def example_load_and_modify():
    """Example: Load an existing PCB and modify it."""
    print("=== Example 2: Load and Modify ===\n")

    # First, create a file to load
    pcb = PCBBoard()
    pcb.add_footprint("R1", "Resistor_SMD:R_0603_1608Metric", 50, 50, value="10k")
    input_file = Path("/tmp/input_pcb.kicad_pcb")
    pcb.save(input_file)
    print(f"Created test file: {input_file}")

    # Load the file
    pcb2 = PCBBoard()
    pcb2.load(input_file)
    print(f"Loaded PCB from {input_file}")
    print(f"  Footprints: {pcb2.get_footprint_count()}")
    print(f"  Modified: {pcb2.is_modified}")

    # Modify it
    pcb2.add_footprint("R2", "Resistor_SMD:R_0603_1608Metric", 60, 50, value="20k")
    print(f"Added component. Modified: {pcb2.is_modified}")

    # Save changes (uses original filepath)
    pcb2.save()
    print(f"Saved changes. Modified: {pcb2.is_modified}\n")


def example_load_via_constructor():
    """Example: Load a PCB file via constructor."""
    print("=== Example 3: Load via Constructor ===\n")

    # First, create a file
    pcb = PCBBoard()
    pcb.add_footprint("R1", "Resistor_SMD:R_0603_1608Metric", 50, 50, value="10k")
    input_file = Path("/tmp/constructor_test.kicad_pcb")
    pcb.save(input_file)

    # Load via constructor
    pcb2 = PCBBoard(input_file)
    print(f"Loaded PCB via constructor")
    print(f"  Footprints: {pcb2.get_footprint_count()}")
    print(f"  Filepath: {pcb2.filepath}")
    print(f"  Modified: {pcb2.is_modified}\n")


def example_save_to_different_file():
    """Example: Save to a different file."""
    print("=== Example 4: Save to Different File ===\n")

    # Create and save
    pcb = PCBBoard()
    pcb.add_footprint("R1", "Resistor_SMD:R_0603_1608Metric", 50, 50, value="10k")
    file1 = Path("/tmp/original.kicad_pcb")
    pcb.save(file1)
    print(f"Saved to {file1}")

    # Save to different file
    file2 = Path("/tmp/copy.kicad_pcb")
    pcb.save(file2)
    print(f"Saved to {file2}")
    print(f"Current filepath: {pcb.filepath}\n")


def example_modification_tracking():
    """Example: Track modifications."""
    print("=== Example 5: Modification Tracking ===\n")

    # Create PCB
    pcb = PCBBoard()
    print(f"New PCB - Modified: {pcb.is_modified}")

    # Add component
    pcb.add_footprint("R1", "Resistor_SMD:R_0603_1608Metric", 50, 50, value="10k")
    print(f"Added component - Modified: {pcb.is_modified}")

    # Save
    pcb.save(Path("/tmp/tracking_test.kicad_pcb"))
    print(f"After save - Modified: {pcb.is_modified}")

    # Modify again
    pcb.add_footprint("R2", "Resistor_SMD:R_0603_1608Metric", 60, 50, value="20k")
    print(f"Added another component - Modified: {pcb.is_modified}")

    # Manually reset (usually not needed)
    pcb.reset_modified()
    print(f"After reset_modified() - Modified: {pcb.is_modified}\n")


def example_error_handling():
    """Example: Handle file errors."""
    print("=== Example 6: Error Handling ===\n")

    pcb = PCBBoard()

    # Try to load non-existent file
    try:
        pcb.load("nonexistent_file.kicad_pcb")
    except FileNotFoundError as e:
        print(f"Caught expected error: {e}")

    # Try to load file with wrong extension
    try:
        pcb.load("test_file.txt")
    except ValueError as e:
        print(f"Caught expected error: {e}")

    # Try to save without filepath
    try:
        pcb2 = PCBBoard()
        pcb2.save()
    except ValueError as e:
        print(f"Caught expected error: {e}")

    # Try to save with wrong extension
    try:
        pcb2 = PCBBoard()
        pcb2.save("output.txt")
    except ValueError as e:
        print(f"Caught expected error: {e}\n")


def example_round_trip():
    """Example: Round-trip file preservation."""
    print("=== Example 7: Round-trip Preservation ===\n")

    # Create original PCB
    pcb1 = PCBBoard()
    pcb1.add_footprint("R1", "Resistor_SMD:R_0603_1608Metric", 50, 50, value="10k")
    pcb1.add_footprint("R2", "Resistor_SMD:R_0603_1608Metric", 60, 50, value="20k")

    # Save
    file1 = Path("/tmp/roundtrip1.kicad_pcb")
    pcb1.save(file1)
    print(f"Created PCB with {pcb1.get_footprint_count()} footprints")

    # Load and save again
    pcb2 = PCBBoard()
    pcb2.load(file1)
    file2 = Path("/tmp/roundtrip2.kicad_pcb")
    pcb2.save(file2)
    print(f"Loaded and saved to new file")

    # Load the second file and compare
    pcb3 = PCBBoard()
    pcb3.load(file2)
    print(f"Reloaded PCB - Footprints: {pcb3.get_footprint_count()}")

    # Verify footprints
    for ref in ["R1", "R2"]:
        fp = pcb3.get_footprint(ref)
        if fp:
            print(f"  {ref}: {fp.value} at ({fp.position.x}, {fp.position.y})")
    print()


def main():
    """Run all examples."""
    print("PCB File I/O Examples")
    print("=" * 50)
    print()

    example_create_and_save()
    example_load_and_modify()
    example_load_via_constructor()
    example_save_to_different_file()
    example_modification_tracking()
    example_error_handling()
    example_round_trip()

    print("=" * 50)
    print("All examples completed successfully!")


if __name__ == "__main__":
    main()
