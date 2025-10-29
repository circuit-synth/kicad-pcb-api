# Routing Module

PCB routing integration with Freerouting and manual routing utilities.

## Overview

This module provides tools for PCB routing, including integration with the Freerouting auto-router, DSN/SES format conversion, and manual routing utilities. Supports both JAR-based and Docker-based Freerouting execution.

## Features

### Complete Workflow
The routing module enables end-to-end automated routing:

1. **Export PCB to DSN** - Specctra DSN format for router
2. **Run Freerouting** - Auto-router (JAR or Docker)
3. **Import SES** - Bring routed tracks back into PCB

**Recent Updates** (as per existing README):
- Complete Freerouting workflow fixed
- DSN placement format corrected
- Via padstack definitions added
- SES parser improvements
- Multi-line wire parsing fixed

## Quick Start

### Basic Auto-Routing
```python
from kicad_pcb_api.routing import export_pcb_to_dsn, route_pcb, import_ses_to_pcb

# Step 1: Export to DSN
export_pcb_to_dsn("board.kicad_pcb", "board.dsn")

# Step 2: Auto-route
success, result = route_pcb("board.dsn", "board.ses")

# Step 3: Import back
if success:
    import_ses_to_pcb("board.kicad_pcb", "board.ses", "board_routed.kicad_pcb")
```

### Docker-Based Routing (No Java Required)
```python
from kicad_pcb_api.routing import route_pcb_docker

# Route using Docker
success, result = route_pcb_docker("board.dsn", "board.ses")
```

## Module Components

### DSN Exporter (`dsn_exporter.py`)
Export PCB to Specctra DSN format.

**Features**:
- Multi-layer board support
- Configurable design rules
- Automatic net extraction
- Board outline detection
- Via padstack generation

**Example**:
```python
from kicad_pcb_api.routing import DSNExporter

# Create exporter with custom rules
exporter = DSNExporter(
    pcb_file="board.kicad_pcb",
    track_width=0.2,      # 0.2mm tracks
    clearance=0.15,       # 0.15mm clearance
    via_diameter=0.6,     # 0.6mm via diameter
    via_drill=0.3         # 0.3mm via drill
)

# Export to DSN
exporter.export("board.dsn")
```

### Freerouting Runner (`freerouting_runner.py`)
JAR-based Freerouting execution with progress tracking.

**Features**:
- Subprocess management
- Progress tracking
- Timeout handling
- Configurable effort levels
- Memory allocation

**Example**:
```python
from kicad_pcb_api.routing import FreeroutingRunner, FreeroutingConfig, RoutingEffort

# Configure routing
config = FreeroutingConfig(
    effort=RoutingEffort.HIGH,
    optimization_passes=20,
    via_costs=100.0,
    timeout_seconds=3600,
    memory_mb=2048
)

# Create runner and route
runner = FreeroutingRunner(config)
success, result = runner.route("board.dsn", "board.ses")

# Track progress
progress, status = runner.get_progress()
print(f"Progress: {progress}% - {status}")
```

### Docker Runner (`freerouting_docker.py`)
Docker-based Freerouting (no Java installation required).

**Features**:
- No Java installation needed
- Automatic image pull
- Same API as JAR runner
- Cross-platform

**Example**:
```python
from kicad_pcb_api.routing import FreeroutingDockerRunner, FreeroutingConfig

# Configure and run
config = FreeroutingConfig(
    effort=RoutingEffort.HIGH,
    optimization_passes=20
)

runner = FreeroutingDockerRunner(config)
success, result = runner.route("board.dsn", "board.ses")
```

**Docker Image**: Uses `ghcr.io/freerouting/freerouting:nightly`

### SES Importer (`ses_importer.py`)
Import routed boards from Freerouting SES files.

**Features**:
- Automatic track placement
- Via placement
- Layer mapping
- Net preservation
- Protected routing support

**Example**:
```python
from kicad_pcb_api.routing import SESImporter

# Create importer
importer = SESImporter(
    pcb_file="board.kicad_pcb",
    ses_file="board.ses"
)

# Import routing
importer.import_routing("board_routed.kicad_pcb")
```

### Installation Helper (`install_freerouting.py`)
Helper script for Freerouting installation.

**Features**:
- Download Freerouting JAR
- Verify Java installation
- Configure paths
- Test installation

**Example**:
```python
from kicad_pcb_api.routing import install_freerouting

# Install Freerouting
install_freerouting(
    jar_dir="~/freerouting/",
    version="2.1.0"
)
```

