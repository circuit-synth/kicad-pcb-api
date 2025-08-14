"""
Basic usage example for kicad-pcb-api.

Shows how to create a simple PCB with components and save it.
"""

import kicad_pcb_api as kpa

def main():
    # Create a new PCB
    pcb = kpa.create_pcb()
    
    # Set board outline (50x30mm board)
    pcb.set_board_outline_rect(0, 0, 50, 30)
    
    # Add some components
    resistor = pcb.add_footprint(
        reference="R1",
        footprint_lib="Resistor_SMD:R_0603_1608Metric", 
        x=20, y=15,
        value="10k"
    )
    
    capacitor = pcb.add_footprint(
        reference="C1",
        footprint_lib="Capacitor_SMD:C_0603_1608Metric",
        x=30, y=15, 
        value="100nF"
    )
    
    # Connect them
    pcb.connect_pads("R1", "1", "C1", "1", "Signal")
    
    # Get board info
    info = pcb.get_board_info()
    print(f"Board has {info['footprint_count']} footprints and {info['net_count']} nets")
    
    # List footprints
    for ref, value, x, y in pcb.list_footprints():
        print(f"{ref}: {value} at ({x:.1f}, {y:.1f})")
    
    # Save the PCB
    pcb.save("example_board.kicad_pcb")
    print("Saved example_board.kicad_pcb")

if __name__ == "__main__":
    main()