"""Geometry utilities for PCB operations."""

import math
from dataclasses import dataclass
from typing import List, Optional, Tuple

from .types import Point


@dataclass
class BoundingBox:
    """Axis-aligned bounding box."""

    min_x: float
    min_y: float
    max_x: float
    max_y: float

    @property
    def width(self) -> float:
        """Get box width.

        Returns:
            Width in mm
        """
        return self.max_x - self.min_x

    @property
    def height(self) -> float:
        """Get box height.

        Returns:
            Height in mm
        """
        return self.max_y - self.min_y

    @property
    def center(self) -> Point:
        """Get box center point.

        Returns:
            Center point
        """
        return Point((self.min_x + self.max_x) / 2, (self.min_y + self.max_y) / 2)

    @property
    def area(self) -> float:
        """Get box area.

        Returns:
            Area in mm²
        """
        return self.width * self.height

    def contains_point(self, point: Point) -> bool:
        """Check if point is inside box.

        Args:
            point: Point to check

        Returns:
            True if point is inside box
        """
        return (
            self.min_x <= point.x <= self.max_x and self.min_y <= point.y <= self.max_y
        )

    def overlaps(self, other: "BoundingBox") -> bool:
        """Check if this box overlaps with another.

        Args:
            other: Other bounding box

        Returns:
            True if boxes overlap
        """
        return not (
            self.max_x < other.min_x
            or self.min_x > other.max_x
            or self.max_y < other.min_y
            or self.min_y > other.max_y
        )

    def expand(self, margin: float) -> "BoundingBox":
        """Expand box by a margin.

        Args:
            margin: Margin to add on all sides in mm

        Returns:
            New expanded bounding box
        """
        return BoundingBox(
            min_x=self.min_x - margin,
            min_y=self.min_y - margin,
            max_x=self.max_x + margin,
            max_y=self.max_y + margin,
        )

    def union(self, other: "BoundingBox") -> "BoundingBox":
        """Create union box containing both boxes.

        Args:
            other: Other bounding box

        Returns:
            New bounding box containing both
        """
        return BoundingBox(
            min_x=min(self.min_x, other.min_x),
            min_y=min(self.min_y, other.min_y),
            max_x=max(self.max_x, other.max_x),
            max_y=max(self.max_y, other.max_y),
        )

    @staticmethod
    def from_points(points: List[Point]) -> "BoundingBox":
        """Create bounding box from list of points.

        Args:
            points: List of points

        Returns:
            Bounding box containing all points

        Raises:
            ValueError: If points list is empty
        """
        if not points:
            raise ValueError("Cannot create bounding box from empty point list")

        xs = [p.x for p in points]
        ys = [p.y for p in points]

        return BoundingBox(min_x=min(xs), min_y=min(ys), max_x=max(xs), max_y=max(ys))

    @staticmethod
    def from_center_and_size(center: Point, width: float, height: float) -> "BoundingBox":
        """Create bounding box from center point and size.

        Args:
            center: Center point
            width: Box width
            height: Box height

        Returns:
            Bounding box
        """
        half_w = width / 2
        half_h = height / 2

        return BoundingBox(
            min_x=center.x - half_w,
            min_y=center.y - half_h,
            max_x=center.x + half_w,
            max_y=center.y + half_h,
        )


def distance(p1: Point, p2: Point) -> float:
    """Calculate Euclidean distance between two points.

    Args:
        p1: First point
        p2: Second point

    Returns:
        Distance in mm
    """
    dx = p2.x - p1.x
    dy = p2.y - p1.y
    return math.sqrt(dx * dx + dy * dy)


def distance_squared(p1: Point, p2: Point) -> float:
    """Calculate squared distance (faster, no sqrt).

    Args:
        p1: First point
        p2: Second point

    Returns:
        Squared distance in mm²
    """
    dx = p2.x - p1.x
    dy = p2.y - p1.y
    return dx * dx + dy * dy


def manhattan_distance(p1: Point, p2: Point) -> float:
    """Calculate Manhattan distance between two points.

    Args:
        p1: First point
        p2: Second point

    Returns:
        Manhattan distance in mm
    """
    return abs(p2.x - p1.x) + abs(p2.y - p1.y)


