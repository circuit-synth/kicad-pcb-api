"""
Tests for TrackCollection.

Following kicad-sch-api WireCollection pattern for track management.
"""

import pytest
from kicad_pcb_api.collections.tracks import TrackCollection
from kicad_pcb_api.core.types import Track, Point


class TestTrackCollectionBasics:
    """Test basic track collection operations."""

    def test_create_empty_collection(self):
        """Test creating empty track collection."""
        collection = TrackCollection()
        assert len(collection) == 0

    def test_add_track(self):
        """Test adding a track to collection."""
        collection = TrackCollection()
        track = Track(
            start=Point(10.0, 20.0),
            end=Point(30.0, 40.0),
            width=0.25,
            layer="F.Cu",
            net=1,
            uuid="track-uuid-1"
        )

        collection.add(track)

        assert len(collection) == 1
        assert collection.get("track-uuid-1") == track

    def test_add_duplicate_uuid_raises_error(self):
        """Test that adding duplicate UUID raises error."""
        collection = TrackCollection()
        track1 = Track(
            start=Point(10.0, 20.0),
            end=Point(30.0, 40.0),
            width=0.25,
            layer="F.Cu",
            net=1,
            uuid="track-uuid-1"
        )
        track2 = Track(
            start=Point(50.0, 60.0),
            end=Point(70.0, 80.0),
            width=0.25,
            layer="F.Cu",
            net=1,
            uuid="track-uuid-1"  # Duplicate UUID
        )

        collection.add(track1)

        with pytest.raises(ValueError, match="already exists"):
            collection.add(track2)


class TestTrackCollectionNetIndex:
    """Test net-based indexing."""

    def test_filter_by_net(self):
        """Test filtering tracks by net number."""
        collection = TrackCollection()
        collection.add(Track(
            start=Point(10.0, 20.0),
            end=Point(30.0, 40.0),
            width=0.25,
            layer="F.Cu",
            net=1,
            uuid="track-uuid-1"
        ))
        collection.add(Track(
            start=Point(50.0, 60.0),
            end=Point(70.0, 80.0),
            width=0.25,
            layer="F.Cu",
            net=1,
            uuid="track-uuid-2"
        ))
        collection.add(Track(
            start=Point(100.0, 110.0),
            end=Point(120.0, 130.0),
            width=0.25,
            layer="F.Cu",
            net=2,
            uuid="track-uuid-3"
        ))

        net1_tracks = collection.filter_by_net(1)

        assert len(net1_tracks) == 2
        assert all(track.net == 1 for track in net1_tracks)

    def test_filter_by_net_no_matches(self):
        """Test filtering by net with no matches."""
        collection = TrackCollection()
        collection.add(Track(
            start=Point(10.0, 20.0),
            end=Point(30.0, 40.0),
            width=0.25,
            layer="F.Cu",
            net=1,
            uuid="track-uuid-1"
        ))

        result = collection.filter_by_net(999)

        assert len(result) == 0

    def test_get_by_net(self):
        """Test getting tracks grouped by net."""
        collection = TrackCollection()
        collection.add(Track(
            start=Point(10.0, 20.0),
            end=Point(30.0, 40.0),
            width=0.25,
            layer="F.Cu",
            net=1,
            uuid="track-uuid-1"
        ))
        collection.add(Track(
            start=Point(50.0, 60.0),
            end=Point(70.0, 80.0),
            width=0.25,
            layer="F.Cu",
            net=2,
            uuid="track-uuid-2"
        ))
        collection.add(Track(
            start=Point(100.0, 110.0),
            end=Point(120.0, 130.0),
            width=0.25,
            layer="F.Cu",
            net=2,
            uuid="track-uuid-3"
        ))

        by_net = collection.get_by_net()

        assert 1 in by_net
        assert 2 in by_net
        assert len(by_net[1]) == 1
        assert len(by_net[2]) == 2


