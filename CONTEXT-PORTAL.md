# Context Portal Integration - kicad-pcb-api

## Setup

```bash
# Install Context Portal
cd tools/context-portal && pip install -e .

# Start server for this repository
uvx context-portal --workspace kicad-pcb-api --port 8002
```

## Repository Context

**kicad-pcb-api** provides professional file-based PCB manipulation for KiCAD.

### Key Development Areas

- **PCB File Operations**: Direct .kicad_pcb manipulation without KiCAD runtime
- **Placement Algorithms**: Hierarchical and spiral component placement
- **Routing Integration**: Freerouting DSN export/import workflows
- **Format Preservation**: Exact S-expression compatibility with KiCAD
- **MCP Integration**: AI agent interface for automated PCB design

### Context Categories

- `pcb-operations`: Core PCB file manipulation decisions
- `placement`: Component placement algorithm choices and trade-offs
- `routing`: Auto-routing integration strategies
- `performance`: Optimization techniques for large PCBs
- `compatibility`: KiCAD version compatibility decisions
- `testing`: PCB manipulation test strategies

### Usage Examples

```bash
# Add context about placement decisions
uvx context-portal add --category placement "Chose hierarchical over force-directed for stability"

# Query routing strategies  
uvx context-portal query "freerouting integration patterns"

# Search performance optimizations
uvx context-portal query "large PCB performance"
```

This provides AI assistants with structured memory about PCB manipulation development patterns and decisions.