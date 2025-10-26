# Architecture Analysis: Reference Implementations

**Date:** October 26, 2025
**Purpose:** Extract architectural patterns from kicad-sch-api, pykicad, and kicad-skip to guide kicad-pcb-api development

---

## Executive Summary

This document analyzes three reference implementations for KiCAD file manipulation:

1. **kicad-sch-api** - Our primary reference, modern Python library for schematic manipulation
2. **pykicad** - Mature PCB library with S-expression abstraction
3. **kicad-skip** - Universal S-expression manipulator (schematics + PCB)

**Key Takeaway:** kicad-sch-api provides the blueprint for our architecture (collections, managers, enhanced UX), while pykicad shows successful PCB-specific patterns we should adapt.

---

## 1. kicad-sch-api: Primary Reference Architecture

### 1.1 Project Structure

```
kicad-sch-api/
├── kicad_sch_api/
│   ├── core/                      # Core functionality
│   │   ├── schematic.py           # Main Schematic class
│   │   ├── parser.py              # S-expression parser
│   │   ├── formatter.py           # S-expression formatter
│   │   ├── types.py               # Data types (Point, Component, etc.)
│   │   ├── components.py          # Component management
│   │   ├── wires.py               # Wire management
│   │   ├── labels.py              # Label management
│   │   ├── geometry.py            # Geometric calculations
│   │   ├── component_bounds.py    # Bounding box calculations
│   │   ├── ic_manager.py          # IC-specific utilities
│   │   └── managers/              # Specialized managers
│   │       ├── wire.py            # Wire routing logic
│   │       ├── graphics.py        # Graphics management
│   │       ├── metadata.py        # Metadata management
│   │       ├── format_sync.py     # Format synchronization
│   │       └── validation.py      # Validation utilities
│   ├── collections/               # Collection classes
│   │   ├── base.py                # IndexedCollection base class
│   │   ├── components.py          # ComponentCollection
│   │   ├── wires.py               # WireCollection
│   │   ├── junctions.py           # JunctionCollection
│   │   └── labels.py              # LabelCollection
│   ├── geometry/                  # Geometric operations
│   │   ├── symbol_bbox.py         # Symbol bounding boxes
│   │   └── font_metrics.py        # Text metrics
│   ├── library/                   # Library management
│   │   └── cache.py               # Symbol library cache
│   ├── symbols/                   # Symbol handling
│   │   ├── cache.py               # Symbol caching
│   │   ├── resolver.py            # Symbol resolution
│   │   └── validators.py          # Symbol validation
│   ├── parsers/                   # Element parsers
│   │   ├── base.py                # Base parser
│   │   ├── registry.py            # Parser registry
│   │   └── elements/              # Element-specific parsers
│   │       ├── symbol_parser.py
│   │       ├── wire_parser.py
│   │       ├── label_parser.py
│   │       ├── text_parser.py
│   │       ├── graphics_parser.py
│   │       ├── sheet_parser.py
│   │       └── library_parser.py
│   ├── discovery/                 # Search and indexing
│   │   └── search_index.py        # Search index
│   ├── interfaces/                # Abstract interfaces
│   │   ├── parser.py              # Parser interface
│   │   ├── repository.py          # Repository interface
│   │   └── resolver.py            # Resolver interface
│   └── utils/                     # Utilities
│       └── validation.py          # Validation helpers
├── examples/                      # Usage examples
├── tests/                         # Comprehensive tests
│   └── reference_tests/           # Format preservation tests
└── .memory_bank/                  # Development context
```

### 1.2 Core Design Patterns

#### Pattern 1: IndexedCollection System

**File:** `collections/base.py`

**Key Features:**
- Generic base class `IndexedCollection[T]` using TypeVar
- Automatic UUID indexing for O(1) lookups
- Lazy index rebuilding when data changes
- Modification tracking (`_modified`, `_dirty_indexes`)
- Iterator protocol support (`__iter__`, `__len__`, `__contains__`)
- Predicate-based filtering (`find()`, `filter()`)

