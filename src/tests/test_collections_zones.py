"""
Tests for ZoneCollection.

Following pattern from test_collections_footprints.py for zone management.
"""

import pytest
from kicad_pcb_api.collections.zones import ZoneCollection
from kicad_pcb_api.core.types import Point, Zone


class TestZoneCollectionBasics:
    """Test basic zone collection operations."""

    def test_create_empty_collection(self):
        """Test creating empty zone collection."""
        collection = ZoneCollection()
        assert len(collection) == 0

    def test_add_zone(self):
        """Test adding a zone to collection."""
        collection = ZoneCollection()
        zone = Zone(
            layer="F.Cu",
            net=0,
            net_name="GND",
            polygon=[Point(0, 0), Point(10, 0), Point(10, 10), Point(0, 10)],
            uuid="zone-uuid-1",
        )

        collection.add(zone)

        assert len(collection) == 1
        assert collection.get("zone-uuid-1") == zone

    def test_add_duplicate_uuid_raises_error(self):
        """Test that adding duplicate UUID raises error."""
        collection = ZoneCollection()
        zone1 = Zone(
            layer="F.Cu",
            net=0,
            net_name="GND",
            polygon=[Point(0, 0), Point(10, 0), Point(10, 10), Point(0, 10)],
            uuid="zone-uuid-1",
        )
        zone2 = Zone(
            layer="B.Cu",
            net=1,
            net_name="VCC",
            polygon=[Point(20, 20), Point(30, 20), Point(30, 30), Point(20, 30)],
            uuid="zone-uuid-1",  # Duplicate UUID
        )

        collection.add(zone1)

        with pytest.raises(ValueError, match="already exists"):
            collection.add(zone2)

    def test_remove_zone(self):
        """Test removing zone from collection."""
        collection = ZoneCollection()
        zone = Zone(
            layer="F.Cu",
            net=0,
            polygon=[Point(0, 0), Point(10, 0), Point(10, 10)],
            uuid="zone-uuid-1",
        )
        collection.add(zone)

        result = collection.remove("zone-uuid-1")

        assert result is True
        assert len(collection) == 0

    def test_remove_nonexistent_zone(self):
        """Test removing nonexistent zone returns False."""
        collection = ZoneCollection()

        result = collection.remove("nonexistent-uuid")

        assert result is False


class TestZoneCollectionNetIndex:
    """Test net-based indexing."""

    def test_filter_by_net(self):
        """Test filtering zones by net."""
        collection = ZoneCollection()
        gnd_zone = Zone(
            layer="F.Cu",
            net=0,
            net_name="GND",
            polygon=[Point(0, 0), Point(10, 0), Point(10, 10)],
            uuid="zone-1",
        )
        vcc_zone = Zone(
            layer="F.Cu",
            net=1,
            net_name="VCC",
            polygon=[Point(20, 20), Point(30, 20), Point(30, 30)],
            uuid="zone-2",
        )
        collection.add(gnd_zone)
        collection.add(vcc_zone)

        gnd_zones = collection.filter_by_net(0)

        assert len(gnd_zones) == 1
        assert gnd_zones[0].data == gnd_zone

    def test_filter_by_net_returns_empty_list_if_none(self):
        """Test filter_by_net returns empty list if no zones on that net."""
        collection = ZoneCollection()

        zones = collection.filter_by_net(99)

        assert len(zones) == 0

    def test_get_zones_by_net(self):
        """Test grouping zones by net."""
        collection = ZoneCollection()
        zone1 = Zone(
            layer="F.Cu", net=0, polygon=[Point(0, 0), Point(10, 0), Point(10, 10)], uuid="z1"
        )
        zone2 = Zone(
            layer="B.Cu", net=0, polygon=[Point(0, 0), Point(10, 0), Point(10, 10)], uuid="z2"
        )
        zone3 = Zone(
            layer="F.Cu", net=1, polygon=[Point(0, 0), Point(10, 0), Point(10, 10)], uuid="z3"
        )
        collection.add(zone1)
        collection.add(zone2)
        collection.add(zone3)

        by_net = collection.get_zones_by_net()

        assert len(by_net) == 2
        assert len(by_net[0]) == 2  # Two zones on net 0
        assert len(by_net[1]) == 1  # One zone on net 1

    def test_net_index_updated_on_add(self):
        """Test that net index is updated when adding zones."""
        collection = ZoneCollection()

        zone1 = Zone(
            layer="F.Cu", net=0, polygon=[Point(0, 0), Point(10, 0), Point(10, 10)], uuid="z1"
        )
        collection.add(zone1)

        zones = collection.filter_by_net(0)
        assert len(zones) == 1

        zone2 = Zone(
            layer="F.Cu", net=0, polygon=[Point(0, 0), Point(10, 0), Point(10, 10)], uuid="z2"
        )
        collection.add(zone2)

        zones = collection.filter_by_net(0)
        assert len(zones) == 2


