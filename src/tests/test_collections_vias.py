"""
Tests for ViaCollection.

Vias are specialized PCB elements that connect different copper layers.
"""

import pytest
from kicad_pcb_api.collections.vias import ViaCollection
from kicad_pcb_api.core.types import Via, Point


class TestViaCollectionBasics:
    """Test basic via collection operations."""

    def test_create_empty_collection(self):
        """Test creating empty via collection."""
        collection = ViaCollection()
        assert len(collection) == 0

    def test_add_via(self):
        """Test adding a via to collection."""
        collection = ViaCollection()
        via = Via(
            position=Point(10.0, 20.0),
            size=0.8,
            drill=0.4,
            layers=["F.Cu", "B.Cu"],
            net=1,
            uuid="via-uuid-1"
        )

        collection.add(via)

        assert len(collection) == 1
        assert collection.get("via-uuid-1") == via

    def test_add_duplicate_uuid_raises_error(self):
        """Test that adding duplicate UUID raises error."""
        collection = ViaCollection()
        via1 = Via(
            position=Point(10.0, 20.0),
            size=0.8,
            drill=0.4,
            layers=["F.Cu", "B.Cu"],
            net=1,
            uuid="via-uuid-1"
        )
        via2 = Via(
            position=Point(30.0, 40.0),
            size=0.8,
            drill=0.4,
            layers=["F.Cu", "B.Cu"],
            net=1,
            uuid="via-uuid-1"  # Duplicate UUID
        )

        collection.add(via1)

        with pytest.raises(ValueError, match="already exists"):
            collection.add(via2)


class TestViaCollectionNetIndex:
    """Test net-based indexing."""

    def test_filter_by_net(self):
        """Test filtering vias by net number."""
        collection = ViaCollection()
        collection.add(Via(
            position=Point(10.0, 20.0),
            size=0.8,
            drill=0.4,
            layers=["F.Cu", "B.Cu"],
            net=1,
            uuid="via-uuid-1"
        ))
        collection.add(Via(
            position=Point(30.0, 40.0),
            size=0.8,
            drill=0.4,
            layers=["F.Cu", "B.Cu"],
            net=1,
            uuid="via-uuid-2"
        ))
        collection.add(Via(
            position=Point(50.0, 60.0),
            size=0.8,
            drill=0.4,
            layers=["F.Cu", "B.Cu"],
            net=2,
            uuid="via-uuid-3"
        ))

        net1_vias = collection.filter_by_net(1)

        assert len(net1_vias) == 2
        assert all(via.net == 1 for via in net1_vias)

    def test_get_by_net(self):
        """Test getting vias grouped by net."""
        collection = ViaCollection()
        collection.add(Via(
            position=Point(10.0, 20.0),
            size=0.8,
            drill=0.4,
            layers=["F.Cu", "B.Cu"],
            net=1,
            uuid="via-uuid-1"
        ))
        collection.add(Via(
            position=Point(30.0, 40.0),
            size=0.8,
            drill=0.4,
            layers=["F.Cu", "B.Cu"],
            net=2,
            uuid="via-uuid-2"
        ))

        by_net = collection.get_by_net()

        assert 1 in by_net
        assert 2 in by_net
        assert len(by_net[1]) == 1
        assert len(by_net[2]) == 1


class TestViaCollectionLayerPairs:
    """Test layer pair indexing."""

    def test_filter_by_layer_pair(self):
        """Test filtering vias by layer pair."""
        collection = ViaCollection()
        collection.add(Via(
            position=Point(10.0, 20.0),
            size=0.8,
            drill=0.4,
            layers=["F.Cu", "B.Cu"],  # Through-hole via
            net=1,
            uuid="via-uuid-1"
        ))
        collection.add(Via(
            position=Point(30.0, 40.0),
            size=0.6,
            drill=0.3,
            layers=["F.Cu", "In1.Cu"],  # Blind via
            net=1,
            uuid="via-uuid-2"
        ))
        collection.add(Via(
            position=Point(50.0, 60.0),
            size=0.8,
            drill=0.4,
            layers=["F.Cu", "B.Cu"],  # Through-hole via
            net=2,
            uuid="via-uuid-3"
        ))

        through_vias = collection.filter_by_layer_pair("F.Cu", "B.Cu")

        assert len(through_vias) == 2
        assert all("F.Cu" in via.layers and "B.Cu" in via.layers
                  for via in through_vias)

    def test_filter_through_vias(self):
        """Test filtering for through-hole vias."""
        collection = ViaCollection()
        collection.add(Via(
            position=Point(10.0, 20.0),
            size=0.8,
            drill=0.4,
            layers=["F.Cu", "B.Cu"],
            net=1,
            uuid="via-uuid-1"
        ))
        collection.add(Via(
            position=Point(30.0, 40.0),
            size=0.6,
            drill=0.3,
            layers=["F.Cu", "In1.Cu"],  # Not through-hole
            net=1,
            uuid="via-uuid-2"
        ))

        through_vias = collection.filter_through_vias()

        assert len(through_vias) == 1
        assert through_vias[0].uuid == "via-uuid-1"

    def test_filter_blind_buried_vias(self):
        """Test filtering for blind/buried vias."""
        collection = ViaCollection()
        collection.add(Via(
            position=Point(10.0, 20.0),
            size=0.8,
            drill=0.4,
            layers=["F.Cu", "B.Cu"],  # Through-hole
            net=1,
            uuid="via-uuid-1"
        ))
        collection.add(Via(
            position=Point(30.0, 40.0),
            size=0.6,
            drill=0.3,
            layers=["F.Cu", "In1.Cu"],  # Blind
            net=1,
            uuid="via-uuid-2"
        ))
        collection.add(Via(
            position=Point(50.0, 60.0),
            size=0.6,
            drill=0.3,
            layers=["In1.Cu", "In2.Cu"],  # Buried
            net=2,
            uuid="via-uuid-3"
        ))

        blind_buried = collection.filter_blind_buried_vias()

        assert len(blind_buried) == 2
        assert all(not ("F.Cu" in via.layers and "B.Cu" in via.layers)
                  for via in blind_buried)


