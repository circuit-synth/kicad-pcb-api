"""Validation utilities for PCB elements."""

import re
from typing import Any, List, Optional

from .exceptions import (
    GeometryError,
    LayerError,
    NetError,
    ReferenceError,
    ValidationError,
)

# Standard KiCAD layers
STANDARD_LAYERS = {
    "F.Cu",
    "B.Cu",
    "In1.Cu",
    "In2.Cu",
    "In3.Cu",
    "In4.Cu",
    "In5.Cu",
    "In6.Cu",
    "F.SilkS",
    "B.SilkS",
    "F.Mask",
    "B.Mask",
    "F.Paste",
    "B.Paste",
    "F.Adhes",
    "B.Adhes",
    "F.CrtYd",
    "B.CrtYd",
    "F.Fab",
    "B.Fab",
    "Edge.Cuts",
    "Margin",
    "Dwgs.User",
    "Cmts.User",
    "Eco1.User",
    "Eco2.User",
}

# Reference designator pattern: Letter(s) followed by number(s)
REFERENCE_PATTERN = re.compile(r"^[A-Z]+\d+$")


def validate_reference(reference: str) -> None:
    """Validate a reference designator.

    Args:
        reference: Reference designator to validate (e.g., 'R1', 'C42', 'U10')

    Raises:
        ReferenceError: If reference is invalid
    """
    if not reference:
        raise ReferenceError("Reference cannot be empty", field="reference", value=reference)

    if not REFERENCE_PATTERN.match(reference):
        raise ReferenceError(
            f"Invalid reference format: '{reference}'. "
            f"Expected format: letter(s) followed by number(s) (e.g., 'R1', 'C42', 'U10')",
            field="reference",
            value=reference,
        )


def validate_layer(layer: str, allow_user_layers: bool = True) -> None:
    """Validate a layer name.

    Args:
        layer: Layer name to validate
        allow_user_layers: Whether to allow non-standard user-defined layers

    Raises:
        LayerError: If layer is invalid
    """
    if not layer:
        raise LayerError("Layer cannot be empty", field="layer", value=layer)

    if layer in STANDARD_LAYERS:
        return

    if allow_user_layers and (layer.endswith(".Cu") or layer.endswith(".User")):
        return

    raise LayerError(
        f"Invalid layer: '{layer}'. "
        f"Must be a standard KiCAD layer or valid user layer.",
        field="layer",
        value=layer,
    )


def validate_layers(layers: List[str], allow_user_layers: bool = True) -> None:
    """Validate a list of layer names.

    Args:
        layers: List of layer names to validate
        allow_user_layers: Whether to allow non-standard user-defined layers

    Raises:
        LayerError: If any layer is invalid
    """
    if not layers:
        raise LayerError("Layers list cannot be empty", field="layers", value=layers)

    for layer in layers:
        validate_layer(layer, allow_user_layers)


def validate_net(net: int, net_name: Optional[str] = None) -> None:
    """Validate a net specification.

    Args:
        net: Net number (0 for unconnected)
        net_name: Optional net name

    Raises:
        NetError: If net is invalid
    """
    if net < 0:
        raise NetError(
            f"Net number cannot be negative: {net}",
            field="net",
            value=net,
        )

    if net == 0 and net_name:
        raise NetError(
            "Net 0 (unconnected) cannot have a name",
            field="net",
            value=(net, net_name),
        )


def validate_positive(value: float, field_name: str) -> None:
    """Validate that a value is positive.

    Args:
        value: Value to validate
        field_name: Name of the field being validated

    Raises:
        ValidationError: If value is not positive
    """
    if value <= 0:
        raise ValidationError(
            f"{field_name} must be positive, got: {value}",
            field=field_name,
            value=value,
        )


def validate_non_negative(value: float, field_name: str) -> None:
    """Validate that a value is non-negative.

    Args:
        value: Value to validate
        field_name: Name of the field being validated

    Raises:
        ValidationError: If value is negative
    """
    if value < 0:
        raise ValidationError(
            f"{field_name} must be non-negative, got: {value}",
            field=field_name,
            value=value,
        )


def validate_track_width(width: float, min_width: float = 0.1, max_width: float = 10.0) -> None:
    """Validate track width is within reasonable bounds.

    Args:
        width: Track width in mm
        min_width: Minimum allowed width in mm
        max_width: Maximum allowed width in mm

    Raises:
        GeometryError: If width is invalid
    """
    if width < min_width:
        raise GeometryError(
            f"Track width {width}mm is below minimum {min_width}mm",
            field="width",
            value=width,
        )

    if width > max_width:
        raise GeometryError(
            f"Track width {width}mm exceeds maximum {max_width}mm",
            field="width",
            value=width,
        )


def validate_via_size(
    size: float,
    drill: float,
    min_size: float = 0.2,
    max_size: float = 10.0,
    min_drill: float = 0.1,
) -> None:
    """Validate via size and drill are within reasonable bounds.

    Args:
        size: Via pad size in mm
        drill: Via drill size in mm
        min_size: Minimum allowed pad size in mm
        max_size: Maximum allowed pad size in mm
        min_drill: Minimum allowed drill size in mm

    Raises:
        GeometryError: If sizes are invalid
    """
    if size < min_size:
        raise GeometryError(
            f"Via size {size}mm is below minimum {min_size}mm",
            field="size",
            value=size,
        )

    if size > max_size:
        raise GeometryError(
            f"Via size {size}mm exceeds maximum {max_size}mm",
            field="size",
            value=size,
        )

    if drill < min_drill:
        raise GeometryError(
            f"Via drill {drill}mm is below minimum {min_drill}mm",
            field="drill",
            value=drill,
        )

    if drill >= size:
        raise GeometryError(
            f"Via drill {drill}mm must be smaller than pad size {size}mm",
            field="drill",
            value=drill,
        )


def validate_uuid(uuid: str) -> None:
    """Validate a UUID string.

    Args:
        uuid: UUID string to validate

    Raises:
        ValidationError: If UUID is invalid
    """
    if not uuid:
        raise ValidationError("UUID cannot be empty", field="uuid", value=uuid)

    # KiCAD UUIDs are hex strings with dashes
    uuid_pattern = re.compile(r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$")
    if not uuid_pattern.match(uuid.lower()):
        raise ValidationError(
            f"Invalid UUID format: '{uuid}'. "
            f"Expected format: 8-4-4-4-12 hexadecimal digits with dashes",
            field="uuid",
            value=uuid,
        )
