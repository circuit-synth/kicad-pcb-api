"""
Via collection with specialized indexing and via-specific operations.

Extends IndexedCollection to provide via-specific features like
net indexing, layer pair filtering, size filtering, and spatial queries.
"""

import logging
import math
from collections import defaultdict
from typing import Any, Dict, List, Optional

from ..core.types import Via, Point
from ..wrappers.via import ViaWrapper
from .base import IndexedCollection

logger = logging.getLogger(__name__)


class ViaCollection(IndexedCollection[Via]):
    """
    Collection class for efficient via management.

    Extends IndexedCollection with via-specific features:
    - Net-based indexing for fast via lookup by net
    - Layer pair filtering for blind/buried via analysis
    - Size and drill filtering for DRC
    - Spatial queries (region, nearest via)
    - Through-hole vs blind/buried classification
    """

    def __init__(self, vias: Optional[List[Via]] = None):
        """
        Initialize via collection.

        Args:
            vias: Initial list of vias to add
        """
        # Additional indexes
        self._net_index: Dict[int, List[int]] = defaultdict(list)

        # Call parent init
        super().__init__(vias)

        logger.debug(f"ViaCollection initialized with {len(self._items)} vias")

    # Abstract method implementations

    def _get_item_uuid(self, item: Via) -> str:
        """Extract UUID from via."""
        return item.uuid

    def _create_item(self, **kwargs) -> Via:
        """Create new via instance."""
        return Via(**kwargs)

    def _build_additional_indexes(self) -> None:
        """Build via-specific indexes."""
        # Build net index
        self._net_index = defaultdict(list)
        for i, via in enumerate(self._items):
            if via.net is not None:
                self._net_index[via.net].append(i)

        logger.debug(f"Built indexes: {len(self._net_index)} nets")

    # Via-specific access methods

    def filter_by_net(self, net: int) -> List[ViaWrapper]:
        """
        Filter vias by net number.

        Args:
            net: Net number to filter by

        Returns:
            List of via wrappers on the specified net

        Example:
            gnd_vias = collection.filter_by_net(0)
        """
        self._ensure_indexes_current()

        indices = self._net_index.get(net, [])
        return [ViaWrapper(self._items[i], self) for i in indices]

    def get_by_net(self) -> Dict[int, List[ViaWrapper]]:
        """
        Get vias grouped by net number.

        Returns:
            Dictionary mapping net numbers to lists of via wrappers

        Example:
            by_net = collection.get_by_net()
            for net_num, vias in by_net.items():
                print(f"Net {net_num}: {len(vias)} vias")
        """
        self._ensure_indexes_current()

        result = {}
        for net_num, indices in self._net_index.items():
            result[net_num] = [ViaWrapper(self._items[i], self) for i in indices]
        return result

    def filter_by_layer_pair(self, layer1: str, layer2: str) -> List[ViaWrapper]:
        """
        Filter vias connecting specific layer pair.

        Args:
            layer1: First layer name
            layer2: Second layer name

        Returns:
            List of via wrappers connecting the specified layers

        Example:
            front_to_back = collection.filter_by_layer_pair("F.Cu", "B.Cu")
        """
        def connects_layers(via: Via) -> bool:
            return (layer1 in via.layers and layer2 in via.layers)

        matching = self.find(connects_layers)
        return [ViaWrapper(via, self) for via in matching]

    def filter_through_vias(self) -> List[ViaWrapper]:
        """
        Filter for through-hole vias (F.Cu to B.Cu).

        Returns:
            List of through-hole via wrappers

        Example:
            through_vias = collection.filter_through_vias()
        """
        return self.filter_by_layer_pair("F.Cu", "B.Cu")

    def filter_blind_buried_vias(self) -> List[ViaWrapper]:
        """
        Filter for blind or buried vias (not through-hole).

        Returns:
            List of blind/buried via wrappers

        Example:
            blind_buried = collection.filter_blind_buried_vias()
        """
        def is_blind_or_buried(via: Via) -> bool:
            # Through-hole vias have both F.Cu and B.Cu
            return not ("F.Cu" in via.layers and "B.Cu" in via.layers)

        matching = self.find(is_blind_or_buried)
        return [ViaWrapper(via, self) for via in matching]

    def filter_by_size(self, size: float) -> List[ViaWrapper]:
        """
        Filter vias by exact size.

        Args:
            size: Via size (diameter) in millimeters

        Returns:
            List of via wrappers with the specified size

        Example:
            standard_vias = collection.filter_by_size(0.8)
        """
        matching = self.filter(size=size)
        return [ViaWrapper(via, self) for via in matching]

    def filter_by_drill(self, drill: float) -> List[ViaWrapper]:
        """
        Filter vias by exact drill size.

        Args:
            drill: Drill diameter in millimeters

        Returns:
            List of via wrappers with the specified drill size

        Example:
            large_drill = collection.filter_by_drill(0.4)
        """
        matching = self.filter(drill=drill)
        return [ViaWrapper(via, self) for via in matching]

    # Spatial queries

    def find_nearest(self, point: Point, net: Optional[int] = None) -> Optional[ViaWrapper]:
        """
        Find the nearest via to a point.

        Args:
            point: Reference point
            net: Optional net filter (only search vias on this net)

        Returns:
            Nearest via wrapper, or None if no vias exist

        Example:
            nearest = collection.find_nearest(Point(50, 50), net=1)
        """
        # Get raw candidates (wrappers if filtered by net, raw if all)
        if net is None:
            candidates = self._items
        else:
            wrappers = self.filter_by_net(net)
            candidates = [w.data for w in wrappers]

        if not candidates:
            return None

        def distance_squared(via: Via) -> float:
            dx = via.position.x - point.x
            dy = via.position.y - point.y
            return dx * dx + dy * dy

        nearest = min(candidates, key=distance_squared)
        return ViaWrapper(nearest, self)

    def find_in_region(self, min_x: float, min_y: float,
                       max_x: float, max_y: float) -> List[ViaWrapper]:
        """
        Find vias within a rectangular region.

        Args:
            min_x: Minimum X coordinate
            min_y: Minimum Y coordinate
            max_x: Maximum X coordinate
            max_y: Maximum Y coordinate

        Returns:
            List of via wrappers within the region

        Example:
            region_vias = collection.find_in_region(0, 0, 100, 100)
        """
        def in_region(via: Via) -> bool:
            return (min_x <= via.position.x <= max_x and
                   min_y <= via.position.y <= max_y)

        matching = self.find(in_region)
        return [ViaWrapper(via, self) for via in matching]

    # Statistics and debugging

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get detailed collection statistics.

        Returns:
            Dictionary with collection statistics including via counts,
            through-hole vs blind/buried, size statistics
        """
        base_stats = super().get_statistics()

        self._ensure_indexes_current()

        # Count via types
        through_count = len(self.filter_through_vias())
        blind_buried_count = len(self.filter_blind_buried_vias())

        # Size statistics
        if self._items:
            sizes = [via.size for via in self._items]
            drills = [via.drill for via in self._items]

            size_stats = {
                "min_size": min(sizes),
                "max_size": max(sizes),
                "avg_size": sum(sizes) / len(sizes),
                "min_drill": min(drills),
                "max_drill": max(drills),
                "avg_drill": sum(drills) / len(drills),
            }
        else:
            size_stats = {
                "min_size": 0.0,
                "max_size": 0.0,
                "avg_size": 0.0,
                "min_drill": 0.0,
                "max_drill": 0.0,
                "avg_drill": 0.0,
            }

        # Add via-specific stats
        base_stats.update({
            "unique_nets": len(self._net_index),
            "vias_by_net": {
                net: len(indices) for net, indices in self._net_index.items()
            },
            "through_via_count": through_count,
            "blind_buried_via_count": blind_buried_count,
            **size_stats,
        })

        return base_stats