**Architecture:**
```python
class IndexedCollection(Generic[T], ABC):
    # Abstract methods for subclasses
    @abstractmethod
    def _get_item_uuid(self, item: T) -> str: ...

    @abstractmethod
    def _create_item(self, **kwargs) -> T: ...

    @abstractmethod
    def _build_additional_indexes(self) -> None: ...

    # Core operations
    def add(self, item: T) -> T: ...
    def remove(self, identifier: Union[str, T]) -> bool: ...
    def get(self, uuid: str) -> Optional[T]: ...
    def find(self, predicate: Callable[[T], bool]) -> List[T]: ...
    def filter(self, **criteria) -> List[T]: ...

    # Index management
    def _ensure_indexes_current(self) -> None: ...
    def _rebuild_indexes(self) -> None: ...
```

**Direct Application to PCB:**
```python
class FootprintCollection(IndexedCollection[Footprint]):
    def __init__(self):
        super().__init__()
        self._reference_index: Dict[str, int] = {}  # R1 -> index
        self._net_index: Dict[str, List[int]] = {}  # net_name -> [indices]

    def _get_item_uuid(self, item: Footprint) -> str:
        return item.uuid

    def _build_additional_indexes(self):
        # Build reference index
        self._reference_index = {
            fp.reference: i for i, fp in enumerate(self._items)
        }
        # Build net index (footprints by net)
        self._net_index = defaultdict(list)
        for i, fp in enumerate(self._items):
            for pad in fp.pads:
                if pad.net_name:
                    self._net_index[pad.net_name].append(i)

    def get_by_reference(self, ref: str) -> Optional[Footprint]:
        self._ensure_indexes_current()
        idx = self._reference_index.get(ref)
        return self._items[idx] if idx is not None else None
```

#### Pattern 2: Enhanced Wrapper Classes

**File:** `collections/components.py`

**Key Features:**
- Wrapper class (`Component`) around raw data (`SchematicSymbol`)
- Properties with validation and change tracking
- Parent collection reference for index updates
- Fluent interface for method chaining

**Architecture:**
```python
class Component:
    """Enhanced wrapper with modern API."""

    def __init__(self, symbol_data: SchematicSymbol,
                 parent_collection: "ComponentCollection"):
        self._data = symbol_data
        self._collection = parent_collection
        self._validator = SchematicValidator()

    @property
    def reference(self) -> str:
        return self._data.reference

    @reference.setter
    def reference(self, value: str):
        # Validation
        if not self._validator.validate_reference(value):
            raise ValidationError(f"Invalid reference: {value}")

        # Update indexes in parent collection
        old_ref = self._data.reference
        self._data.reference = value
        self._collection._update_reference_index(old_ref, value)
        self._collection._mark_modified()
```

**Direct Application to PCB:**
```python
class Footprint:
    """Enhanced footprint wrapper."""

    def __init__(self, footprint_data: FootprintData,
                 parent_collection: "FootprintCollection"):
        self._data = footprint_data
        self._collection = parent_collection

    @property
    def reference(self) -> str:
        return self._data.reference

    @reference.setter
    def reference(self, value: str):
        if not is_valid_reference(value):
            raise ValueError(f"Invalid reference: {value}")
        old_ref = self._data.reference
        self._data.reference = value
        self._collection._update_reference_index(old_ref, value)
        self._collection._mark_modified()

    def get_bounding_box(self) -> BoundingBox:
        """Get footprint bounding box including courtyard."""
        return calculate_footprint_bbox(self._data)

    def check_collision(self, other: 'Footprint') -> bool:
        """Check if this footprint collides with another."""
        return check_courtyard_collision(
            self.get_bounding_box(),
            other.get_bounding_box()
        )
```

#### Pattern 3: Manager Classes for Complex Operations

**File:** `core/managers/wire.py`

**Key Features:**
- Separation of concerns (routing logic separate from data model)
- Stateful managers with configuration
- Complex algorithms isolated in manager classes

