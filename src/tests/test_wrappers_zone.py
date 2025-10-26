"""
Tests for ZoneWrapper.

Following pattern from test_wrappers_footprint.py for zone wrapper functionality.
"""

import pytest
from kicad_pcb_api.collections.zones import ZoneCollection
from kicad_pcb_api.core.exceptions import ValidationError
from kicad_pcb_api.core.types import Point, Zone
from kicad_pcb_api.wrappers.zone import ZoneWrapper


class TestZoneWrapperBasics:
    """Test basic zone wrapper operations."""

    def test_create_wrapper(self):
        """Test creating a zone wrapper."""
        collection = ZoneCollection()
        zone = Zone(
            layer="F.Cu",
            net=0,
            polygon=[Point(0, 0), Point(10, 0), Point(10, 10), Point(0, 10)],
            uuid="z1",
        )
        collection.add(zone)

        wrapper = ZoneWrapper(zone, collection)

        assert wrapper.uuid == "z1"
        assert wrapper.layer == "F.Cu"
        assert wrapper.net == 0

    def test_wrapper_data_property(self):
        """Test accessing underlying data."""
        collection = ZoneCollection()
        zone = Zone(
            layer="F.Cu", polygon=[Point(0, 0), Point(10, 0), Point(10, 10)], uuid="z1"
        )
        collection.add(zone)

        wrapper = ZoneWrapper(zone, collection)

        assert wrapper.data == zone


class TestZoneWrapperLayerProperty:
    """Test layer property with validation."""

    def test_get_layer(self):
        """Test getting layer."""
        collection = ZoneCollection()
        zone = Zone(
            layer="F.Cu", polygon=[Point(0, 0), Point(10, 0), Point(10, 10)], uuid="z1"
        )
        collection.add(zone)
        wrapper = ZoneWrapper(zone, collection)

        assert wrapper.layer == "F.Cu"

    def test_set_valid_layer(self):
        """Test setting valid layer."""
        collection = ZoneCollection()
        zone = Zone(
            layer="F.Cu", polygon=[Point(0, 0), Point(10, 0), Point(10, 10)], uuid="z1"
        )
        collection.add(zone)
        wrapper = ZoneWrapper(zone, collection)

        wrapper.layer = "B.Cu"

        assert wrapper.layer == "B.Cu"
        assert collection.is_modified

    def test_set_inner_layer(self):
        """Test setting inner layer."""
        collection = ZoneCollection()
        zone = Zone(
            layer="F.Cu", polygon=[Point(0, 0), Point(10, 0), Point(10, 10)], uuid="z1"
        )
        collection.add(zone)
        wrapper = ZoneWrapper(zone, collection)

        wrapper.layer = "In1.Cu"

        assert wrapper.layer == "In1.Cu"

    def test_set_invalid_layer_raises_error(self):
        """Test setting invalid layer raises error."""
        collection = ZoneCollection()
        zone = Zone(
            layer="F.Cu", polygon=[Point(0, 0), Point(10, 0), Point(10, 10)], uuid="z1"
        )
        collection.add(zone)
        wrapper = ZoneWrapper(zone, collection)

        with pytest.raises(ValidationError, match="copper layer"):
            wrapper.layer = "F.SilkS"


