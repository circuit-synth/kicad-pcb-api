# kicad_pcb_api - Core Package

Professional KiCAD PCB manipulation library with exact format preservation.

## Overview

This is the main package directory containing all core functionality for programmatic manipulation of KiCAD PCB files (.kicad_pcb). The library provides a modern, Pythonic API while maintaining exact format compatibility with KiCAD's native output.

## Quick Start

```python
import kicad_pcb_api as kpa

# Load or create PCB
pcb = kpa.load_pcb('board.kicad_pcb')  # or kpa.create_pcb()

# Add footprints
resistor = pcb.footprints.add('Resistor_SMD:R_0603_1608Metric', 'R1', (50, 50))
resistor.value = '10k'

# Auto-placement
pcb.placement.hierarchical(component_spacing=5.0)

# Connect pads with tracks
pcb.routing.connect('R1', 1, 'C1', 1, 'Signal')

# Save
pcb.save()
```

## Directory Structure

### Core Modules

- **`core/`** - Core PCB manipulation and data structures
  - `pcb_board.py` - Main PCBBoard class and entry point
  - `pcb_parser.py` - S-expression parser for KiCAD format
  - `pcb_formatter.py` - Format preservation and output generation
  - `types.py` - Core data types (Footprint, Track, Via, etc.)
  - `geometry.py` - Geometric calculations and utilities
  - `config.py` - Configuration system for KiCAD behavior
  - `factory.py` - Element creation factory
  - `validation.py` - Core validation logic
  - `exceptions.py` - Custom exception hierarchy

### Manager System

Located in `managers/`, specialized managers handle distinct responsibilities:

- `base.py` - Base manager class
- `drc.py` - Design rule checking
- `net.py` - Net connectivity management
- `placement.py` - Component placement algorithms
- `routing.py` - Track and via routing
- `validation.py` - Comprehensive validation

### Collection Architecture

Located in `collections/`, enhanced collection classes for efficient management:

- `base.py` - IndexedCollection base class
- `footprints.py` - FootprintCollection with UUID indexing
- `tracks.py` - TrackCollection for trace management
- `vias.py` - ViaCollection for via management
- `zones.py` - ZoneCollection for copper pour areas

### Wrapper Pattern

Located in `wrappers/`, enhanced element wrappers with validation:

- `base.py` - Base wrapper with property tracking
- `footprint.py` - FootprintWrapper with convenience methods
- `track.py` - TrackWrapper for trace manipulation
- `via.py` - ViaWrapper for via management
- `zone.py` - ZoneWrapper for zone operations

### Specialized Modules

- **`placement/`** - Component placement algorithms
  - `hierarchical_placement.py` - Hierarchical grouping algorithm
  - `spiral_placement.py` - Spiral outward placement
  - `bbox.py` - Bounding box calculations
  - `courtyard_collision.py` - Collision detection

- **`routing/`** - Routing integration
  - `dsn_exporter.py` - Export to Specctra DSN format
  - `freerouting_runner.py` - Freerouting integration
  - `freerouting_docker.py` - Docker-based routing
  - `ses_importer.py` - Import routed boards

- **`footprints/`** - Footprint library management
  - `footprint_library.py` - Footprint caching and lookup

- **`utils/`** - Validation and utility functions
  - `validation.py` - PCB validation system
  - `kicad_cli.py` - KiCAD CLI integration

- **`interfaces/`** - Type definitions and protocols
  - Protocol definitions for extensibility

## Key Files

| File | Purpose |
|------|---------|
| `core/pcb_board.py` | Main API, manager coordination |
| `core/pcb_parser.py` | S-expression parsing (CRITICAL) |
| `core/pcb_formatter.py` | Format preservation logic |
| `core/types.py` | Type definitions |
| `collections/base.py` | Indexed collection pattern |
| `managers/base.py` | Manager architecture |
| `wrappers/base.py` | Wrapper pattern base |

## Architecture Patterns

### Manager-Based Design
The PCBBoard class coordinates specialized managers, each with a single responsibility:
- Separation of concerns
- Easier testing and maintenance
- Clear dependencies
- Consistent API

### Collection Pattern
Enhanced collections with:
- UUID-based O(1) lookups
- Lazy index rebuilding
- Modification tracking
- Consistent iteration interface

### Wrapper Pattern
Element wrappers provide:
- Validation on property setters
- Parent collection tracking
- Convenient methods
- Type-safe operations

### Exact Format Preservation
Every S-expression maintains original formatting to ensure output matches KiCAD byte-perfectly:
- Parser preserves structure
- Formatter reconstructs exactly
- Critical for version control

## Module Organization

### Load/Create PCB
```python
import kicad_pcb_api as kpa

# Load existing
pcb = kpa.load_pcb('board.kicad_pcb')

# Create new
pcb = kpa.create_pcb()
```

### Use Collections
```python
# Add footprint
fp = pcb.footprints.add('Device:R_0603', 'R1', (100, 100))

# Find footprints
resistors = pcb.footprints.filter(reference='R*')

# Get by UUID
fp = pcb.footprints.get(uuid)
```

### Use Managers
```python
# Auto-placement
pcb.placement.hierarchical(spacing=5.0)

# Net management
nets = pcb.net.get_all_nets()
pcb.net.rename('Net-1', 'VCC')

# DRC checks
violations = pcb.drc.check_clearances()

# Validation
results = pcb.validation.validate_all()
```

### Use Wrappers
```python
# Get wrapped footprint
fp_wrapper = pcb.footprints.get_wrapper('R1')

# Use convenient methods
fp_wrapper.move_by(10, 10)
fp_wrapper.rotate(90)
pads = fp_wrapper.get_pads()
```

## API Access Patterns

### Direct Access (Simple)
```python
pcb.footprints  # Collection
pcb.tracks      # Collection
pcb.vias        # Collection
```

### Manager Access (Complex Operations)
```python
pcb.placement   # PlacementManager
pcb.routing     # RoutingManager
pcb.drc         # DRCManager
pcb.net         # NetManager
pcb.validation  # ValidationManager
```

### Configuration
```python
import kicad_pcb_api as kpa

# Global config
kpa.config.track_width = 0.25
kpa.config.clearance = 0.2

# Per-board config
pcb.config.via_diameter = 0.8
```

## Code Quality

- **Type Checking**: Strict mypy enabled
- **Formatting**: Black/isort compliance
- **Testing**: Comprehensive test suite
- **Documentation**: Module and class docstrings throughout

## Version Info

- **Current Version**: 0.1.1
- **Package Version**: 0.1.1 (in __init__.py)
- **Project Version**: 0.1.1 (in pyproject.toml)

## Related Documentation

- See `core/README.md` for core module details
- See `collections/README.md` for collection pattern details
- See `managers/README.md` for manager architecture
- See `wrappers/README.md` for wrapper pattern details
- See `placement/README.md` for placement algorithms
- See `routing/README.md` for routing integration
- See root `CLAUDE.md` for development guide
- See root `README.md` for user-facing documentation
