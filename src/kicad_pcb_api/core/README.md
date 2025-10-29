# Core Module

Core PCB manipulation and data structures.

## Overview

This module contains the fundamental classes for KiCAD PCB manipulation. It provides the main PCBBoard class, S-expression parser/formatter, type definitions, and core utilities.

## Main Classes

### PCBBoard (`pcb_board.py`)
- **Purpose**: Main API entry point and manager coordinator
- **Key Methods**:
  - `load(filepath)` - Load existing PCB file
  - `save(filepath)` - Save with exact format preservation
  - `validate()` - Run validation checks
  - Property accessors: `.footprints`, `.tracks`, `.vias`, etc.
- **Managers**: DRC, Net, Placement, Routing, Validation
- **Collections**: Footprints, Tracks, Vias, Zones

**Example**:
```python
import kicad_pcb_api as kpa

# Load PCB
pcb = kpa.load_pcb('board.kicad_pcb')

# Access collections
print(f"Footprints: {len(pcb.footprints)}")
print(f"Tracks: {len(pcb.tracks)}")

# Access managers
pcb.placement.hierarchical(spacing=5.0)
pcb.drc.check_clearances()

# Save
pcb.save()
```

### PCBParser (`pcb_parser.py`)
- **Purpose**: S-expression parser for KiCAD format
- **Responsibility**: Convert KiCAD file text to Python objects
- **Critical for**: Format preservation and parsing accuracy
- **Key Classes**:
  - `PCBParser` - Main parser class
  - `ParseError` - Custom exception type

**Example**:
```python
from kicad_pcb_api.core import PCBParser

parser = PCBParser()
pcb_data = parser.parse_file('board.kicad_pcb')

# Access parsed data
print(f"Version: {pcb_data['version']}")
print(f"Layers: {len(pcb_data['layers'])}")
```

### PCBFormatter (`pcb_formatter.py`)
- **Purpose**: Convert Python objects back to KiCAD S-expression format
- **Key Methods**:
  - `format_pcb(pcb_data)` - Generate output text
  - `format_footprint(fp)` - Format individual footprints
  - `format_track(track)` - Format tracks
  - `format_via(via)` - Format vias

**Example**:
```python
from kicad_pcb_api.core import PCBFormatter

formatter = PCBFormatter()
output = formatter.format_pcb(pcb_data)

# Write to file
with open('output.kicad_pcb', 'w') as f:
    f.write(output)
```

### Types (`types.py`)
- **Purpose**: Core data type definitions
- **Key Classes**:
  - `Point` - 2D coordinate
  - `Footprint` - PCB component
  - `Track` - Copper trace
  - `Via` - Through-hole connection
  - `Zone` - Copper pour area
  - `Net` - Electrical net
  - `Pad` - Component pad
  - `Layer` - PCB layer
  - `Property` - Element property
- **Pattern**: Frozen dataclasses for immutability

**Example**:
```python
from kicad_pcb_api.core.types import Point, Footprint, Track

# Create point
pos = Point(x=100, y=100)

# Create track
track = Track(
    start=Point(100, 100),
    end=Point(150, 100),
    width=0.25,
    layer='F.Cu',
    net='Signal'
)
```

## Supporting Classes

### Configuration (`config.py`)
- **Purpose**: Global configuration for PCB behavior
- **Instances**: `config` (global singleton)
- **Configurable**: Track width, clearances, via specs, etc.

**Example**:
```python
from kicad_pcb_api import config

# Set defaults
config.track_width = 0.25  # mm
config.clearance = 0.2     # mm
config.via_diameter = 0.8  # mm
config.via_drill = 0.4     # mm
```

### Factory (`factory.py`)
- **Purpose**: Element creation with defaults and validation
- **Key Methods**:
  - `create_footprint()` - Create footprint with defaults
  - `create_track()` - Create track with validation
  - `create_via()` - Create via with validation
  - `create_zone()` - Create zone with defaults

