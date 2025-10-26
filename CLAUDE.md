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
# Install dependencies
cd src && pip install -e ".[dev]"

# Run tests
pytest src/tests

# Install MCP server
cd mcp-server && npm install && npm run build

# Build package
python -m build

# Upload to PyPI (from root)
python -m twine upload dist/*
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

## Memory Bank System - REQUIRED WORKFLOW

This repository uses a **Code Memory Bank** system for persistent development context. **ALL DEVELOPMENT WORK MUST FOLLOW THIS WORKFLOW.**

### 🚨 MANDATORY WORKFLOW FOR ALL AI DEVELOPMENT

#### 1. BEFORE Starting Any Work:
```bash
# ALWAYS start by reading existing context
1. Read .memory_bank/activeContext.md (current state)
2. Read .memory_bank/decisionLog.md (past decisions) 
3. Read .memory_bank/progress.md (current milestones)
4. Check .memory_bank/productContext.md (project scope)
```

#### 2. FOR New Features (REQUIRED):
```bash
# Create PRD BEFORE coding
1. Write PRD in .memory_bank/features/[feature-name].md
2. Document requirements, design approach, success criteria
3. Get alignment on approach before implementation
```

#### 3. DURING Development:
```bash
# Keep context current
1. Update .memory_bank/activeContext.md with current work
2. Document decisions in .memory_bank/decisionLog.md (ADR format)
3. Track progress in .memory_bank/progress.md
```

#### 4. AFTER Completing Work:
```bash
# ALWAYS update memory bank
/umb
```

### Memory Bank Structure

- **activeContext.md**: Current session state, focus areas, files being worked on
- **decisionLog.md**: All architectural decisions in ADR format with rationale
- **productContext.md**: Project overview, value proposition, target users  
- **progress.md**: Milestones, current tasks, success metrics
- **features/**: PRDs for all planned features (REQUIRED before coding)

### 🔍 Query Memory Bank

Ask natural language questions about past decisions:
- "What placement algorithms were chosen and why?"
- "What are the current PCB performance optimization priorities?"
- "How does routing integration work with Freerouting?"

### ⚠️ CRITICAL: No Development Without Memory Bank

1. **Never start coding** without reading existing memory bank context
2. **Always write PRDs** for new features before implementation
3. **Document all decisions** in ADR format with rationale
4. **Use /umb command** before ending development sessions

## Contributing

When working on this repository:

1. **Follow Memory Bank Workflow**: Use required workflow above
2. **Maintain API Compatibility**: Follow existing patterns for PCBBoard class
3. **Test Coverage**: Add tests for new functionality
4. **Import Management**: Keep imports clean and well-organized
5. **Documentation**: Update docstrings and examples

## Related Projects

- **kicad-sch-api**: Schematic manipulation library
- **engineering-memory-bank**: AI-powered decision documentation
- **circuit-synth**: Main circuit design automation project

---

*This repository is part of the Circuit-Synth professional ecosystem*