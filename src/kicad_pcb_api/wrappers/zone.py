"""Wrapper class for zone elements."""

import math
from typing import TYPE_CHECKING, List, Optional, Tuple

from ..core.exceptions import ValidationError
from ..core.types import Point, Zone
from .base import ElementWrapper

if TYPE_CHECKING:
    from ..collections.zones import ZoneCollection


class ZoneWrapper(ElementWrapper[Zone]):
    """Enhanced wrapper for Zone with validation and parent tracking.

    Provides:
    - Net assignment validation
    - Layer validation
    - Area calculation from polygon points
    - Spatial queries (contains_point, overlaps)
    - Automatic index updates when properties change
    """

    def __init__(self, zone: Zone, parent_collection: "ZoneCollection"):
        """Initialize zone wrapper.

        Args:
            zone: The underlying Zone dataclass
            parent_collection: The ZoneCollection this belongs to
        """
        super().__init__(zone, parent_collection)

    @property
    def uuid(self) -> str:
        """Get the zone UUID.

        Returns:
            UUID string
        """
        return self._data.uuid

    @property
    def layer(self) -> str:
        """Get the zone layer.

        Returns:
            Layer name (e.g., 'F.Cu', 'B.Cu')
        """
        return self._data.layer

    @layer.setter
    def layer(self, value: str) -> None:
        """Set the zone layer with validation.

        Args:
            value: New layer name

        Raises:
            ValidationError: If layer is invalid
        """
        # Validate layer is a copper layer
        valid_copper_layers = [
            "F.Cu",
            "B.Cu",
            "In1.Cu",
            "In2.Cu",
            "In3.Cu",
            "In4.Cu",
            "In5.Cu",
            "In6.Cu",
            "In7.Cu",
            "In8.Cu",
            "In9.Cu",
            "In10.Cu",
            "In11.Cu",
            "In12.Cu",
            "In13.Cu",
            "In14.Cu",
            "In15.Cu",
            "In16.Cu",
            "In17.Cu",
            "In18.Cu",
            "In19.Cu",
            "In20.Cu",
            "In21.Cu",
            "In22.Cu",
            "In23.Cu",
            "In24.Cu",
            "In25.Cu",
            "In26.Cu",
            "In27.Cu",
            "In28.Cu",
            "In29.Cu",
            "In30.Cu",
        ]

        if value not in valid_copper_layers:
            raise ValidationError(
                f"Zone layer must be a copper layer, got: '{value}'",
                field="layer",
                value=value,
            )

        self._data.layer = value
        self._invalidate_indexes()
        self._mark_modified()

    @property
    def net(self) -> Optional[int]:
        """Get the zone net number.

        Returns:
            Net number or None
        """
        return self._data.net

    @net.setter
    def net(self, value: Optional[int]) -> None:
        """Set the zone net with validation.

        Args:
            value: Net number (0 or positive integer) or None

        Raises:
            ValidationError: If net number is negative
        """
        if value is not None and value < 0:
            raise ValidationError(
                f"Net number must be non-negative, got: {value}",
                field="net",
                value=value,
            )

        self._data.net = value
        self._invalidate_indexes()
        self._mark_modified()

    @property
    def net_name(self) -> Optional[str]:
        """Get the zone net name.

        Returns:
            Net name or None
        """
        return self._data.net_name

    @net_name.setter
    def net_name(self, value: Optional[str]) -> None:
        """Set the zone net name.

        Args:
            value: Net name or None
        """
        self._data.net_name = value
        self._mark_modified()

    @property
    def priority(self) -> int:
        """Get the zone priority.

        Returns:
            Priority value (higher = higher priority)
        """
        return self._data.priority

    @priority.setter
    def priority(self, value: int) -> None:
        """Set the zone priority.

        Args:
            value: Priority value
        """
        self._data.priority = value
        self._mark_modified()

    @property
    def filled(self) -> bool:
        """Get whether the zone is filled.

        Returns:
            True if zone is filled
        """
        return self._data.filled

    @filled.setter
    def filled(self, value: bool) -> None:
        """Set whether the zone is filled.

        Args:
            value: True to fill the zone
        """
        self._data.filled = value
        self._mark_modified()

    @property
    def polygon(self) -> List[Point]:
        """Get the zone polygon points.

        Returns:
            List of points defining the zone boundary
        """
        return self._data.polygon

    @polygon.setter
    def polygon(self, value: List[Point]) -> None:
        """Set the zone polygon points with validation.

        Args:
            value: List of points (minimum 3 for a valid polygon)

        Raises:
            ValidationError: If polygon has less than 3 points
        """
        if len(value) < 3:
            raise ValidationError(
                f"Zone polygon must have at least 3 points, got: {len(value)}",
                field="polygon",
                value=value,
            )

        self._data.polygon = value
        self._mark_modified()

    def get_area(self) -> float:
        """Calculate the area of the zone using the shoelace formula.

        Returns:
            Area in square millimeters

        Example:
            area = zone.get_area()
            print(f"Zone area: {area:.2f} mm²")
        """
        if len(self._data.polygon) < 3:
            return 0.0

        # Shoelace formula
        area = 0.0
        n = len(self._data.polygon)
        for i in range(n):
            j = (i + 1) % n
            area += self._data.polygon[i].x * self._data.polygon[j].y
            area -= self._data.polygon[j].x * self._data.polygon[i].y

        return abs(area) / 2.0

    def get_bounding_box(self) -> Optional[Tuple[float, float, float, float]]:
        """Get the bounding box of the zone.

        Returns:
            Tuple of (min_x, min_y, max_x, max_y) or None if no polygon

        Example:
            bbox = zone.get_bounding_box()
            if bbox:
                min_x, min_y, max_x, max_y = bbox
        """
        if not self._data.polygon:
            return None

        xs = [p.x for p in self._data.polygon]
        ys = [p.y for p in self._data.polygon]

        return (min(xs), min(ys), max(xs), max(ys))

    def contains_point(self, point: Point) -> bool:
        """Check if a point is inside the zone using ray casting algorithm.

        Args:
            point: Point to check

        Returns:
            True if point is inside the zone polygon

        Example:
            if zone.contains_point(Point(50, 50)):
                print("Point is inside zone")
        """
        if len(self._data.polygon) < 3:
            return False

        # Ray casting algorithm
        x, y = point.x, point.y
        n = len(self._data.polygon)
        inside = False

        p1 = self._data.polygon[0]
        for i in range(1, n + 1):
            p2 = self._data.polygon[i % n]

            if y > min(p1.y, p2.y):
                if y <= max(p1.y, p2.y):
                    if x <= max(p1.x, p2.x):
                        if p1.y != p2.y:
                            x_intersection = (y - p1.y) * (p2.x - p1.x) / (
                                p2.y - p1.y
                            ) + p1.x
                            if p1.x == p2.x or x <= x_intersection:
                                inside = not inside

            p1 = p2

        return inside

    def overlaps(self, other: "ZoneWrapper") -> bool:
        """Check if this zone overlaps with another zone.

        Args:
            other: Another zone wrapper

        Returns:
            True if zones overlap (bounding boxes intersect)

        Note:
            This is a conservative check using bounding boxes.
            For precise overlap detection, use polygon intersection algorithms.

        Example:
            if zone1.overlaps(zone2):
                print("Zones overlap")
        """
        bbox1 = self.get_bounding_box()
        bbox2 = other.get_bounding_box()

        if bbox1 is None or bbox2 is None:
            return False

        min_x1, min_y1, max_x1, max_y1 = bbox1
        min_x2, min_y2, max_x2, max_y2 = bbox2

        # Check if bounding boxes intersect
        return not (
            max_x1 < min_x2 or max_x2 < min_x1 or max_y1 < min_y2 or max_y2 < min_y1
        )

    def get_perimeter(self) -> float:
        """Calculate the perimeter of the zone.

        Returns:
            Perimeter in millimeters

        Example:
            perimeter = zone.get_perimeter()
            print(f"Zone perimeter: {perimeter:.2f} mm")
        """
        if len(self._data.polygon) < 2:
            return 0.0

        perimeter = 0.0
        n = len(self._data.polygon)

        for i in range(n):
            j = (i + 1) % n
            p1 = self._data.polygon[i]
            p2 = self._data.polygon[j]

            # Euclidean distance
            dx = p2.x - p1.x
            dy = p2.y - p1.y
            perimeter += math.sqrt(dx * dx + dy * dy)

        return perimeter

    def is_copper_layer(self) -> bool:
        """Check if zone is on a copper layer.

        Returns:
            True if zone is on a copper layer
        """
        return self._data.layer.endswith(".Cu")

    def __repr__(self) -> str:
        """Get string representation.

        Returns:
            String representation with layer, net, and area info
        """
        area = self.get_area()
        net_info = (
            f"net={self._data.net}"
            if self._data.net is not None
            else "no net"
        )
        return (
            f"ZoneWrapper(layer={self._data.layer}, "
            f"{net_info}, "
            f"area={area:.2f}mm², "
            f"priority={self._data.priority})"
        )
