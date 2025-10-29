# Collections Module

Enhanced collection classes with filtering, searching, and bulk operations.

## Overview

This module provides specialized collection classes that extend Python's built-in functionality with domain-specific features for managing PCB elements. Based on the IndexedCollection pattern from kicad-sch-api, these collections offer O(1) UUID lookups and efficient bulk operations.

## Collection Classes

### Base Collection Pattern
All collections inherit from `IndexedCollection`:
```python
class IndexedCollection(Generic[T], ABC):
    def add(self, item: T) -> T:
        """Add element and return it"""

    def remove(self, identifier: Union[str, T]) -> bool:
        """Remove element by UUID or instance"""

    def get(self, uuid: str) -> Optional[T]:
        """Get element by UUID (O(1))"""

    def find(self, predicate: Callable[[T], bool]) -> List[T]:
        """Find all elements matching a predicate"""

    def filter(self, **criteria) -> List[T]:
        """Filter by attribute criteria"""

    def clear(self) -> None:
        """Clear all elements"""
```

## Available Collections

### FootprintCollection
- **Location**: `footprints.py`
- **Elements**: Footprint objects
- **Key Features**:
  - UUID-based fast lookup
  - Reference-based lookup (secondary index)
  - Layer filtering
  - Bounding box queries
- **Key Methods**:
  - `add(footprint_name, reference, position)` - Add footprint from library
  - `remove(uuid_or_reference)` - Remove by UUID or reference
  - `get_by_reference(reference)` - Get specific footprint by reference
  - `filter_by_layer(layer)` - Find footprints on specific layer
  - `find_in_region(x, y, width, height)` - Spatial query
  - `get_wrapper(uuid)` - Get wrapped footprint with enhanced methods

### TrackCollection
- **Location**: `tracks.py`
- **Elements**: Track (trace) objects
- **Key Features**:
  - Net-based indexing
  - Layer-based filtering
  - Connection point queries
- **Key Methods**:
  - `add(start, end, width, layer, net)` - Add track
  - `remove(uuid)` - Remove by UUID
  - `filter_by_net(net)` - Get all tracks in a net
  - `filter_by_layer(layer)` - Get tracks on specific layer
  - `find_connected_to(point)` - Find tracks connected to a point
  - `get_net_tracks(net_name)` - Get all tracks in named net

### ViaCollection
- **Location**: `vias.py`
- **Elements**: Via objects
- **Key Features**:
  - Net-based indexing
  - Layer pair filtering
  - Position-based queries
- **Key Methods**:
  - `add(position, size, drill, net, layers)` - Add via
  - `remove(uuid)` - Remove by UUID
  - `filter_by_net(net)` - Get vias in a net
  - `find_at_position(x, y, tolerance)` - Find via at position
  - `get_layer_vias(from_layer, to_layer)` - Get vias between layers

### ZoneCollection
- **Location**: `zones.py`
- **Elements**: Zone (copper pour) objects
- **Key Features**:
  - Net-based indexing
  - Layer filtering
  - Priority ordering
- **Key Methods**:
  - `add(net, layer, outline, priority)` - Add zone
  - `remove(uuid)` - Remove by UUID
  - `filter_by_net(net)` - Get zones in a net
  - `filter_by_layer(layer)` - Get zones on layer
  - `get_by_priority(layer)` - Get zones ordered by priority

## Common Operations

### Adding Elements
```python
# Add footprint from library
fp = pcb.footprints.add('Resistor_SMD:R_0603_1608Metric', 'R1', (100, 100))

# Add track
track = pcb.tracks.add(
    start=(100, 100),
    end=(150, 100),
    width=0.25,
    layer='F.Cu',
    net='Signal'
)

# Add via
via = pcb.vias.add(
    position=(125, 100),
    size=0.8,
    drill=0.4,
    net='Signal',
    layers=['F.Cu', 'B.Cu']
)

# Add zone
zone = pcb.zones.add(
    net='GND',
    layer='B.Cu',
    outline=[(0, 0), (100, 0), (100, 100), (0, 100)],
    priority=0
)
```

### Querying Elements
```python
# Get by UUID (O(1))
fp = pcb.footprints.get(uuid)

# Get by reference (O(1) with secondary index)
fp = pcb.footprints.get_by_reference('R1')

# Filter by attributes
power_resistors = pcb.footprints.filter(value='10k', layer='F.Cu')

# Custom predicate
large_footprints = pcb.footprints.find(
    lambda fp: fp.width > 10 and fp.height > 10
)

# Filter by net
signal_tracks = pcb.tracks.filter_by_net('Signal')
signal_vias = pcb.vias.filter_by_net('Signal')
```

