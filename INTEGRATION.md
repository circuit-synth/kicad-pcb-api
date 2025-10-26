# Integration Guide for circuit-synth

This guide helps you integrate kicad-pcb-api into the circuit-synth project.

## Installation in circuit-synth

Add to your `pyproject.toml`:

```toml
[project]
dependencies = [
    "kicad-pcb-api>=0.1.0",
    # ... other dependencies
]
```

Or install with uv:

```bash
uv add kicad-pcb-api
```

## Architecture Overview

### What kicad-pcb-api Provides

**Core Classes**:
- `PCBBoard` - Main PCB manipulation class with managers
- `PCBParser` - S-expression parser/formatter
- `PCBElementFactory` - Factory for creating PCB elements

**Managers** (attached to PCBBoard):
- `pcb.drc` - Design rule checking
- `pcb.net` - Net operations
- `pcb.placement` - Component placement
- `pcb.routing` - Track routing
- `pcb.validation` - Board validation

**Collections** (O(1) lookups):
- `pcb.footprints` - FootprintCollection
- `pcb.tracks` - TrackCollection
- `pcb.vias` - ViaCollection

**Data Types** (from `kicad_pcb_api.core.types`):
- `Point`, `Track`, `Via`, `Footprint`, `Zone`, `Net`, `Pad`, etc.

## Integration Patterns

### Pattern 1: Generate PCB from circuit-synth Circuit

```python
import kicad_pcb_api as kpa
from circuit_synth import Circuit

def circuit_to_pcb(circuit: Circuit) -> kpa.PCBBoard:
    """Convert circuit-synth Circuit to KiCAD PCB."""

    # Create new PCB
    pcb = kpa.create_pcb()

    # Add components
    for component in circuit.components:
        footprint = pcb.add_footprint(
            reference=component.reference,
            library=component.footprint_lib,
            name=component.footprint_name,
            value=component.value,
            x=component.x,
            y=component.y,
            rotation=component.rotation
        )

    # Add nets/connections
    for net in circuit.nets:
        net_num = pcb.add_net(net.name)

        # Connect pads to net
        for pad_connection in net.connections:
            pcb.connect_pad(
                reference=pad_connection.component,
                pad_number=pad_connection.pad,
                net=net_num
            )

    # Auto-place components
    pcb.placement.place_in_grid(
        references=[c.reference for c in circuit.components],
        start_x=50, start_y=50,
        spacing_x=10, spacing_y=10
    )

    # Run DRC
    violations = pcb.drc.check_all()
    if violations > 0:
        for error in pcb.drc.get_errors():
            print(f"DRC Error: {error.description}")

    return pcb
```

### Pattern 2: Modify Existing PCB

```python
def update_pcb_from_changes(pcb_path: str, changes: dict) -> None:
    """Update existing PCB with new changes."""

    # Load existing PCB
    pcb = kpa.load_pcb(pcb_path)

    # Update component values
    for ref, new_value in changes.get('values', {}).items():
        footprint = pcb.footprints.get_by_reference(ref)
        if footprint:
            footprint.value = new_value

    # Update positions
    for ref, position in changes.get('positions', {}).items():
        footprint = pcb.footprints.get_by_reference(ref)
        if footprint:
            footprint.x = position['x']
            footprint.y = position['y']

    # Validate changes
    issues = pcb.validation.validate_all()
    if issues:
        print(f"Found {issues} validation issues")

    # Save if modified
    if pcb.is_modified:
        pcb.save()
```

### Pattern 3: Query and Analyze PCB

```python
def analyze_pcb(pcb_path: str) -> dict:
    """Analyze PCB and return statistics."""

    pcb = kpa.load_pcb(pcb_path)

    # Get component statistics
    total_components = len(pcb.footprints)
    resistors = len(pcb.footprints.filter_by_lib_id('Resistor_SMD'))
    capacitors = len(pcb.footprints.filter_by_lib_id('Capacitor_SMD'))

    # Get net statistics
    net_stats = pcb.net.get_net_statistics()

    # Get routing statistics
    total_tracks = len(pcb.tracks)
    total_vias = len(pcb.vias)

    return {
        'components': {
            'total': total_components,
            'resistors': resistors,
            'capacitors': capacitors,
        },
        'nets': net_stats,
        'routing': {
            'tracks': total_tracks,
            'vias': total_vias,
        }
    }
```

