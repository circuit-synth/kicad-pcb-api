"""
Tests for FootprintCollection.

Following kicad-sch-api ComponentCollection pattern for footprint management.
"""

import pytest
from kicad_pcb_api.collections.footprints import FootprintCollection
from kicad_pcb_api.core.types import Footprint, Point, Pad


class TestFootprintCollectionBasics:
    """Test basic footprint collection operations."""

    def test_create_empty_collection(self):
        """Test creating empty footprint collection."""
        collection = FootprintCollection()
        assert len(collection) == 0

    def test_add_footprint(self):
        """Test adding a footprint to collection."""
        collection = FootprintCollection()
        fp = Footprint(
            library="Resistor_SMD",
            name="R_0603_1608Metric",
            position=Point(10.0, 20.0),
            reference="R1",
            value="10k",
            uuid="fp-uuid-1"
        )

        collection.add(fp)

        assert len(collection) == 1
        assert collection.get("fp-uuid-1") == fp

    def test_add_duplicate_uuid_raises_error(self):
        """Test that adding duplicate UUID raises error."""
        collection = FootprintCollection()
        fp1 = Footprint(
            library="Resistor_SMD",
            name="R_0603_1608Metric",
            position=Point(10.0, 20.0),
            reference="R1",
            value="10k",
            uuid="fp-uuid-1"
        )
        fp2 = Footprint(
            library="Resistor_SMD",
            name="R_0603_1608Metric",
            position=Point(30.0, 40.0),
            reference="R2",
            value="20k",
            uuid="fp-uuid-1"  # Duplicate UUID
        )

        collection.add(fp1)

        with pytest.raises(ValueError, match="already exists"):
            collection.add(fp2)


class TestFootprintCollectionReferenceIndex:
    """Test reference-based indexing."""

    def test_get_by_reference(self):
        """Test retrieving footprint by reference."""
        collection = FootprintCollection()
        fp = Footprint(
            library="Resistor_SMD",
            name="R_0603_1608Metric",
            position=Point(10.0, 20.0),
            reference="R1",
            value="10k",
            uuid="fp-uuid-1"
        )
        collection.add(fp)

        result = collection.get_by_reference("R1")

        # get_by_reference now returns a wrapper
        assert result is not None
        assert result.data == fp  # Compare underlying data
        assert result.value == "10k"

    def test_get_nonexistent_reference_returns_none(self):
        """Test that nonexistent reference returns None."""
        collection = FootprintCollection()

        result = collection.get_by_reference("R999")

        assert result is None

    def test_reference_index_updated_on_add(self):
        """Test that reference index is updated when adding."""
        collection = FootprintCollection()
        fp1 = Footprint(
            library="Resistor_SMD",
            name="R_0603_1608Metric",
            position=Point(10.0, 20.0),
            reference="R1",
            value="10k",
            uuid="fp-uuid-1"
        )
        fp2 = Footprint(
            library="Resistor_SMD",
            name="R_0603_1608Metric",
            position=Point(30.0, 40.0),
            reference="R2",
            value="20k",
            uuid="fp-uuid-2"
        )

        collection.add(fp1)
        collection.add(fp2)

        # get_by_reference now returns wrappers
        result1 = collection.get_by_reference("R1")
        result2 = collection.get_by_reference("R2")
        assert result1 is not None and result1.data == fp1
        assert result2 is not None and result2.data == fp2

    def test_reference_index_updated_on_remove(self):
        """Test that reference index is updated when removing."""
        collection = FootprintCollection()
        fp = Footprint(
            library="Resistor_SMD",
            name="R_0603_1608Metric",
            position=Point(10.0, 20.0),
            reference="R1",
            value="10k",
            uuid="fp-uuid-1"
        )
        collection.add(fp)

        collection.remove("fp-uuid-1")

        assert collection.get_by_reference("R1") is None