class TestZoneCollectionLayerIndex:
    """Test layer-based indexing."""

    def test_filter_by_layer(self):
        """Test filtering zones by layer."""
        collection = ZoneCollection()
        front_zone = Zone(
            layer="F.Cu",
            net=0,
            polygon=[Point(0, 0), Point(10, 0), Point(10, 10)],
            uuid="zone-1",
        )
        back_zone = Zone(
            layer="B.Cu",
            net=0,
            polygon=[Point(0, 0), Point(10, 0), Point(10, 10)],
            uuid="zone-2",
        )
        collection.add(front_zone)
        collection.add(back_zone)

        front_zones = collection.filter_by_layer("F.Cu")

        assert len(front_zones) == 1
        assert front_zones[0].data == front_zone

    def test_get_zones_by_layer(self):
        """Test grouping zones by layer."""
        collection = ZoneCollection()
        zone1 = Zone(
            layer="F.Cu", net=0, polygon=[Point(0, 0), Point(10, 0), Point(10, 10)], uuid="z1"
        )
        zone2 = Zone(
            layer="F.Cu", net=1, polygon=[Point(0, 0), Point(10, 0), Point(10, 10)], uuid="z2"
        )
        zone3 = Zone(
            layer="B.Cu", net=0, polygon=[Point(0, 0), Point(10, 0), Point(10, 10)], uuid="z3"
        )
        collection.add(zone1)
        collection.add(zone2)
        collection.add(zone3)

        by_layer = collection.get_zones_by_layer()

        assert len(by_layer) == 2
        assert len(by_layer["F.Cu"]) == 2
        assert len(by_layer["B.Cu"]) == 1


class TestZoneCollectionAreaFiltering:
    """Test area-based filtering."""

    def test_filter_by_area_finds_intersecting_zones(self):
        """Test filtering zones by bounding box."""
        collection = ZoneCollection()
        # Zone inside the bounding box
        zone1 = Zone(
            layer="F.Cu",
            polygon=[Point(5, 5), Point(15, 5), Point(15, 15), Point(5, 15)],
            uuid="z1",
        )
        # Zone outside the bounding box
        zone2 = Zone(
            layer="F.Cu",
            polygon=[Point(50, 50), Point(60, 50), Point(60, 60), Point(50, 60)],
            uuid="z2",
        )
        collection.add(zone1)
        collection.add(zone2)

        # Filter for zones in area 0-20, 0-20
        zones = collection.filter_by_area(0, 0, 20, 20)

        assert len(zones) == 1
        assert zones[0].data == zone1

    def test_filter_by_area_with_partial_overlap(self):
        """Test filtering zones with partial overlap."""
        collection = ZoneCollection()
        # Zone partially overlapping the bounding box
        zone = Zone(
            layer="F.Cu",
            polygon=[Point(-5, -5), Point(5, -5), Point(5, 5), Point(-5, 5)],
            uuid="z1",
        )
        collection.add(zone)

        # Filter for zones in area 0-10, 0-10 (partial overlap)
        zones = collection.filter_by_area(0, 0, 10, 10)

        assert len(zones) == 1

    def test_filter_by_area_with_no_zones(self):
        """Test filtering with no matching zones."""
        collection = ZoneCollection()
        zone = Zone(
            layer="F.Cu",
            polygon=[Point(50, 50), Point(60, 50), Point(60, 60)],
            uuid="z1",
        )
        collection.add(zone)

        zones = collection.filter_by_area(0, 0, 10, 10)

        assert len(zones) == 0


