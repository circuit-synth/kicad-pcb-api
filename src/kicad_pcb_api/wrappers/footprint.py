"""Wrapper class for footprint elements."""

from typing import TYPE_CHECKING, Any, List, Optional

from ..core.exceptions import ReferenceError, ValidationError
from ..core.types import Footprint, Point
from ..core.validation import validate_reference
from .base import ElementWrapper

if TYPE_CHECKING:
    from ..collections.footprints import FootprintCollection


class FootprintWrapper(ElementWrapper[Footprint]):
    """Enhanced wrapper for Footprint with validation and parent tracking.

    Provides:
    - Reference validation on updates
    - Automatic index updates when properties change
    - Convenient property access
    - Layer and net queries
    """

    def __init__(self, footprint: Footprint, parent_collection: "FootprintCollection"):
        """Initialize footprint wrapper.

        Args:
            footprint: The underlying Footprint dataclass
            parent_collection: The FootprintCollection this belongs to
        """
        super().__init__(footprint, parent_collection)

    @property
    def uuid(self) -> str:
        """Get the footprint UUID.

        Returns:
            UUID string
        """
        return self._data.uuid

    @property
    def reference(self) -> str:
        """Get the reference designator.

        Returns:
            Reference designator (e.g., 'R1', 'C5')
        """
        return self._data.reference

    @reference.setter
    def reference(self, value: str) -> None:
        """Set the reference designator with validation.

        Args:
            value: New reference designator

        Raises:
            ReferenceError: If reference is invalid or already exists
        """
        # Validate format
        validate_reference(value)

        # Check for duplicates (excluding self)
        collection = self._collection  # type: FootprintCollection
        existing = collection.get_by_reference(value)
        if existing is not None and existing.uuid != self.uuid:
            raise ReferenceError(
                f"Reference '{value}' already exists in footprint {existing.uuid}",
                field="reference",
                value=value,
            )

        # Update the value and indexes
        old_ref = self._data.reference
        self._data.reference = value

        # Notify collection to update indexes
        self._invalidate_indexes()
        self._mark_modified()

    @property
    def value(self) -> str:
        """Get the footprint value.

        Returns:
            Value string (e.g., '10k', '0.1uF')
        """
        return self._data.value

    @value.setter
    def value(self, new_value: str) -> None:
        """Set the footprint value.

        Args:
            new_value: New value string
        """
        self._data.value = new_value
        self._mark_modified()

    @property
    def lib_id(self) -> str:
        """Get the library identifier.

        Returns:
            Library ID (e.g., 'Resistor_SMD:R_0603_1608Metric')
        """
        return f"{self._data.library}:{self._data.name}"

    @property
    def library(self) -> str:
        """Get the library name.

        Returns:
            Library name (e.g., 'Resistor_SMD')
        """
        return self._data.library

    @property
    def name(self) -> str:
        """Get the footprint name.

        Returns:
            Footprint name (e.g., 'R_0603_1608Metric')
        """
        return self._data.name

    @property
    def position(self) -> Point:
        """Get the footprint position.

        Returns:
            Position point
        """
        return self._data.position

    @position.setter
    def position(self, new_position: Point) -> None:
        """Set the footprint position.

        Args:
            new_position: New position point
        """
        if not isinstance(new_position, Point):
            raise ValidationError(
                "Position must be a Point instance",
                field="position",
                value=new_position,
            )
        self._data.position = new_position
        self._mark_modified()

    @property
    def rotation(self) -> float:
        """Get the footprint rotation in degrees.

        Returns:
            Rotation angle in degrees
        """
        return self._data.rotation

    @rotation.setter
    def rotation(self, angle: float) -> None:
        """Set the footprint rotation.

        Args:
            angle: Rotation angle in degrees
        """
        # Normalize to 0-360 range
        normalized = angle % 360.0
        self._data.rotation = normalized
        self._mark_modified()

    @property
    def layer(self) -> str:
        """Get the footprint layer.

        Returns:
            Layer name (typically 'F.Cu' or 'B.Cu')
        """
        return self._data.layer

    @layer.setter
    def layer(self, new_layer: str) -> None:
        """Set the footprint layer.

        Args:
            new_layer: New layer name

        Raises:
            ValidationError: If layer is not F.Cu or B.Cu
        """
        if new_layer not in ("F.Cu", "B.Cu"):
            raise ValidationError(
                f"Footprint layer must be 'F.Cu' or 'B.Cu', got: '{new_layer}'",
                field="layer",
                value=new_layer,
            )
        self._data.layer = new_layer
        self._invalidate_indexes()
        self._mark_modified()

    @property
    def pads(self) -> List[Any]:
        """Get the footprint pads.

        Returns:
            List of pad objects
        """
        return self._data.pads

    @property
    def nets(self) -> List[int]:
        """Get all unique net numbers from pads.

        Returns:
            List of net numbers (0 = unconnected)
        """
        nets = set()
        for pad in self._data.pads:
            if hasattr(pad, "net") and pad.net is not None:
                nets.add(pad.net)
        return sorted(nets)

    def is_on_layer(self, layer: str) -> bool:
        """Check if footprint is on a specific layer.

        Args:
            layer: Layer name to check

        Returns:
            True if footprint is on the layer
        """
        return self._data.layer == layer

    def is_connected_to_net(self, net: int) -> bool:
        """Check if any pad is connected to a specific net.

        Args:
            net: Net number to check

        Returns:
            True if any pad is on the net
        """
        return net in self.nets

    def move_by(self, dx: float, dy: float) -> None:
        """Move footprint by a delta.

        Args:
            dx: X offset in mm
            dy: Y offset in mm
        """
        self._data.position = Point(
            self._data.position.x + dx, self._data.position.y + dy
        )
        self._mark_modified()

    def rotate_by(self, angle: float) -> None:
        """Rotate footprint by an angle.

        Args:
            angle: Rotation delta in degrees
        """
        self.rotation = self._data.rotation + angle

    def flip_to_other_side(self) -> None:
        """Flip footprint to the opposite side of the board."""
        self.layer = "B.Cu" if self._data.layer == "F.Cu" else "F.Cu"

    def __repr__(self) -> str:
        """Get string representation.

        Returns:
            String representation with reference and position
        """
        return (
            f"FootprintWrapper(ref={self.reference}, "
            f"value={self.value}, "
            f"pos=({self.position.x:.2f}, {self.position.y:.2f}), "
            f"layer={self.layer})"
        )
