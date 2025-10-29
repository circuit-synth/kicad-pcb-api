"""
Parser registry for managing S-expression element parsers.

Provides a central registry for all element parsers and handles
dispatching parsing requests to the appropriate parser.
"""

import logging
from typing import Any, Dict, List, Optional

from .base import BaseElementParser

logger = logging.getLogger(__name__)


class ParserRegistry:
    """
    Central registry for all S-expression element parsers.

    This class manages the registration of element-specific parsers
    and provides a unified interface for parsing any S-expression element.
    """

    def __init__(self):
        """Initialize the parser registry."""
        self._parsers: Dict[str, BaseElementParser] = {}
        self._fallback_parser: Optional[BaseElementParser] = None
        self._logger = logger.getChild(self.__class__.__name__)

    def register(self, element_type: str, parser: BaseElementParser) -> None:
        """
        Register a parser for a specific element type.

        Args:
            element_type: The S-expression element type (e.g., "footprint", "via")
            parser: Parser instance that handles this element type

        Raises:
            ValueError: If element_type is already registered
        """
        if element_type in self._parsers:
            self._logger.warning(
                f"Overriding existing parser for element type: {element_type}"
            )

        self._parsers[element_type] = parser
        self._logger.debug(f"Registered parser for element type: {element_type}")

    def unregister(self, element_type: str) -> bool:
        """
        Unregister a parser for a specific element type.

        Args:
            element_type: The element type to unregister

        Returns:
            True if parser was removed, False if not found
        """
        if element_type in self._parsers:
            del self._parsers[element_type]
            self._logger.debug(f"Unregistered parser for element type: {element_type}")
            return True
        return False

    def set_fallback_parser(self, parser: BaseElementParser) -> None:
        """
        Set a fallback parser for unknown element types.

        Args:
            parser: Parser to use when no specific parser is registered
        """
        self._fallback_parser = parser
        self._logger.debug("Set fallback parser")

    def parse_element(self, element: List[Any]) -> Optional[Any]:
        """
        Parse an S-expression element using the appropriate registered parser.

        Args:
            element: S-expression element to parse

        Returns:
            Parsed element data or None if parsing failed
        """
        if not element or not isinstance(element, list):
            self._logger.debug("Invalid element: not a list or empty")
            return None

        element_type = element[0] if element else None
        # Convert sexpdata.Symbol to string for lookup
        element_type_str = str(element_type) if element_type else None
        if not element_type_str:
            self._logger.debug(f"Invalid element type: {element_type}")
            return None

        # Try specific parser first
        parser = self._parsers.get(element_type_str)
        if parser:
            self._logger.debug(
                f"Using registered parser for element type: {element_type_str}"
            )
            return parser.parse(element)

        # Try fallback parser
        if self._fallback_parser:
            self._logger.debug(
                f"Using fallback parser for unknown element type: {element_type_str}"
            )
            return self._fallback_parser.parse(element)

        # No parser available
        self._logger.debug(f"No parser available for element type: {element_type_str}")
        return None

    def parse_elements(self, elements: List[List[Any]]) -> List[Any]:
        """
        Parse multiple S-expression elements.

        Args:
            elements: List of S-expression elements to parse

        Returns:
            List of parsed element data (excluding failed parses)
        """
        results = []
        for element in elements:
            parsed = self.parse_element(element)
            if parsed is not None:
                results.append(parsed)

        self._logger.debug(f"Parsed {len(results)} of {len(elements)} elements")
        return results

    def get_registered_types(self) -> List[str]:
        """
        Get list of all registered element types.

        Returns:
            List of registered element type names
        """
        return list(self._parsers.keys())

    def has_parser(self, element_type: str) -> bool:
        """
        Check if a parser is registered for the given element type.

        Args:
            element_type: Element type to check

        Returns:
            True if parser is registered
        """
        return element_type in self._parsers

    def clear(self) -> None:
        """Clear all registered parsers."""
        self._parsers.clear()
        self._fallback_parser = None
        self._logger.debug("Cleared all registered parsers")
