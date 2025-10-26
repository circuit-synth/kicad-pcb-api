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

# New foundation components
from .core.config import config, PCBConfig
from .core.factory import PCBElementFactory
from .core.geometry import BoundingBox, distance, rotate_point
from .core.exceptions import (
    KiCadPCBError,
    ValidationError,
    ReferenceError,
    LayerError,
    NetError,
    GeometryError,
)

# Managers
from .managers import (
    DRCManager,
    NetManager,
    PlacementManager,
    RoutingManager,
    ValidationManager,
)

# Wrappers
from .wrappers import (
    FootprintWrapper,
    TrackWrapper,
    ViaWrapper,
)

# Collections
from .collections import (
    FootprintCollection,
    TrackCollection,
    ViaCollection,
)

# Protocols
from .interfaces import PCBElement, Placeable, Routable

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
    # Main API
    "PCBBoard",
    "PCBParser",
    "load_pcb",
    "create_pcb",

    # Configuration
    "config",
    "PCBConfig",

    # Factory
    "PCBElementFactory",

    # Geometry
    "BoundingBox",
    "distance",
    "rotate_point",

    # Exceptions
    "KiCadPCBError",
    "ValidationError",
    "ReferenceError",
    "LayerError",
    "NetError",
    "GeometryError",

    # Managers
    "DRCManager",
    "NetManager",
    "PlacementManager",
    "RoutingManager",
    "ValidationManager",

    # Wrappers
    "FootprintWrapper",
    "TrackWrapper",
    "ViaWrapper",

    # Collections
    "FootprintCollection",
    "TrackCollection",
    "ViaCollection",

    # Protocols
    "PCBElement",
    "Placeable",
    "Routable",

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