**Example**:
```python
from kicad_pcb_api.core import PCBElementFactory

factory = PCBElementFactory()

# Create footprint with defaults
fp = factory.create_footprint(
    reference='R1',
    library='Resistor_SMD:R_0603_1608Metric',
    position=(100, 100)
)

# Create track with validation
track = factory.create_track(
    start=(100, 100),
    end=(150, 100),
    width=0.25,
    layer='F.Cu'
)
```

### Geometry (`geometry.py`)
- **Purpose**: Geometric calculations and utilities
- **Key Functions**:
  - `distance(p1, p2)` - Distance between points
  - `rotate_point(point, angle, origin)` - Rotate point
  - `BoundingBox` - Axis-aligned bounding box

**Example**:
```python
from kicad_pcb_api.core.geometry import distance, rotate_point, BoundingBox

# Calculate distance
d = distance((0, 0), (100, 100))  # Returns 141.42...

# Rotate point
rotated = rotate_point((100, 0), 90, (0, 0))  # Returns (0, 100)

# Create bounding box
bbox = BoundingBox(x=0, y=0, width=100, height=100)
print(f"Area: {bbox.area}")  # Returns 10000
```

### Validation (`validation.py`)
- **Purpose**: Core validation logic
- **Key Methods**:
  - `validate_reference(ref)` - Check reference validity
  - `validate_net_name(net)` - Check net name validity
  - `validate_layer(layer)` - Check layer validity

**Example**:
```python
from kicad_pcb_api.core.validation import validate_reference, validate_layer

# Validate reference
is_valid = validate_reference('R1')  # True
is_valid = validate_reference('R-1')  # False (invalid character)

# Validate layer
is_valid = validate_layer('F.Cu')  # True
is_valid = validate_layer('Invalid')  # False
```

### Exceptions (`exceptions.py`)
- **Purpose**: Custom exception hierarchy
- **Key Exceptions**:
  - `KiCadPCBError` - Base exception
  - `ValidationError` - Validation failures
  - `ReferenceError` - Invalid references
  - `LayerError` - Layer-related errors
  - `NetError` - Net-related errors
  - `GeometryError` - Geometric errors

**Example**:
```python
from kicad_pcb_api.core.exceptions import ValidationError, ReferenceError

try:
    pcb.footprints.add('Invalid:Footprint', 'R-1', (0, 0))
except ReferenceError as e:
    print(f"Invalid reference: {e}")
except ValidationError as e:
    print(f"Validation error: {e}")
```

## Architecture Patterns

### Format Preservation Pipeline
1. **Parser** reads .kicad_pcb file
2. Preserves all original formatting
3. Python code modifies structure
4. **Formatter** writes back exactly as KiCAD would

```
.kicad_pcb file
     ↓
PCBParser (parse S-expressions)
     ↓
Python objects (modify)
     ↓
PCBFormatter (generate S-expressions)
     ↓
.kicad_pcb file (byte-perfect)
```

### Manager Coordination
```
PCBBoard (main API)
├── Collections (data storage)
│   ├── FootprintCollection
│   ├── TrackCollection
│   ├── ViaCollection
│   └── ZoneCollection
└── Managers (operations)
    ├── DRCManager
    ├── NetManager
    ├── PlacementManager
    ├── RoutingManager
    └── ValidationManager
```

### Type System
Strong typing throughout with strict mypy configuration:
- Frozen dataclasses for immutability
- Comprehensive type hints
- Protocol-based interfaces
- Type-safe operations

## Code Quality

- **Type System**: Strict mypy enabled
- **Format**: Black/isort compliance
- **Documentation**: Module/class docstrings throughout
- **Testing**: Comprehensive test coverage

## Testing

Located in `../../tests/`, includes:
- Format preservation tests
- Round-trip validation
- Element manipulation tests
- Geometry tests
- Integration tests

## Dependencies

- `sexpdata` - S-expression parsing
- `typing-extensions` - Type hint support

## Related Documentation

- See `../collections/README.md` for collection details
- See `../managers/README.md` for manager details
- See `../wrappers/README.md` for wrapper details
- See root `CLAUDE.md` for development guidelines