class TestZoneWrapperNetProperty:
    """Test net property with validation."""

    def test_get_net(self):
        """Test getting net."""
        collection = ZoneCollection()
        zone = Zone(
            layer="F.Cu", net=5, polygon=[Point(0, 0), Point(10, 0), Point(10, 10)], uuid="z1"
        )
        collection.add(zone)
        wrapper = ZoneWrapper(zone, collection)

        assert wrapper.net == 5

    def test_set_valid_net(self):
        """Test setting valid net."""
        collection = ZoneCollection()
        zone = Zone(
            layer="F.Cu", net=0, polygon=[Point(0, 0), Point(10, 0), Point(10, 10)], uuid="z1"
        )
        collection.add(zone)
        wrapper = ZoneWrapper(zone, collection)

        wrapper.net = 10

        assert wrapper.net == 10
        assert collection.is_modified

    def test_set_net_to_none(self):
        """Test setting net to None."""
        collection = ZoneCollection()
        zone = Zone(
            layer="F.Cu", net=5, polygon=[Point(0, 0), Point(10, 0), Point(10, 10)], uuid="z1"
        )
        collection.add(zone)
        wrapper = ZoneWrapper(zone, collection)

        wrapper.net = None

        assert wrapper.net is None

    def test_set_negative_net_raises_error(self):
        """Test setting negative net raises error."""
        collection = ZoneCollection()
        zone = Zone(
            layer="F.Cu", net=0, polygon=[Point(0, 0), Point(10, 0), Point(10, 10)], uuid="z1"
        )
        collection.add(zone)
        wrapper = ZoneWrapper(zone, collection)

        with pytest.raises(ValidationError, match="non-negative"):
            wrapper.net = -1


class TestZoneWrapperPolygonProperty:
    """Test polygon property with validation."""

    def test_get_polygon(self):
        """Test getting polygon."""
        collection = ZoneCollection()
        polygon = [Point(0, 0), Point(10, 0), Point(10, 10), Point(0, 10)]
        zone = Zone(layer="F.Cu", polygon=polygon, uuid="z1")
        collection.add(zone)
        wrapper = ZoneWrapper(zone, collection)

        assert wrapper.polygon == polygon

    def test_set_valid_polygon(self):
        """Test setting valid polygon."""
        collection = ZoneCollection()
        zone = Zone(
            layer="F.Cu", polygon=[Point(0, 0), Point(10, 0), Point(10, 10)], uuid="z1"
        )
        collection.add(zone)
        wrapper = ZoneWrapper(zone, collection)

        new_polygon = [Point(5, 5), Point(15, 5), Point(15, 15), Point(5, 15)]
        wrapper.polygon = new_polygon

        assert wrapper.polygon == new_polygon
        assert collection.is_modified

    def test_set_polygon_with_less_than_3_points_raises_error(self):
        """Test setting polygon with less than 3 points raises error."""
        collection = ZoneCollection()
        zone = Zone(
            layer="F.Cu", polygon=[Point(0, 0), Point(10, 0), Point(10, 10)], uuid="z1"
        )
        collection.add(zone)
        wrapper = ZoneWrapper(zone, collection)

        with pytest.raises(ValidationError, match="at least 3 points"):
            wrapper.polygon = [Point(0, 0), Point(10, 0)]


class TestZoneWrapperAreaCalculation:
    """Test area calculation methods."""

    def test_get_area_square(self):
        """Test area calculation for square."""
        collection = ZoneCollection()
        # 10x10 square = 100 mm²
        zone = Zone(
            layer="F.Cu",
            polygon=[Point(0, 0), Point(10, 0), Point(10, 10), Point(0, 10)],
            uuid="z1",
        )
        collection.add(zone)
        wrapper = ZoneWrapper(zone, collection)

        area = wrapper.get_area()

        assert area == pytest.approx(100.0, rel=1e-6)

    def test_get_area_triangle(self):
        """Test area calculation for triangle."""
        collection = ZoneCollection()
        # Triangle with base 10, height 10 = 50 mm²
        zone = Zone(
            layer="F.Cu",
            polygon=[Point(0, 0), Point(10, 0), Point(5, 10)],
            uuid="z1",
        )
        collection.add(zone)
        wrapper = ZoneWrapper(zone, collection)

        area = wrapper.get_area()

        assert area == pytest.approx(50.0, rel=1e-6)

    def test_get_area_with_less_than_3_points(self):
        """Test area calculation with invalid polygon."""
        collection = ZoneCollection()
        zone = Zone(layer="F.Cu", polygon=[Point(0, 0), Point(10, 0)], uuid="z1")
        collection.add(zone)
        wrapper = ZoneWrapper(zone, collection)

        area = wrapper.get_area()

        assert area == 0.0