## Key Integration Points

### 1. Component Mapping

Map circuit-synth components to KiCAD footprints:

```python
# In circuit-synth, you might have:
FOOTPRINT_MAP = {
    'Device:R': 'Resistor_SMD:R_0603_1608Metric',
    'Device:C': 'Capacitor_SMD:C_0603_1608Metric',
    'Device:LED': 'LED_SMD:LED_0603_1608Metric',
}

def get_footprint_for_symbol(symbol: str) -> tuple[str, str]:
    """Get (library, name) for a symbol."""
    footprint = FOOTPRINT_MAP.get(symbol)
    if footprint:
        return footprint.split(':', 1)
    return None, None
```

### 2. Net Management

```python
def sync_nets(circuit, pcb):
    """Synchronize nets between circuit and PCB."""

    # Clear existing nets (optional)
    # pcb.net.clear_all_nets()

    # Add nets from circuit
    for net in circuit.nets:
        net_num = pcb.add_net(net.name)

        # Add connections
        for conn in net.connections:
            pcb.connect_pad(
                reference=conn.component,
                pad_number=conn.pad,
                net=net_num
            )
```

### 3. Placement Strategies

```python
def place_components(pcb, strategy='hierarchical'):
    """Place components using different strategies."""

    if strategy == 'grid':
        pcb.placement.place_in_grid(
            references=pcb.footprints.get_all_references(),
            start_x=50, start_y=50,
            spacing_x=10, spacing_y=10,
            columns=10
        )

    elif strategy == 'circular':
        pcb.placement.place_in_circle(
            references=pcb.footprints.get_all_references(),
            center_x=100, center_y=100,
            radius=50
        )

    elif strategy == 'by_net':
        # Group by net for better routing
        for net_num, net_name in pcb.net.get_all_nets().items():
            components = pcb.net.get_components_on_net(net_num)
            # Place close together
            pcb.placement.place_in_grid(
                references=components,
                start_x=50 + net_num * 30,
                start_y=50,
                spacing_x=5,
                spacing_y=5
            )
```

## Error Handling

```python
from kicad_pcb_api import (
    KiCadPCBError,
    ValidationError,
    ReferenceError,
    NetError,
)

try:
    pcb = kpa.load_pcb('board.kicad_pcb')
    pcb.add_footprint('R1', 'Resistor_SMD:R_0603', 50, 50)
    pcb.save()

except ReferenceError as e:
    print(f"Component reference error: {e}")

except ValidationError as e:
    print(f"Validation failed: {e}")

except KiCadPCBError as e:
    print(f"PCB operation failed: {e}")
```

## Testing Integration

```python
import pytest
import kicad_pcb_api as kpa

def test_circuit_to_pcb_conversion():
    """Test converting circuit to PCB."""

    # Create test circuit (circuit-synth)
    circuit = create_test_circuit()

    # Convert to PCB
    pcb = circuit_to_pcb(circuit)

    # Verify components
    assert len(pcb.footprints) == len(circuit.components)

    # Verify nets
    assert len(pcb.net.get_all_nets()) == len(circuit.nets)

    # Verify no DRC errors
    violations = pcb.drc.check_all()
    assert violations == 0

def test_pcb_roundtrip():
    """Test PCB load/save preserves data."""

    # Create PCB
    pcb = kpa.create_pcb()
    pcb.add_footprint('R1', 'Resistor_SMD:R_0603', 50, 50, value='10k')

    # Save
    pcb.save('test.kicad_pcb')

    # Load
    pcb2 = kpa.load_pcb('test.kicad_pcb')

    # Verify
    r1 = pcb2.footprints.get_by_reference('R1')
    assert r1.value == '10k'
    assert r1.x == 50
    assert r1.y == 50
```

