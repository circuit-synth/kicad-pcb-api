# Utils Module

Validation utilities and KiCAD CLI integration.

## Overview

This module provides utility functions for PCB validation and KiCAD command-line interface integration. These utilities support quality assurance and external tool integration.

## Validation Utilities (`validation.py`)

Comprehensive PCB validation system for detecting errors and ensuring quality.

### PCBValidator Class

Main validation class with comprehensive checks:

```python
from kicad_pcb_api.utils import PCBValidator

# Create validator
validator = PCBValidator(pcb)

# Run all validations
results = validator.validate_all()

# Check results
for result in results:
    if result.severity == 'error':
        print(f"ERROR: {result.message}")
    elif result.severity == 'warning':
        print(f"WARNING: {result.message}")
```

### Validation Categories

#### Footprint Validation
```python
# Validate all footprints
results = validator.validate_footprints()

# Checks:
# - Reference uniqueness
# - Valid library references
# - Pad connectivity
# - Courtyard presence
# - Text visibility
```

#### Net Validation
```python
# Validate nets
results = validator.validate_nets()

# Checks:
# - Net name validity
# - Unconnected nets
# - Short circuits
# - Net class compliance
```

#### Layer Validation
```python
# Validate layers
results = validator.validate_layers()

# Checks:
# - Layer consistency
# - Valid layer names
# - Track layer validity
# - Via layer pairs
```

#### Reference Validation
```python
# Validate references
results = validator.validate_references()

# Checks:
# - Reference uniqueness
# - Valid naming convention
# - No duplicate references
# - Reference prefix consistency
```

#### Design Rule Validation
```python
# Validate design rules
results = validator.validate_design_rules()

# Checks:
# - Minimum track width
# - Minimum clearance
# - Via size limits
# - Annular ring width
```

### ValidationResult Class

Result object with detailed information:

```python
class ValidationResult:
    severity: str       # 'error', 'warning', 'info'
    category: str       # 'footprint', 'net', 'layer', etc.
    message: str        # Human-readable message
    location: Point     # Location of issue (if applicable)
    element_id: str     # UUID of affected element
    suggestions: List[str]  # Fix suggestions
```

**Example**:
```python
result = ValidationResult(
    severity='error',
    category='footprint',
    message='Duplicate reference: R1',
    location=Point(100, 100),
    element_id='uuid-123',
    suggestions=['Rename one of the components']
)
```

### Validation Functions

Standalone validation functions:

```python
from kicad_pcb_api.utils.validation import (
    validate_reference,
    validate_net_name,
    validate_layer,
    validate_pad_number
)

# Validate reference
if not validate_reference('R1'):
    print("Invalid reference")

# Validate net name
if not validate_net_name('VCC'):
    print("Invalid net name")

# Validate layer
if not validate_layer('F.Cu'):
    print("Invalid layer")
```

## KiCAD CLI Integration (`kicad_cli.py`)

Integration with KiCAD command-line tools for advanced operations.

### KiCADCLI Class

Wrapper for KiCAD CLI commands:

```python
from kicad_pcb_api.utils import KiCADCLI

# Create CLI interface
cli = KiCADCLI(kicad_path='/Applications/KiCad/KiCad.app')

# Run DRC
drc_result = cli.run_drc('board.kicad_pcb', 'drc_report.json')

# Generate Gerbers
cli.generate_gerbers('board.kicad_pcb', output_dir='gerbers/')

# Export BOM
cli.export_bom('board.kicad_pcb', 'bom.csv')

# Generate 3D view
cli.generate_3d('board.kicad_pcb', 'board.step')
```

### Available Commands

#### DRC (Design Rule Check)
```python
# Run DRC with KiCAD
result = cli.run_drc(
    pcb_file='board.kicad_pcb',
    output_file='drc_report.json',
    severity='error'  # or 'warning', 'all'
)

# Parse results
if result.has_errors:
    for error in result.errors:
        print(f"DRC Error: {error.message}")
```

