# Product Context - kicad-pcb-api

## Project Overview

**kicad-pcb-api** is a professional Python library for programmatic manipulation of KiCAD PCB files (.kicad_pcb) with file-based operations, advanced placement algorithms, and exact format preservation.

## Core Value Proposition

1. **File-Based Operations**: Direct .kicad_pcb manipulation without requiring running KiCAD instance
2. **Advanced Placement**: Professional placement algorithms (hierarchical, spiral) vs manual placement
3. **Routing Integration**: Freerouting DSN export/import for automated routing workflows
4. **Format Preservation**: Exact compatibility with KiCAD's native PCB output format
5. **Professional API**: Enhanced object model for PCB manipulation vs verbose existing solutions

## Target Users

### Primary Users
- **PCB Layout Engineers**: Automating component placement and routing preparation
- **Circuit Design Engineers**: Programmatic PCB generation from schematics
- **Manufacturing Engineers**: Automated DRC, Gerber generation, pick-and-place files

### Secondary Users
- **EDA Tool Developers**: Building higher-level PCB automation tools
- **Hardware Startups**: Streamlining PCB iteration and manufacturing prep
- **AI/Automation Engineers**: Creating intelligent PCB design assistants

## Key Differentiators

### vs KiCAD Official API
- **File-Based**: Works without running KiCAD instance (CI/CD compatible)
- **Enhanced Operations**: Advanced placement algorithms and routing integration
- **Automation Ready**: Designed for scripted workflows and batch processing

### vs Manual PCB Layout
- **Placement Algorithms**: Intelligent component positioning vs manual placement
- **Bulk Operations**: Process hundreds of components in seconds
- **Consistency**: Programmatic design rules and validation
- **Integration**: Part of automated design-to-manufacturing flows

### vs Other PCB Libraries
- **Professional Placement**: Advanced algorithms (hierarchical, spiral) vs basic positioning
- **Routing Integration**: Native Freerouting support vs manual routing only
- **Manufacturing Focus**: DRC, Gerber, drill, pick-and-place generation

## Technical Architecture

- **Core Engine**: S-expression parsing for .kicad_pcb files
- **Object Model**: PCBBoard, Footprint, Track, Via, Zone classes
- **Placement System**: Hierarchical and spiral placement algorithms
- **Routing Integration**: DSN export, Freerouting runner, SES import
- **Manufacturing**: KiCAD CLI integration for DRC, Gerber export

## Success Metrics

### Technical
- **Format Fidelity**: 100% round-trip compatibility with KiCAD PCB files
- **Performance**: Handle 500+ component PCBs efficiently
- **Placement Quality**: Measurable improvement in trace length vs manual

### Adoption
- **PyPI Downloads**: Growing usage in PCB automation workflows
- **Community Contributions**: Active developer ecosystem focusing on placement and routing

## Current Status

- ✅ **Core Library**: Professional PCB file manipulation
- ✅ **Placement Algorithms**: Hierarchical and spiral placement implemented
- ✅ **Routing Integration**: Freerouting DSN/SES support
- ✅ **Manufacturing**: DRC, Gerber, drill file generation
- ✅ **PyPI Package**: v0.0.1 published and available