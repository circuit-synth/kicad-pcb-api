# Wrappers Module

Enhanced element wrappers with validation and convenience methods.

## Overview

This module provides wrapper classes that enhance raw dataclass objects with validation, convenience methods, and parent collection tracking. Wrappers make working with PCB elements more intuitive and type-safe.

## Wrapper Pattern

### Base Wrapper

All wrappers inherit from `ElementWrapper`:

```python
class ElementWrapper(ABC, Generic[T]):
    def __init__(self, data: T, parent_collection):
        self._data = data
        self._collection = parent_collection

    @property
    def data(self) -> T:
        """Get underlying dataclass"""
        return self._data

    @abstractmethod
    def uuid(self) -> str:
        """Get element UUID"""
        pass
```

## Benefits of Wrappers

### 1. Validation on Setters
```python
# Without wrapper - no validation
footprint.position = (999999, 999999)  # Invalid but allowed

# With wrapper - validated
fp_wrapper.position = (999999, 999999)  # Raises ValidationError
```

### 2. Convenient Methods
```python
# Without wrapper - manual calculation
new_x = footprint.position.x + 10
new_y = footprint.position.y + 10
footprint.position = Point(new_x, new_y)

# With wrapper - convenient method
fp_wrapper.move_by(10, 10)
```

### 3. Parent Collection Tracking
```python
# Wrapper automatically marks collection as modified
fp_wrapper.value = '10k'  # Collection marked dirty, indexes updated
```

### 4. Type Safety
```python
# Wrapper ensures correct types
fp_wrapper.rotation = 90.0  # OK
fp_wrapper.rotation = "90"  # Type error caught by mypy
```

## Available Wrappers

### FootprintWrapper (`footprint.py`)
Enhanced footprint with convenient methods.

**Properties**:
- `reference` - Component reference (with validation)
- `value` - Component value
- `position` - X, Y position
- `rotation` - Rotation angle (0-360)
- `layer` - Front or back copper
- `locked` - Lock state

**Methods**:
- `move_to(x, y)` - Move to absolute position
- `move_by(dx, dy)` - Move relative
- `rotate(angle)` - Rotate by angle
- `rotate_to(angle)` - Set absolute rotation
- `flip()` - Flip to other side
- `get_pads()` - Get all pads
- `get_pad(number)` - Get specific pad
- `get_bounding_box()` - Calculate bounds
- `get_courtyard()` - Get courtyard polygon

**Example**:
```python
# Get wrapped footprint
fp = pcb.footprints.get_wrapper('R1')

# Convenient positioning
fp.move_to(100, 100)
fp.rotate(45)
fp.move_by(10, 10)

# Flip to back
fp.flip()

# Access pads
pads = fp.get_pads()
pad1 = fp.get_pad(1)

# Get bounds
bbox = fp.get_bounding_box()
print(f"Width: {bbox.width}, Height: {bbox.height}")
```

### TrackWrapper (`track.py`)
Enhanced track with routing utilities.

**Properties**:
- `start` - Start point
- `end` - End point
- `width` - Track width
- `layer` - Copper layer
- `net` - Net name
- `locked` - Lock state

**Methods**:
- `length()` - Calculate track length
- `midpoint()` - Get center point
- `angle()` - Get track angle
- `extend(distance)` - Extend track
- `split_at(point)` - Split into two tracks
- `is_horizontal()` - Check if horizontal
- `is_vertical()` - Check if vertical
- `connects_to(track)` - Check if connects to another track

**Example**:
```python
# Get wrapped track
track = pcb.tracks.get_wrapper(uuid)

# Get properties
length = track.length()
angle = track.angle()
mid = track.midpoint()

# Check orientation
if track.is_horizontal():
    print("Horizontal track")

# Extend track
track.extend(5.0)  # Extend by 5mm

# Split at point
track1, track2 = track.split_at((125, 100))
```

### ViaWrapper (`via.py`)
Enhanced via with layer utilities.

**Properties**:
- `position` - X, Y position
- `size` - Via diameter
- `drill` - Drill diameter
- `net` - Net name
- `layers` - Connected layers
- `locked` - Lock state