## Performance Considerations

### 1. Use Collections for Queries

```python
# GOOD - O(1) lookup
footprint = pcb.footprints.get_by_reference('R1')

# BAD - O(n) iteration
for fp in pcb.pcb_data['footprints']:
    if fp.reference == 'R1':
        footprint = fp
        break
```

### 2. Batch Operations

```python
# GOOD - Single validation pass
pcb.add_footprint('R1', ...)
pcb.add_footprint('R2', ...)
pcb.add_footprint('R3', ...)
violations = pcb.drc.check_all()  # Once at the end

# BAD - Multiple validation passes
pcb.add_footprint('R1', ...)
pcb.drc.check_all()
pcb.add_footprint('R2', ...)
pcb.drc.check_all()
```

### 3. Lazy Loading

Collections use lazy indexing - indexes are only rebuilt when needed:

```python
# Fast - no index rebuild
pcb.add_footprint('R1', ...)
pcb.add_footprint('R2', ...)

# Index built here on first query
footprint = pcb.footprints.get_by_reference('R1')
```

## API Reference

See the main README for complete API documentation:
- [PCBBoard API](README.md#pcbboard-api)
- [Manager APIs](README.md#managers)
- [Collection APIs](README.md#collections)

## Example: Complete Integration

```python
from circuit_synth import Circuit, Component, Net
import kicad_pcb_api as kpa

def generate_pcb_from_circuit(circuit: Circuit, output_path: str):
    """Complete circuit-synth to KiCAD PCB workflow."""

    # 1. Create PCB
    pcb = kpa.create_pcb()

    # 2. Add components with footprints
    footprint_map = load_footprint_mapping()
    for component in circuit.components:
        lib, name = footprint_map.get(component.symbol, (None, None))
        if lib and name:
            pcb.add_footprint(
                reference=component.reference,
                library=lib,
                name=name,
                value=component.value,
                x=0, y=0  # Will be placed later
            )

    # 3. Add nets
    for net in circuit.nets:
        net_num = pcb.add_net(net.name)
        for conn in net.connections:
            pcb.connect_pad(conn.component, conn.pad, net_num)

    # 4. Place components
    pcb.placement.place_in_grid(
        references=[c.reference for c in circuit.components],
        start_x=50, start_y=50,
        spacing_x=10, spacing_y=10,
        columns=8
    )

    # 5. Validate
    issues = pcb.validation.validate_all()
    if issues > 0:
        print(f"⚠️  Found {issues} validation issues")
        for issue in pcb.validation.get_all_issues():
            print(f"  - {issue.category}: {issue.description}")

    # 6. Run DRC
    violations = pcb.drc.check_all()
    if violations > 0:
        print(f"⚠️  Found {violations} DRC violations")
        for error in pcb.drc.get_errors():
            print(f"  - {error.description}")

    # 7. Save
    pcb.save(output_path)
    print(f"✅ PCB saved to {output_path}")

    return pcb
```

## Troubleshooting

### Issue: "Module not found"
```bash
# Ensure kicad-pcb-api is installed
pip list | grep kicad-pcb-api

# Reinstall if needed
pip install --upgrade kicad-pcb-api
```

### Issue: "Invalid footprint library"
```python
# Verify footprint exists in KiCAD libraries
# Use full library:name format
pcb.add_footprint('R1', 'Resistor_SMD', 'R_0603_1608Metric', ...)
```

### Issue: "DRC violations"
```python
# Get detailed error information
violations = pcb.drc.check_all()
for error in pcb.drc.get_errors():
    print(f"Error: {error.description}")
    print(f"Location: ({error.x}, {error.y})")
```

## Support

- **GitHub Issues**: https://github.com/circuit-synth/kicad-pcb-api/issues
- **Documentation**: https://github.com/circuit-synth/kicad-pcb-api
- **PyPI Package**: https://pypi.org/project/kicad-pcb-api/
