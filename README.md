# kicad-pcb-api

**Professional KiCAD PCB Manipulation Library with File-Based Operations**

A modern, high-performance Python library for programmatic manipulation of KiCAD PCB files (.kicad_pcb) with exact format preservation, advanced placement algorithms, and AI agent integration. Unlike KiCAD's official PCB API which requires a running KiCAD instance, kicad-pcb-api works directly with PCB files for CI/CD and automated workflows.

## 🚀 Key Features

- **📋 File-Based Operations**: Manipulate .kicad_pcb files without running KiCAD
- **⚡ Advanced Placement**: Force-directed, hierarchical, and spiral algorithms
- **🤖 AI Agent Integration**: Native MCP server for AI-assisted PCB design
- **🔧 Enhanced Routing**: Freerouting integration with DSN export/import
- **📚 Footprint Management**: Advanced footprint library integration
- **✅ Format Preservation**: Exact compatibility with KiCAD's native output
- **🎯 KiCAD 9 Optimized**: Built specifically for latest KiCAD PCB format

## 🆚 vs. Existing Solutions

| Feature | kicad-pcb-api | KiCAD Official API | pcbnew Python API |
|---------|---------------|-------------------|-------------------|
| **File Operations** | ✅ Direct file manipulation | ❌ Runtime only | ❌ Runtime only |
| **CI/CD Compatible** | ✅ No GUI required | ❌ Requires KiCAD | ❌ Requires KiCAD |
| **Placement Algorithms** | ✅ Multiple advanced | ⚠️ Basic | ⚠️ Manual |
| **Routing Integration** | ✅ Freerouting + DSN | ❌ Limited | ⚠️ Basic |
| **AI Integration** | ✅ Native MCP | ❌ None | ❌ None |
| **Format Preservation** | ✅ Exact | ✅ Native | ✅ Native |

## 📦 Installation

```bash
# Install from PyPI (coming soon)
pip install kicad-pcb-api

# Or install from source
git clone https://github.com/circuit-synth/kicad-pcb-api.git
cd kicad-pcb-api
pip install -e .
```

## 🎯 Quick Start

### Basic PCB Manipulation

```python
import kicad_pcb_api as kpa

# Load existing PCB
pcb = kpa.load_pcb('my_board.kicad_pcb')

# Add footprints
resistor = pcb.footprints.add(
    'Resistor_SMD:R_0603_1608Metric', 
    reference='R1', 
    position=(50, 50)
)

# Update properties
resistor.value = '10k'
resistor.layer = 'F.Cu'
resistor.rotation = 90

# Save with format preservation
pcb.save()
```

### Advanced Placement

```python
# Automatic component placement
placer = kpa.placement.ForceDirectedPlacer(pcb)
placer.place_components(
    algorithm='hierarchical',
    optimize_for='trace_length'
)

# Custom placement strategies
spiral_placer = kpa.placement.SpiralPlacer(pcb)
spiral_placer.place_in_spiral(
    components=['R1', 'R2', 'C1'],
    center=(100, 100),
    spacing=5.0
)
```

### Routing Integration

```python
# Export for routing
router = kpa.routing.FreeroutingRunner(pcb)
dsn_file = router.export_dsn('board.dsn')

# Import routed traces
router.import_routes('board.ses')

# Validate routing
issues = pcb.validate_routing()
```

## 🏗️ Architecture

```
kicad-pcb-api/
├── python/                          # Core Python library
│   ├── kicad_pcb_api/
│   │   ├── core/                   # Core PCB manipulation
│   │   ├── placement/              # Placement algorithms
│   │   ├── routing/                # Routing integration
│   │   ├── footprints/             # Footprint management
│   │   ├── mcp/                    # MCP server interface
│   │   └── utils/                  # Utilities and validation
│   └── tests/                      # Comprehensive test suite
├── mcp-server/                     # TypeScript MCP server
└── examples/                       # Usage examples
```

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

**Built with ❤️ by the Circuit-Synth team**