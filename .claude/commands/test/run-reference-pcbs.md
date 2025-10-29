---
name: run-reference-pcbs
description: Quick reference PCB validation tests
---

# Reference PCB Tests Command - kicad-pcb-api

## Usage
```bash
/run-reference-pcbs [options]
```

## Description
Runs comprehensive tests against reference KiCAD PCB files to validate parsing, manipulation, and format preservation across all PCB element types.

## Parameters
- `--format-validation`: Focus on format preservation testing
- `--performance`: Include performance benchmarking
- `--verbose`: Show detailed test output

## Implementation

```bash
#!/bin/bash

# Parse arguments
FORMAT_VALIDATION=false
PERFORMANCE=false
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --format-validation)
            FORMAT_VALIDATION=true
            shift
            ;;
        --performance)
            PERFORMANCE=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Ensure we're in project root
cd /Users/shanemattner/Desktop/kicad-pcb-api || {
    echo "❌ Must run from kicad-pcb-api root"
    exit 1
}

echo "🧪 Testing reference PCB projects..."

# Build pytest arguments
PYTEST_ARGS="-v"
[[ "$VERBOSE" == "true" ]] && PYTEST_ARGS="$PYTEST_ARGS -s"

# Run tests based on options
if [[ "$FORMAT_VALIDATION" == "true" ]]; then
    echo "📋 Running format preservation tests..."
    uv run pytest src/tests/test_reference_exact_format.py $PYTEST_ARGS
elif [[ "$PERFORMANCE" == "true" ]]; then
    echo "⚡ Running performance benchmarks..."
    uv run pytest src/tests/test_reference_pcbs.py $PYTEST_ARGS -k "performance"
else
    echo "🏗️ Running all reference PCB tests..."
    uv run pytest src/tests/test_reference_pcbs.py src/tests/test_reference_exact_format.py $PYTEST_ARGS
fi
```

## Test Categories

### Format Preservation Tests
Validates that loading and saving PCB files produces byte-perfect output:
```bash
/run-reference-pcbs --format-validation
```

Tests:
- Round-trip format preservation
- Whitespace and indentation preservation
- Element ordering preservation
- String quoting consistency

### Performance Benchmarks
Measures performance characteristics:
```bash
/run-reference-pcbs --performance
```

Benchmarks:
- PCB parsing time
- Footprint collection operations
- Track/via modifications
- Zone fill updates

### Full Validation
Runs all reference PCB tests:
```bash
/run-reference-pcbs
```

Coverage:
- Basic PCB parsing
- Footprint management
- Track and via routing
- Zone fills and polygons
- Graphics and text elements
- Format preservation
- Performance validation

## Reference PCB Test Files

Located in `src/tests/fixtures/`:
- **Simple boards**: Basic footprints and tracks
- **Complex routing**: Multiple layers, vias, zones
- **Mixed elements**: Graphics, text, dimensions
- **Edge cases**: Special formatting, unusual elements

## Expected Coverage

### Footprint Operations
- Add, remove, modify footprints
- Property updates
- Position and rotation changes
- Reference and value updates

### Routing Operations
- Track creation and modification
- Via placement and sizing
- Zone fills and keepouts
- Net assignments

### Graphics Elements
- Lines, arcs, circles
- Text annotations
- Dimension markers
- Custom graphics

### Format Preservation
- Exact byte-level match for unchanged elements
- Proper formatting for modified elements
- Correct ordering preservation
- String quoting compliance

## Usage Examples

```bash
# Quick validation (default)
/run-reference-pcbs

# Format preservation focus
/run-reference-pcbs --format-validation

# Performance analysis
/run-reference-pcbs --performance

# Detailed output
/run-reference-pcbs --verbose

# Combined options
/run-reference-pcbs --format-validation --verbose
```

## Quality Metrics

### Performance Targets
- **Parsing time**: <100ms for typical PCBs
- **Memory usage**: <50MB for complex PCBs
- **Collection lookups**: <1ms for indexed access
- **Bulk operations**: <10ms per 100 operations

### Accuracy Targets
- **Format preservation**: 100% byte-level accuracy for unchanged elements
- **Round-trip fidelity**: 100% data preservation
- **Validation coverage**: All PCB rules validated
- **Error detection**: All format violations caught

## CI/CD Integration

```yaml
# GitHub Actions integration
- name: Reference PCB Tests
  run: /run-reference-pcbs --format-validation

- name: Performance Benchmarks
  run: /run-reference-pcbs --performance
```

## Troubleshooting

**If reference tests fail**:
1. Check that reference PCB files are valid KiCAD format
2. Verify kicad-pcb-api installation: `uv run python -c "import kicad_pcb_api"`
3. Run with verbose output: `/run-reference-pcbs --verbose`
4. Check test logs for specific parsing errors

**If format preservation fails**:
1. Enable debug logging to see parsing details
2. Compare original vs. output files manually
3. Check for whitespace or encoding differences
4. Validate S-expression structure integrity

This command ensures all reference PCBs work correctly with kicad-pcb-api and maintain professional quality standards.