**Architecture:**
```python
class WireManager:
    """Manages wire routing operations."""

    def __init__(self, schematic):
        self.schematic = schematic
        self.config = schematic.config

    def route_manhattan(self, start: Point, end: Point,
                       clearance: float = 0.0) -> List[Wire]:
        """Route wires using Manhattan algorithm."""
        # Complex routing logic here
        pass

    def add_wire_between_pins(self, comp1_ref: str, pin1: str,
                             comp2_ref: str, pin2: str) -> List[str]:
        """High-level pin-to-pin routing."""
        # Get pin positions
        # Calculate route
        # Create wires
        # Return wire UUIDs
        pass
```

**Direct Application to PCB:**
```python
class TrackManager:
    """Manages track routing operations."""

    def __init__(self, pcb: 'PCBBoard'):
        self.pcb = pcb
        self.config = pcb.config
        self.obstacle_map = None

    def route_manhattan(self, from_pad: Pad, to_pad: Pad,
                       width: float = 0.25,
                       clearance: float = 0.2,
                       preferred_layer: str = 'F.Cu') -> List[Track]:
        """Route tracks between pads using Manhattan algorithm."""
        # Build obstacle map
        self._build_obstacle_map(clearance)

        # A* pathfinding on grid
        path = self._find_path(from_pad.position, to_pad.position,
                              preferred_layer)

        # Convert path to track segments
        return self._path_to_tracks(path, width, preferred_layer)

    def _build_obstacle_map(self, clearance: float):
        """Build spatial index of obstacles."""
        self.obstacle_map = SpatialIndex()
        # Add footprint courtyards
        for fp in self.pcb.footprints:
            bbox = fp.get_bounding_box().expand(clearance)
            self.obstacle_map.insert(bbox)
        # Add existing tracks
        for track in self.pcb.tracks:
            bbox = track.get_bounding_box().expand(clearance)
            self.obstacle_map.insert(bbox)
```

#### Pattern 4: Parser/Formatter Separation

**Files:** `core/parser.py`, `core/formatter.py`

**Key Features:**
- Parser converts S-expressions → Python objects
- Formatter converts Python objects → S-expressions
- Format preservation through careful handling
- Parser registry for extensibility

**Architecture:**
```python
# Parser
class SchematicParser:
    def __init__(self):
        self.parsers = ParserRegistry()

    def parse_file(self, filepath: Path) -> Schematic:
        sexp = sexpdata.loads(filepath.read_text())
        return self._parse_schematic(sexp)

    def _parse_schematic(self, sexp) -> Schematic:
        # Parse header, metadata
        # Dispatch to element parsers
        for element in sexp:
            parser = self.parsers.get_parser(element[0])
            parser.parse(element)

# Formatter
class SchematicFormatter:
    def format_schematic(self, sch: Schematic) -> str:
        sexp = self._schematic_to_sexp(sch)
        return self._format_sexp(sexp)

    def _format_sexp(self, sexp) -> str:
        # Exact format preservation
        # Proper indentation
        # Symbol handling
        pass
```

**Direct Application to PCB:**
Same pattern, PCBParser and PCBFormatter classes.

#### Pattern 5: Library Caching System

**File:** `library/cache.py`

**Key Features:**
- Lazy loading of library symbols
- In-memory cache with LRU eviction
- Fast search by name, description, tags
- Library path scanning

**Direct Application to PCB:**
```python
class FootprintCache:
    """Global footprint library cache."""

    def __init__(self):
        self._cache: Dict[str, FootprintData] = {}
        self._search_index: SearchIndex = SearchIndex()
        self._library_paths: List[Path] = []

    def get_footprint(self, lib_id: str) -> Optional[FootprintData]:
        """Get footprint by library ID (e.g., 'Resistor_SMD:R_0603')."""
        if lib_id in self._cache:
            return self._cache[lib_id]

        # Load from library
        fp_data = self._load_from_library(lib_id)
        if fp_data:
            self._cache[lib_id] = fp_data
        return fp_data

    def search_footprints(self, query: str,
                         filters: Optional[Dict] = None) -> List[FootprintInfo]:
        """Search footprints by name, description, tags."""
        return self._search_index.search(query, filters)
```