class TestZoneWrapperBoundingBox:
    """Test bounding box calculation."""

    def test_get_bounding_box(self):
        """Test getting bounding box."""
        collection = ZoneCollection()
        zone = Zone(
            layer="F.Cu",
            polygon=[Point(5, 10), Point(15, 5), Point(20, 15), Point(10, 20)],
            uuid="z1",
        )
        collection.add(zone)
        wrapper = ZoneWrapper(zone, collection)

        bbox = wrapper.get_bounding_box()

        assert bbox is not None
        min_x, min_y, max_x, max_y = bbox
        assert min_x == 5
        assert min_y == 5
        assert max_x == 20
        assert max_y == 20

    def test_get_bounding_box_with_empty_polygon(self):
        """Test bounding box with empty polygon."""
        collection = ZoneCollection()
        zone = Zone(layer="F.Cu", polygon=[], uuid="z1")
        collection.add(zone)
        wrapper = ZoneWrapper(zone, collection)

        bbox = wrapper.get_bounding_box()

        assert bbox is None


class TestZoneWrapperContainsPoint:
    """Test point containment checking."""

    def test_contains_point_inside_square(self):
        """Test point inside square zone."""
        collection = ZoneCollection()
        zone = Zone(
            layer="F.Cu",
            polygon=[Point(0, 0), Point(10, 0), Point(10, 10), Point(0, 10)],
            uuid="z1",
        )
        collection.add(zone)
        wrapper = ZoneWrapper(zone, collection)

        assert wrapper.contains_point(Point(5, 5)) is True

    def test_contains_point_outside_square(self):
        """Test point outside square zone."""
        collection = ZoneCollection()
        zone = Zone(
            layer="F.Cu",
            polygon=[Point(0, 0), Point(10, 0), Point(10, 10), Point(0, 10)],
            uuid="z1",
        )
        collection.add(zone)
        wrapper = ZoneWrapper(zone, collection)

        assert wrapper.contains_point(Point(15, 15)) is False

    def test_contains_point_on_edge(self):
        """Test point on edge of zone."""
        collection = ZoneCollection()
        zone = Zone(
            layer="F.Cu",
            polygon=[Point(0, 0), Point(10, 0), Point(10, 10), Point(0, 10)],
            uuid="z1",
        )
        collection.add(zone)
        wrapper = ZoneWrapper(zone, collection)

        # Point on edge behavior depends on ray casting implementation
        # This test just verifies it doesn't crash
        result = wrapper.contains_point(Point(5, 0))
        assert isinstance(result, bool)

    def test_contains_point_inside_triangle(self):
        """Test point inside triangular zone."""
        collection = ZoneCollection()
        zone = Zone(
            layer="F.Cu",
            polygon=[Point(0, 0), Point(10, 0), Point(5, 10)],
            uuid="z1",
        )
        collection.add(zone)
        wrapper = ZoneWrapper(zone, collection)

        assert wrapper.contains_point(Point(5, 3)) is True

    def test_contains_point_with_invalid_polygon(self):
        """Test contains_point with invalid polygon."""
        collection = ZoneCollection()
        zone = Zone(layer="F.Cu", polygon=[Point(0, 0), Point(10, 0)], uuid="z1")
        collection.add(zone)
        wrapper = ZoneWrapper(zone, collection)

        assert wrapper.contains_point(Point(5, 5)) is False


