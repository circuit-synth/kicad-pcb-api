"""Wrapper class for via elements."""

from typing import TYPE_CHECKING, List, Optional

from ..core.exceptions import ValidationError
from ..core.types import Point, Via
from ..core.validation import validate_layers, validate_net, validate_via_size
from .base import ElementWrapper

if TYPE_CHECKING:
    from ..collections.vias import ViaCollection


class ViaWrapper(ElementWrapper[Via]):
    """Enhanced wrapper for Via with validation and parent tracking.

    Provides:
    - Size and drill validation on updates
    - Layer validation
    - Net validation
    - Via type classification (through-hole, blind, buried)
    - Automatic index updates when properties change
    """

    def __init__(self, via: Via, parent_collection: "ViaCollection"):
        """Initialize via wrapper.

        Args:
            via: The underlying Via dataclass
            parent_collection: The ViaCollection this belongs to
        """
        super().__init__(via, parent_collection)

    @property
    def uuid(self) -> str:
        """Get the via UUID.

        Returns:
            UUID string
        """
        return self._data.uuid

    @property
    def position(self) -> Point:
        """Get the via position.

        Returns:
            Position point
        """
        return self._data.position

    @position.setter
    def position(self, point: Point) -> None:
        """Set the via position.

        Args:
            point: New position point
        """
        if not isinstance(point, Point):
            raise ValidationError(
                "Position must be a Point instance",
                field="position",
                value=point,
            )
        self._data.position = point
        self._mark_modified()

    @property
    def size(self) -> float:
        """Get the via pad size in mm.

        Returns:
            Via pad diameter
        """
        return self._data.size

    @size.setter
    def size(self, value: float) -> None:
        """Set the via pad size with validation.

        Args:
            value: New pad size in mm

        Raises:
            GeometryError: If size is invalid
        """
        validate_via_size(value, self._data.drill)
        old_size = self._data.size
        self._data.size = value

        # Size changes affect indexes
        if old_size != value:
            self._invalidate_indexes()
        self._mark_modified()

    @property
    def drill(self) -> float:
        """Get the via drill size in mm.

        Returns:
            Drill diameter
        """
        return self._data.drill

    @drill.setter
    def drill(self, value: float) -> None:
        """Set the via drill size with validation.

        Args:
            value: New drill size in mm

        Raises:
            GeometryError: If drill is invalid
        """
        validate_via_size(self._data.size, value)
        old_drill = self._data.drill
        self._data.drill = value

        # Drill changes affect indexes
        if old_drill != value:
            self._invalidate_indexes()
        self._mark_modified()

    @property
    def layers(self) -> List[str]:
        """Get the via layer span.

        Returns:
            List of layer names
        """
        return self._data.layers

    @layers.setter
    def layers(self, value: List[str]) -> None:
        """Set the via layer span with validation.

        Args:
            value: New layer list

        Raises:
            LayerError: If layers are invalid
        """
        # Validate all layers are copper layers
        for layer in value:
            if not layer.endswith(".Cu"):
                raise ValidationError(
                    f"Via layer must be a copper layer (*.Cu), got: '{layer}'",
                    field="layers",
                    value=value,
                )

        validate_layers(value, allow_user_layers=True)

        # Must have at least 2 layers
        if len(value) < 2:
            raise ValidationError(
                "Via must span at least 2 layers",
                field="layers",
                value=value,
            )

        old_layers = set(self._data.layers)
        self._data.layers = value

        # Layer changes affect indexes
        if set(value) != old_layers:
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

    def is_through_hole(self) -> bool:
        """Check if via is a through-hole via (F.Cu to B.Cu).

        Returns:
            True if via spans from front to back copper
        """
        return "F.Cu" in self._data.layers and "B.Cu" in self._data.layers

    def is_blind_or_buried(self) -> bool:
        """Check if via is blind or buried (not through-hole).

        Returns:
            True if via does not span from front to back
        """
        return not self.is_through_hole()

    def is_blind(self) -> bool:
        """Check if via is a blind via (connects outer layer to inner).

        Returns:
            True if via connects F.Cu or B.Cu to inner layers only
        """
        has_front = "F.Cu" in self._data.layers
        has_back = "B.Cu" in self._data.layers
        has_inner = any(layer.startswith("In") for layer in self._data.layers)

        # Blind via connects exactly one outer layer to inner layers
        return (has_front ^ has_back) and has_inner

    def is_buried(self) -> bool:
        """Check if via is a buried via (connects only inner layers).

        Returns:
            True if via connects only inner layers
        """
        has_outer = "F.Cu" in self._data.layers or "B.Cu" in self._data.layers
        has_inner = any(layer.startswith("In") for layer in self._data.layers)

        # Buried via connects only inner layers
        return not has_outer and has_inner

    def get_layer_pair(self) -> tuple[str, str]:
        """Get the layer pair (start and end layers).

        Returns:
            Tuple of (first_layer, last_layer)
        """
        if len(self._data.layers) < 2:
            return ("", "")
        return (self._data.layers[0], self._data.layers[-1])

    def is_on_layer(self, layer: str) -> bool:
        """Check if via connects to a specific layer.

        Args:
            layer: Layer name to check

        Returns:
            True if via connects to the layer
        """
        return layer in self._data.layers

    def is_connected_to_net(self, net: int) -> bool:
        """Check if via is connected to a specific net.

        Args:
            net: Net number to check

        Returns:
            True if via is on the net
        """
        return self._data.net == net

    def move_by(self, dx: float, dy: float) -> None:
        """Move via by a delta.

        Args:
            dx: X offset in mm
            dy: Y offset in mm
        """
        self._data.position = Point(
            self._data.position.x + dx, self._data.position.y + dy
        )
        self._mark_modified()

    def __repr__(self) -> str:
        """Get string representation.

        Returns:
            String representation with key properties
        """
        via_type = "through" if self.is_through_hole() else "blind/buried"
        return (
            f"ViaWrapper("
            f"pos=({self.position.x:.2f}, {self.position.y:.2f}), "
            f"size={self.size:.3f}, "
            f"drill={self.drill:.3f}, "
            f"layers={self.layers[0]}-{self.layers[-1]}, "
            f"net={self.net}, "
            f"type={via_type})"
        )