class TestZoneCollectionAreaCalculations:
    """Test area calculation methods."""

    def test_get_total_area_single_zone(self):
        """Test total area calculation for single zone."""
        collection = ZoneCollection()
        # 10x10 square = 100 mm²
        zone = Zone(
            layer="F.Cu",
            polygon=[Point(0, 0), Point(10, 0), Point(10, 10), Point(0, 10)],
            uuid="z1",
        )
        collection.add(zone)

        total_area = collection.get_total_area()

        assert total_area == pytest.approx(100.0, rel=1e-6)

    def test_get_total_area_multiple_zones(self):
        """Test total area calculation for multiple zones."""
        collection = ZoneCollection()
        # Two 10x10 squares = 200 mm²
        zone1 = Zone(
            layer="F.Cu",
            polygon=[Point(0, 0), Point(10, 0), Point(10, 10), Point(0, 10)],
            uuid="z1",
        )
        zone2 = Zone(
            layer="B.Cu",
            polygon=[Point(20, 20), Point(30, 20), Point(30, 30), Point(20, 30)],
            uuid="z2",
        )
        collection.add(zone1)
        collection.add(zone2)

        total_area = collection.get_total_area()

        assert total_area == pytest.approx(200.0, rel=1e-6)

    def test_get_total_area_with_empty_collection(self):
        """Test total area with empty collection."""
        collection = ZoneCollection()

        total_area = collection.get_total_area()

        assert total_area == 0.0

    def test_get_total_area_with_triangle(self):
        """Test area calculation with triangle."""
        collection = ZoneCollection()
        # Triangle with base 10, height 10 = 50 mm²
        zone = Zone(
            layer="F.Cu",
            polygon=[Point(0, 0), Point(10, 0), Point(5, 10)],
            uuid="z1",
        )
        collection.add(zone)

        total_area = collection.get_total_area()

        assert total_area == pytest.approx(50.0, rel=1e-6)


class TestZoneCollectionPriority:
    """Test priority-based operations."""

    def test_get_zones_sorted_by_priority_descending(self):
        """Test getting zones sorted by priority (highest first)."""
        collection = ZoneCollection()
        zone1 = Zone(
            layer="F.Cu",
            priority=1,
            polygon=[Point(0, 0), Point(10, 0), Point(10, 10)],
            uuid="z1",
        )
        zone2 = Zone(
            layer="F.Cu",
            priority=5,
            polygon=[Point(0, 0), Point(10, 0), Point(10, 10)],
            uuid="z2",
        )
        zone3 = Zone(
            layer="F.Cu",
            priority=3,
            polygon=[Point(0, 0), Point(10, 0), Point(10, 10)],
            uuid="z3",
        )
        collection.add(zone1)
        collection.add(zone2)
        collection.add(zone3)

        sorted_zones = collection.get_zones_sorted_by_priority()

        assert len(sorted_zones) == 3
        assert sorted_zones[0].data.priority == 5
        assert sorted_zones[1].data.priority == 3
        assert sorted_zones[2].data.priority == 1

    def test_get_zones_sorted_by_priority_ascending(self):
        """Test getting zones sorted by priority (lowest first)."""
        collection = ZoneCollection()
        zone1 = Zone(
            layer="F.Cu",
            priority=1,
            polygon=[Point(0, 0), Point(10, 0), Point(10, 10)],
            uuid="z1",
        )
        zone2 = Zone(
            layer="F.Cu",
            priority=5,
            polygon=[Point(0, 0), Point(10, 0), Point(10, 10)],
            uuid="z2",
        )
        collection.add(zone1)
        collection.add(zone2)

        sorted_zones = collection.get_zones_sorted_by_priority(descending=False)

        assert sorted_zones[0].data.priority == 1
        assert sorted_zones[1].data.priority == 5