class TestZoneWrapperOverlaps:
    """Test zone overlap detection."""

    def test_overlaps_with_intersecting_zones(self):
        """Test overlaps with intersecting zones."""
        collection = ZoneCollection()
        zone1 = Zone(
            layer="F.Cu",
            polygon=[Point(0, 0), Point(10, 0), Point(10, 10), Point(0, 10)],
            uuid="z1",
        )
        zone2 = Zone(
            layer="F.Cu",
            polygon=[Point(5, 5), Point(15, 5), Point(15, 15), Point(5, 15)],
            uuid="z2",
        )
        collection.add(zone1)
        collection.add(zone2)

        wrapper1 = ZoneWrapper(zone1, collection)
        wrapper2 = ZoneWrapper(zone2, collection)

        assert wrapper1.overlaps(wrapper2) is True
        assert wrapper2.overlaps(wrapper1) is True

    def test_overlaps_with_non_intersecting_zones(self):
        """Test overlaps with non-intersecting zones."""
        collection = ZoneCollection()
        zone1 = Zone(
            layer="F.Cu",
            polygon=[Point(0, 0), Point(10, 0), Point(10, 10), Point(0, 10)],
            uuid="z1",
        )
        zone2 = Zone(
            layer="F.Cu",
            polygon=[Point(20, 20), Point(30, 20), Point(30, 30), Point(20, 30)],
            uuid="z2",
        )
        collection.add(zone1)
        collection.add(zone2)

        wrapper1 = ZoneWrapper(zone1, collection)
        wrapper2 = ZoneWrapper(zone2, collection)

        assert wrapper1.overlaps(wrapper2) is False

    def test_overlaps_with_empty_polygon(self):
        """Test overlaps with empty polygon."""
        collection = ZoneCollection()
        zone1 = Zone(
            layer="F.Cu",
            polygon=[Point(0, 0), Point(10, 0), Point(10, 10)],
            uuid="z1",
        )
        zone2 = Zone(layer="F.Cu", polygon=[], uuid="z2")
        collection.add(zone1)
        collection.add(zone2)

        wrapper1 = ZoneWrapper(zone1, collection)
        wrapper2 = ZoneWrapper(zone2, collection)

        assert wrapper1.overlaps(wrapper2) is False


class TestZoneWrapperPerimeter:
    """Test perimeter calculation."""

    def test_get_perimeter_square(self):
        """Test perimeter calculation for square."""
        collection = ZoneCollection()
        # 10x10 square = perimeter 40
        zone = Zone(
            layer="F.Cu",
            polygon=[Point(0, 0), Point(10, 0), Point(10, 10), Point(0, 10)],
            uuid="z1",
        )
        collection.add(zone)
        wrapper = ZoneWrapper(zone, collection)

        perimeter = wrapper.get_perimeter()

        assert perimeter == pytest.approx(40.0, rel=1e-6)

    def test_get_perimeter_triangle(self):
        """Test perimeter calculation for triangle."""
        collection = ZoneCollection()
        # Right triangle 3-4-5
        zone = Zone(
            layer="F.Cu",
            polygon=[Point(0, 0), Point(3, 0), Point(0, 4)],
            uuid="z1",
        )
        collection.add(zone)
        wrapper = ZoneWrapper(zone, collection)

        perimeter = wrapper.get_perimeter()

        # 3 + 4 + 5 = 12
        assert perimeter == pytest.approx(12.0, rel=1e-6)

    def test_get_perimeter_with_invalid_polygon(self):
        """Test perimeter with invalid polygon."""
        collection = ZoneCollection()
        zone = Zone(layer="F.Cu", polygon=[Point(0, 0)], uuid="z1")
        collection.add(zone)
        wrapper = ZoneWrapper(zone, collection)

        perimeter = wrapper.get_perimeter()

        assert perimeter == 0.0


