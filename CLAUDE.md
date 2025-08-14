# CLAUDE.md - kicad-pcb-api

This file provides guidance to Claude Code when working on the kicad-pcb-api project.

## Project Overview

**kicad-pcb-api** is a professional Python library for programmatic manipulation of KiCAD PCB files (.kicad_pcb). It provides file-based operations without requiring a running KiCAD instance, making it ideal for CI/CD workflows and automated PCB generation.

## Key Features

- **File-Based Operations**: Direct manipulation of .kicad_pcb files
- **Advanced Placement Algorithms**: Hierarchical, spiral, and basic placement
- **Routing Integration**: Freerouting integration with DSN export/import  
- **MCP Server**: Native AI agent integration via Model Context Protocol
- **Format Preservation**: Exact compatibility with KiCAD's native output
- **Professional API**: Enhanced object model vs verbose existing solutions

## Project Structure

```
kicad-pcb-api/
├── python/                          # Core Python library
│   ├── kicad_pcb_api/
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
│   │   ├── mcp/                    # MCP server interface
│   │   │   └── server.py           # Python MCP server
│   │   └── utils/                  # Utilities
│   │       ├── validation.py       # PCB validation
│   │       └── kicad_cli.py        # KiCAD CLI integration
│   ├── examples/                   # Usage examples
│   └── tests/                      # Test suite
├── mcp-server/                     # TypeScript MCP server
│   ├── src/index.ts               # Main MCP server
│   ├── package.json
│   └── tsconfig.json
└── README.md
```

## Development Commands

```bash
# Install dependencies
cd python && pip install -e ".[dev]"

# Run tests
cd python && pytest

# Install MCP server
cd mcp-server && npm install && npm run build

# Build package
cd python && python -m build

# Upload to PyPI
cd python && python -m twine upload dist/*
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

## MCP Integration

The package includes both Python and TypeScript MCP servers:

- **Python MCP**: `kicad-pcb-mcp` command-line tool
- **TypeScript MCP**: Full-featured server with Python bridge

## Development Notes

- **File Format**: KiCAD PCB files use S-expressions - maintain exact format compatibility
- **Placement Algorithms**: Focus on practical algorithms (hierarchical, spiral) - avoid complex force-directed
- **Import Structure**: Use relative imports within package, absolute for external
- **Testing**: Comprehensive test coverage for core functionality
- **MCP Server**: Use stderr for logging, never stdout (breaks JSON-RPC)

## Key Dependencies

- `sexpdata`: S-expression parsing
- `loguru`: Advanced logging  
- `mcp`: Model Context Protocol SDK

## Contributing

When working on this repository:

1. **Maintain API Compatibility**: Follow existing patterns for PCBBoard class
2. **Test Coverage**: Add tests for new functionality
3. **Import Management**: Keep imports clean and well-organized
4. **Documentation**: Update docstrings and examples
5. **MCP Integration**: Ensure MCP tools work with both servers

## Related Projects

- **kicad-sch-api**: Schematic manipulation library
- **engineering-memory-bank**: AI-powered decision documentation
- **circuit-synth**: Main circuit design automation project

---

*This repository is part of the Circuit-Synth professional ecosystem*