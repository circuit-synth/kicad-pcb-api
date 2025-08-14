"""
MCP Server for KiCAD PCB API

Provides Model Context Protocol interface for AI agent integration
with KiCAD PCB manipulation capabilities.
"""

import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from mcp.server.fastmcp import FastMCP
from mcp.types import Resource, TextContent, Tool

from ..core.pcb_board import PCBBoard
from ..core.types import Point

# Configure logging to stderr (never stdout for MCP servers)
logging.basicConfig(
    level=logging.INFO,
    stream=sys.stderr,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("kicad-pcb-api")

# Global PCB board instance
_current_pcb: Optional[PCBBoard] = None

@mcp.tool()
async def load_pcb(filepath: str) -> str:
    """
    Load a KiCAD PCB file for manipulation.
    
    Args:
        filepath: Path to the .kicad_pcb file
        
    Returns:
        Success message with PCB info
    """
    global _current_pcb
    try:
        _current_pcb = PCBBoard(filepath)
        info = _current_pcb.get_board_info()
        return f"Loaded PCB: {info['footprint_count']} footprints, {info['net_count']} nets"
    except Exception as e:
        logger.error(f"Error loading PCB {filepath}: {e}")
        return f"Error loading PCB: {e}"

@mcp.tool()
async def create_pcb() -> str:
    """
    Create a new empty PCB.
    
    Returns:
        Success message
    """
    global _current_pcb
    try:
        _current_pcb = PCBBoard()
        return "Created new empty PCB"
    except Exception as e:
        logger.error(f"Error creating PCB: {e}")
        return f"Error creating PCB: {e}"

@mcp.tool()
async def save_pcb(filepath: str) -> str:
    """
    Save the current PCB to a file.
    
    Args:
        filepath: Path to save the .kicad_pcb file
        
    Returns:
        Success message
    """
    if not _current_pcb:
        return "Error: No PCB loaded. Use load_pcb() or create_pcb() first"
    
    try:
        _current_pcb.save(filepath)
        return f"Saved PCB to {filepath}"
    except Exception as e:
        logger.error(f"Error saving PCB to {filepath}: {e}")
        return f"Error saving PCB: {e}"

@mcp.tool()
async def add_footprint(
    reference: str,
    footprint_lib: str, 
    x: float,
    y: float,
    rotation: float = 0.0,
    value: str = "",
    layer: str = "F.Cu"
) -> str:
    """
    Add a footprint to the PCB.
    
    Args:
        reference: Component reference (e.g., "R1")
        footprint_lib: Footprint library ID (e.g., "Resistor_SMD:R_0603_1608Metric")
        x: X position in mm
        y: Y position in mm
        rotation: Rotation in degrees (default: 0)
        value: Component value (e.g., "10k")
        layer: PCB layer (default: "F.Cu")
        
    Returns:
        Success message
    """
    if not _current_pcb:
        return "Error: No PCB loaded. Use load_pcb() or create_pcb() first"
    
    try:
        footprint = _current_pcb.add_footprint(
            reference, footprint_lib, x, y, rotation, value, layer
        )
        return f"Added footprint {reference} ({footprint_lib}) at ({x}, {y})"
    except Exception as e:
        logger.error(f"Error adding footprint: {e}")
        return f"Error adding footprint: {e}"

@mcp.tool()
async def remove_footprint(reference: str) -> str:
    """
    Remove a footprint from the PCB.
    
    Args:
        reference: Component reference to remove
        
    Returns:
        Success message
    """
    if not _current_pcb:
        return "Error: No PCB loaded"
    
    try:
        success = _current_pcb.remove_footprint(reference)
        if success:
            return f"Removed footprint {reference}"
        else:
            return f"Footprint {reference} not found"
    except Exception as e:
        logger.error(f"Error removing footprint {reference}: {e}")
        return f"Error removing footprint: {e}"

@mcp.tool()
async def move_footprint(
    reference: str,
    x: float, 
    y: float,
    rotation: Optional[float] = None
) -> str:
    """
    Move a footprint to a new position.
    
    Args:
        reference: Component reference to move
        x: New X position in mm
        y: New Y position in mm  
        rotation: Optional new rotation in degrees
        
    Returns:
        Success message
    """
    if not _current_pcb:
        return "Error: No PCB loaded"
    
    try:
        success = _current_pcb.move_footprint(reference, x, y, rotation)
        if success:
            rot_msg = f", rotation {rotation}°" if rotation is not None else ""
            return f"Moved {reference} to ({x}, {y}){rot_msg}"
        else:
            return f"Footprint {reference} not found"
    except Exception as e:
        logger.error(f"Error moving footprint {reference}: {e}")
        return f"Error moving footprint: {e}"

@mcp.tool()
async def list_footprints() -> str:
    """
    List all footprints on the PCB.
    
    Returns:
        Formatted list of footprints with positions
    """
    if not _current_pcb:
        return "Error: No PCB loaded"
    
    try:
        footprints = _current_pcb.list_footprints()
        if not footprints:
            return "No footprints on PCB"
        
        result = "Footprints on PCB:\n"
        for ref, value, x, y in footprints:
            result += f"  {ref}: {value} at ({x:.2f}, {y:.2f})\n"
        return result.strip()
    except Exception as e:
        logger.error(f"Error listing footprints: {e}")
        return f"Error listing footprints: {e}"

@mcp.tool()
async def auto_place_components(
    algorithm: str = "hierarchical",
    component_spacing: float = 5.0,
    board_width: float = 100.0,
    board_height: float = 100.0
) -> str:
    """
    Automatically place components using specified algorithm.
    
    Args:
        algorithm: Placement algorithm ("hierarchical", "spiral", "force_directed")
        component_spacing: Minimum spacing between components in mm
        board_width: Board width in mm
        board_height: Board height in mm
        
    Returns:
        Success message with placement results
    """
    if not _current_pcb:
        return "Error: No PCB loaded"
    
    try:
        result = _current_pcb.auto_place_components(
            algorithm=algorithm,
            component_spacing=component_spacing,
            board_width=board_width,
            board_height=board_height
        )
        return f"Completed {algorithm} placement successfully"
    except Exception as e:
        logger.error(f"Error in auto placement: {e}")
        return f"Error in auto placement: {e}"

@mcp.tool()
async def get_board_info() -> str:
    """
    Get information about the current PCB.
    
    Returns:
        Formatted board information
    """
    if not _current_pcb:
        return "Error: No PCB loaded"
    
    try:
        info = _current_pcb.get_board_info()
        result = "PCB Information:\n"
        result += f"  Version: {info.get('version', 'Unknown')}\n"
        result += f"  Generator: {info.get('generator', 'Unknown')}\n"
        result += f"  Paper Size: {info.get('paper_size', 'Unknown')}\n"
        result += f"  Thickness: {info.get('thickness', 'Unknown')}mm\n"
        result += f"  Footprints: {info.get('footprint_count', 0)}\n"
        result += f"  Nets: {info.get('net_count', 0)}\n"
        result += f"  Vias: {info.get('via_count', 0)}\n"
        result += f"  Tracks: {info.get('track_count', 0)}"
        return result
    except Exception as e:
        logger.error(f"Error getting board info: {e}")
        return f"Error getting board info: {e}"

@mcp.tool()
async def connect_pads(
    ref1: str,
    pad1: str,
    ref2: str, 
    pad2: str,
    net_name: Optional[str] = None
) -> str:
    """
    Connect two pads with a net.
    
    Args:
        ref1: First component reference
        pad1: First component pad number
        ref2: Second component reference
        pad2: Second component pad number
        net_name: Optional net name
        
    Returns:
        Success message
    """
    if not _current_pcb:
        return "Error: No PCB loaded"
    
    try:
        success = _current_pcb.connect_pads(ref1, pad1, ref2, pad2, net_name)
        if success:
            return f"Connected {ref1}.{pad1} to {ref2}.{pad2}"
        else:
            return "Failed to connect pads"
    except Exception as e:
        logger.error(f"Error connecting pads: {e}")
        return f"Error connecting pads: {e}"

@mcp.tool() 
async def get_ratsnest() -> str:
    """
    Get the ratsnest (unrouted connections) for the PCB.
    
    Returns:
        Formatted list of unrouted connections
    """
    if not _current_pcb:
        return "Error: No PCB loaded"
    
    try:
        ratsnest = _current_pcb.get_ratsnest()
        if not ratsnest:
            return "No unrouted connections found"
        
        result = f"Ratsnest ({len(ratsnest)} connections):\n"
        for conn in ratsnest:
            result += f"  {conn['from_ref']}.{conn['from_pad']} -> {conn['to_ref']}.{conn['to_pad']} "
            result += f"(net: {conn['net_name']}, {conn['distance']:.2f}mm)\n"
        return result.strip()
    except Exception as e:
        logger.error(f"Error getting ratsnest: {e}")
        return f"Error getting ratsnest: {e}"

@mcp.tool()
async def set_board_outline_rect(
    x: float,
    y: float, 
    width: float,
    height: float
) -> str:
    """
    Set a rectangular board outline.
    
    Args:
        x: X position of top-left corner in mm
        y: Y position of top-left corner in mm
        width: Board width in mm
        height: Board height in mm
        
    Returns:
        Success message
    """
    if not _current_pcb:
        return "Error: No PCB loaded"
    
    try:
        _current_pcb.set_board_outline_rect(x, y, width, height)
        return f"Set rectangular board outline: {width}x{height}mm at ({x}, {y})"
    except Exception as e:
        logger.error(f"Error setting board outline: {e}")
        return f"Error setting board outline: {e}"

def create_server() -> FastMCP:
    """Create and return the MCP server instance."""
    return mcp

def main():
    """Main entry point for MCP server."""
    import asyncio
    mcp.run()

if __name__ == "__main__":
    main()