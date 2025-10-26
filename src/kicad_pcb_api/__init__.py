"""
KiCAD PCB API - Professional KiCAD PCB Manipulation Library

A modern, high-performance Python library for programmatic manipulation of 
KiCAD PCB files (.kicad_pcb) with exact format preservation, advanced placement 
algorithms, and AI agent integration.

Example usage:
    import kicad_pcb_api as kpa
    
    # Load PCB
    pcb = kpa.load_pcb('board.kicad_pcb')
    
    # Add footprints
    resistor = pcb.footprints.add('Resistor_SMD:R_0603_1608Metric', 'R1', (50, 50))
    resistor.value = '10k'
    
    # Auto-place components
    pcb.auto_place_components('hierarchical')
    
    # Save
    pcb.save()
"""

from .core.pcb_board import PCBBoard
from .core.pcb_parser import PCBParser
from .core.types import (
    Arc,
    Footprint,
    Layer,
    Line,
    Net,
    Pad,
    Point,
    Property,
    Rectangle,
    Text,
    Track,
    Via,
    Zone,
)

__version__ = "0.0.1"
__author__ = "Circuit-Synth Team"
__email__ = "contact@circuit-synth.com"

# Main API
def load_pcb(filepath):
    """Load a PCB from file."""
    return PCBBoard(filepath)

def create_pcb():
    """Create a new empty PCB."""
    return PCBBoard()

# Export key classes
__all__ = [
    "PCBBoard",
    "PCBParser", 
    "load_pcb",
    "create_pcb",
    # Types
    "Arc",
    "Footprint", 
    "Layer",
    "Line",
    "Net",
    "Pad",
    "Point",
    "Property",
    "Rectangle",
    "Text",
    "Track",
    "Via", 
    "Zone",
]