class TestFootprintCollectionLibIdFilter:
    """Test filtering by library ID."""

    def test_filter_by_lib_id(self):
        """Test filtering footprints by library ID."""
        collection = FootprintCollection()
        collection.add(Footprint(
            library="Resistor_SMD",
            name="R_0603_1608Metric",
            position=Point(10.0, 20.0),
            reference="R1",
            value="10k",
            uuid="fp-uuid-1"
        ))
        collection.add(Footprint(
            library="Resistor_SMD",
            name="R_0805_2012Metric",
            position=Point(30.0, 40.0),
            reference="R2",
            value="20k",
            uuid="fp-uuid-2"
        ))
        collection.add(Footprint(
            library="Capacitor_SMD",
            name="C_0603_1608Metric",
            position=Point(50.0, 60.0),
            reference="C1",
            value="100nF",
            uuid="fp-uuid-3"
        ))

        resistors = collection.filter_by_lib_id("Resistor_SMD")

        assert len(resistors) == 2
        assert all(fp.library == "Resistor_SMD" for fp in resistors)

    def test_get_by_lib_id(self):
        """Test getting footprints grouped by library ID."""
        collection = FootprintCollection()
        collection.add(Footprint(
            library="Resistor_SMD",
            name="R_0603_1608Metric",
            position=Point(10.0, 20.0),
            reference="R1",
            value="10k",
            uuid="fp-uuid-1"
        ))
        collection.add(Footprint(
            library="Resistor_SMD",
            name="R_0805_2012Metric",
            position=Point(30.0, 40.0),
            reference="R2",
            value="20k",
            uuid="fp-uuid-2"
        ))
        collection.add(Footprint(
            library="Capacitor_SMD",
            name="C_0603_1608Metric",
            position=Point(50.0, 60.0),
            reference="C1",
            value="100nF",
            uuid="fp-uuid-3"
        ))

        by_lib_id = collection.get_by_lib_id()

        assert "Resistor_SMD" in by_lib_id
        assert "Capacitor_SMD" in by_lib_id
        assert len(by_lib_id["Resistor_SMD"]) == 2
        assert len(by_lib_id["Capacitor_SMD"]) == 1


class TestFootprintCollectionNetFilter:
    """Test filtering by net."""

    def test_filter_by_net(self):
        """Test filtering footprints by net name."""
        collection = FootprintCollection()

        # Create footprints with pads on different nets
        fp1 = Footprint(
            library="Resistor_SMD",
            name="R_0603_1608Metric",
            position=Point(10.0, 20.0),
            reference="R1",
            value="10k",
            uuid="fp-uuid-1"
        )
        fp1.pads = [
            Pad(number="1", type="smd", shape="rect",
                position=Point(0, 0), size=(0.8, 0.95),
                layers=["F.Cu"], net=1, net_name="GND",
                uuid="pad-uuid-1"),
            Pad(number="2", type="smd", shape="rect",
                position=Point(1.65, 0), size=(0.8, 0.95),
                layers=["F.Cu"], net=2, net_name="VCC",
                uuid="pad-uuid-2"),
        ]

        fp2 = Footprint(
            library="Resistor_SMD",
            name="R_0603_1608Metric",
            position=Point(30.0, 40.0),
            reference="R2",
            value="20k",
            uuid="fp-uuid-2"
        )
        fp2.pads = [
            Pad(number="1", type="smd", shape="rect",
                position=Point(0, 0), size=(0.8, 0.95),
                layers=["F.Cu"], net=1, net_name="GND",
                uuid="pad-uuid-3"),
            Pad(number="2", type="smd", shape="rect",
                position=Point(1.65, 0), size=(0.8, 0.95),
                layers=["F.Cu"], net=3, net_name="SIGNAL",
                uuid="pad-uuid-4"),
        ]

        collection.add(fp1)
        collection.add(fp2)

        gnd_footprints = collection.filter_by_net("GND")

        # filter_by_net now returns wrappers
        assert len(gnd_footprints) == 2
        assert any(w.data == fp1 for w in gnd_footprints)
        assert any(w.data == fp2 for w in gnd_footprints)

    def test_filter_by_net_no_matches(self):
        """Test filtering by net with no matches."""
        collection = FootprintCollection()
        fp = Footprint(
            library="Resistor_SMD",
            name="R_0603_1608Metric",
            position=Point(10.0, 20.0),
            reference="R1",
            value="10k",
            uuid="fp-uuid-1"
        )
        collection.add(fp)

        result = collection.filter_by_net("NONEXISTENT")

        assert len(result) == 0


class TestFootprintCollectionLayerFilter:
    """Test filtering by layer."""

    def test_filter_by_layer(self):
        """Test filtering footprints by layer."""
        collection = FootprintCollection()
        collection.add(Footprint(
            library="Resistor_SMD",
            name="R_0603_1608Metric",
            position=Point(10.0, 20.0),
            reference="R1",
            value="10k",
            layer="F.Cu",
            uuid="fp-uuid-1"
        ))
        collection.add(Footprint(
            library="Resistor_SMD",
            name="R_0603_1608Metric",
            position=Point(30.0, 40.0),
            reference="R2",
            value="20k",
            layer="B.Cu",
            uuid="fp-uuid-2"
        ))
        collection.add(Footprint(
            library="Capacitor_SMD",
            name="C_0603_1608Metric",
            position=Point(50.0, 60.0),
            reference="C1",
            value="100nF",
            layer="F.Cu",
            uuid="fp-uuid-3"
        ))

        front_footprints = collection.filter_by_layer("F.Cu")

        assert len(front_footprints) == 2
        assert all(fp.layer == "F.Cu" for fp in front_footprints)


