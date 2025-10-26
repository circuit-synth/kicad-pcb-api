"""
Track collection with specialized indexing and track-specific operations.

Extends IndexedCollection to provide track-specific features like
net indexing, layer filtering, width filtering, and length calculations.

Based on kicad-sch-api's WireCollection pattern.
"""

import logging
from collections import defaultdict
from typing import Any, Dict, List, Optional

from ..core.types import Track
from .base import IndexedCollection

logger = logging.getLogger(__name__)


class TrackCollection(IndexedCollection[Track]):
    """
    Collection class for efficient track (trace) management.

    Extends IndexedCollection with track-specific features:
    - Net-based indexing for fast track lookup by net
    - Layer indexing for filtering tracks by copper layer
    - Width filtering for design rule checking
    - Length calculations for individual and net totals
    - Connected track finding
    """

    def __init__(self, tracks: Optional[List[Track]] = None):
        """
        Initialize track collection.

        Args:
            tracks: Initial list of tracks to add
        """
        # Additional indexes
        self._net_index: Dict[int, List[int]] = defaultdict(list)
        self._layer_index: Dict[str, List[int]] = defaultdict(list)

        # Call parent init
        super().__init__(tracks)

        logger.debug(f"TrackCollection initialized with {len(self._items)} tracks")

    # Abstract method implementations

    def _get_item_uuid(self, item: Track) -> str:
        """Extract UUID from track."""
        return item.uuid

    def _create_item(self, **kwargs) -> Track:
        """Create new track instance."""
        return Track(**kwargs)

    def _build_additional_indexes(self) -> None:
        """Build track-specific indexes."""
        # Build net index
        self._net_index = defaultdict(list)
        for i, track in enumerate(self._items):
            if track.net is not None:
                self._net_index[track.net].append(i)

        # Build layer index
        self._layer_index = defaultdict(list)
        for i, track in enumerate(self._items):
            if track.layer:
                self._layer_index[track.layer].append(i)

        logger.debug(
            f"Built indexes: {len(self._net_index)} nets, "
            f"{len(self._layer_index)} layers"
        )

    # Track-specific access methods

    def filter_by_net(self, net: int) -> List[Track]:
        """
        Filter tracks by net number.

        Args:
            net: Net number to filter by

        Returns:
            List of tracks on the specified net

        Example:
            gnd_tracks = collection.filter_by_net(0)  # GND is usually net 0
        """
        self._ensure_indexes_current()

        indices = self._net_index.get(net, [])
        return [self._items[i] for i in indices]

    def get_by_net(self) -> Dict[int, List[Track]]:
        """
        Get tracks grouped by net number.

        Returns:
            Dictionary mapping net numbers to lists of tracks

        Example:
            by_net = collection.get_by_net()
            for net_num, tracks in by_net.items():
                total_length = sum(t.get_length() for t in tracks)
                print(f"Net {net_num}: {len(tracks)} tracks, {total_length:.2f}mm")
        """
        self._ensure_indexes_current()

        result = {}
        for net_num, indices in self._net_index.items():
            result[net_num] = [self._items[i] for i in indices]
        return result

    def filter_by_layer(self, layer: str) -> List[Track]:
        """
        Filter tracks by layer.

        Args:
            layer: Layer name (e.g., "F.Cu", "B.Cu", "In1.Cu")

        Returns:
            List of tracks on the specified layer

        Example:
            front_tracks = collection.filter_by_layer("F.Cu")
        """
        self._ensure_indexes_current()

        indices = self._layer_index.get(layer, [])
        return [self._items[i] for i in indices]

    def get_by_layer(self) -> Dict[str, List[Track]]:
        """
        Get tracks grouped by layer.

        Returns:
            Dictionary mapping layer names to lists of tracks

        Example:
            by_layer = collection.get_by_layer()
            for layer, tracks in by_layer.items():
                print(f"{layer}: {len(tracks)} tracks")
        """
        self._ensure_indexes_current()

        result = {}
        for layer, indices in self._layer_index.items():
            result[layer] = [self._items[i] for i in indices]
        return result

    def filter_by_net_and_layer(self, net: int, layer: str) -> List[Track]:
        """
        Filter tracks by both net and layer.

        Args:
            net: Net number
            layer: Layer name

        Returns:
            List of tracks matching both criteria

        Example:
            front_gnd = collection.filter_by_net_and_layer(0, "F.Cu")
        """
        return self.filter(net=net, layer=layer)

    def filter_by_width(self, width: float) -> List[Track]:
        """
        Filter tracks by exact width.

        Args:
            width: Track width in millimeters

        Returns:
            List of tracks with the specified width

        Example:
            standard_tracks = collection.filter_by_width(0.25)
        """
        return self.filter(width=width)

    # Length calculations

    def get_total_length_by_net(self, net: int) -> float:
        """
        Calculate total track length for a net.

        Args:
            net: Net number

        Returns:
            Total length in millimeters

        Example:
            total_length = collection.get_total_length_by_net(1)
            print(f"Net 1 total trace length: {total_length:.2f}mm")
        """
        tracks = self.filter_by_net(net)
        return sum(track.get_length() for track in tracks)

    def get_total_length_by_layer(self, layer: str) -> float:
        """
        Calculate total track length on a layer.

        Args:
            layer: Layer name

        Returns:
            Total length in millimeters
        """
        tracks = self.filter_by_layer(layer)
        return sum(track.get_length() for track in tracks)

    def get_length_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive length statistics.

        Returns:
            Dictionary with length statistics including:
            - total_length: Total length of all tracks
            - length_by_net: Total length per net
            - length_by_layer: Total length per layer
            - average_length: Average track length
            - min_length: Minimum track length
            - max_length: Maximum track length
        """
        if len(self._items) == 0:
            return {
                "total_length": 0.0,
                "length_by_net": {},
                "length_by_layer": {},
                "average_length": 0.0,
                "min_length": 0.0,
                "max_length": 0.0,
            }

        lengths = [track.get_length() for track in self._items]
        total_length = sum(lengths)

        # Calculate by net
        length_by_net = {}
        for net_num in self._net_index.keys():
            length_by_net[net_num] = self.get_total_length_by_net(net_num)

        # Calculate by layer
        length_by_layer = {}
        for layer in self._layer_index.keys():
            length_by_layer[layer] = self.get_total_length_by_layer(layer)

        return {
            "total_length": total_length,
            "length_by_net": length_by_net,
            "length_by_layer": length_by_layer,
            "average_length": total_length / len(self._items),
            "min_length": min(lengths),
            "max_length": max(lengths),
        }

    # Statistics and debugging

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get detailed collection statistics.

        Returns:
            Dictionary with collection statistics including track counts
            by net, layer, and width statistics
        """
        base_stats = super().get_statistics()

        self._ensure_indexes_current()

        # Add track-specific stats
        base_stats.update({
            "unique_nets": len(self._net_index),
            "unique_layers": len(self._layer_index),
            "tracks_by_net": {
                net: len(indices) for net, indices in self._net_index.items()
            },
            "tracks_by_layer": {
                layer: len(indices) for layer, indices in self._layer_index.items()
            },
        })

        # Add length statistics
        length_stats = self.get_length_statistics()
        base_stats["length_statistics"] = length_stats

        return base_stats
