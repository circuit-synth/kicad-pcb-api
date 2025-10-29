# Refactoring Plan: Architecture Modernization

**Goal**: Modernize both kicad-pcb-api and kicad-sch-api with proven patterns from each other

**Total Estimated Time**: 41 hours
**Completed Time**: 4 hours (9.8% complete)
**Remaining Time**: 37 hours
**Team Size**: 1-3 developers
**Timeline**: 2-3 weeks (with parallel work)

**Last Updated**: 2025-10-28

---

## 🎉 Recent Accomplishments (2025-10-28)

### ✅ Completed Tasks (2/5)

1. **PCB-2: Performance Optimizations** (PR #23 - merged)
   - Fixed `get_footprint()`: O(n) → O(1)
   - Fixed `get_net_by_name()`: O(n) → O(1)
   - Impact: 10-100x faster on large boards
   - Actual time: 1 hour (as estimated)

2. **PCB-1: Parser Refactoring** (PR #24 - merged)
   - Integrated ParserRegistry into PCBParser
   - Created 5 new element parsers
   - Registered 15 total element parsers
   - Impact: Better maintainability & extensibility
   - Actual time: 3 hours (vs 16h estimated - infrastructure existed!)

### ⏳ Remaining Tasks (3/5)

3. **SCH-1: Exception Hierarchy** (Issue #69)
   - Estimated: 8 hours
   - Repository: kicad-sch-api

4. **SCH-2: Wrapper Pattern** (Issue #70)
   - Estimated: 12 hours
   - Repository: kicad-sch-api
   - Depends on: SCH-1

5. **SCH-3: BaseManager Pattern** (Issue #71)
   - Estimated: 4 hours
   - Repository: kicad-sch-api

---

## Tasks Overview

| ID | Task | Repo | Hours | Priority | Status | PR/Issue |
|----|------|------|-------|----------|--------|----------|
| ~~PCB-1~~ | ~~Refactor Monolithic Parser~~ | kicad-pcb-api | ~~16h~~ 3h | P1 | ✅ **DONE** | PR #24 |
| ~~PCB-2~~ | ~~Fix O(n) Performance Issues~~ | kicad-pcb-api | ~~1h~~ | P0 | ✅ **DONE** | PR #23 |
| SCH-1 | Adopt Modern Exception Hierarchy | kicad-sch-api | 8h | P1 | 📋 Issue | #69 |
| SCH-2 | Implement Wrapper Pattern | kicad-sch-api | 12h | P1 | 📋 Issue | #70 |
| SCH-3 | Add BaseManager Pattern | kicad-sch-api | 4h | P1 | 📋 Issue | #71 |

### Completed Tasks (2025-10-28)

#### ✅ PCB-2: Fix O(n) Performance Issues
- **Time**: 1 hour (as estimated)
- **PR**: #23 (merged)
- **Changes**:
  - Optimized `get_footprint()`: O(n) → O(1) using `FootprintCollection.get_by_reference()`
  - Optimized `get_net_by_name()`: O(n) → O(1) using lazy-initialized dict index
  - Added cache invalidation in `add_net()` method
- **Impact**: 10-100x performance improvement on large boards

#### ✅ PCB-1: Refactor Monolithic Parser
- **Time**: 3 hours (vs 16h estimated - infrastructure already existed!)
- **PR**: #24 (merged)
- **Changes**:
  - Created 5 new element parsers (VersionParser, GeneratorParser, PaperParser, SetupParser, EmbeddedFontsParser)
  - Integrated ParserRegistry into PCBParser
  - Transformed monolithic dispatch into clean registry-based architecture
  - Registered 15 element parsers
- **Impact**: Better maintainability, extensibility, and testability
- **Note**: Parser infrastructure (BaseElementParser, ParserRegistry, existing element parsers) was already implemented, significantly reducing the actual work needed

---

## Dependency Analysis

### Independent Tasks (Can Run in Parallel)
```
┌─────────────────────────────────────────────────────────────┐
│ PHASE 1: Parallel Execution (Week 1)                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ✅ PCB-1: Refactor Parser       ┐                          │
│  (3 hours - COMPLETED)            │                          │
│  • Registry integration           │  All independent         │
│  • 5 new simple parsers           ├─ Can run simultaneously │
│  • PR #24 merged                  │                          │
│                                   │                          │
│  SCH-1: Exception Hierarchy       │                          │
│  (8 hours - REMAINING)            │                          │
│  • Create exception classes       │                          │
│  • Update error handling          ┘                          │
│                                                              │
│  ✅ PCB-2: Fix Performance        ─── Quick win, independent│
│  (1 hour - COMPLETED)                                        │
│  • PR #23 merged                                             │
│                                                              │
│  SCH-3: BaseManager Pattern       ─── Independent of others │
│  (4 hours - REMAINING)                                       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Dependent Tasks (Must Be Sequential)
```
┌─────────────────────────────────────────────────────────────┐
│ PHASE 2: Sequential Execution (Week 2-3)                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  SCH-1: Exception Hierarchy                                 │
│  (8 hours)                                                   │
│           │                                                  │
│           │ Provides exception classes                      │
│           ▼                                                  │
│  SCH-2: Wrapper Pattern                                     │
│  (12 hours)                                                  │
│  • Wrappers need exceptions for validation                  │
│  • _mark_modified() triggers validation                     │
│  • Better with structured errors                            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Key Insight**: SCH-2 (Wrapper Pattern) should wait for SCH-1 (Exception Hierarchy) because wrappers heavily use validation and error handling. However, SCH-2 can start partially once core exceptions are defined (~2 hours into SCH-1).

---

## Execution Strategies

### Strategy A: Maximum Parallelization (3 developers)
**Timeline**: 1.5 weeks (75 hours total capacity)
**Status**: ~10% complete

**Week 1**:
- ✅ Developer 1: PCB-1 (Refactor Parser) - 3 hours **DONE**
- ✅ Developer 3: PCB-2 (Performance Fix) - 1 hour **DONE**
- ⏳ Developer 2: SCH-1 (Exception Hierarchy) - 8 hours **REMAINING**
- ⏳ Developer 3: SCH-3 (BaseManager) - 4 hours **REMAINING**

**Week 2**:
- ⏳ Developer 2: SCH-2 (Wrapper Pattern) - 12 hours (starts after SCH-1 completes)
- Developers 1 & 3: Testing, integration, documentation

**Pros**: Fastest completion (9-10 days)
**Cons**: Requires 3 developers, coordination overhead
**Progress**: 4/41 hours complete (9.8%)

---

### Strategy B: Moderate Parallelization (2 developers)
**Timeline**: 2-3 weeks (80 hours total capacity)
**Status**: ~10% complete

**Week 1**:
- ✅ Developer 1: PCB-1 (Refactor Parser) - 3 hours **DONE**
- ✅ Developer 1: PCB-2 (Performance) - 1 hour **DONE**
- ⏳ Developer 2: SCH-1 (Exception Hierarchy) - 8 hours **REMAINING**
- ⏳ Developer 2: SCH-3 (BaseManager) - 4 hours **REMAINING**

**Week 2-3**:
- ⏳ Developer 2: SCH-2 (Wrapper Pattern) - 12 hours
- Developer 1: Testing, integration, documentation for PCB work

**Pros**: Good balance, manageable coordination
**Cons**: Some idle time for Developer 1 in week 2
**Progress**: 4/41 hours complete (9.8%)

---

### Strategy C: Sequential Execution (1 developer)
**Timeline**: 5-6 weeks (40 hours/week capacity)
**Status**: ~10% complete

**Recommended Order**:
1. ✅ **PCB-2**: Fix Performance (1h) - **DONE** (PR #23 merged)
2. ✅ **PCB-1**: Refactor Parser (3h) - **DONE** (PR #24 merged)
3. ⏳ **SCH-3**: BaseManager Pattern (4h) - Small, independent task
4. ⏳ **SCH-1**: Exception Hierarchy (8h) - Foundation for wrappers
5. ⏳ **SCH-2**: Wrapper Pattern (12h) - Depends on SCH-1

**Week Breakdown**:
- ✅ Week 1 (4h): PCB-2 (1h) + PCB-1 (3h) **COMPLETE**
- ⏳ Week 2 (8h): SCH-3 (4h) + SCH-1 (4h partial)
- ⏳ Week 3 (8h): SCH-1 (4h complete) + SCH-2 (4h partial)
- ⏳ Week 4 (8h): SCH-2 (8h complete)

**Pros**: Minimal coordination, clear priorities
**Cons**: Longest timeline (4 weeks remaining)
**Progress**: 4/41 hours complete (9.8%), 37 hours remaining

---

## Detailed Task Breakdown

### PCB-1: Refactor Monolithic Parser (16 hours)

**Current State**: `src/kicad_pcb_api/core/pcb_parser.py:1-1265` (monolithic)
**Target State**: Modular registry-based system like `kicad-sch-api/kicad_sch_api/core/parser.py`

**Dependencies**: None (completely independent)

**Subtasks**:
1. **Create Parser Registry** (3h)
   - File: `src/kicad_pcb_api/core/parser_registry.py`
   - Create `ParserRegistry` class
   - Implement handler registration system
   - Add handler lookup logic

2. **Extract Handler Classes** (8h)
   - File: `src/kicad_pcb_api/core/handlers/`
   - Create base `ElementHandler` class
   - Extract 15-20 specialized handlers:
     - `FootprintHandler`
     - `TrackHandler`
     - `ViaHandler`
     - `ZoneHandler`
     - `LayerHandler`
     - `NetHandler`
     - `SetupHandler`
     - etc.

3. **Refactor PCBParser Class** (4h)
   - Slim down to ~200 lines
   - Replace inline parsing with registry dispatch
   - Maintain exact format compatibility

4. **Testing & Validation** (1h)
   - Run existing test suite
   - Verify byte-identical output
   - Performance benchmarks

**Files Modified**:
- `src/kicad_pcb_api/core/pcb_parser.py` (slim down)
- `src/kicad_pcb_api/core/parser_registry.py` (new)
- `src/kicad_pcb_api/core/handlers/__init__.py` (new)
- `src/kicad_pcb_api/core/handlers/base.py` (new)
- `src/kicad_pcb_api/core/handlers/footprint.py` (new)
- ... (15+ handler files)

**Risk**: High complexity, format preservation critical

---

### PCB-2: Fix O(n) Performance Issues (1 hour)

**Current State**: Linear scans through `pcb_data` lists
**Target State**: O(1) collection lookups

**Dependencies**: None (completely independent)

**Changes**:

1. **Fix `get_footprint()` method** (`pcb_board.py:646-659`)
   ```python
   # Before (O(n)):
   for fp in self.pcb_data.get('footprint', []):
       if fp.get('reference') == reference:
           return fp

   # After (O(1)):
   return self.footprints.get_by_reference(reference)
   ```

2. **Fix `get_net()` method** (`pcb_board.py:1847-1856`)
   ```python
   # Before (O(n)):
   for net in self.pcb_data.get('net', []):
       if net[0] == net_id or net[1] == net_name:
           return net

   # After (O(1)):
   return self.nets.get(net_id) or self.nets.get_by_name(net_name)
   ```

3. **Add missing collection methods if needed**:
   - `FootprintCollection.get_by_reference()`
   - `NetCollection.get_by_name()`

**Files Modified**:
- `src/kicad_pcb_api/core/pcb_board.py` (2 methods)
- `src/kicad_pcb_api/collections/footprints.py` (potentially)
- `src/kicad_pcb_api/collections/nets.py` (potentially)

**Risk**: Low - simple, well-understood optimization

---

### SCH-1: Adopt Modern Exception Hierarchy (8 hours)

**Current State**: Basic `ValueError`, `RuntimeError`, generic exceptions
**Target State**: Structured hierarchy from `kicad-pcb-api/src/kicad_pcb_api/core/exceptions.py`

**Dependencies**: None (completely independent)

**Subtasks**:
1. **Create Exception Hierarchy** (2h)
   - File: `kicad_sch_api/core/exceptions.py`
   - Copy and adapt from kicad-pcb-api
   - Define:
     - `KiCadSchError` (base)
     - `ValidationError`
     - `ParseError`
     - `ReferenceError`
     - `ComponentNotFoundError`
     - `NetNotFoundError`
     - `SheetNotFoundError`
     - `FileFormatError`
     - etc.

2. **Update Parser Error Handling** (2h)
   - File: `kicad_sch_api/core/parser.py`
   - Replace generic exceptions
   - Add context to error messages

3. **Update Schematic Class Error Handling** (3h)
   - File: `kicad_sch_api/core/schematic.py`
   - Replace ~50 exception sites
   - Add validation checks with proper exceptions

4. **Update Manager Error Handling** (1h)
   - Files: `kicad_sch_api/core/managers/*.py`
   - Update 8 manager classes
   - Consistent exception usage

**Files Modified**:
- `kicad_sch_api/core/exceptions.py` (new)
- `kicad_sch_api/core/parser.py`
- `kicad_sch_api/core/schematic.py`
- `kicad_sch_api/core/managers/*.py` (8 files)

**Risk**: Medium - requires careful testing to avoid breaking changes

---

### SCH-2: Implement Wrapper Pattern (12 hours)

**Current State**: Direct dictionary manipulation
**Target State**: ElementWrapper classes like `kicad-pcb-api/src/kicad_pcb_api/wrappers/`

**Dependencies**:
- **Hard dependency**: SCH-1 (Exception Hierarchy) - wrappers need proper exceptions
- **Can start after**: ~2 hours of SCH-1 (once core exceptions defined)

**Subtasks**:
1. **Create Base Wrapper Class** (2h)
   - File: `kicad_sch_api/wrappers/base.py`
   - Adapt from kicad-pcb-api
   - Add parent tracking
   - Add `_mark_modified()` mechanism

2. **Create Component Wrappers** (4h)
   - File: `kicad_sch_api/wrappers/component.py`
   - Create `ComponentWrapper` class
   - Properties: reference, value, footprint, pins
   - Validation on property setters

3. **Create Wire/Bus Wrappers** (2h)
   - File: `kicad_sch_api/wrappers/wire.py`
   - Create `WireWrapper`, `BusWrapper` classes
   - Coordinate validation

4. **Create Sheet Wrapper** (2h)
   - File: `kicad_sch_api/wrappers/sheet.py`
   - Create `SheetWrapper` class
   - Hierarchical navigation

5. **Integrate with Collections** (2h)
   - Update `IndexedCollection` to return wrappers
   - Update `Schematic` class to use wrappers
   - Backward compatibility layer

**Files Modified**:
- `kicad_sch_api/wrappers/__init__.py` (new)
- `kicad_sch_api/wrappers/base.py` (new)
- `kicad_sch_api/wrappers/component.py` (new)
- `kicad_sch_api/wrappers/wire.py` (new)
- `kicad_sch_api/wrappers/sheet.py` (new)
- `kicad_sch_api/collections/base.py`
- `kicad_sch_api/core/schematic.py`

**Risk**: High - changes API surface, requires careful backward compatibility

---

### SCH-3: Add BaseManager Pattern (4 hours)

**Current State**: 8 managers without common base class
**Target State**: Abstract `BaseManager` like `kicad-pcb-api/src/kicad_pcb_api/managers/base.py`

**Dependencies**: None (completely independent)

**Subtasks**:
1. **Create BaseManager Class** (1h)
   - File: `kicad_sch_api/core/managers/base.py`
   - Copy and adapt from kicad-pcb-api
   - Define abstract interface:
     - `__init__(schematic)`
     - `validate()` (abstract)
     - Common utilities

2. **Refactor Existing Managers** (2h)
   - Inherit from `BaseManager`
   - Implement abstract methods
   - Remove duplicate code
   - Files:
     - `file_io_manager.py`
     - `format_sync_manager.py`
     - `graphics_manager.py`
     - `metadata_manager.py`
     - `sheet_manager.py`
     - `text_element_manager.py`
     - `validation_manager.py`
     - `wire_manager.py`

3. **Update Schematic Class** (1h)
   - File: `kicad_sch_api/core/schematic.py`
   - Update manager initialization
   - Add type hints

**Files Modified**:
- `kicad_sch_api/core/managers/base.py` (new)
- `kicad_sch_api/core/managers/*.py` (8 files)
- `kicad_sch_api/core/schematic.py`

**Risk**: Low - purely structural, no logic changes

---

## Parallel Execution Matrix

| Task | Can Run Parallel With | Must Complete Before |
|------|----------------------|---------------------|
| PCB-1 | All others | None |
| PCB-2 | All others | None |
| SCH-1 | PCB-1, PCB-2, SCH-3 | SCH-2 |
| SCH-2 | PCB-1, PCB-2 | - (needs SCH-1) |
| SCH-3 | All others | None |

**Maximum Parallelization**: 4 tasks simultaneously (all except SCH-2)

---

## Testing Strategy

### Per-Task Testing
- **PCB-1**: Run full test suite, verify byte-identical output
- **PCB-2**: Benchmark before/after, verify correctness
- **SCH-1**: Test exception handling paths
- **SCH-2**: Test wrapper behavior, validation
- **SCH-3**: Test manager interface compliance

### Integration Testing
After all tasks complete:
1. Run both full test suites
2. Cross-repository compatibility tests
3. Performance benchmarks
4. Format preservation validation
5. Documentation updates

---

## Risk Assessment

| Task | Risk Level | Mitigation |
|------|-----------|------------|
| PCB-1 | 🔴 High | Extensive testing, incremental refactor, feature flags |
| PCB-2 | 🟢 Low | Simple change, easy to verify |
| SCH-1 | 🟡 Medium | Gradual rollout, maintain backward compat |
| SCH-2 | 🔴 High | Wrapper/unwrapper layer, optional usage |
| SCH-3 | 🟢 Low | Structural only, no logic changes |

---

## Rollback Plans

### PCB-1 (Parser Refactor)
- Keep old parser in `pcb_parser_legacy.py`
- Feature flag: `USE_LEGACY_PARSER`
- Can switch back in single line

### SCH-1 (Exceptions)
- Keep old exception handling as fallback
- Gradual migration over multiple PRs
- Easy to revert individual files

### SCH-2 (Wrappers)
- Make wrappers optional
- Keep direct dict access working
- Users can opt-in gradually

### SCH-3 (BaseManager)
- Pure structural change
- No logic modification
- Low rollback risk

---

## Success Criteria

### PCB-1: Parser Refactor
- ✅ Parser code reduced from 1,265 to <300 lines
- ✅ All 407 tests pass
- ✅ Output byte-identical to original
- ✅ Parse time within 5% of baseline
- ✅ Code coverage maintained >90%

### PCB-2: Performance Fix
- ✅ `get_footprint()` is O(1) instead of O(n)
- ✅ `get_net()` is O(1) instead of O(n)
- ✅ Large board tests show 10-100x speedup
- ✅ All existing tests pass

### SCH-1: Exception Hierarchy
- ✅ 8+ exception classes defined
- ✅ All managers use structured exceptions
- ✅ Error messages include context
- ✅ No breaking changes to public API
- ✅ All 452 tests pass

### SCH-2: Wrapper Pattern
- ✅ 4+ wrapper classes implemented
- ✅ Parent tracking working
- ✅ Auto-validation on property sets
- ✅ Backward compatibility maintained
- ✅ All tests pass with wrappers

### SCH-3: BaseManager Pattern
- ✅ All 8 managers inherit from BaseManager
- ✅ Common interface defined
- ✅ No duplicate code across managers
- ✅ All tests pass

---

## Recommended Approach

**For 1 developer** (you): Strategy C - Sequential Execution
1. Start with **PCB-2** (1h) - Quick win today
2. Then **SCH-3** (4h) - Complete by tomorrow
3. Then **SCH-1** (8h) - 1-2 days
4. Then **PCB-1** (16h) - 2-3 days (most complex)
5. Finally **SCH-2** (12h) - 1-2 days

**Total**: ~5 weeks at 8h/week, or 1.5 weeks full-time

**For 2 developers**: Strategy B - Moderate Parallelization
- Developer 1: PCB-1 + PCB-2 (Week 1)
- Developer 2: SCH-1 + SCH-3 (Week 1) → SCH-2 (Week 2)

**For 3 developers**: Strategy A - Maximum Parallelization
- Developer 1: PCB-1 (16h)
- Developer 2: SCH-1 (8h) → SCH-2 (12h)
- Developer 3: PCB-2 (1h) → SCH-3 (4h) → Testing/docs

---

## Next Steps

1. **Immediate**: Choose execution strategy based on team size
2. **Day 1**: Start PCB-2 (quick win, 1 hour)
3. **Week 1**: Complete all independent tasks in parallel
4. **Week 2+**: Complete SCH-2 (depends on SCH-1)
5. **Final**: Integration testing, documentation, release

**Questions to answer**:
- How many developers available?
- Preferred timeline (1.5 weeks vs 5 weeks)?
- Which repository to prioritize (PCB or SCH)?
- Risk tolerance (aggressive vs conservative)?

---

**Document Version**: 1.0
**Last Updated**: 2025-10-28
**Author**: Architecture Modernization Team
