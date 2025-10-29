# Managers Module

Manager pattern for complex PCB operations.

## Overview

This module implements the manager pattern to encapsulate complex operations and keep PCBBoard focused on coordination. Each manager handles a specific domain of PCB manipulation with well-defined responsibilities.

## Manager Architecture

Managers follow a consistent pattern:
- Extend `BaseManager`
- Reference parent `PCBBoard` instance
- Provide domain-specific operations
- Coordinate with collections and other managers

## Base Manager

### BaseManager (`base.py`)
Base class for all managers with board reference:

```python
from kicad_pcb_api.managers import BaseManager

class CustomManager(BaseManager):
    def custom_operation(self):
        # Access board
        footprints = self.board.footprints
        # Perform operation
        ...
```

## Available Managers

### DRCManager (`drc.py`)
Design Rule Checking manager.

**Purpose**: Validate design rules and detect violations

**Key Methods**:
- `check_clearances()` - Check minimum clearances
- `check_track_widths()` - Validate track widths
- `check_via_sizes()` - Validate via dimensions
- `check_courtyard_collisions()` - Detect footprint overlaps
- `get_violations()` - Get all DRC violations

**Example**:
```python
# Run clearance checks
violations = pcb.drc.check_clearances(min_clearance=0.15)

for v in violations:
    print(f"Clearance violation: {v.description}")
    print(f"  Location: {v.location}")
    print(f"  Distance: {v.distance}mm")

# Check track widths
track_violations = pcb.drc.check_track_widths(min_width=0.15)

# Get all violations
all_violations = pcb.drc.get_violations()
print(f"Total violations: {len(all_violations)}")
```

### NetManager (`net.py`)
Net connectivity management.

**Purpose**: Manage electrical nets and connectivity

**Key Methods**:
- `get_all_nets()` - Get list of all nets
- `get_net_elements(net)` - Get all elements in a net
- `rename_net(old, new)` - Rename a net
- `merge_nets(nets, new_name)` - Merge multiple nets
- `get_unconnected_pads()` - Find unconnected pads
- `trace_connectivity(start_pad)` - Trace connections from pad

**Example**:
```python
# Get all nets
nets = pcb.net.get_all_nets()
print(f"Nets: {', '.join(nets)}")

# Get net elements
vcc_elements = pcb.net.get_net_elements('VCC')
print(f"VCC tracks: {len(vcc_elements['tracks'])}")
print(f"VCC vias: {len(vcc_elements['vias'])}")

# Rename net
pcb.net.rename_net('Net-1', 'VCC')

# Find unconnected pads
unconnected = pcb.net.get_unconnected_pads()
for pad in unconnected:
    print(f"Unconnected: {pad.reference}.{pad.number}")
```

### PlacementManager (`placement.py`)
Component placement algorithms.

**Purpose**: Automatic and guided component placement

**Key Methods**:
- `hierarchical(spacing, groups)` - Hierarchical placement
- `spiral(center, spacing)` - Spiral outward placement
- `grid(cols, spacing)` - Grid-based placement
- `place_group(components, region)` - Place component group
- `optimize_placement()` - Optimize existing placement

**Example**:
```python
# Hierarchical placement with groups
pcb.placement.hierarchical(
    spacing=5.0,
    groups={
        'power': ['U1', 'C1', 'C2'],
        'signal': ['R1', 'R2', 'R3']
    }
)

# Spiral placement from center
pcb.placement.spiral(
    center=(100, 100),
    spacing=10.0
)

# Grid placement
pcb.placement.grid(
    cols=4,
    spacing=15.0
)

# Place specific group in region
pcb.placement.place_group(
    components=['R1', 'R2', 'R3'],
    region=(0, 0, 50, 50)
)
```

### RoutingManager (`routing.py`)
Track and via routing operations.

**Purpose**: Create and manage PCB routing

**Key Methods**:
- `connect(ref1, pad1, ref2, pad2, net)` - Connect two pads
- `route_net(net)` - Auto-route entire net
- `add_track(start, end, width, layer, net)` - Add single track
- `add_via(position, size, drill, net)` - Add via
- `optimize_routing()` - Optimize track layout
- `remove_routing(net)` - Remove all routing for net

**Example**:
```python
# Connect two pads
pcb.routing.connect(
    ref1='R1', pad1=1,
    ref2='C1', pad2=1,
    net='Signal'
)

# Add manual track
pcb.routing.add_track(
    start=(100, 100),
    end=(150, 100),
    width=0.25,
    layer='F.Cu',
    net='VCC'
)

# Add via
pcb.routing.add_via(
    position=(125, 100),
    size=0.8,
    drill=0.4,
    net='Signal'
)

# Auto-route net
pcb.routing.route_net('GND')

# Optimize routing
pcb.routing.optimize_routing()
```

### ValidationManager (`validation.py`)
Comprehensive PCB validation.

**Purpose**: Validate PCB integrity and correctness

**Key Methods**:
- `validate_all()` - Run all validation checks
- `validate_footprints()` - Check footprint integrity
- `validate_nets()` - Validate net connectivity
- `validate_layers()` - Check layer consistency
- `validate_references()` - Check reference uniqueness
- `get_validation_report()` - Get detailed report

**Example**:
```python
# Run all validations
results = pcb.validation.validate_all()

for result in results:
    if result.severity == 'error':
        print(f"ERROR: {result.message}")
    elif result.severity == 'warning':
        print(f"WARNING: {result.message}")

# Validate specific aspects
footprint_results = pcb.validation.validate_footprints()
net_results = pcb.validation.validate_nets()

# Get detailed report
report = pcb.validation.get_validation_report()
print(report)
```

## When to Use Managers

### Use Managers For:
- **Complex Operations**: Multi-step operations requiring coordination
- **Domain Logic**: Business logic for specific domains (DRC, placement, etc.)
- **Stateful Operations**: Operations that need to maintain state
- **Cross-Collection Operations**: Operations spanning multiple collections

### Use Collections For:
- **CRUD Operations**: Simple add/remove/get operations
- **Filtering/Querying**: Finding elements by criteria
- **Iteration**: Looping over elements
- **Direct Access**: Getting specific elements by UUID

## Integration Points

### Manager to Collection
Managers access collections through board:
```python
class CustomManager(BaseManager):
    def operation(self):
        footprints = self.board.footprints  # Access collection
        for fp in footprints:
            # Process footprint
            pass
```

### Manager to Manager
Managers can coordinate with each other:
```python
class RoutingManager(BaseManager):
    def route_net(self, net):
        # Get net info from NetManager
        elements = self.board.net.get_net_elements(net)
        # Perform routing
        ...
```

### User to Manager
Users access managers through board:
```python
pcb = kpa.load_pcb('board.kicad_pcb')

# Direct manager access
pcb.placement.hierarchical(spacing=5.0)
pcb.drc.check_clearances()
pcb.net.rename_net('Net-1', 'VCC')
```

## Testing

Tests located in `../../tests/`:
- `test_managers.py` - Manager functionality
- `test_drc_manager.py` - DRC-specific tests
- `test_net_manager.py` - Net management tests
- `test_placement_manager.py` - Placement tests
- Integration tests with real PCBs

## Related Modules

- `core/pcb_board.py` - Board coordination
- `collections/` - Collection implementations
- `wrappers/` - Element wrappers
- `utils/validation.py` - Validation utilities

## Future Improvements

- [ ] Undo/redo support for manager operations
- [ ] Operation batching and optimization
- [ ] Progress tracking for long operations
- [ ] Async operation support
- [ ] Manager plugin system