### 1.3 Testing Strategy

**Format Preservation Tests:**
- Reference KiCAD projects manually created in KiCAD
- Round-trip testing (load → modify → save → compare)
- Byte-level diff validation where possible
- Located in `tests/reference_tests/`

**Pattern to Adopt:**
1. Create reference PCB manually in KiCAD
2. Load with kicad-pcb-api
3. Modify programmatically
4. Save and reload in KiCAD
5. Validate no corruption or format deviation

---

## 2. PyKiCad: PCB-Specific Patterns

### 2.1 Project Structure

```
pykicad/
├── pykicad/
│   ├── sexpr.py          # S-expression framework
│   ├── pcb.py            # PCB classes (Segment, Via, Zone, etc.)
│   ├── module.py         # Footprint/Module classes
│   └── __init__.py
├── tests/
│   ├── test_pcb.py
│   ├── test_module.py
│   └── test_sexpr.py
└── setup.py
```

**Observation:** Very flat structure, minimal abstraction. Good for understanding PCB elements, but lacks the sophisticated architecture of kicad-sch-api.

### 2.2 Key Design Patterns

#### Pattern 1: AST-Based S-Expression Mapping

**File:** `sexpr.py` + `pcb.py`

**Key Features:**
- Base `AST` class for all S-expression elements
- Declarative schema definition
- Automatic parsing and formatting
- Type coercion (number, text, integer, boolean, flag)

**Architecture:**
```python
class AST:
    """Base class for S-expression elements."""
    tag = None
    schema = {}

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def parse(cls, sexp):
        """Parse S-expression into AST."""
        # Schema-driven parsing
        pass

    def to_sexp(self):
        """Convert AST to S-expression."""
        # Schema-driven formatting
        pass

# Example: Track segment
class Segment(AST):
    tag = 'segment'
    schema = {
        'start': number + number,
        'end': number + number,
        'width': number,
        'layer': text,
        'net': integer,
        'tstamp': hex,
    }

    def __init__(self, start, end, net, width=None,
                 layer='F.Cu', tstamp=None):
        super().__init__(start=start, end=end, width=width,
                        layer=layer, net=net, tstamp=tstamp)
```

**Evaluation:**
- ✅ Simple and declarative
- ✅ Type safety through schema
- ❌ No collections or advanced indexing
- ❌ No validation or error handling
- ❌ Minimal abstraction beyond S-expression mapping

**Adaptation for kicad-pcb-api:**
- Use dataclasses instead of AST for cleaner syntax
- Keep schema concept for validation
- Add collections layer on top

#### Pattern 2: PCB Element Classes

**File:** `pcb.py`

**Observations:**
```python
# Graphics primitives
class GrLine(AST): ...
class GrArc(AST): ...
class GrCircle(AST): ...
class GrPolygon(AST): ...
class GrCurve(AST): ...

# Board elements
class Segment(AST): ...  # Track segment
class Via(AST): ...
class Zone(AST): ...

# Footprint elements (in module.py)
class Pad(AST): ...
class FpLine(AST): ...
class FpArc(AST): ...
class FpCircle(AST): ...
```

**Key Insight:** Clear separation between:
- Board-level elements (gr_*, segment, via, zone)
- Footprint-level elements (fp_*, pad)

**Direct Application:**
Our `types.py` should mirror this structure with dataclasses:
```python
# Board-level graphics
@dataclass
class Line:
    start: Point
    end: Point
    layer: str
    width: float
    uuid: str

# Footprint-level graphics (same structure, different context)
@dataclass
class FpLine:
    start: Point  # Relative to footprint origin
    end: Point
    layer: str
    width: float
```

