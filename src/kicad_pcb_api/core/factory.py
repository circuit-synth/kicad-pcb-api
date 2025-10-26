"""Element factory for creating PCB elements with proper initialization."""

import uuid
from typing import List, Optional, Tuple

from .types import Footprint, Pad, Point, Track, Via


class PCBElementFactory:
    """Factory for creating properly initialized PCB elements.

    Ensures consistent UUID generation, default values, and proper initialization.
    """

    @staticmethod
    def generate_uuid() -> str:
        """Generate a new UUID for PCB elements.

        Returns:
            UUID string in standard format
        """
        return str(uuid.uuid4())

    @staticmethod
    def create_footprint(
        library: str,
        name: str,
        reference: str,
        value: str = "",
        position: Optional[Point] = None,
        rotation: float = 0.0,
        layer: str = "F.Cu",
    ) -> Footprint:
        """Create a new footprint with proper defaults.

        Args:
            library: Library name (e.g., 'Resistor_SMD')
            name: Footprint name (e.g., 'R_0603_1608Metric')
            reference: Reference designator (e.g., 'R1')
            value: Component value (e.g., '10k')
            position: Position on board (defaults to origin)
            rotation: Rotation in degrees
            layer: Layer (F.Cu or B.Cu)

        Returns:
            Initialized Footprint instance
        """
        if position is None:
            position = Point(0.0, 0.0)

        return Footprint(
            library=library,
            name=name,
            reference=reference,
            value=value,
            position=position,
            rotation=rotation,
            layer=layer,
            uuid=PCBElementFactory.generate_uuid(),
            locked=False,
            placed=True,
        )

    @staticmethod
    def create_pad(
        number: str,
        pad_type: str,
        shape: str,
        position: Point,
        size: Tuple[float, float],
        layers: Optional[List[str]] = None,
        drill: Optional[float] = None,
        net: Optional[int] = None,
        net_name: Optional[str] = None,
    ) -> Pad:
        """Create a new pad with proper defaults.

        Args:
            number: Pad number (e.g., '1', '2')
            pad_type: Pad type ('smd', 'thru_hole', 'np_thru_hole')
            shape: Pad shape ('circle', 'rect', 'roundrect', 'oval')
            position: Position relative to footprint origin
            size: Pad size (width, height) in mm
            layers: List of layers (defaults to ['F.Cu'] for SMD)
            drill: Drill diameter for through-hole pads
            net: Net number (0 = unconnected)
            net_name: Net name

        Returns:
            Initialized Pad instance
        """
        if layers is None:
            if pad_type == "smd":
                layers = ["F.Cu", "F.Paste", "F.Mask"]
            elif pad_type == "thru_hole":
                layers = ["*.Cu", "*.Mask"]
            else:
                layers = []

        return Pad(
            number=number,
            type=pad_type,
            shape=shape,
            position=position,
            size=size,
            layers=layers,
            drill=drill,
            net=net,
            net_name=net_name,
            uuid=PCBElementFactory.generate_uuid(),
        )

    @staticmethod
    def create_track(
        start: Point,
        end: Point,
        width: float,
        layer: str,
        net: Optional[int] = None,
        net_name: Optional[str] = None,
    ) -> Track:
        """Create a new track with proper defaults.

        Args:
            start: Track start point
            end: Track end point
            width: Track width in mm
            layer: Layer name (must be copper layer)
            net: Optional net number
            net_name: Optional net name

        Returns:
            Initialized Track instance
        """
        return Track(
            start=start,
            end=end,
            width=width,
            layer=layer,
            net=net,
            net_name=net_name,
            uuid=PCBElementFactory.generate_uuid(),
        )

    @staticmethod
    def create_via(
        position: Point,
        size: float,
        drill: float,
        layers: Optional[List[str]] = None,
        net: Optional[int] = None,
        net_name: Optional[str] = None,
    ) -> Via:
        """Create a new via with proper defaults.

        Args:
            position: Via position
            size: Via pad diameter in mm
            drill: Via drill diameter in mm
            layers: Layer span (defaults to through-hole F.Cu to B.Cu)
            net: Optional net number
            net_name: Optional net name

        Returns:
            Initialized Via instance
        """
        if layers is None:
            layers = ["F.Cu", "B.Cu"]  # Default to through-hole via

        return Via(
            position=position,
            size=size,
            drill=drill,
            layers=layers,
            net=net,
            net_name=net_name,
            uuid=PCBElementFactory.generate_uuid(),
        )

    @staticmethod
    def create_through_via(
        position: Point, size: float = 0.8, drill: float = 0.4
    ) -> Via:
        """Create a standard through-hole via.

        Args:
            position: Via position
            size: Via pad diameter in mm (default 0.8mm)
            drill: Via drill diameter in mm (default 0.4mm)

        Returns:
            Initialized through-hole Via
        """
        return PCBElementFactory.create_via(
            position=position,
            size=size,
            drill=drill,
            layers=["F.Cu", "B.Cu"],
        )

    @staticmethod
    def create_blind_via(
        position: Point,
        from_layer: str,
        to_layer: str,
        size: float = 0.6,
        drill: float = 0.3,
    ) -> Via:
        """Create a blind via (outer layer to inner layer).

        Args:
            position: Via position
            from_layer: Starting layer (e.g., 'F.Cu')
            to_layer: Ending layer (e.g., 'In1.Cu')
            size: Via pad diameter in mm
            drill: Via drill diameter in mm

        Returns:
            Initialized blind Via
        """
        # Determine layer span
        layers = [from_layer]
        if to_layer != from_layer:
            layers.append(to_layer)

        return PCBElementFactory.create_via(
            position=position, size=size, drill=drill, layers=layers
        )