def midpoint(p1: Point, p2: Point) -> Point:
    """Calculate midpoint between two points.

    Args:
        p1: First point
        p2: Second point

    Returns:
        Midpoint
    """
    return Point((p1.x + p2.x) / 2, (p1.y + p2.y) / 2)


def rotate_point(point: Point, center: Point, angle_degrees: float) -> Point:
    """Rotate point around center.

    Args:
        point: Point to rotate
        center: Center of rotation
        angle_degrees: Rotation angle in degrees (counterclockwise)

    Returns:
        Rotated point
    """
    angle_rad = math.radians(angle_degrees)
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)

    # Translate to origin
    dx = point.x - center.x
    dy = point.y - center.y

    # Rotate
    x_new = dx * cos_a - dy * sin_a
    y_new = dx * sin_a + dy * cos_a

    # Translate back
    return Point(x_new + center.x, y_new + center.y)


def point_on_line_segment(
    point: Point, line_start: Point, line_end: Point, tolerance: float = 0.001
) -> bool:
    """Check if point lies on a line segment.

    Args:
        point: Point to check
        line_start: Line segment start
        line_end: Line segment end
        tolerance: Distance tolerance in mm

    Returns:
        True if point is on line segment within tolerance
    """
    # Calculate distances
    d1 = distance(line_start, point)
    d2 = distance(point, line_end)
    line_length = distance(line_start, line_end)

    # Point is on line if d1 + d2 ≈ line_length
    return abs(d1 + d2 - line_length) < tolerance


def closest_point_on_line_segment(point: Point, line_start: Point, line_end: Point) -> Point:
    """Find closest point on line segment to given point.

    Args:
        point: Point to find closest point to
        line_start: Line segment start
        line_end: Line segment end

    Returns:
        Closest point on line segment
    """
    # Vector from line_start to line_end
    dx = line_end.x - line_start.x
    dy = line_end.y - line_start.y

    # If line segment is actually a point
    if dx == 0 and dy == 0:
        return line_start

    # Parameter t for projection onto line
    t = ((point.x - line_start.x) * dx + (point.y - line_start.y) * dy) / (
        dx * dx + dy * dy
    )

    # Clamp t to [0, 1] to stay on segment
    t = max(0, min(1, t))

    # Calculate point on segment
    return Point(line_start.x + t * dx, line_start.y + t * dy)


def line_segments_intersect(
    p1: Point, p2: Point, p3: Point, p4: Point
) -> Optional[Point]:
    """Check if two line segments intersect and return intersection point.

    Args:
        p1: First segment start
        p2: First segment end
        p3: Second segment start
        p4: Second segment end

    Returns:
        Intersection point if segments intersect, None otherwise
    """
    # Line segment 1: p1 + t * (p2 - p1)
    # Line segment 2: p3 + u * (p4 - p3)

    dx1 = p2.x - p1.x
    dy1 = p2.y - p1.y
    dx2 = p4.x - p3.x
    dy2 = p4.y - p3.y

    denominator = dx1 * dy2 - dy1 * dx2

    # Lines are parallel
    if abs(denominator) < 1e-10:
        return None

    dx3 = p3.x - p1.x
    dy3 = p3.y - p1.y

    t = (dx3 * dy2 - dy3 * dx2) / denominator
    u = (dx3 * dy1 - dy3 * dx1) / denominator

    # Check if intersection is within both segments
    if 0 <= t <= 1 and 0 <= u <= 1:
        return Point(p1.x + t * dx1, p1.y + t * dy1)

    return None


def circle_circle_collision(
    center1: Point, radius1: float, center2: Point, radius2: float
) -> bool:
    """Check if two circles collide.

    Args:
        center1: First circle center
        radius1: First circle radius
        center2: Second circle center
        radius2: Second circle radius

    Returns:
        True if circles overlap
    """
    dist_squared = distance_squared(center1, center2)
    radius_sum = radius1 + radius2
    return dist_squared < (radius_sum * radius_sum)


def point_in_circle(point: Point, center: Point, radius: float) -> bool:
    """Check if point is inside circle.

    Args:
        point: Point to check
        center: Circle center
        radius: Circle radius

    Returns:
        True if point is inside circle
    """
    return distance_squared(point, center) < (radius * radius)
