# Placement Module

Component placement algorithms for automated PCB layout.

## Overview

This module provides algorithms for automatic and semi-automatic component placement. Algorithms range from simple (spiral) to complex (hierarchical grouping) and include collision detection and optimization.

## Available Algorithms

### Hierarchical Placement (`hierarchical_placement.py`)
Group-based placement with hierarchical organization.

**Algorithm**: Places components in logical groups with configurable spacing and hierarchy.

**Best For**:
- Complex boards with functional blocks
- Boards with power/signal separation
- Designs requiring logical organization

**Configuration**:
- `component_spacing` - Spacing between components (mm)
- `group_spacing` - Spacing between groups (mm)
- `groups` - Dictionary of group definitions
- `hierarchy` - Parent-child group relationships

**Example**:
```python
# Define groups
groups = {
    'power': ['U1', 'C1', 'C2', 'L1'],
    'mcu': ['U2', 'C3', 'C4', 'R1', 'R2'],
    'sensors': ['U3', 'U4', 'R3', 'R4']
}

# Define hierarchy (optional)
hierarchy = {
    'power': None,  # Top level
    'mcu': 'power',  # Near power
    'sensors': 'mcu'  # Near MCU
}

# Run placement
pcb.placement.hierarchical(
    component_spacing=5.0,
    group_spacing=15.0,
    groups=groups,
    hierarchy=hierarchy
)
```

**Algorithm Details**:
1. Calculate bounding boxes for each group
2. Place groups according to hierarchy
3. Place components within each group
4. Check for collisions and adjust
5. Optimize spacing within groups

### Spiral Placement (`spiral_placement.py`)
Spiral outward from center point.

**Algorithm**: Places components in an Archimedean spiral pattern from a center point.

**Best For**:
- Simple boards
- Uniform component distribution
- Quick rough placement

**Configuration**:
- `center` - Center point (x, y)
- `spacing` - Spacing between rings (mm)
- `start_radius` - Initial radius (mm)
- `angular_step` - Angle between components (degrees)

**Example**:
```python
# Spiral from board center
pcb.placement.spiral(
    center=(100, 100),
    spacing=10.0,
    start_radius=20.0,
    angular_step=30
)

# Spiral with custom components
pcb.placement.spiral(
    center=(100, 100),
    spacing=8.0,
    components=['R1', 'R2', 'R3', 'C1', 'C2']
)
```

**Algorithm Details**:
1. Start at center + start_radius
2. Place components at calculated angle
3. Increase radius based on spacing
4. Continue until all components placed
5. Avoid collisions by adjusting radius

### Grid Placement (`base.py`)
Simple grid-based placement.

**Algorithm**: Places components in a regular grid pattern.

**Best For**:
- Uniform components (resistor arrays, etc.)
- Test points
- Connector layouts

**Configuration**:
- `cols` - Number of columns
- `spacing` - Spacing between components (mm)
- `origin` - Top-left corner (x, y)
- `row_spacing` - Custom row spacing (optional)

**Example**:
```python
# 4-column grid
pcb.placement.grid(
    cols=4,
    spacing=15.0,
    origin=(50, 50)
)

# Custom row/column spacing
pcb.placement.grid(
    cols=3,
    spacing=10.0,
    row_spacing=20.0
)
```

## Supporting Utilities

### Bounding Box (`bbox.py`)
Bounding box calculations for placement.

**Key Functions**:
- `calculate_bbox(footprints)` - Get bounding box for footprints
- `bbox_contains(bbox, point)` - Check point containment
- `bbox_intersects(bbox1, bbox2)` - Check overlap
- `expand_bbox(bbox, margin)` - Add margin

**Example**:
```python
from kicad_pcb_api.placement import calculate_bbox, expand_bbox

# Get bounding box for components
fp_list = [pcb.footprints.get('R1'), pcb.footprints.get('R2')]
bbox = calculate_bbox(fp_list)

# Add margin
bbox_with_margin = expand_bbox(bbox, margin=5.0)

print(f"Width: {bbox.width}, Height: {bbox.height}")
```