### Spatial Queries
```python
# Find footprints in region
fps = pcb.footprints.find_in_region(
    x=50, y=50, width=100, height=100
)

# Find tracks connected to a point
tracks = pcb.tracks.find_connected_to((100, 100))

# Find via at position
via = pcb.vias.find_at_position(125, 100, tolerance=0.1)
```

### Removing Elements
```python
# Remove by UUID
pcb.footprints.remove(uuid)

# Remove by reference
pcb.footprints.remove('R1')

# Remove by instance
pcb.tracks.remove(track)

# Clear all
pcb.footprints.clear()
```

### Iteration
```python
# Iterate over all footprints
for fp in pcb.footprints:
    print(f"{fp.reference}: {fp.value}")

# Iterate over filtered subset
for track in pcb.tracks.filter_by_net('GND'):
    print(f"Track on layer: {track.layer}")

# Enumerate with index
for i, via in enumerate(pcb.vias):
    print(f"Via {i}: {via.position}")
```

## Collection Features

### UUID-Based Fast Lookup
All collections maintain UUID indexes for O(1) lookups:
```python
# O(1) lookup by UUID
fp = pcb.footprints.get(uuid)
```

### Secondary Indexes
Collections maintain specialized indexes for common queries:
- **FootprintCollection**: Reference index for O(1) reference lookup
- **TrackCollection**: Net index for fast net filtering
- **ViaCollection**: Net and layer indexes

### Lazy Index Rebuilding
Indexes are automatically rebuilt only when needed:
- Marked dirty on modifications
- Rebuilt on next query
- Efficient bulk operations

### Modification Tracking
Collections track modifications for save optimization:
```python
if pcb.footprints.is_modified:
    pcb.save()
```

## Performance Characteristics

| Operation | Complexity | Time |
|-----------|-----------|------|
| Add element | O(1) | ~1µs |
| Remove by UUID | O(1) | ~1µs |
| Get by UUID | O(1) | ~1µs |
| Get by reference | O(1) | ~1µs |
| Filter by net | O(n) | ~100µs |
| Filter by layer | O(n) | ~100µs |
| Spatial query | O(n) | ~1ms |
| Iterate all | O(n) | ~10µs/item |

Where n = number of elements in collection.

## Extending Collections

To create a custom collection:

```python
from kicad_pcb_api.collections.base import IndexedCollection
from typing import Optional

class CustomCollection(IndexedCollection[CustomElement]):
    def __init__(self, items=None):
        super().__init__(items)
        self._custom_index = {}

    def _get_item_uuid(self, item: CustomElement) -> str:
        """Extract UUID from item"""
        return item.uuid

    def _create_item(self, **kwargs) -> CustomElement:
        """Create new item"""
        return CustomElement(**kwargs)

    def _build_additional_indexes(self) -> None:
        """Build custom indexes"""
        self._custom_index = {
            item.custom_field: i
            for i, item in enumerate(self._items)
        }

    def find_by_custom_field(self, value):
        """Custom finder using secondary index"""
        self._ensure_indexes_current()
        if value in self._custom_index:
            idx = self._custom_index[value]
            return self._items[idx]
        return None
```

## Integration Points

### Used By
- `PCBBoard` class - Owns all collections
- Managers - Access via board instance
- Wrappers - Track parent collection
- User code - Direct collection manipulation

### Related Modules
- `core/types.py` - Element type definitions
- `core/pcb_board.py` - Collection ownership
- `managers/*` - Manager implementations
- `wrappers/*` - Element wrapper classes

## Testing

Tests located in `../../tests/`:
- `test_collections.py` - Collection functionality
- `test_footprint_collection.py` - Footprint-specific tests
- `test_track_collection.py` - Track-specific tests
- `test_via_collection.py` - Via-specific tests
- Integration tests with real PCBs

## Known Issues

1. **Large PCB Performance** - Spatial queries may be slow on large PCBs (>10k elements)
2. **Memory Usage** - Multiple indexes increase memory consumption
3. **Index Coherency** - Modifications outside collections don't update indexes

## Future Improvements

- [ ] Spatial indexing (R-tree) for fast region queries
- [ ] Lazy collection evaluation for large PCBs
- [ ] Event listeners on collection changes
- [ ] Collection change history/undo
- [ ] Parallel operations for large collections
- [ ] Query optimization and caching

## References

- Python Collections: https://docs.python.org/3/library/collections.html
- kicad-sch-api IndexedCollection: See reference implementation
- Type system: See `core/types.py`
