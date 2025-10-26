"""
Zone collection with specialized indexing and zone-specific operations.

Extends IndexedCollection to provide zone-specific features like
net indexing, layer filtering, area calculations, and spatial queries.
"""

import logging
import math
from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple

from ..core.types import Point, Zone
from ..wrappers.zone import ZoneWrapper
from .base import IndexedCollection

logger = logging.getLogger(__name__)


class ZoneCollection(IndexedCollection[Zone]):
    """
    Collection class for efficient zone management.

    Extends IndexedCollection with zone-specific features:
    - Net-based indexing for fast zone lookup by net
    - Layer-based indexing for finding zones on specific layers
    - Area filtering by bounding box
    - Total area calculations
    - Priority-based sorting
    - Spatial overlap queries
    """

    def __init__(self, zones: Optional[List[Zone]] = None):
        """
        Initialize zone collection.

        Args:
            zones: Initial list of zones to add
        """
        # Additional indexes
        self._net_index: Dict[int, List[int]] = defaultdict(list)
        self._layer_index: Dict[str, List[int]] = defaultdict(list)

        # Call parent init
        super().__init__(zones)

        logger.debug(f"ZoneCollection initialized with {len(self._items)} zones")

    # Abstract method implementations

    def _get_item_uuid(self, item: Zone) -> str:
        """Extract UUID from zone."""
        return item.uuid

    def _create_item(self, **kwargs) -> Zone:
        """Create new zone instance."""
        return Zone(**kwargs)

    def _build_additional_indexes(self) -> None:
        """Build zone-specific indexes."""
        # Build net index
        self._net_index = defaultdict(list)
        for i, zone in enumerate(self._items):
            if zone.net is not None:
                self._net_index[zone.net].append(i)

        # Build layer index
        self._layer_index = defaultdict(list)
        for i, zone in enumerate(self._items):
            if zone.layer:
                self._layer_index[zone.layer].append(i)

        logger.debug(
            f"Built indexes: {len(self._net_index)} nets, "
            f"{len(self._layer_index)} layers"
        )

    # Zone-specific access methods

    def filter_by_net(self, net: int) -> List[ZoneWrapper]:
        """
        Filter zones by net number.

        Args:
            net: Net number to filter by

        Returns:
            List of zone wrappers on the specified net

        Example:
            gnd_zones = collection.filter_by_net(0)
        """
        self._ensure_indexes_current()

        indices = self._net_index.get(net, [])
        return [ZoneWrapper(self._items[i], self) for i in indices]

    def filter_by_layer(self, layer: str) -> List[ZoneWrapper]:
        """
        Filter zones on a specific layer.

        Args:
            layer: Layer name (e.g., "F.Cu", "B.Cu")

        Returns:
            List of zone wrappers on the specified layer

        Example:
            front_zones = collection.filter_by_layer("F.Cu")
        """
        self._ensure_indexes_current()

        indices = self._layer_index.get(layer, [])
        return [ZoneWrapper(self._items[i], self) for i in indices]

    def filter_by_area(
        self, min_x: float, min_y: float, max_x: float, max_y: float
    ) -> List[ZoneWrapper]:
        """
        Filter zones that intersect with a bounding box.

        Args:
            min_x: Minimum X coordinate of bounding box
            min_y: Minimum Y coordinate of bounding box
            max_x: Maximum X coordinate of bounding box
            max_y: Maximum Y coordinate of bounding box

        Returns:
            List of zone wrappers that intersect the bounding box

        Example:
            zones_in_area = collection.filter_by_area(0, 0, 100, 100)
        """

        def intersects_bbox(zone: Zone) -> bool:
            """Check if zone intersects with bounding box."""
            if not zone.polygon:
                return False

            # Get zone bounding box
            zone_min_x = min(p.x for p in zone.polygon)
            zone_max_x = max(p.x for p in zone.polygon)
            zone_min_y = min(p.y for p in zone.polygon)
            zone_max_y = max(p.y for p in zone.polygon)

            # Check for intersection
            return not (
                zone_max_x < min_x
                or zone_min_x > max_x
                or zone_max_y < min_y
                or zone_min_y > max_y
            )

        matching = self.find(intersects_bbox)
        return [ZoneWrapper(zone, self) for zone in matching]

    def get_total_area(self) -> float:
        """
        Calculate the total area of all zones.

        Returns:
            Total area in square millimeters

        Note:
            This is an approximation using the shoelace formula for each polygon.
            Does not account for overlapping zones.

        Example:
            total = collection.get_total_area()
            print(f"Total copper pour area: {total:.2f} mm²")
        """
        total = 0.0
        for zone in self._items:
            if zone.polygon and len(zone.polygon) >= 3:
                total += self._calculate_polygon_area(zone.polygon)
        return total

    def get_zones_by_net(self) -> Dict[int, List[ZoneWrapper]]:
        """
        Get zones grouped by net number.

        Returns:
            Dictionary mapping net numbers to lists of zone wrappers

        Example:
            by_net = collection.get_zones_by_net()
            for net, zones in by_net.items():
                print(f"Net {net}: {len(zones)} zones")
        """
        self._ensure_indexes_current()

        result = {}
        for net, indices in self._net_index.items():
            result[net] = [ZoneWrapper(self._items[i], self) for i in indices]
        return result

    def get_zones_by_layer(self) -> Dict[str, List[ZoneWrapper]]:
        """
        Get zones grouped by layer.

        Returns:
            Dictionary mapping layer names to lists of zone wrappers

        Example:
            by_layer = collection.get_zones_by_layer()
            for layer, zones in by_layer.items():
                print(f"{layer}: {len(zones)} zones")
        """
        self._ensure_indexes_current()

        result = {}
        for layer, indices in self._layer_index.items():
            result[layer] = [ZoneWrapper(self._items[i], self) for i in indices]
        return result

    def get_zones_sorted_by_priority(
        self, descending: bool = True
    ) -> List[ZoneWrapper]:
        """
        Get all zones sorted by priority.

        Args:
            descending: If True, sort highest priority first (default: True)

        Returns:
            List of zone wrappers sorted by priority

        Example:
            zones = collection.get_zones_sorted_by_priority()
        """
        sorted_zones = sorted(
            self._items, key=lambda z: z.priority, reverse=descending
        )
        return [ZoneWrapper(zone, self) for zone in sorted_zones]

    # Helper methods

    @staticmethod
    def _calculate_polygon_area(polygon: List[Point]) -> float:
        """
        Calculate the area of a polygon using the shoelace formula.

        Args:
            polygon: List of points defining the polygon

        Returns:
            Area in square millimeters (always positive)
        """
        if len(polygon) < 3:
            return 0.0

        # Shoelace formula
        area = 0.0
        n = len(polygon)
        for i in range(n):
            j = (i + 1) % n
            area += polygon[i].x * polygon[j].y
            area -= polygon[j].x * polygon[i].y

        return abs(area) / 2.0

    # Statistics and debugging

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get detailed collection statistics.

        Returns:
            Dictionary with collection statistics including zone counts
            by net, layer, and total area.
        """
        base_stats = super().get_statistics()

        self._ensure_indexes_current()

        # Calculate statistics
        total_area = self.get_total_area()
        filled_zones = sum(1 for z in self._items if z.filled)

        # Add zone-specific stats
        base_stats.update(
            {
                "unique_nets": len(self._net_index),
                "unique_layers": len(self._layer_index),
                "total_area_mm2": total_area,
                "filled_zones": filled_zones,
                "unfilled_zones": len(self._items) - filled_zones,
                "zones_by_net": {
                    net: len(indices) for net, indices in self._net_index.items()
                },
                "zones_by_layer": {
                    layer: len(indices) for layer, indices in self._layer_index.items()
                },
            }
        )

        return base_stats
