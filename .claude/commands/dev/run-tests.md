---
name: run-tests
description: Multi-level test orchestration (quick/standard/full/coverage/reference)
---

# Test Runner Command - kicad-pcb-api

## Usage
```bash
/run-tests [options]
```

## Description
Orchestrates comprehensive testing for kicad-pcb-api using uv and pytest, covering all functionality areas with professional test reporting.

## Options
- `--suite=standard` - Test suite: `quick`, `standard`, `full`, `coverage`, `reference-pcbs` (default: standard)
- `--skip-install` - Skip dependency reinstallation (faster for development)
- `--keep-outputs` - Don't delete generated test files
- `--verbose` - Show detailed output
- `--format=true` - Auto-format code before testing (default: true)
- `--fail-fast=false` - Stop on first failure (default: false)

## Test Suites

### 🚀 Quick Suite (~10 seconds)
Fast development testing:
```bash
uv run pytest src/tests/test_collections_base.py src/tests/test_parser.py -q
```

### 📋 Standard Suite - Default (~30 seconds)
Comprehensive core functionality:
```bash
# Auto-format if requested
uv run ruff format src/
uv run ruff check src/ --fix

# Run core tests
uv run pytest src/tests/ -v --tb=short
```

### 🔬 Full Suite (~2 minutes)
Complete validation including reference PCBs:
```bash
# Python library tests
uv run pytest src/tests/ -v --cov=kicad_pcb_api --cov-report=html

# Format preservation tests
uv run pytest src/tests/test_reference_exact_format.py -v

# Reference PCB tests
uv run pytest src/tests/test_reference_pcbs.py -v
```

### 📊 Coverage Suite (~1 minute)
Detailed coverage analysis:
```bash
uv run pytest src/tests/ --cov=kicad_pcb_api --cov-report=term-missing --cov-report=html --cov-fail-under=80
```

### 🏗️ Reference PCB Suite (~30 seconds)
Only reference PCB validation:
```bash
uv run pytest src/tests/test_reference_pcbs.py src/tests/test_reference_exact_format.py -v
```

## Implementation

```bash
#!/bin/bash

# Parse arguments
SUITE="standard"
SKIP_INSTALL=false
KEEP_OUTPUTS=false
VERBOSE=false
FORMAT=true
FAIL_FAST=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --suite=*)
            SUITE="${1#*=}"
            shift
            ;;
        --skip-install)
            SKIP_INSTALL=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --format=*)
            FORMAT="${1#*=}"
            shift
            ;;
        --fail-fast)
            FAIL_FAST=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Ensure we're in project root
cd /Users/shanemattner/Desktop/kicad-pcb-api || { echo "❌ Must run from kicad-pcb-api root"; exit 1; }

# Install dependencies if needed
if [[ "$SKIP_INSTALL" == "false" ]]; then
    echo "📦 Installing dependencies..."
    uv pip install -e .[dev] --quiet
fi

# Pre-test formatting
if [[ "$FORMAT" == "true" ]]; then
    echo "🎨 Auto-formatting code..."
    uv run ruff format src/ --quiet
    uv run ruff check src/ --fix --quiet
    echo "✅ Code formatted"
fi

# Build pytest arguments
PYTEST_ARGS=""
[[ "$VERBOSE" == "true" ]] && PYTEST_ARGS="$PYTEST_ARGS -v"
[[ "$FAIL_FAST" == "true" ]] && PYTEST_ARGS="$PYTEST_ARGS -x"

# Execute test suite
case $SUITE in
    quick)
        echo "🚀 Running quick test suite..."
        uv run pytest src/tests/test_collections_base.py src/tests/test_parser.py -q $PYTEST_ARGS
        ;;

    standard)
        echo "📋 Running standard test suite..."
        uv run pytest src/tests/ --tb=short $PYTEST_ARGS
        ;;

    full)
        echo "🔬 Running full test suite..."

        # Python library tests with coverage
        uv run pytest src/tests/ --cov=kicad_pcb_api --cov-report=term-missing $PYTEST_ARGS || exit 1

        # Reference PCB tests
        if [[ -f "src/tests/test_reference_pcbs.py" ]]; then
            echo "📋 Testing reference PCBs..."
            uv run pytest src/tests/test_reference_pcbs.py src/tests/test_reference_exact_format.py -v $PYTEST_ARGS
        fi
        ;;

    coverage)
        echo "📊 Running coverage analysis..."
        uv run pytest src/tests/ --cov=kicad_pcb_api --cov-report=term-missing --cov-report=html --cov-fail-under=70 $PYTEST_ARGS
        echo "📊 Coverage report: htmlcov/index.html"
        ;;

    reference-pcbs)
        echo "🏗️ Running reference PCB tests..."
        uv run pytest src/tests/test_reference_pcbs.py src/tests/test_reference_exact_format.py -v $PYTEST_ARGS
        ;;

    *)
        echo "❌ Unknown suite: $SUITE"
        echo "Available suites: quick, standard, full, coverage, reference-pcbs"
        exit 1
        ;;
esac

# Cleanup if requested
if [[ "$KEEP_OUTPUTS" == "false" ]]; then
    echo "🧹 Cleaning up test outputs..."
    rm -rf test_outputs/ .pytest_cache/ .coverage htmlcov/ 2>/dev/null || true
fi

echo "✅ Test suite completed"
```

## Expected Results by Suite

**Quick Suite**:
- ~5-10 tests, core functionality only
- <10 seconds execution time
- Good for rapid development iteration

**Standard Suite**:
- ~15-20 tests covering all core functionality
- ~30 seconds execution time
- Recommended for pre-commit validation

**Full Suite**:
- All tests + reference PCBs
- ~2 minutes execution time
- Recommended for pre-merge validation

**Coverage Suite**:
- Same as Standard but with detailed coverage analysis
- Target: >70% code coverage
- Generates HTML coverage report

**Reference PCB Suite**:
- Only reference PCB validation tests
- ~30 seconds execution time
- Good for verifying format preservation

## Usage Examples

```bash
# Quick development check
/run-tests --suite=quick

# Standard pre-commit validation (default)
/run-tests

# Full validation before merge
/run-tests --suite=full --verbose

# Coverage analysis
/run-tests --suite=coverage

# Reference PCB validation only
/run-tests --suite=reference-pcbs

# Debug specific failures
/run-tests --suite=standard --verbose --fail-fast

# Fast iteration during debugging
/run-tests --suite=quick --skip-install --format=false
```

## CI/CD Integration

```yaml
# GitHub Actions example
- name: Quick Tests
  run: /run-tests --suite=quick --fail-fast

- name: Full Tests (on PR)
  run: /run-tests --suite=full

- name: Coverage Tests (on main)
  run: /run-tests --suite=coverage
```

## Best Practices for kicad-pcb-api

1. **Development**: Use `--suite=quick` for rapid iteration
2. **Pre-commit**: Run `--suite=standard` before committing
3. **Pre-merge**: Run `--suite=full` before merging branches
4. **Coverage analysis**: Use `--suite=coverage` to identify gaps
5. **Debugging**: Use `--verbose --fail-fast` to isolate issues

## kicad-pcb-api Specific Testing

### Core Functionality Tests
- S-expression parsing and formatting
- Collection management (footprints, tracks, vias, zones)
- PCB board operations and validation
- Validation and error handling

### Integration Tests
- Round-trip format preservation
- Large PCB performance
- Reference PCB parsing

### Reference PCB Coverage
- Basic components and footprints
- Track and via routing
- Zone fills and polygons
- Graphics and text elements

This command provides a single entry point for all kicad-pcb-api testing while maintaining the flexibility of specialized test tools.
