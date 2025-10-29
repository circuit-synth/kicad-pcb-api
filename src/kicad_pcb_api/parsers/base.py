"""
Base parser implementation for S-expression elements.

Provides common functionality and utilities for all element parsers.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

import sexpdata

logger = logging.getLogger(__name__)


class BaseElementParser(ABC):
    """Base implementation for S-expression element parsers."""

    def __init__(self, element_type: str):
        """
        Initialize base parser.

        Args:
            element_type: The S-expression element type this parser handles
        """
        self.element_type = element_type
        self._logger = logger.getChild(self.__class__.__name__)

    def can_parse(self, element: List[Any]) -> bool:
        """Check if this parser can handle the given element type."""
        if not element or not isinstance(element, list):
            return False

        element_type = element[0] if element else None
        # Convert sexpdata.Symbol to string for comparison
        element_type_str = self._get_symbol_name(element_type)
        return element_type_str == self.element_type

    def parse(self, element: List[Any]) -> Optional[Any]:
        """
        Parse an S-expression element with error handling.

        This method provides common error handling and validation,
        then delegates to the specific parse_element implementation.
        """
        if not self.can_parse(element):
            return None

        try:
            result = self.parse_element(element)
            if result is not None:
                self._logger.debug(f"Successfully parsed {self.element_type} element")
            return result
        except Exception as e:
            self._logger.error(f"Failed to parse {self.element_type} element: {e}")
            return None

    @abstractmethod
    def parse_element(self, element: List[Any]) -> Optional[Any]:
        """
        Parse the specific element type.

        This method should be implemented by subclasses to handle
        the specific parsing logic for their element type.

        Args:
            element: S-expression element to parse

        Returns:
            Parsed element data or None if parsing failed

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError(
            f"parse_element not implemented for {self.element_type}"
        )

    # Helper methods for S-expression manipulation

    def _is_sexp_list(self, obj: Any) -> bool:
        """Check if object is a list (S-expression)."""
        return isinstance(obj, list)

    def _get_symbol_name(self, obj: Any) -> Optional[str]:
        """Get the name of a symbol if it is one."""
        if isinstance(obj, sexpdata.Symbol):
            return str(obj)
        return None

    def _to_string(self, obj: Any) -> str:
        """Convert a value to string, handling Symbol objects."""
        if isinstance(obj, sexpdata.Symbol):
            return str(obj)
        return obj

    def _find_element(self, sexp: List, name: str) -> Optional[Any]:
        """Find an element by name in an S-expression."""
        for item in sexp:
            if self._is_sexp_list(item) and self._get_symbol_name(item[0]) == name:
                return item
        return None

    def _find_all_elements(self, sexp: List, name: str) -> List[Any]:
        """Find all elements by name in an S-expression."""
        results = []
        for item in sexp:
            if self._is_sexp_list(item) and self._get_symbol_name(item[0]) == name:
                results.append(item)
        return results

    def _get_value(self, sexp: List, name: str, default: Any = None) -> Any:
        """Get the value of a named element."""
        element = self._find_element(sexp, name)
        if element and len(element) > 1:
            return element[1]
        return default