class TestFootprintCollectionBulkOperations:
    """Test bulk operations on footprints."""

    def test_bulk_update_value(self):
        """Test bulk updating footprint values."""
        collection = FootprintCollection()
        collection.add(Footprint(
            library="Resistor_SMD",
            name="R_0603_1608Metric",
            position=Point(10.0, 20.0),
            reference="R1",
            value="10k",
            uuid="fp-uuid-1"
        ))
        collection.add(Footprint(
            library="Resistor_SMD",
            name="R_0603_1608Metric",
            position=Point(30.0, 40.0),
            reference="R2",
            value="10k",
            uuid="fp-uuid-2"
        ))

        # Bulk update all 10k resistors to 20k
        updated = collection.bulk_update(
            criteria={'value': '10k'},
            updates={'value': '20k'}
        )

        assert updated == 2
        assert collection.get_by_reference("R1").value == "20k"
        assert collection.get_by_reference("R2").value == "20k"

    def test_bulk_update_layer(self):
        """Test bulk updating footprint layers."""
        collection = FootprintCollection()
        collection.add(Footprint(
            library="Resistor_SMD",
            name="R_0603_1608Metric",
            position=Point(10.0, 20.0),
            reference="R1",
            value="10k",
            layer="F.Cu",
            uuid="fp-uuid-1"
        ))
        collection.add(Footprint(
            library="Resistor_SMD",
            name="R_0603_1608Metric",
            position=Point(30.0, 40.0),
            reference="R2",
            value="20k",
            layer="F.Cu",
            uuid="fp-uuid-2"
        ))

        # Move all front components to back
        updated = collection.bulk_update(
            criteria={'layer': 'F.Cu'},
            updates={'layer': 'B.Cu'}
        )

        assert updated == 2
        assert collection.get_by_reference("R1").layer == "B.Cu"
        assert collection.get_by_reference("R2").layer == "B.Cu"


class TestFootprintCollectionSearch:
    """Test advanced search capabilities."""

    def test_search_by_reference_pattern(self):
        """Test searching by reference pattern."""
        collection = FootprintCollection()
        collection.add(Footprint(
            library="Resistor_SMD",
            name="R_0603_1608Metric",
            position=Point(10.0, 20.0),
            reference="R1",
            value="10k",
            uuid="fp-uuid-1"
        ))
        collection.add(Footprint(
            library="Resistor_SMD",
            name="R_0603_1608Metric",
            position=Point(30.0, 40.0),
            reference="R2",
            value="20k",
            uuid="fp-uuid-2"
        ))
        collection.add(Footprint(
            library="Capacitor_SMD",
            name="C_0603_1608Metric",
            position=Point(50.0, 60.0),
            reference="C1",
            value="100nF",
            uuid="fp-uuid-3"
        ))

        # Search for all resistors (references starting with R)
        resistors = collection.find(lambda fp: fp.reference.startswith("R"))

        assert len(resistors) == 2
        assert all(fp.reference.startswith("R") for fp in resistors)

    def test_search_by_position_region(self):
        """Test searching by position (within bounding box)."""
        collection = FootprintCollection()
        collection.add(Footprint(
            library="Resistor_SMD",
            name="R_0603_1608Metric",
            position=Point(10.0, 20.0),
            reference="R1",
            value="10k",
            uuid="fp-uuid-1"
        ))
        collection.add(Footprint(
            library="Resistor_SMD",
            name="R_0603_1608Metric",
            position=Point(30.0, 40.0),
            reference="R2",
            value="20k",
            uuid="fp-uuid-2"
        ))
        collection.add(Footprint(
            library="Capacitor_SMD",
            name="C_0603_1608Metric",
            position=Point(100.0, 100.0),
            reference="C1",
            value="100nF",
            uuid="fp-uuid-3"
        ))

        # Find footprints in region (0, 0) to (50, 50)
        in_region = collection.find(
            lambda fp: 0 <= fp.position.x <= 50 and 0 <= fp.position.y <= 50
        )

        # find() returns raw dataclasses, get_by_reference() returns wrappers
        assert len(in_region) == 2
        r1_wrapper = collection.get_by_reference("R1")
        r2_wrapper = collection.get_by_reference("R2")
        assert r1_wrapper is not None and r1_wrapper.data in in_region
        assert r2_wrapper is not None and r2_wrapper.data in in_region