### 2.3 PCB-Specific Elements

**Via Types:**
```python
class Via(AST):
    schema = {
        'micro': flag('micro'),
        'blind': flag('blind'),
        'at': number + number,
        'size': number,
        'drill': number,
        'layers': text + text,
        'net': integer,
    }
```

**Zone (Copper Pour):**
```python
class Zone(AST):
    schema = {
        'net': integer,
        'net_name': text,
        'layer': text,
        'tstamp': hex,
        'hatch': ...,
        'connect_pads': ...,
        'min_thickness': number,
        'fill': {...},  # Complex fill parameters
        'polygon': {...},  # Zone boundary
    }
```

**Learning:** Zones are complex with fill rules, thermal relief, priority. Need dedicated `ZoneManager` class.

---

## 3. kicad-skip: S-Expression Abstraction Layer

### 3.1 Architecture

**Key Concept:** Thin abstraction over S-expressions with named attribute access.

```python
# Access S-expression elements as attributes
pcb.footprint.D1  # Access footprint by reference
pcb.layers.B_Cu   # Access layer by name
pcb.net.GND       # Access net by name

# Element manipulation
pcb.footprint.D1.move(new_position)
pcb.segment[42].layer = 'F.Cu'
```

**Evaluation:**
- ✅ Very flexible, works with any S-expression
- ✅ Minimal code, easy to understand
- ❌ Limited type safety
- ❌ No validation
- ❌ Performance issues with large boards (no indexing)

**Not Recommended for kicad-pcb-api:** Too minimal, lacks structure we need.

---

## 4. Architectural Recommendations for kicad-pcb-api

### 4.1 Adopt from kicad-sch-api (Primary Reference)

1. **IndexedCollection System**
   - `FootprintCollection` with reference and net indexing
   - `TrackCollection` with net and layer indexing
   - `ViaCollection` with layer pair indexing
   - `ZoneCollection` with net and layer indexing

2. **Enhanced Wrapper Classes**
   - `Footprint` wrapper with validation and parent tracking
   - `Track` wrapper with routing helpers
   - `Via` wrapper with layer management
   - `Zone` wrapper with fill operations

3. **Manager Classes**
   - `TrackManager` for routing algorithms
   - `PlacementManager` for component placement
   - `ZoneManager` for copper pour management
   - `ValidationManager` for DRC

4. **Parser/Formatter Architecture**
   - `PCBParser` with element parser registry
   - `PCBFormatter` with exact format preservation
   - Element parsers in `parsers/elements/`

5. **Library System**
   - `FootprintCache` with search indexing
   - Lazy loading from KiCAD libraries
   - LRU cache eviction

6. **Testing Strategy**
   - Reference PCB projects in `tests/reference_pcbs/`
   - Round-trip format preservation tests
   - Byte-level diff validation

### 4.2 Adapt from PyKiCad (PCB-Specific Patterns)

1. **PCB Element Definitions**
   - Use PyKiCad's element catalog as reference
   - Convert AST classes to dataclasses
   - Add validation on top

2. **Schema-Driven Validation**
   - Define schemas for each element type
   - Validate on creation and modification
   - Type coercion for numbers, booleans, flags

3. **Via and Zone Modeling**
   - Support micro, blind, buried vias
   - Complex zone fill parameters
   - Thermal relief configuration

### 4.3 Avoid from kicad-skip

- Avoid minimal abstraction approach
- Need stronger typing and validation
- Need indexing for performance

### 4.4 Proposed Architecture

