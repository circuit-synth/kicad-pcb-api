# Decision Log - kicad-pcb-api

## Architectural Decisions

### ADR-001: File-Based PCB Operations
**Date**: 2025-08-12  
**Status**: Implemented  

**Context**: Need for PCB manipulation without requiring running KiCAD instance.

**Decision**: Build file-based PCB manipulation library working directly with .kicad_pcb files.

**Rationale**:
- CI/CD compatibility - no GUI dependencies
- Automated workflows can run in containers
- Faster processing without KiCAD startup overhead
- Better integration with scripted design flows

**Consequences**:
- ✅ Full automation capability
- ✅ Container and CI/CD ready
- ✅ High performance for batch operations
- ⚠️ Must maintain exact format compatibility manually

### ADR-002: Placement Algorithm Focus
**Date**: 2025-08-12  
**Status**: Implemented

**Context**: Multiple approaches for automated component placement.

**Decision**: Implement basic placement algorithms (hierarchical, spiral) rather than complex force-directed systems.

**Rationale**:
- Immediate high-value functionality
- Predictable, stable placement results
- Easier to understand and debug
- Foundation for future advanced algorithms

**Implementation**:
- Hierarchical: Grid-based placement with component spacing
- Spiral: Radial placement from board center
- Focus on practical, working solutions

### ADR-003: Freerouting Integration Strategy
**Date**: 2025-08-12  
**Status**: Implemented

**Context**: Need for automated routing capabilities.

**Decision**: Integrate with Freerouting via DSN export/SES import workflow.

**Rationale**:
- Freerouting is mature, proven auto-router
- DSN format is industry standard
- Avoids implementing complex routing algorithms
- Provides professional-quality results

**Implementation**:
- DSN exporter for board geometry and nets
- Docker integration for Freerouting execution
- SES importer for routed trace integration

### ADR-004: Enhanced Object Model
**Date**: 2025-08-12  
**Status**: Implemented

**Context**: Balance between direct S-expression access and user-friendly API.

**Decision**: Provide enhanced object model with direct property access.

**Rationale**:
- Improved developer experience vs verbose S-expression manipulation
- Type safety and IDE support
- Natural mapping to PCB concepts (footprints, tracks, vias)
- Professional API design standards

**Example**:
```python
# Enhanced API
footprint = pcb.add_footprint('R1', 'Resistor_SMD:R_0603_1608Metric', 50, 50)
footprint.value = '10k'
footprint.rotation = 90

# vs verbose S-expression manipulation
```

### ADR-005: Manufacturing Integration Approach
**Date**: 2025-08-12  
**Status**: Implemented

**Context**: PCBs need manufacturing file generation (Gerbers, drill files, pick-and-place).

**Decision**: Integrate with KiCAD CLI for manufacturing file generation.

**Rationale**:
- Leverage KiCAD's proven manufacturing output
- Avoid reimplementing complex Gerber generation
- Maintain compatibility with existing manufacturing workflows
- Enable end-to-end automation (design → manufacturing)

**Implementation**:
- KiCAD CLI wrapper for DRC, Gerber export
- Automated drill file generation
- Pick-and-place file creation