**Methods**:
- `connects_layers(layer1, layer2)` - Check if connects layers
- `add_layer(layer)` - Add layer to via
- `remove_layer(layer)` - Remove layer
- `get_layer_pair()` - Get from/to layers
- `is_through_hole()` - Check if through-hole
- `is_blind_buried()` - Check if blind/buried

**Example**:
```python
# Get wrapped via
via = pcb.vias.get_wrapper(uuid)

# Check properties
if via.is_through_hole():
    print("Through-hole via")

# Check layer connectivity
if via.connects_layers('F.Cu', 'B.Cu'):
    print("Connects front and back")

# Modify layers
via.add_layer('In1.Cu')
via.remove_layer('B.Cu')
```

### ZoneWrapper (`zone.py`)
Enhanced zone with fill utilities.

**Properties**:
- `net` - Net name
- `layer` - Copper layer
- `outline` - Zone outline polygon
- `priority` - Fill priority
- `filled` - Fill state
- `hatch_style` - Hatch pattern

**Methods**:
- `get_area()` - Calculate zone area
- `contains_point(point)` - Check if point inside
- `get_bounding_box()` - Calculate bounds
- `intersects(zone)` - Check overlap with another zone
- `refill()` - Recalculate fill
- `clear_fill()` - Remove fill

**Example**:
```python
# Get wrapped zone
zone = pcb.zones.get_wrapper(uuid)

# Get properties
area = zone.get_area()
bbox = zone.get_bounding_box()

# Check containment
if zone.contains_point((125, 100)):
    print("Point is in zone")

# Refill zone
zone.refill()
```

## Usage Patterns

### Getting Wrappers

Collections provide wrapper access:
```python
# Get wrapper by UUID
fp_wrapper = pcb.footprints.get_wrapper(uuid)

# Get wrapper by reference
fp_wrapper = pcb.footprints.get_wrapper('R1')

# Get wrapper by index
fp_wrapper = pcb.footprints[0].wrapper
```

### Modifying Through Wrappers

Changes through wrappers automatically sync:
```python
# Modify through wrapper
fp = pcb.footprints.get_wrapper('R1')
fp.position = (100, 100)  # Collection marked dirty
fp.rotation = 90          # Indexes updated
fp.value = '10k'          # Change tracked

# Save propagates changes
pcb.save()  # Changes written to file
```

### Wrapper vs Direct Access

**Use Wrappers For**:
- Interactive manipulation
- Validation requirements
- Convenience methods
- Type safety

**Use Direct Access For**:
- Bulk operations
- Performance-critical code
- Simple property reads
- Low-level control

## Implementation Details

### Property Tracking
Wrappers track modifications:
```python
class FootprintWrapper(ElementWrapper):
    @property
    def value(self):
        return self._data.value

    @value.setter
    def value(self, new_value):
        # Validate
        if not new_value:
            raise ValidationError("Value cannot be empty")
        # Update data
        self._data.value = new_value
        # Mark modified
        self._mark_modified()
```

### Collection Synchronization
Wrappers sync with parent collection:
```python
class FootprintWrapper(ElementWrapper):
    def move_to(self, x, y):
        self._data.position = Point(x, y)
        # Mark collection as needing index rebuild
        self._invalidate_indexes()
        # Mark as modified
        self._mark_modified()
```

## Testing

Tests located in `../../tests/`:
- `test_wrappers.py` - Wrapper functionality
- `test_footprint_wrapper.py` - Footprint-specific tests
- `test_track_wrapper.py` - Track-specific tests
- `test_via_wrapper.py` - Via-specific tests
- Integration tests with real PCBs

## Related Modules

- `collections/base.py` - Collection base class
- `core/types.py` - Underlying dataclasses
- `core/validation.py` - Validation logic
- `managers/` - Manager implementations

## Future Improvements

- [ ] Lazy wrapper creation
- [ ] Wrapper caching for performance
- [ ] Change history/undo support
- [ ] Batch modification API
- [ ] Custom wrapper plugins