class TestZoneWrapperOtherProperties:
    """Test other properties and methods."""

    def test_net_name_property(self):
        """Test net_name property."""
        collection = ZoneCollection()
        zone = Zone(
            layer="F.Cu",
            net=0,
            net_name="GND",
            polygon=[Point(0, 0), Point(10, 0), Point(10, 10)],
            uuid="z1",
        )
        collection.add(zone)
        wrapper = ZoneWrapper(zone, collection)

        assert wrapper.net_name == "GND"

        wrapper.net_name = "VCC"
        assert wrapper.net_name == "VCC"

    def test_priority_property(self):
        """Test priority property."""
        collection = ZoneCollection()
        zone = Zone(
            layer="F.Cu",
            priority=5,
            polygon=[Point(0, 0), Point(10, 0), Point(10, 10)],
            uuid="z1",
        )
        collection.add(zone)
        wrapper = ZoneWrapper(zone, collection)

        assert wrapper.priority == 5

        wrapper.priority = 10
        assert wrapper.priority == 10

    def test_filled_property(self):
        """Test filled property."""
        collection = ZoneCollection()
        zone = Zone(
            layer="F.Cu",
            filled=True,
            polygon=[Point(0, 0), Point(10, 0), Point(10, 10)],
            uuid="z1",
        )
        collection.add(zone)
        wrapper = ZoneWrapper(zone, collection)

        assert wrapper.filled is True

        wrapper.filled = False
        assert wrapper.filled is False

    def test_is_copper_layer(self):
        """Test is_copper_layer method."""
        collection = ZoneCollection()
        zone = Zone(
            layer="F.Cu", polygon=[Point(0, 0), Point(10, 0), Point(10, 10)], uuid="z1"
        )
        collection.add(zone)
        wrapper = ZoneWrapper(zone, collection)

        assert wrapper.is_copper_layer() is True


class TestZoneWrapperRepresentation:
    """Test string representation."""

    def test_repr_with_net(self):
        """Test __repr__ with net assigned."""
        collection = ZoneCollection()
        zone = Zone(
            layer="F.Cu",
            net=0,
            net_name="GND",
            priority=5,
            polygon=[Point(0, 0), Point(10, 0), Point(10, 10), Point(0, 10)],
            uuid="z1",
        )
        collection.add(zone)
        wrapper = ZoneWrapper(zone, collection)

        repr_str = repr(wrapper)

        assert "ZoneWrapper" in repr_str
        assert "F.Cu" in repr_str
        assert "net=0" in repr_str
        assert "priority=5" in repr_str
        assert "100.00mm²" in repr_str

    def test_repr_without_net(self):
        """Test __repr__ without net assigned."""
        collection = ZoneCollection()
        zone = Zone(
            layer="B.Cu",
            polygon=[Point(0, 0), Point(10, 0), Point(10, 10)],
            uuid="z1",
        )
        collection.add(zone)
        wrapper = ZoneWrapper(zone, collection)

        repr_str = repr(wrapper)

        assert "ZoneWrapper" in repr_str
        assert "B.Cu" in repr_str
        assert "no net" in repr_str


class TestZoneWrapperModificationTracking:
    """Test modification tracking."""

    def test_modification_tracking_on_layer_change(self):
        """Test that changing layer marks collection as modified."""
        collection = ZoneCollection()
        zone = Zone(
            layer="F.Cu", polygon=[Point(0, 0), Point(10, 0), Point(10, 10)], uuid="z1"
        )
        collection.add(zone)
        collection.mark_clean()

        wrapper = ZoneWrapper(zone, collection)
        wrapper.layer = "B.Cu"

        assert collection.is_modified

    def test_modification_tracking_on_net_change(self):
        """Test that changing net marks collection as modified."""
        collection = ZoneCollection()
        zone = Zone(
            layer="F.Cu", net=0, polygon=[Point(0, 0), Point(10, 0), Point(10, 10)], uuid="z1"
        )
        collection.add(zone)
        collection.mark_clean()

        wrapper = ZoneWrapper(zone, collection)
        wrapper.net = 5

        assert collection.is_modified

    def test_modification_tracking_on_polygon_change(self):
        """Test that changing polygon marks collection as modified."""
        collection = ZoneCollection()
        zone = Zone(
            layer="F.Cu", polygon=[Point(0, 0), Point(10, 0), Point(10, 10)], uuid="z1"
        )
        collection.add(zone)
        collection.mark_clean()

        wrapper = ZoneWrapper(zone, collection)
        wrapper.polygon = [Point(5, 5), Point(15, 5), Point(15, 15), Point(5, 15)]

        assert collection.is_modified
