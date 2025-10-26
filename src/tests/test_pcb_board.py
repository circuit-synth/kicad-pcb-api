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


# Manager Integration Tests

def test_managers_initialized():
    """Test that all managers are initialized."""
    pcb = PCBBoard()

    # Verify managers exist
    assert pcb.drc is not None
    assert pcb.net is not None
    assert pcb.placement is not None
    assert pcb.routing is not None
    assert pcb.validation is not None


def test_collections_initialized():
    """Test that all collections are initialized."""
    pcb = PCBBoard()

    # Verify collections exist
    assert pcb.footprints is not None
    assert pcb.tracks is not None
    assert pcb.vias is not None


def test_drc_manager_integration():
    """Test DRC manager integration."""
    pcb = PCBBoard()

    # Add a track with invalid width
    from kicad_pcb_api import Track, Point
    track = Track(
        start=Point(0, 0),
        end=Point(10, 10),
        width=0.05,  # Below minimum
        layer="F.Cu",
        uuid="test-track-1"
    )
    pcb.pcb_data["tracks"].append(track)

    # Run DRC via convenience method
    violations = pcb.check_drc(min_track_width=0.1)
    assert violations > 0

    # Check violations are accessible
    assert len(pcb.drc.violations) > 0


def test_validation_manager_integration():
    """Test validation manager integration."""
    pcb = PCBBoard()

    # Add footprints with duplicate references
    pcb.add_footprint("R1", "Resistor_SMD:R_0603_1608Metric", 10, 20)
    pcb.add_footprint("R1", "Resistor_SMD:R_0603_1608Metric", 30, 20)  # Duplicate ref

    # Run validation via convenience method
    issues = pcb.validate()
    assert issues > 0

    # Check issues are accessible via property
    assert len(pcb.issues) > 0
    assert any(issue.category == "reference" for issue in pcb.issues)


def test_placement_manager_integration():
    """Test placement manager integration."""
    pcb = PCBBoard()

    # Add multiple footprints
    pcb.add_footprint("R1", "Resistor_SMD:R_0603_1608Metric", 0, 0)
    pcb.add_footprint("R2", "Resistor_SMD:R_0603_1608Metric", 0, 0)
    pcb.add_footprint("R3", "Resistor_SMD:R_0603_1608Metric", 0, 0)
    pcb.add_footprint("R4", "Resistor_SMD:R_0603_1608Metric", 0, 0)

    # Place in grid via convenience method
    placed = pcb.place_grid(["R1", "R2", "R3", "R4"], 10, 10, 5, 5, 2)
    assert placed == 4

    # Verify positions changed
    r1 = pcb.get_footprint("R1")
    r2 = pcb.get_footprint("R2")
    assert r1.position.x == 10
    assert r1.position.y == 10
    assert r2.position.x == 15  # 10 + 5 spacing
    assert r2.position.y == 10


def test_net_manager_integration():
    """Test net manager integration."""
    pcb = PCBBoard()

    # Add footprints and connect them
    pcb.add_footprint("R1", "Resistor_SMD:R_0603_1608Metric", 10, 20)
    pcb.add_footprint("R2", "Resistor_SMD:R_0603_1608Metric", 30, 20)
    pcb.connect_pads("R1", "1", "R2", "1", "Signal")

    # Test nets property
    nets = pcb.nets
    assert len(nets) > 0

    # Test net manager methods
    net_stats = pcb.net.get_net_statistics()
    assert isinstance(net_stats, dict)


def test_routing_manager_integration():
    """Test routing manager integration."""
    pcb = PCBBoard()

    # Add a track via routing manager
    from kicad_pcb_api import Point
    track_uuid = pcb.routing.add_track(
        Point(0, 0), Point(10, 10),
        width=0.25, layer="F.Cu"
    )

    assert track_uuid is not None

    # Verify track was added
    tracks = list(pcb.tracks)
    assert len(tracks) == 1


def test_collections_sync_on_load(tmp_path):
    """Test that collections sync correctly when loading a file."""
    # Create and save PCB
    pcb1 = PCBBoard()
    pcb1.add_footprint("R1", "Resistor_SMD:R_0603_1608Metric", 10, 20)

    file_path = tmp_path / "test.kicad_pcb"
    pcb1.save(file_path)

    # Load in new instance
    pcb2 = PCBBoard(str(file_path))

    # Verify collections are synced
    assert len(list(pcb2.footprints)) == 1
    assert pcb2.footprints.get_by_reference("R1") is not None