class TestTrackCollectionLayerIndex:
    """Test layer-based indexing."""

    def test_filter_by_layer(self):
        """Test filtering tracks by layer."""
        collection = TrackCollection()
        collection.add(Track(
            start=Point(10.0, 20.0),
            end=Point(30.0, 40.0),
            width=0.25,
            layer="F.Cu",
            net=1,
            uuid="track-uuid-1"
        ))
        collection.add(Track(
            start=Point(50.0, 60.0),
            end=Point(70.0, 80.0),
            width=0.25,
            layer="B.Cu",
            net=1,
            uuid="track-uuid-2"
        ))
        collection.add(Track(
            start=Point(100.0, 110.0),
            end=Point(120.0, 130.0),
            width=0.25,
            layer="F.Cu",
            net=2,
            uuid="track-uuid-3"
        ))

        front_tracks = collection.filter_by_layer("F.Cu")

        assert len(front_tracks) == 2
        assert all(track.layer == "F.Cu" for track in front_tracks)

    def test_get_by_layer(self):
        """Test getting tracks grouped by layer."""
        collection = TrackCollection()
        collection.add(Track(
            start=Point(10.0, 20.0),
            end=Point(30.0, 40.0),
            width=0.25,
            layer="F.Cu",
            net=1,
            uuid="track-uuid-1"
        ))
        collection.add(Track(
            start=Point(50.0, 60.0),
            end=Point(70.0, 80.0),
            width=0.25,
            layer="B.Cu",
            net=1,
            uuid="track-uuid-2"
        ))

        by_layer = collection.get_by_layer()

        assert "F.Cu" in by_layer
        assert "B.Cu" in by_layer
        assert len(by_layer["F.Cu"]) == 1
        assert len(by_layer["B.Cu"]) == 1


class TestTrackCollectionNetAndLayer:
    """Test filtering by both net and layer."""

    def test_filter_by_net_and_layer(self):
        """Test filtering tracks by both net and layer."""
        collection = TrackCollection()
        collection.add(Track(
            start=Point(10.0, 20.0),
            end=Point(30.0, 40.0),
            width=0.25,
            layer="F.Cu",
            net=1,
            uuid="track-uuid-1"
        ))
        collection.add(Track(
            start=Point(50.0, 60.0),
            end=Point(70.0, 80.0),
            width=0.25,
            layer="B.Cu",
            net=1,
            uuid="track-uuid-2"
        ))
        collection.add(Track(
            start=Point(100.0, 110.0),
            end=Point(120.0, 130.0),
            width=0.25,
            layer="F.Cu",
            net=2,
            uuid="track-uuid-3"
        ))

        result = collection.filter_by_net_and_layer(1, "F.Cu")

        assert len(result) == 1
        assert result[0].net == 1
        assert result[0].layer == "F.Cu"


class TestTrackCollectionWidth:
    """Test filtering by track width."""

    def test_filter_by_width(self):
        """Test filtering tracks by width."""
        collection = TrackCollection()
        collection.add(Track(
            start=Point(10.0, 20.0),
            end=Point(30.0, 40.0),
            width=0.25,
            layer="F.Cu",
            net=1,
            uuid="track-uuid-1"
        ))
        collection.add(Track(
            start=Point(50.0, 60.0),
            end=Point(70.0, 80.0),
            width=0.5,
            layer="F.Cu",
            net=1,
            uuid="track-uuid-2"
        ))
        collection.add(Track(
            start=Point(100.0, 110.0),
            end=Point(120.0, 130.0),
            width=0.25,
            layer="F.Cu",
            net=2,
            uuid="track-uuid-3"
        ))

        thin_tracks = collection.filter_by_width(0.25)

        assert len(thin_tracks) == 2
        assert all(track.width == 0.25 for track in thin_tracks)

    def test_filter_by_min_width(self):
        """Test filtering tracks by minimum width."""
        collection = TrackCollection()
        collection.add(Track(
            start=Point(10.0, 20.0),
            end=Point(30.0, 40.0),
            width=0.15,
            layer="F.Cu",
            net=1,
            uuid="track-uuid-1"
        ))
        collection.add(Track(
            start=Point(50.0, 60.0),
            end=Point(70.0, 80.0),
            width=0.25,
            layer="F.Cu",
            net=1,
            uuid="track-uuid-2"
        ))
        collection.add(Track(
            start=Point(100.0, 110.0),
            end=Point(120.0, 130.0),
            width=0.5,
            layer="F.Cu",
            net=2,
            uuid="track-uuid-3"
        ))

        wide_tracks = collection.find(lambda t: t.width >= 0.25)

        assert len(wide_tracks) == 2
        assert all(track.width >= 0.25 for track in wide_tracks)