class TestZoneCollectionStatistics:
    """Test collection statistics."""

    def test_get_statistics(self):
        """Test getting collection statistics."""
        collection = ZoneCollection()
        zone1 = Zone(
            layer="F.Cu",
            net=0,
            filled=True,
            polygon=[Point(0, 0), Point(10, 0), Point(10, 10), Point(0, 10)],
            uuid="z1",
        )
        zone2 = Zone(
            layer="B.Cu",
            net=1,
            filled=False,
            polygon=[Point(0, 0), Point(10, 0), Point(10, 10), Point(0, 10)],
            uuid="z2",
        )
        collection.add(zone1)
        collection.add(zone2)

        stats = collection.get_statistics()

        assert stats["item_count"] == 2
        assert stats["unique_nets"] == 2
        assert stats["unique_layers"] == 2
        assert stats["filled_zones"] == 1
        assert stats["unfilled_zones"] == 1
        assert stats["total_area_mm2"] == pytest.approx(200.0, rel=1e-6)

    def test_get_statistics_empty_collection(self):
        """Test statistics for empty collection."""
        collection = ZoneCollection()

        stats = collection.get_statistics()

        assert stats["item_count"] == 0
        assert stats["unique_nets"] == 0
        assert stats["unique_layers"] == 0
        assert stats["total_area_mm2"] == 0.0


class TestZoneCollectionIteration:
    """Test collection iteration and access."""

    def test_iterate_over_zones(self):
        """Test iterating over zones in collection."""
        collection = ZoneCollection()
        zone1 = Zone(
            layer="F.Cu", polygon=[Point(0, 0), Point(10, 0), Point(10, 10)], uuid="z1"
        )
        zone2 = Zone(
            layer="B.Cu", polygon=[Point(0, 0), Point(10, 0), Point(10, 10)], uuid="z2"
        )
        collection.add(zone1)
        collection.add(zone2)

        zones = list(collection)

        assert len(zones) == 2
        assert zones[0] == zone1
        assert zones[1] == zone2

    def test_index_access(self):
        """Test accessing zones by index."""
        collection = ZoneCollection()
        zone = Zone(
            layer="F.Cu", polygon=[Point(0, 0), Point(10, 0), Point(10, 10)], uuid="z1"
        )
        collection.add(zone)

        retrieved = collection[0]

        assert retrieved == zone

    def test_contains_by_uuid(self):
        """Test checking if UUID is in collection."""
        collection = ZoneCollection()
        zone = Zone(
            layer="F.Cu", polygon=[Point(0, 0), Point(10, 0), Point(10, 10)], uuid="z1"
        )
        collection.add(zone)

        assert "z1" in collection
        assert "nonexistent" not in collection


class TestZoneCollectionModificationTracking:
    """Test modification tracking."""

    def test_is_modified_after_add(self):
        """Test that collection is marked modified after adding zone."""
        collection = ZoneCollection()
        zone = Zone(
            layer="F.Cu", polygon=[Point(0, 0), Point(10, 0), Point(10, 10)], uuid="z1"
        )

        collection.add(zone)

        assert collection.is_modified

    def test_mark_clean(self):
        """Test marking collection as clean."""
        collection = ZoneCollection()
        zone = Zone(
            layer="F.Cu", polygon=[Point(0, 0), Point(10, 0), Point(10, 10)], uuid="z1"
        )
        collection.add(zone)

        collection.mark_clean()

        assert not collection.is_modified

    def test_is_modified_after_remove(self):
        """Test that collection is marked modified after removing zone."""
        collection = ZoneCollection()
        zone = Zone(
            layer="F.Cu", polygon=[Point(0, 0), Point(10, 0), Point(10, 10)], uuid="z1"
        )
        collection.add(zone)
        collection.mark_clean()

        collection.remove("z1")

        assert collection.is_modified