#### Gerber Generation
```python
# Generate production files
cli.generate_gerbers(
    pcb_file='board.kicad_pcb',
    output_dir='gerbers/',
    layers=['F.Cu', 'B.Cu', 'F.Mask', 'B.Mask', 'Edge.Cuts']
)

# Generate drill files
cli.generate_drill_files(
    pcb_file='board.kicad_pcb',
    output_dir='gerbers/'
)
```

#### BOM Export
```python
# Export BOM
cli.export_bom(
    pcb_file='board.kicad_pcb',
    output_file='bom.csv',
    format='csv',  # or 'xml', 'html'
    fields=['Reference', 'Value', 'Footprint', 'Datasheet']
)
```

#### 3D Export
```python
# Export STEP file
cli.generate_3d(
    pcb_file='board.kicad_pcb',
    output_file='board.step',
    format='step'  # or 'vrml'
)
```

#### PCB Info
```python
# Get PCB information
info = cli.get_pcb_info('board.kicad_pcb')

print(f"Layers: {info.layer_count}")
print(f"Footprints: {info.footprint_count}")
print(f"Nets: {info.net_count}")
print(f"Board area: {info.area_mm2} mm²")
```

### Path Configuration

Configure KiCAD installation path:

```python
from kicad_pcb_api import config

# Set KiCAD path globally
config.kicad_path = '/Applications/KiCad/KiCad.app'

# Or per-instance
cli = KiCADCLI(kicad_path='/opt/kicad/')
```

### Error Handling

```python
from kicad_pcb_api.utils import KiCADCLI, KiCADCLIError

cli = KiCADCLI()

try:
    result = cli.run_drc('board.kicad_pcb')
except KiCADCLIError as e:
    print(f"CLI Error: {e}")
    print(f"Command: {e.command}")
    print(f"Output: {e.output}")
```

## Common Use Cases

### Pre-Flight Validation
```python
from kicad_pcb_api import load_pcb
from kicad_pcb_api.utils import PCBValidator

# Load board
pcb = load_pcb('board.kicad_pcb')

# Validate
validator = PCBValidator(pcb)
results = validator.validate_all()

# Check for errors
errors = [r for r in results if r.severity == 'error']
if errors:
    print(f"Found {len(errors)} errors:")
    for error in errors:
        print(f"  - {error.message}")
    exit(1)
else:
    print("Validation passed!")
```

### Automated DRC
```python
from kicad_pcb_api.utils import KiCADCLI

cli = KiCADCLI()

# Run DRC
result = cli.run_drc('board.kicad_pcb', 'drc_report.json')

if result.has_errors:
    print("DRC FAILED")
    for error in result.errors:
        print(f"  {error.type}: {error.message}")
    exit(1)
else:
    print("DRC PASSED")
```

### Production File Generation
```python
from kicad_pcb_api.utils import KiCADCLI

cli = KiCADCLI()

# Generate all production files
cli.generate_gerbers('board.kicad_pcb', 'output/gerbers/')
cli.generate_drill_files('board.kicad_pcb', 'output/gerbers/')
cli.export_bom('board.kicad_pcb', 'output/bom.csv')
cli.generate_3d('board.kicad_pcb', 'output/board.step')

print("Production files generated!")
```

## Testing

Tests located in `../../tests/`:
- `test_validation.py` - Validation tests
- `test_kicad_cli.py` - CLI integration tests
- Integration tests with real PCBs

## Related Modules

- `core/validation.py` - Core validation logic
- `core/exceptions.py` - Exception definitions
- `managers/validation.py` - ValidationManager
- `managers/drc.py` - DRCManager

## Future Improvements

- [ ] ERC (Electrical Rule Check) integration
- [ ] Custom validation rules
- [ ] Validation report generation
- [ ] KiCAD plugin integration
- [ ] Automated fix suggestions
- [ ] Performance profiling utilities