class TestTrackCollectionLength:
    """Test track length calculations."""

    def test_get_track_length(self):
        """Test calculating individual track length."""
        track = Track(
            start=Point(0.0, 0.0),
            end=Point(3.0, 4.0),  # 3-4-5 triangle
            width=0.25,
            layer="F.Cu",
            net=1,
            uuid="track-uuid-1"
        )

        length = track.get_length()

        assert abs(length - 5.0) < 0.001

    def test_get_total_length_by_net(self):
        """Test calculating total track length for a net."""
        collection = TrackCollection()
        collection.add(Track(
            start=Point(0.0, 0.0),
            end=Point(10.0, 0.0),  # Length 10
            width=0.25,
            layer="F.Cu",
            net=1,
            uuid="track-uuid-1"
        ))
        collection.add(Track(
            start=Point(10.0, 0.0),
            end=Point(10.0, 5.0),  # Length 5
            width=0.25,
            layer="F.Cu",
            net=1,
            uuid="track-uuid-2"
        ))
        collection.add(Track(
            start=Point(0.0, 0.0),
            end=Point(20.0, 0.0),  # Length 20 (different net)
            width=0.25,
            layer="F.Cu",
            net=2,
            uuid="track-uuid-3"
        ))

        total_length = collection.get_total_length_by_net(1)

        assert abs(total_length - 15.0) < 0.001


class TestTrackCollectionSearch:
    """Test advanced search capabilities."""

    def test_search_by_region(self):
        """Test searching tracks within a region."""
        collection = TrackCollection()
        collection.add(Track(
            start=Point(10.0, 10.0),
            end=Point(20.0, 20.0),
            width=0.25,
            layer="F.Cu",
            net=1,
            uuid="track-uuid-1"
        ))
        collection.add(Track(
            start=Point(50.0, 50.0),
            end=Point(60.0, 60.0),
            width=0.25,
            layer="F.Cu",
            net=1,
            uuid="track-uuid-2"
        ))
        collection.add(Track(
            start=Point(100.0, 100.0),
            end=Point(110.0, 110.0),
            width=0.25,
            layer="F.Cu",
            net=2,
            uuid="track-uuid-3"
        ))

        # Find tracks in region (0, 0) to (30, 30)
        in_region = collection.find(
            lambda t: (0 <= t.start.x <= 30 and 0 <= t.start.y <= 30) or
                     (0 <= t.end.x <= 30 and 0 <= t.end.y <= 30)
        )

        assert len(in_region) == 1
        assert in_region[0].uuid == "track-uuid-1"

    def test_search_connected_tracks(self):
        """Test finding tracks connected to a point."""
        collection = TrackCollection()
        connection_point = Point(10.0, 10.0)

        collection.add(Track(
            start=Point(0.0, 0.0),
            end=connection_point,
            width=0.25,
            layer="F.Cu",
            net=1,
            uuid="track-uuid-1"
        ))
        collection.add(Track(
            start=connection_point,
            end=Point(20.0, 20.0),
            width=0.25,
            layer="F.Cu",
            net=1,
            uuid="track-uuid-2"
        ))
        collection.add(Track(
            start=Point(50.0, 50.0),
            end=Point(60.0, 60.0),
            width=0.25,
            layer="F.Cu",
            net=1,
            uuid="track-uuid-3"
        ))

        # Find tracks connected to the point
        connected = collection.find(
            lambda t: (t.start.x == connection_point.x and t.start.y == connection_point.y) or
                     (t.end.x == connection_point.x and t.end.y == connection_point.y)
        )

        assert len(connected) == 2
