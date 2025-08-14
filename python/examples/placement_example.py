"""
Advanced placement example for kicad-pcb-api.

Shows how to use different placement algorithms for component optimization.
"""

import kicad_pcb_api as kpa

def main():
    # Create a new PCB
    pcb = kpa.create_pcb()
    
    # Set board outline (80x50mm board)
    pcb.set_board_outline_rect(0, 0, 80, 50)
    
    # Add multiple components
    components = [
        ("U1", "Package_QFP:LQFP-64_10x10mm_P0.5mm", 40, 25, "STM32"),
        ("C1", "Capacitor_SMD:C_0603_1608Metric", 35, 20, "100nF"),
        ("C2", "Capacitor_SMD:C_0603_1608Metric", 45, 20, "100nF"),
        ("R1", "Resistor_SMD:R_0603_1608Metric", 35, 30, "10k"),
        ("R2", "Resistor_SMD:R_0603_1608Metric", 45, 30, "10k"),
        ("L1", "Inductor_SMD:L_0603_1608Metric", 40, 35, "10uH"),
    ]
    
    for ref, footprint, x, y, value in components:
        pcb.add_footprint(ref, footprint, x, y, value=value)
    
    # Create some connections
    pcb.connect_pads("U1", "25", "C1", "1", "VDD")  # Power connections
    pcb.connect_pads("U1", "26", "C2", "1", "VDD")
    pcb.connect_pads("C1", "2", "C2", "2", "GND")   # Ground connections
    
    print("Before placement:")
    for ref, value, x, y in pcb.list_footprints():
        print(f"  {ref}: ({x:.1f}, {y:.1f})")
    
    # Try different placement algorithms
    algorithms = ["hierarchical", "spiral"]
    
    for algo in algorithms:
        print(f"\nUsing {algo} placement algorithm...")
        try:
            pcb.auto_place_components(
                algorithm=algo,
                component_spacing=3.0,
                board_width=80,
                board_height=50
            )
            
            print(f"After {algo} placement:")
            for ref, value, x, y in pcb.list_footprints():
                print(f"  {ref}: ({x:.1f}, {y:.1f})")
                
            # Save each result
            pcb.save(f"placement_{algo}_example.kicad_pcb")
            print(f"Saved placement_{algo}_example.kicad_pcb")
            
        except Exception as e:
            print(f"Error with {algo} placement: {e}")

if __name__ == "__main__":
    main()