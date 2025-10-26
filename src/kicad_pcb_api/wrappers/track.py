"""Wrapper class for track elements."""

from typing import TYPE_CHECKING, Optional

from ..core.exceptions import ValidationError
from ..core.types import Point, Track
from ..core.validation import validate_layer, validate_net, validate_track_width
from .base import ElementWrapper

if TYPE_CHECKING:
    from ..collections.tracks import TrackCollection


class TrackWrapper(ElementWrapper[Track]):
    """Enhanced wrapper for Track with validation and parent tracking.

    Provides:
    - Width validation on updates
    - Layer validation
    - Net validation
    - Length calculation
    - Automatic index updates when properties change
    """

    def __init__(self, track: Track, parent_collection: "TrackCollection"):
        """Initialize track wrapper.

        Args:
            track: The underlying Track dataclass
            parent_collection: The TrackCollection this belongs to
        """
        super().__init__(track, parent_collection)

    @property
    def uuid(self) -> str:
        """Get the track UUID.

        Returns:
            UUID string
        """
        return self._data.uuid

    @property
    def start(self) -> Point:
        """Get the track start point.

        Returns:
            Start point
        """
        return self._data.start

    @start.setter
    def start(self, point: Point) -> None:
        """Set the track start point.

        Args:
            point: New start point
        """
        if not isinstance(point, Point):
            raise ValidationError(
                "Start point must be a Point instance",
                field="start",
                value=point,
            )
        self._data.start = point
        self._mark_modified()

    @property
    def end(self) -> Point:
        """Get the track end point.

        Returns:
            End point
        """
        return self._data.end

    @end.setter
    def end(self, point: Point) -> None:
        """Set the track end point.

        Args:
            point: New end point
        """
        if not isinstance(point, Point):
            raise ValidationError(
                "End point must be a Point instance",
                field="end",
                value=point,
            )
        self._data.end = point
        self._mark_modified()

    @property
    def width(self) -> float:
        """Get the track width in mm.

        Returns:
            Track width
        """
        return self._data.width

    @width.setter
    def width(self, value: float) -> None:
        """Set the track width with validation.

        Args:
            value: New track width in mm

        Raises:
            GeometryError: If width is invalid
        """
        validate_track_width(value)
        old_width = self._data.width
        self._data.width = value

        # Width changes affect indexes
        if old_width != value:
            self._invalidate_indexes()
        self._mark_modified()

    @property
    def layer(self) -> str:
        """Get the track layer.

        Returns:
            Layer name (e.g., 'F.Cu', 'B.Cu')
        """
        return self._data.layer

    @layer.setter
    def layer(self, value: str) -> None:
        """Set the track layer with validation.

        Args:
            value: New layer name

        Raises:
            LayerError: If layer is invalid
        """
        # Tracks must be on copper layers
        if not value.endswith(".Cu"):
            raise ValidationError(
                f"Track layer must be a copper layer (*.Cu), got: '{value}'",
                field="layer",
                value=value,
            )

        validate_layer(value, allow_user_layers=True)
        old_layer = self._data.layer
        self._data.layer = value

        # Layer changes affect indexes
        if old_layer != value:
            self._invalidate_indexes()
        self._mark_modified()

    @property
    def net(self) -> Optional[int]:
        """Get the net number.

        Returns:
            Net number (0 = unconnected, None = no net)
        """
        return self._data.net

    @net.setter
    def net(self, value: Optional[int]) -> None:
        """Set the net number with validation.

        Args:
            value: New net number

        Raises:
            NetError: If net is invalid
        """
        if value is not None:
            validate_net(value, self._data.net_name)

        old_net = self._data.net
        self._data.net = value

        # Net changes affect indexes
        if old_net != value:
            self._invalidate_indexes()
        self._mark_modified()

    @property
    def net_name(self) -> Optional[str]:
        """Get the net name.

        Returns:
            Net name string or None
        """
        return self._data.net_name

    @net_name.setter
    def net_name(self, value: Optional[str]) -> None:
        """Set the net name.

        Args:
            value: New net name
        """
        self._data.net_name = value
        self._mark_modified()

    @property
    def length(self) -> float:
        """Calculate and return the track length in mm.

        Returns:
            Track length (Euclidean distance)
        """
        return self._data.get_length()

    def move_by(self, dx: float, dy: float) -> None:
        """Move track by a delta.

        Args:
            dx: X offset in mm
            dy: Y offset in mm
        """
        self._data.start = Point(self._data.start.x + dx, self._data.start.y + dy)
        self._data.end = Point(self._data.end.x + dx, self._data.end.y + dy)
        self._mark_modified()

    def is_horizontal(self, tolerance: float = 0.001) -> bool:
        """Check if track is horizontal.

        Args:
            tolerance: Y difference tolerance in mm

        Returns:
            True if track is horizontal within tolerance
        """
        return abs(self._data.start.y - self._data.end.y) < tolerance

    def is_vertical(self, tolerance: float = 0.001) -> bool:
        """Check if track is vertical.

        Args:
            tolerance: X difference tolerance in mm

        Returns:
            True if track is vertical within tolerance
        """
        return abs(self._data.start.x - self._data.end.x) < tolerance

    def is_connected_to_net(self, net: int) -> bool:
        """Check if track is connected to a specific net.

        Args:
            net: Net number to check

        Returns:
            True if track is on the net
        """
        return self._data.net == net

    def is_on_layer(self, layer: str) -> bool:
        """Check if track is on a specific layer.

        Args:
            layer: Layer name to check

        Returns:
            True if track is on the layer
        """
        return self._data.layer == layer

    def reverse(self) -> None:
        """Reverse the track direction (swap start and end)."""
        self._data.start, self._data.end = self._data.end, self._data.start
        self._mark_modified()

    def __repr__(self) -> str:
        """Get string representation.

        Returns:
            String representation with key properties
        """
        return (
            f"TrackWrapper("
            f"start=({self.start.x:.2f}, {self.start.y:.2f}), "
            f"end=({self.end.x:.2f}, {self.end.y:.2f}), "
            f"width={self.width:.3f}, "
            f"layer={self.layer}, "
            f"net={self.net}, "
            f"length={self.length:.2f}mm)"
        )
