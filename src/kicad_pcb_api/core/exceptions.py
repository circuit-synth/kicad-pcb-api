"""Exception hierarchy for kicad-pcb-api."""


class KiCadPCBError(Exception):
    """Base exception for all kicad-pcb-api errors."""

    pass


class ValidationError(KiCadPCBError):
    """Raised when validation fails."""

    def __init__(self, message: str, field: str = "", value: object = None):
        """Initialize validation error with context.

        Args:
            message: Error message describing the validation failure
            field: The field name that failed validation
            value: The invalid value that was provided
        """
        self.field = field
        self.value = value
        super().__init__(message)


class ReferenceError(ValidationError):
    """Raised when a reference designator is invalid."""

    pass


class LayerError(ValidationError):
    """Raised when a layer specification is invalid."""

    pass


class NetError(ValidationError):
    """Raised when a net specification is invalid."""

    pass


class GeometryError(ValidationError):
    """Raised when geometry validation fails."""

    pass


class ParseError(KiCadPCBError):
    """Raised when parsing a PCB file fails."""

    pass


class FormatError(KiCadPCBError):
    """Raised when formatting a PCB file fails."""

    pass


class CollectionError(KiCadPCBError):
    """Raised when a collection operation fails."""

    pass


class ElementNotFoundError(CollectionError):
    """Raised when an element is not found in a collection."""

    def __init__(self, message: str, element_type: str = "", identifier: str = ""):
        """Initialize element not found error.

        Args:
            message: Error message
            element_type: Type of element (e.g., 'footprint', 'track')
            identifier: The identifier used to search (e.g., 'R1', UUID)
        """
        self.element_type = element_type
        self.identifier = identifier
        super().__init__(message)


class DuplicateElementError(CollectionError):
    """Raised when attempting to add a duplicate element."""

    def __init__(self, message: str, element_type: str = "", identifier: str = ""):
        """Initialize duplicate element error.

        Args:
            message: Error message
            element_type: Type of element (e.g., 'footprint', 'track')
            identifier: The duplicate identifier (e.g., 'R1', UUID)
        """
        self.element_type = element_type
        self.identifier = identifier
        super().__init__(message)
