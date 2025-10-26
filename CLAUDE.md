# CLAUDE.md - kicad-pcb-api

This file provides guidance to Claude Code when working on the kicad-pcb-api project.

## Project Overview

**kicad-pcb-api** is a professional Python library for programmatic manipulation of KiCAD PCB files (.kicad_pcb). It provides file-based operations without requiring a running KiCAD instance, making it ideal for CI/CD workflows and automated PCB generation.

## Key Features

- **File-Based Operations**: Direct manipulation of .kicad_pcb files
- **Advanced Placement Algorithms**: Hierarchical, spiral, and basic placement
- **Routing Integration**: Freerouting integration with DSN export/import  
- **Format Preservation**: Exact compatibility with KiCAD's native output
- **Professional API**: Enhanced object model vs verbose existing solutions

## Project Structure

```
kicad-pcb-api/
├── src/                             # Core Python library
│   ├── kicad_pcb_api/
│   │   ├── collections/            # Collection management (NEW)
│   │   │   ├── base.py             # IndexedCollection base
│   │   │   ├── footprints.py       # FootprintCollection
│   │   │   ├── tracks.py           # TrackCollection
│   │   │   └── vias.py             # ViaCollection
│   │   ├── core/                   # Core PCB manipulation
│   │   │   ├── pcb_board.py        # Main PCBBoard class
│   │   │   ├── pcb_parser.py       # S-expression parser
│   │   │   ├── pcb_formatter.py    # S-expression formatter
│   │   │   └── types.py            # Data structures
│   │   ├── placement/              # Placement algorithms
│   │   │   ├── base.py             # Base classes
│   │   │   ├── hierarchical_placement.py
│   │   │   └── spiral_placement.py
│   │   ├── routing/                # Routing integration
│   │   │   ├── dsn_exporter.py     # DSN format export
│   │   │   ├── freerouting_runner.py
│   │   │   └── ses_importer.py     # SES import
│   │   ├── footprints/             # Footprint management
│   │   │   └── footprint_library.py
│   │   └── utils/                  # Utilities
│   │       ├── validation.py       # PCB validation
│   │       └── kicad_cli.py        # KiCAD CLI integration
│   ├── examples/                   # Usage examples
│   └── tests/                      # Test suite (69 tests)
├── docs/                           # Documentation
└── README.md
```

## Development Commands

```bash
# Install dependencies (uses uv)
uv pip install -e ".[dev]"

# Run tests
uv run pytest src/tests

# Build package
uv build

# Upload to PyPI
uv publish
```

## Core API Usage

```python
import kicad_pcb_api as kpa

# Load/create PCB
pcb = kpa.load_pcb('board.kicad_pcb')  # or kpa.create_pcb()

# Add footprints
resistor = pcb.add_footprint('R1', 'Resistor_SMD:R_0603_1608Metric', 50, 50)
resistor.value = '10k'

# Connect components
pcb.connect_pads('R1', '1', 'C1', '1', 'Signal')

# Auto-placement
pcb.auto_place_components('hierarchical', component_spacing=5.0)

# Save
pcb.save()
```


## Development Notes

- **File Format**: KiCAD PCB files use S-expressions - maintain exact format compatibility
- **Placement Algorithms**: Focus on practical algorithms (hierarchical, spiral) - avoid complex force-directed
- **Import Structure**: Use relative imports within package, absolute for external
- **Testing**: Comprehensive test coverage for core functionality

## Key Dependencies

- `sexpdata`: S-expression parsing
- `loguru`: Advanced logging

## Contributing

When working on this repository:

1. **Maintain API Compatibility**: Follow existing patterns for PCBBoard class
2. **Test Coverage**: Add tests for new functionality
3. **Import Management**: Keep imports clean and well-organized
4. **Documentation**: Update docstrings and examples
5. **Use uv**: This project uses `uv` for package management

## Development Workflow

```bash
# Install with uv
uv pip install -e ".[dev]"

# Run tests
uv run pytest

# Format code
uv run black src/

# Type checking
uv run mypy src/
```

## Related Projects

- **kicad-sch-api**: Schematic manipulation library (reference architecture)
- **pykicad**: PCB format reference implementation
- **kicad-skip**: S-expression parsing reference

---

*This repository is part of the Circuit-Synth professional ecosystem*