```
kicad-pcb-api/
├── python/
│   ├── kicad_pcb_api/
│   │   ├── core/                           # Core PCB functionality
│   │   │   ├── pcb_board.py                # Main PCBBoard class
│   │   │   ├── parser.py                   # PCB file parser
│   │   │   ├── formatter.py                # PCB file formatter
│   │   │   ├── types.py                    # Data types
│   │   │   ├── geometry.py                 # Geometric calculations
│   │   │   ├── footprint_bounds.py         # Bounding box calculations
│   │   │   └── managers/                   # Specialized managers
│   │   │       ├── track.py                # Track routing
│   │   │       ├── placement.py            # Component placement
│   │   │       ├── zone.py                 # Zone management
│   │   │       ├── graphics.py             # Graphics management
│   │   │       ├── validation.py           # DRC and validation
│   │   │       └── format_sync.py          # Format preservation
│   │   ├── collections/                    # Collection classes
│   │   │   ├── base.py                     # IndexedCollection
│   │   │   ├── footprints.py               # FootprintCollection
│   │   │   ├── tracks.py                   # TrackCollection
│   │   │   ├── vias.py                     # ViaCollection
│   │   │   └── zones.py                    # ZoneCollection
│   │   ├── geometry/                       # Geometric operations
│   │   │   ├── footprint_bbox.py           # Footprint bounding boxes
│   │   │   ├── collision.py                # Collision detection
│   │   │   └── spatial_index.py            # Spatial indexing (rtree)
│   │   ├── footprints/                     # Footprint library
│   │   │   ├── cache.py                    # Footprint caching
│   │   │   ├── resolver.py                 # Library resolution
│   │   │   └── validators.py               # Footprint validation
│   │   ├── routing/                        # Routing algorithms
│   │   │   ├── manhattan.py                # Manhattan routing
│   │   │   ├── astar.py                    # A* pathfinding
│   │   │   ├── freerouting.py              # Freerouting integration
│   │   │   └── optimizer.py                # Route optimization
│   │   ├── placement/                      # Placement algorithms
│   │   │   ├── hierarchical.py             # Hierarchical placement
│   │   │   ├── force_directed.py           # Force-directed placement
│   │   │   ├── spiral.py                   # Spiral placement
│   │   │   └── optimizer.py                # Placement optimization
│   │   ├── parsers/                        # Element parsers
│   │   │   ├── base.py                     # Base parser
│   │   │   ├── registry.py                 # Parser registry
│   │   │   └── elements/                   # Element parsers
│   │   │       ├── footprint_parser.py
│   │   │       ├── track_parser.py
│   │   │       ├── via_parser.py
│   │   │       ├── zone_parser.py
│   │   │       └── graphics_parser.py
│   │   ├── drc/                            # Design rule checking
│   │   │   ├── rules.py                    # Rule definitions
│   │   │   ├── checker.py                  # DRC engine
│   │   │   └── reporter.py                 # Violation reporting
│   │   ├── manufacturing/                  # Manufacturing outputs
│   │   │   ├── gerber.py                   # Gerber generation
│   │   │   ├── drill.py                    # Drill file generation
│   │   │   ├── bom.py                      # BOM generation
│   │   │   └── position.py                 # Pick-and-place
│   │   ├── interfaces/                     # Abstract interfaces
│   │   │   ├── parser.py
│   │   │   ├── formatter.py
│   │   │   └── collection.py
│   │   └── utils/                          # Utilities
│   │       ├── validation.py
│   │       └── kicad_cli.py
│   ├── examples/                           # Usage examples
│   ├── tests/                              # Test suite
│   │   ├── reference_pcbs/                 # Reference PCB projects
│   │   ├── test_collections.py
│   │   ├── test_routing.py
│   │   ├── test_placement.py
│   │   └── test_format_preservation.py
│   └── .memory_bank/                       # Development context
└── reference-implementations/              # Reference projects
    ├── kicad-sch-api/
    ├── pykicad/
    └── kicad-skip/
```

---

## 5. Implementation Priorities

### Phase 1: Core Foundation (Weeks 1-6)

**Goal:** Match kicad-sch-api's collection architecture

**Tasks:**
1. Create `IndexedCollection` base class from kicad-sch-api pattern
2. Implement `FootprintCollection` with reference/net indexing
3. Implement `TrackCollection` with net/layer indexing
4. Enhance `PCBParser` with parser registry
5. Implement format preservation testing

