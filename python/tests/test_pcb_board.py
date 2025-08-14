"""
Basic tests for PCBBoard functionality.
"""

import pytest
from pathlib import Path
import tempfile

from kicad_pcb_api import PCBBoard, Point

def test_create_empty_pcb():
    """Test creating an empty PCB."""
    pcb = PCBBoard()
    assert pcb.get_footprint_count() == 0
    assert pcb.get_net_count() == 1  # Net 0 is always present

def test_add_footprint():
    """Test adding a footprint."""
    pcb = PCBBoard()
    
    footprint = pcb.add_footprint(
        reference="R1",
        footprint_lib="Resistor_SMD:R_0603_1608Metric",
        x=10, y=20,
        value="10k"
    )
    
    assert footprint.reference == "R1"
    assert footprint.value == "10k"
    assert footprint.position.x == 10
    assert footprint.position.y == 20
    assert pcb.get_footprint_count() == 1

def test_remove_footprint():
    """Test removing a footprint."""
    pcb = PCBBoard()
    
    # Add footprint
    pcb.add_footprint("R1", "Resistor_SMD:R_0603_1608Metric", 10, 20)
    assert pcb.get_footprint_count() == 1
    
    # Remove footprint
    success = pcb.remove_footprint("R1")
    assert success is True
    assert pcb.get_footprint_count() == 0
    
    # Try to remove non-existent footprint
    success = pcb.remove_footprint("R2")
    assert success is False

def test_move_footprint():
    """Test moving a footprint."""
    pcb = PCBBoard()
    
    # Add footprint
    pcb.add_footprint("R1", "Resistor_SMD:R_0603_1608Metric", 10, 20)
    
    # Move footprint
    success = pcb.move_footprint("R1", 30, 40, 90)
    assert success is True
    
    footprint = pcb.get_footprint("R1")
    assert footprint.position.x == 30
    assert footprint.position.y == 40
    assert footprint.rotation == 90

def test_save_and_load():
    """Test saving and loading PCB files."""
    # Create PCB with content
    pcb1 = PCBBoard()
    pcb1.add_footprint("R1", "Resistor_SMD:R_0603_1608Metric", 10, 20, value="1k")
    pcb1.set_board_outline_rect(0, 0, 50, 30)
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(suffix=".kicad_pcb", delete=False) as tmp:
        tmp_path = Path(tmp.name)
        pcb1.save(tmp_path)
        
        # Load in new PCB instance
        pcb2 = PCBBoard(tmp_path)
        
        # Verify content
        assert pcb2.get_footprint_count() == 1
        footprint = pcb2.get_footprint("R1")
        assert footprint is not None
        assert footprint.value == "1k"
        assert footprint.position.x == 10
        assert footprint.position.y == 20
        
        # Clean up
        tmp_path.unlink()

def test_net_operations():
    """Test net creation and management."""
    pcb = PCBBoard()
    
    # Add components
    pcb.add_footprint("R1", "Resistor_SMD:R_0603_1608Metric", 10, 20)
    pcb.add_footprint("R2", "Resistor_SMD:R_0603_1608Metric", 30, 20)
    
    # Connect pads
    success = pcb.connect_pads("R1", "1", "R2", "1", "Signal")
    assert success is True
    
    # Check net was created
    net = pcb.get_net_by_name("Signal")
    assert net is not None
    assert net.name == "Signal"

def test_board_outline():
    """Test board outline operations."""
    pcb = PCBBoard()
    
    # Set rectangular outline
    rect = pcb.set_board_outline_rect(0, 0, 100, 60)
    assert rect.start.x == 0
    assert rect.start.y == 0
    
    # Get outline
    outline = pcb.get_board_outline()
    assert len(outline) == 1  # Should have one rectangle
    
    # Get bounding box
    bbox = pcb.get_board_outline_bbox()
    assert bbox.width() == 100
    assert bbox.height() == 60