"""Routing and trace management."""

import logging
from typing import Dict, List, Optional

from ..core.types import Point, Track
from .base import BaseManager

logger = logging.getLogger(__name__)


class RoutingManager(BaseManager):
    """Manager for routing operations.

    Handles trace routing, length matching, and routing optimization.
    """

    def add_track(
        self,
        start: Point,
        end: Point,
        width: float,
        layer: str,
        net: Optional[int] = None,
        net_name: Optional[str] = None,
    ) -> str:
        """Add a new track to the board.

        Args:
            start: Track start point
            end: Track end point
            width: Track width in mm
            layer: Layer name (e.g., 'F.Cu')
            net: Optional net number
            net_name: Optional net name

        Returns:
            UUID of created track
        """
        import uuid

        track = Track(
            start=start,
            end=end,
            width=width,
            layer=layer,
            net=net,
            net_name=net_name,
            uuid=str(uuid.uuid4()),
        )

        self.board.tracks.add(track)
        logger.debug(f"Added track on {layer}, net={net}")

        return track.uuid

    def route_manhattan(
        self,
        start: Point,
        end: Point,
        width: float,
        layer: str,
        net: Optional[int] = None,
        net_name: Optional[str] = None,
    ) -> List[str]:
        """Route using Manhattan (90-degree) routing.

        Creates two track segments: horizontal then vertical, or vice versa.

        Args:
            start: Starting point
            end: Ending point
            width: Track width in mm
            layer: Layer name
            net: Optional net number
            net_name: Optional net name

        Returns:
            List of track UUIDs created
        """
        import uuid

        uuids = []

        # Route horizontally first, then vertically
        mid_point = Point(end.x, start.y)

        # First segment (horizontal)
        if start.x != end.x:
            track1 = Track(
                start=start,
                end=mid_point,
                width=width,
                layer=layer,
                net=net,
                net_name=net_name,
                uuid=str(uuid.uuid4()),
            )
            self.board.tracks.add(track1)
            uuids.append(track1.uuid)

        # Second segment (vertical)
        if start.y != end.y:
            track2 = Track(
                start=mid_point,
                end=end,
                width=width,
                layer=layer,
                net=net,
                net_name=net_name,
                uuid=str(uuid.uuid4()),
            )
            self.board.tracks.add(track2)
            uuids.append(track2.uuid)

        logger.info(f"Created Manhattan route with {len(uuids)} segments")
        return uuids

    def get_total_track_length_by_net(self, net: int) -> float:
        """Get total track length for a specific net.

        Args:
            net: Net number

        Returns:
            Total length in mm
        """
        tracks = [t for t in self.board.tracks if t.net == net]
        return sum(t.length for t in tracks)

    def get_length_statistics_by_net(self) -> Dict[int, Dict[str, float]]:
        """Get track length statistics grouped by net.

        Returns:
            Dictionary mapping net numbers to statistics:
            - total_length: Total track length in mm
            - track_count: Number of track segments
            - average_length: Average segment length
        """
        stats = {}

        # Group tracks by net
        nets = {}
        for track in self.board.tracks:
            if track.net is not None:
                if track.net not in nets:
                    nets[track.net] = []
                nets[track.net].append(track)

        # Calculate statistics for each net
        for net, tracks in nets.items():
            lengths = [t.length for t in tracks]
            stats[net] = {
                "total_length": sum(lengths),
                "track_count": len(tracks),
                "average_length": sum(lengths) / len(lengths) if lengths else 0.0,
                "min_length": min(lengths) if lengths else 0.0,
                "max_length": max(lengths) if lengths else 0.0,
            }

        return stats

    def find_stubs(self, min_stub_length: float = 0.1) -> List[str]:
        """Find track stubs (dead-end tracks).

        Args:
            min_stub_length: Minimum length to consider a stub

        Returns:
            List of track UUIDs that are stubs
        """
        # This is a simplified implementation
        # A proper implementation would analyze connectivity
        stubs = []

        for track in self.board.tracks:
            if track.length < min_stub_length:
                stubs.append(track.uuid)

        return stubs

    def optimize_track_order(self) -> None:
        """Optimize track storage order for rendering performance.

        Groups tracks by layer and net for better rendering performance.
        """
        # Sort tracks by layer, then net
        def sort_key(track):
            return (track.data.layer, track.data.net or 0)

        sorted_tracks = sorted(self.board.tracks, key=sort_key)

        # Replace collection items with sorted list
        self.board.tracks._items = [t.data for t in sorted_tracks]
        self.board.tracks._dirty_indexes = True

        logger.info("Optimized track storage order")