## Usage Through Manager

The RoutingManager provides convenient access:

```python
# Auto-route entire net
pcb.routing.route_net('VCC')

# Connect two pads
pcb.routing.connect('R1', 1, 'C1', 1, 'Signal')

# Run Freerouting
pcb.routing.freeroute(
    effort='high',
    optimization_passes=20
)

# Optimize existing routing
pcb.routing.optimize()
```

## Configuration

### Routing Effort Levels
```python
from kicad_pcb_api.routing import RoutingEffort

# Fast - quick routing, may not complete
config.effort = RoutingEffort.FAST

# Medium - balanced (default)
config.effort = RoutingEffort.MEDIUM

# High - thorough routing, longer time
config.effort = RoutingEffort.HIGH
```

### Design Rules
```python
# Configure in DSN exporter
exporter = DSNExporter(
    pcb_file="board.kicad_pcb",
    track_width=0.25,      # Default track width
    clearance=0.2,         # Minimum clearance
    via_diameter=0.8,      # Via outer diameter
    via_drill=0.4,         # Via drill size
    allowed_layers=[0, 31] # F.Cu and B.Cu only
)
```

### Progress Tracking
```python
def show_progress(progress, status):
    print(f"Progress: {progress:.1f}% - {status}")

success, result = route_pcb(
    "board.dsn",
    "board.ses",
    progress_callback=show_progress
)
```

## Workflow Integration

### Complete Automated Workflow
```python
import kicad_pcb_api as kpa
from kicad_pcb_api.routing import export_pcb_to_dsn, route_pcb_docker, import_ses_to_pcb

# 1. Load or create PCB
pcb = kpa.load_pcb('board.kicad_pcb')

# 2. Place components
pcb.placement.hierarchical(spacing=5.0, groups=groups)

# 3. Export to DSN
export_pcb_to_dsn('board.kicad_pcb', 'board.dsn')

# 4. Auto-route with Docker
success, result = route_pcb_docker('board.dsn', 'board.ses')

# 5. Import routing
if success:
    import_ses_to_pcb('board.kicad_pcb', 'board.ses', 'board_routed.kicad_pcb')
    print("Routing complete!")
else:
    print(f"Routing failed: {result}")
```

### Manual + Auto Hybrid
```python
# Manual routing for critical nets
pcb.routing.connect('U1', 1, 'C1', 1, 'VCC')
pcb.routing.connect('U1', 2, 'GND', 1, 'GND')

# Lock manual routing
pcb.routing.lock_net('VCC')
pcb.routing.lock_net('GND')

# Auto-route remaining nets
export_pcb_to_dsn('board.kicad_pcb', 'board.dsn', protect_locked=True)
route_pcb_docker('board.dsn', 'board.ses')
import_ses_to_pcb('board.kicad_pcb', 'board.ses', 'board_routed.kicad_pcb')
```

## Troubleshooting

### Freerouting Not Found
**Docker**:
- Ensure Docker is installed and running
- Check Docker permissions
- Verify image: `docker pull ghcr.io/freerouting/freerouting:nightly`

**JAR**:
- Check Java 21+ installed: `java -version`
- Verify JAR location
- Set path in config

### Routing Failures
- Simplify design rules (wider tracks, larger clearances)
- Increase timeout
- Try different effort levels
- Check for unroutable nets
- Verify board outline exists

### DSN Export Issues
- Ensure valid board outline
- Check net names (no special characters)
- Verify all footprints have pads
- Check layer stack

## Performance

| Operation | Time | Notes |
|-----------|------|-------|
| DSN Export | ~1s | For typical board |
| Freerouting | 10s-10min | Depends on complexity |
| SES Import | ~2s | For typical routing |

## Testing

Tests located in `../../tests/`:
- `test_routing.py` - Routing functionality
- `test_dsn_exporter.py` - DSN export tests
- `test_freerouting.py` - Freerouting tests
- `test_ses_importer.py` - SES import tests
- Integration tests with real PCBs

## Related Modules

- `managers/routing.py` - RoutingManager
- `collections/tracks.py` - TrackCollection
- `collections/vias.py` - ViaCollection
- `core/geometry.py` - Geometric utilities

## Future Improvements

- [ ] KiCad native router integration
- [ ] Custom routing algorithms
- [ ] Interactive routing visualization
- [ ] Length matching support
- [ ] Differential pair routing
- [ ] Bus routing
- [ ] Teardrops