### Collision Detection (`courtyard_collision.py`)
Detect footprint courtyard collisions.

**Key Functions**:
- `check_collisions(footprints)` - Find all collisions
- `has_collision(fp1, fp2)` - Check two footprints
- `get_collision_pairs()` - Get overlapping pairs
- `resolve_collisions()` - Attempt auto-resolution

**Example**:
```python
from kicad_pcb_api.placement import check_collisions, resolve_collisions

# Check for collisions
collisions = check_collisions(pcb.footprints)

for col in collisions:
    print(f"Collision: {col.fp1.reference} and {col.fp2.reference}")
    print(f"  Overlap: {col.overlap_area} mm²")

# Auto-resolve (moves components)
resolved = resolve_collisions(pcb.footprints, min_spacing=0.5)
print(f"Resolved {resolved} collisions")
```

### Placement Utilities (`utils.py`)
General placement helper functions.

**Key Functions**:
- `get_board_center(pcb)` - Calculate board center
- `group_by_value(footprints)` - Group by value
- `group_by_footprint(footprints)` - Group by footprint type
- `sort_by_size(footprints)` - Sort by size
- `optimize_orientation(footprints)` - Optimize rotation

**Example**:
```python
from kicad_pcb_api.placement import get_board_center, sort_by_size

# Get board center for placement origin
center = get_board_center(pcb)

# Sort components by size for placement
sorted_fps = sort_by_size(pcb.footprints)

# Place largest first
for fp in sorted_fps:
    # Placement logic
    pass
```

## Usage Through Manager

The PlacementManager provides convenient access:

```python
# Access through board
pcb.placement.hierarchical(spacing=5.0, groups=groups)
pcb.placement.spiral(center=(100, 100), spacing=10.0)
pcb.placement.grid(cols=4, spacing=15.0)

# With specific components
pcb.placement.spiral(
    center=(100, 100),
    spacing=8.0,
    components=['R1', 'R2', 'R3']
)
```

## Algorithm Selection Guide

### Choose Hierarchical When:
- Complex board with functional blocks
- Need logical organization
- Have related components to group
- Want customizable hierarchy

### Choose Spiral When:
- Simple uniform distribution needed
- Quick rough placement
- No specific organization required
- Testing or prototyping

### Choose Grid When:
- Uniform components (arrays)
- Regular patterns needed
- Test points or connectors
- Precise spacing required

## Configuration Options

### Global Config
```python
from kicad_pcb_api import config

config.placement.default_spacing = 5.0
config.placement.check_collisions = True
config.placement.auto_resolve = True
```

### Per-Algorithm Config
```python
# Hierarchical with custom settings
pcb.placement.hierarchical(
    component_spacing=5.0,
    group_spacing=15.0,
    check_collisions=True,
    optimize=True
)
```

## Performance Considerations

| Algorithm | Complexity | Time (100 components) |
|-----------|-----------|----------------------|
| Grid | O(n) | ~10ms |
| Spiral | O(n) | ~20ms |
| Hierarchical | O(n log n) | ~50ms |

For large boards (>500 components), consider:
- Disabling collision checking during initial placement
- Running optimization as separate step
- Using grid for uniform sections

## Testing

Tests located in `../../tests/`:
- `test_placement.py` - Placement algorithms
- `test_hierarchical_placement.py` - Hierarchical tests
- `test_spiral_placement.py` - Spiral tests
- `test_collision_detection.py` - Collision tests
- Integration tests with real PCBs

## Related Modules

- `managers/placement.py` - PlacementManager
- `collections/footprints.py` - FootprintCollection
- `core/geometry.py` - Geometric utilities

## Future Improvements

- [ ] Force-directed placement algorithm
- [ ] Machine learning-based optimization
- [ ] Multi-objective optimization
- [ ] Thermal-aware placement
- [ ] Signal integrity considerations
- [ ] Import/export placement templates