**Deliverables:**
- `collections/base.py` - IndexedCollection
- `collections/footprints.py` - FootprintCollection
- `collections/tracks.py` - TrackCollection
- `tests/test_collections.py` - Collection tests
- `tests/test_format_preservation.py` - Round-trip tests

### Phase 2: Enhanced Wrappers (Weeks 7-10)

**Goal:** Modern API with validation

**Tasks:**
1. Create `Footprint` wrapper class
2. Add bounding box calculations
3. Implement collision detection
4. Add property validation

**Deliverables:**
- `core/footprint.py` - Enhanced Footprint wrapper
- `geometry/footprint_bbox.py` - Bounding box calculations
- `geometry/collision.py` - Collision detection

### Phase 3: Routing System (Weeks 11-15)

**Goal:** Manhattan routing like kicad-sch-api's wire routing

**Tasks:**
1. Implement `TrackManager` class
2. Create A* pathfinding on grid
3. Implement obstacle map generation
4. Add via insertion for multi-layer

**Deliverables:**
- `core/managers/track.py` - TrackManager
- `routing/manhattan.py` - Manhattan routing
- `routing/astar.py` - A* pathfinding
- `tests/test_routing.py` - Routing tests

---

## 6. Key Architectural Decisions

### Decision 1: Use kicad-sch-api as Primary Reference

**Rationale:**
- Proven architecture with excellent UX
- Same file format family (S-expressions)
- Active development and maintenance
- Professional quality testing

**Alternative Considered:** Use PyKiCad patterns
**Rejected Because:** Too minimal, lacks collections and validation

### Decision 2: IndexedCollection for All Major Element Types

**Rationale:**
- O(1) lookups by UUID
- Additional indexes (reference, net, layer) for fast queries
- Lazy index rebuilding for performance
- Modification tracking for change detection

**Alternative Considered:** Simple lists with linear search
**Rejected Because:** Poor performance with large boards (>1000 components)

### Decision 3: Manager Classes for Complex Algorithms

**Rationale:**
- Separation of concerns (routing logic ≠ data model)
- Testable in isolation
- Swappable algorithms
- Configuration management

**Alternative Considered:** Methods on PCBBoard class
**Rejected Because:** Would create massive god object

### Decision 4: Parser Registry for Extensibility

**Rationale:**
- Easy to add new element types
- Clear separation of parsing logic
- Testable parsers in isolation

**Alternative Considered:** Monolithic parser
**Rejected Because:** Hard to maintain and extend

### Decision 5: Wrapper Classes for Enhanced UX

**Rationale:**
- Validation on property setters
- Parent collection updates
- Calculated properties (bounding boxes)
- Pythonic API

**Alternative Considered:** Direct dataclass manipulation
**Rejected Because:** No validation, no index updates

---

## 7. Code Examples: Before vs. After

### Example 1: Adding Footprints

**Current (Minimal API):**
```python
pcb = PCBBoard()
footprint = pcb.add_footprint('R1', 'Resistor_SMD:R_0603', 10, 20)
footprint.value = '10k'
```

**Proposed (Enhanced API):**
```python
pcb = PCBBoard()

# Using collection
footprint = pcb.footprints.add(
    lib_id='Resistor_SMD:R_0603',
    reference='R1',
    position=(10, 20),
    value='10k',
    rotation=90
)

# Search and filter
resistors = pcb.footprints.filter(lib_id='Device:R')
smd_components = pcb.footprints.find(lambda fp: fp.attr == 'smd')

# Bulk operations
pcb.footprints.bulk_update(
    criteria={'lib_id': 'Device:R'},
    updates={'properties': {'Tolerance': '1%'}}
)
```

### Example 2: Routing Tracks

**Current (Manual):**
```python
track = pcb.add_track(10, 20, 30, 40, width=0.25, layer='F.Cu')
```

