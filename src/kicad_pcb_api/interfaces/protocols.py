"""Protocol definitions for PCB elements.

Protocols define interfaces that elements can implement for duck typing.
This enables extensibility without rigid inheritance hierarchies.
"""

from typing import Optional, Protocol, runtime_checkable

from ..core.types import Point


@runtime_checkable
class PCBElement(Protocol):
    """Protocol for all PCB elements.

    Any object with a UUID can be treated as a PCB element.
    """

    @property
    def uuid(self) -> str:
        """Unique identifier for the element.

        Returns:
            UUID string
        """
        ...


@runtime_checkable
class Placeable(Protocol):
    """Protocol for elements that can be placed on the board.

    Elements implementing this protocol can be positioned and rotated.
    """

    @property
    def position(self) -> Point:
        """Get element position.

        Returns:
            Position point
        """
        ...

    @position.setter
    def position(self, value: Point) -> None:
        """Set element position.

        Args:
            value: New position
        """
        ...

    @property
    def rotation(self) -> float:
        """Get element rotation in degrees.

        Returns:
            Rotation angle
        """
        ...

    @rotation.setter
    def rotation(self, value: float) -> None:
        """Set element rotation.

        Args:
            value: New rotation in degrees
        """
        ...

    @property
    def uuid(self) -> str:
        """Unique identifier.

        Returns:
            UUID string
        """
        ...


@runtime_checkable
class Routable(Protocol):
    """Protocol for elements that carry electrical connections.

    Elements implementing this protocol can be part of routing.
    """

    @property
    def net(self) -> Optional[int]:
        """Get net number.

        Returns:
            Net number or None
        """
        ...

    @net.setter
    def net(self, value: Optional[int]) -> None:
        """Set net number.

        Args:
            value: New net number
        """
        ...

    @property
    def net_name(self) -> Optional[str]:
        """Get net name.

        Returns:
            Net name or None
        """
        ...

    @net_name.setter
    def net_name(self, value: Optional[str]) -> None:
        """Set net name.

        Args:
            value: New net name
        """
        ...

    @property
    def layer(self) -> str:
        """Get layer name.

        Returns:
            Layer name
        """
        ...

    @property
    def uuid(self) -> str:
        """Unique identifier.

        Returns:
            UUID string
        """
        ...


@runtime_checkable
class Connectable(Protocol):
    """Protocol for elements that can be connected (pads, vias, etc.).

    Elements implementing this protocol have a position and can be
    connected by traces.
    """

    @property
    def position(self) -> Point:
        """Get connection point position.

        Returns:
            Position point
        """
        ...

    @property
    def net(self) -> Optional[int]:
        """Get net number.

        Returns:
            Net number or None
        """
        ...

    @property
    def layer(self) -> str:
        """Get layer name.

        Returns:
            Layer name
        """
        ...


@runtime_checkable
class Layered(Protocol):
    """Protocol for elements that exist on specific layers.

    Elements implementing this protocol have a layer property.
    """

    @property
    def layer(self) -> str:
        """Get layer name.

        Returns:
            Layer name
        """
        ...

    @layer.setter
    def layer(self, value: str) -> None:
        """Set layer name.

        Args:
            value: New layer name
        """
        ...
