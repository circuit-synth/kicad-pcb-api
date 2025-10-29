---
name: review-implementation
description: Automated code review checklist for PCB API quality assurance
---

# Review Implementation Command - kicad-pcb-api

## Usage
```bash
/review-implementation [component]
```

## Description
Performs comprehensive code review and analysis of kicad-pcb-api implementation, focusing on professional quality, performance, and API design.

## Parameters
- `component` (optional): Specific component to review (`core`, `collections`, `routing`, `placement`, `utils`, `tests`)
- `--performance`: Focus on performance analysis
- `--api-design`: Focus on API usability review
- `--format-preservation`: Focus on format preservation validation

## Review Areas

### 1. Core Library Review
```bash
/review-implementation core
```

**Focuses on**:
- **S-expression parsing** accuracy and performance
- **PCB board management** API design and efficiency
- **PCB operations** completeness and validation
- **Type system** correctness and usability
- **Error handling** comprehensiveness and clarity

**Key Questions**:
- Does the API feel intuitive and pythonic?
- Are bulk operations efficient for large PCBs?
- Is format preservation truly exact?
- Do validation errors provide actionable feedback?

### 2. Collection Management Review
```bash
/review-implementation collections
```

**Focuses on**:
- **IndexedCollection** base class design and performance
- **Specialized collections** (footprints, tracks, vias, zones)
- **Filtering and search** functionality
- **Bulk operations** efficiency

**Key Questions**:
- Are collection operations O(1) for lookups?
- Do filters provide intuitive query interface?
- Are bulk updates transactional and safe?

### 3. Routing Integration Review
```bash
/review-implementation routing
```

**Focuses on**:
- **DSN export** accuracy and compatibility
- **Freerouting integration** reliability
- **SES import** correctness
- **Error handling** for routing failures

**Key Questions**:
- Does DSN export match Freerouting expectations?
- Is SES import robust against malformed data?
- Are routing errors clearly communicated?

### 4. Placement Algorithms Review
```bash
/review-implementation placement
```

**Focuses on**:
- **Placement algorithms** (hierarchical, spiral, basic)
- **Performance** for large component counts
- **Configuration** flexibility
- **Results quality** and predictability

**Key Questions**:
- Are placement algorithms suitable for real-world use?
- Do algorithms handle edge cases gracefully?
- Is performance acceptable for 100+ components?

### 5. Testing Strategy Review
```bash
/review-implementation tests
```

**Focuses on**:
- **Test coverage** completeness and quality
- **Reference PCBs** representativeness
- **Format preservation** validation accuracy
- **Performance benchmarks** relevance

**Key Questions**:
- Do tests cover all critical functionality?
- Are reference PCBs representative of real-world usage?
- Is format preservation testing comprehensive enough?

## Review Checklist

### API Design Quality
- [ ] **Intuitive naming**: Method and property names are self-explanatory
- [ ] **Consistent patterns**: Similar operations follow same patterns
- [ ] **Type safety**: Proper type hints throughout
- [ ] **Error messages**: Clear, actionable error descriptions
- [ ] **Performance**: O(1) lookups, efficient bulk operations

### Code Quality Standards
- [ ] **Documentation**: All public methods have docstrings
- [ ] **Logging**: Appropriate logging levels and messages
- [ ] **Validation**: Input validation on all public methods
- [ ] **Error handling**: Graceful degradation, no silent failures
- [ ] **Memory efficiency**: No memory leaks, efficient data structures

### Format Preservation
- [ ] **Round-trip accuracy**: load → save → load produces identical results
- [ ] **Whitespace preservation**: Indentation and spacing maintained
- [ ] **Element ordering**: Order of elements preserved
- [ ] **Quote consistency**: String quoting matches KiCAD conventions

### Performance Benchmarks
- [ ] **Component operations**: <100ms for 1000 footprints
- [ ] **File I/O**: <500ms for complex PCBs
- [ ] **Collection lookups**: <1ms for indexed access
- [ ] **Memory usage**: <100MB for large PCBs

### Professional Standards
- [ ] **Code readability**: Self-documenting code
- [ ] **Maintainability**: Clear separation of concerns
- [ ] **Testability**: Easy to unit test and mock
- [ ] **Documentation**: Comprehensive API documentation

## Review Process

### 1. Automated Analysis
```bash
# Code quality metrics
uv run ruff check src/kicad_pcb_api/ --statistics
uv run mypy src/kicad_pcb_api/ --show-error-codes

# Test coverage
uv run pytest src/tests/ --cov=kicad_pcb_api --cov-report=term-missing

# Performance profiling
uv run python -m cProfile -s cumulative src/tests/test_board_integration.py
```

### 2. Manual Review Checklist
- [ ] **API consistency** with established patterns
- [ ] **Documentation completeness** for public methods
- [ ] **Error handling** quality and coverage
- [ ] **Performance characteristics** meet benchmarks
- [ ] **Type annotations** accuracy and completeness

### 3. Integration Validation
- [ ] **Format preservation** validated with real KiCAD files
- [ ] **Routing integration** works correctly with Freerouting
- [ ] **Placement algorithms** produce reasonable results
- [ ] **Bulk operations** perform efficiently

## Professional Standards

### Code Review Standards
- **Readability**: Code should be self-documenting
- **Maintainability**: Clear separation of concerns
- **Testability**: Easy to unit test and mock
- **Performance**: Optimized for real-world usage patterns
- **Documentation**: Comprehensive API documentation

### API Design Standards
- **Intuitive**: Natural mental model for PCB operations
- **Consistent**: Similar operations use similar patterns
- **Powerful**: Supports both simple and complex operations
- **Safe**: Validates inputs and prevents corruption
- **Fast**: Optimized for large PCB workflows

## Review Output

The review generates:
- **Quality metrics** and scores
- **Performance benchmarks** vs. targets
- **API usability** assessment
- **Improvement recommendations** prioritized by impact
- **Comparison analysis** vs. other PCB manipulation solutions

## Component-Specific Focus Areas

### Core (`core/`)
- PCB parser and formatter accuracy
- Type definitions completeness
- PCB board class API design

### Collections (`collections/`)
- IndexedCollection base implementation
- Specialized collection performance
- Filter and query interface

### Routing (`routing/`)
- DSN export correctness
- Freerouting integration reliability
- SES import robustness

### Placement (`placement/`)
- Algorithm correctness and quality
- Performance characteristics
- Configuration flexibility

### Utils (`utils/`)
- Validation comprehensiveness
- KiCAD CLI integration
- Utility function coverage

This ensures kicad-pcb-api maintains professional quality standards while providing superior functionality to existing solutions.