**Proposed (Manhattan Routing):**
```python
# High-level routing
tracks = pcb.tracks.route_between_pads(
    from_footprint='R1',
    from_pad='1',
    to_footprint='C1',
    to_pad='1',
    width=0.25,
    algorithm='manhattan',
    clearance=0.2
)

# Low-level control
track_manager = TrackManager(pcb)
tracks = track_manager.route_manhattan(
    start=Point(10, 20),
    end=Point(30, 40),
    width=0.25,
    layer='F.Cu',
    avoid_obstacles=True,
    clearance=0.2
)
```

### Example 3: Collision Detection

**Current (Not Available):**
```python
# N/A
```

**Proposed:**
```python
# Check single footprint collision
fp1 = pcb.footprints.get_by_reference('R1')
fp2 = pcb.footprints.get_by_reference('R2')

if fp1.check_collision(fp2):
    print(f"Collision detected between {fp1.reference} and {fp2.reference}")

# Check all collisions
collisions = pcb.footprints.find_collisions(clearance=0.5)
for fp1, fp2 in collisions:
    print(f"Collision: {fp1.reference} <-> {fp2.reference}")

# Bounding boxes
bbox = fp1.get_bounding_box(include_courtyard=True)
print(f"Footprint bounds: {bbox.width}mm x {bbox.height}mm")
```

---

## 8. Testing Approach

### Format Preservation (Critical)

Following kicad-sch-api pattern:

1. **Create Reference PCBs:**
   ```
   tests/reference_pcbs/
   ├── simple_resistor/
   │   ├── simple_resistor.kicad_pcb
   │   └── simple_resistor.kicad_pro
   ├── two_resistors_routed/
   │   ├── two_resistors_routed.kicad_pcb
   │   └── two_resistors_routed.kicad_pro
   └── zone_example/
       ├── zone_example.kicad_pcb
       └── zone_example.kicad_pro
   ```

2. **Round-Trip Tests:**
   ```python
   def test_format_preservation_simple_resistor():
       # Load reference PCB
       original = Path('tests/reference_pcbs/simple_resistor/simple_resistor.kicad_pcb')
       pcb = PCBBoard(original)

       # Make no changes
       pcb.save('tests/output/simple_resistor.kicad_pcb')

       # Compare byte-by-byte (or with tolerance for floats)
       assert files_match(original, 'tests/output/simple_resistor.kicad_pcb')
   ```

3. **Modification Tests:**
   ```python
   def test_format_preservation_after_modification():
       pcb = PCBBoard('tests/reference_pcbs/simple_resistor/simple_resistor.kicad_pcb')

       # Modify
       pcb.footprints.get_by_reference('R1').value = '20k'
       pcb.save('tests/output/modified.kicad_pcb')

       # Reload in KiCAD and verify no corruption
       # Manual verification step
   ```

---

## 9. Conclusion

### Key Takeaways

1. **kicad-sch-api provides the blueprint** for our architecture
   - IndexedCollection system
   - Enhanced wrapper classes
   - Manager classes for complex operations
   - Parser/formatter separation
   - Comprehensive testing strategy

2. **PyKiCad provides PCB-specific insights**
   - Element catalog (Segment, Via, Zone, etc.)
   - Schema-driven parsing
   - Via types and zone fill complexity

3. **kicad-skip is too minimal** for our needs
   - Lacks structure and validation
   - No indexing or performance optimization

### Next Steps

1. **Implement IndexedCollection** base class (Week 1)
2. **Create FootprintCollection** with indexing (Week 2)
3. **Enhance PCBParser** with registry (Week 3)
4. **Set up format preservation tests** (Week 4)
5. **Implement FootprintCollection search** (Week 5)
6. **Create TrackCollection** (Week 6)

### Success Criteria

- ✅ All reference PCBs pass round-trip tests
- ✅ O(1) lookups for footprints by reference
- ✅ Manhattan routing produces valid, collision-free tracks
- ✅ API matches kicad-sch-api quality and patterns
- ✅ Comprehensive test coverage (>85%)

---

**End of Architecture Analysis**