class TestViaCollectionSize:
    """Test filtering by via size."""

    def test_filter_by_size(self):
        """Test filtering vias by size."""
        collection = ViaCollection()
        collection.add(Via(
            position=Point(10.0, 20.0),
            size=0.8,
            drill=0.4,
            layers=["F.Cu", "B.Cu"],
            net=1,
            uuid="via-uuid-1"
        ))
        collection.add(Via(
            position=Point(30.0, 40.0),
            size=0.6,
            drill=0.3,
            layers=["F.Cu", "B.Cu"],
            net=1,
            uuid="via-uuid-2"
        ))

        large_vias = collection.filter_by_size(0.8)

        assert len(large_vias) == 1
        assert large_vias[0].size == 0.8

    def test_filter_by_drill(self):
        """Test filtering vias by drill size."""
        collection = ViaCollection()
        collection.add(Via(
            position=Point(10.0, 20.0),
            size=0.8,
            drill=0.4,
            layers=["F.Cu", "B.Cu"],
            net=1,
            uuid="via-uuid-1"
        ))
        collection.add(Via(
            position=Point(30.0, 40.0),
            size=0.6,
            drill=0.3,
            layers=["F.Cu", "B.Cu"],
            net=1,
            uuid="via-uuid-2"
        ))

        large_drill_vias = collection.filter_by_drill(0.4)

        assert len(large_drill_vias) == 1
        assert large_drill_vias[0].drill == 0.4


class TestViaCollectionRegion:
    """Test spatial filtering."""

    def test_filter_by_region(self):
        """Test filtering vias within a region."""
        collection = ViaCollection()
        collection.add(Via(
            position=Point(10.0, 10.0),
            size=0.8,
            drill=0.4,
            layers=["F.Cu", "B.Cu"],
            net=1,
            uuid="via-uuid-1"
        ))
        collection.add(Via(
            position=Point(30.0, 30.0),
            size=0.8,
            drill=0.4,
            layers=["F.Cu", "B.Cu"],
            net=1,
            uuid="via-uuid-2"
        ))
        collection.add(Via(
            position=Point(100.0, 100.0),
            size=0.8,
            drill=0.4,
            layers=["F.Cu", "B.Cu"],
            net=2,
            uuid="via-uuid-3"
        ))

        # Find vias in region (0, 0) to (50, 50)
        in_region = collection.find(
            lambda v: 0 <= v.position.x <= 50 and 0 <= v.position.y <= 50
        )

        assert len(in_region) == 2

    def test_find_nearest_via(self):
        """Test finding nearest via to a point."""
        collection = ViaCollection()
        collection.add(Via(
            position=Point(10.0, 10.0),
            size=0.8,
            drill=0.4,
            layers=["F.Cu", "B.Cu"],
            net=1,
            uuid="via-uuid-1"
        ))
        collection.add(Via(
            position=Point(30.0, 30.0),
            size=0.8,
            drill=0.4,
            layers=["F.Cu", "B.Cu"],
            net=1,
            uuid="via-uuid-2"
        ))
        collection.add(Via(
            position=Point(100.0, 100.0),
            size=0.8,
            drill=0.4,
            layers=["F.Cu", "B.Cu"],
            net=2,
            uuid="via-uuid-3"
        ))

        target = Point(12.0, 12.0)
        nearest = collection.find_nearest(target)

        assert nearest.uuid == "via-uuid-1"


class TestViaCollectionStatistics:
    """Test via statistics."""

    def test_get_statistics(self):
        """Test getting via statistics."""
        collection = ViaCollection()
        collection.add(Via(
            position=Point(10.0, 10.0),
            size=0.8,
            drill=0.4,
            layers=["F.Cu", "B.Cu"],
            net=1,
            uuid="via-uuid-1"
        ))
        collection.add(Via(
            position=Point(30.0, 30.0),
            size=0.6,
            drill=0.3,
            layers=["F.Cu", "In1.Cu"],
            net=1,
            uuid="via-uuid-2"
        ))

        stats = collection.get_statistics()

        assert stats["item_count"] == 2
        assert stats["unique_nets"] == 1
        assert "through_via_count" in stats
        assert "blind_buried_via_count" in stats
