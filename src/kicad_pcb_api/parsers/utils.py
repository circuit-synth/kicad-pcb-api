"""
Utility functions for S-expression parsing.

Common helper functions used across multiple element parsers.
"""

from typing import Any, List, Optional

import sexpdata


def is_sexp_list(obj: Any) -> bool:
    """Check if object is a list (S-expression)."""
    return isinstance(obj, list)


def get_symbol_name(obj: Any) -> Optional[str]:
    """Get the name of a symbol if it is one."""
    if isinstance(obj, sexpdata.Symbol):
        return str(obj)
    return None


def to_string(obj: Any) -> str:
    """Convert a value to string, handling Symbol objects."""
    if isinstance(obj, sexpdata.Symbol):
        return str(obj)
    return obj


def find_element(sexp: List, name: str) -> Optional[Any]:
    """Find an element by name in an S-expression."""
    for item in sexp:
        if is_sexp_list(item) and get_symbol_name(item[0]) == name:
            return item
    return None


def find_all_elements(sexp: List, name: str) -> List[Any]:
    """Find all elements by name in an S-expression."""
    results = []
    for item in sexp:
        if is_sexp_list(item) and get_symbol_name(item[0]) == name:
            results.append(item)
    return results


def get_value(sexp: List, name: str, default: Any = None) -> Any:
    """Get the value of a named element."""
    element = find_element(sexp, name)
    if element and len(element) > 1:
        return element[1]
    return default
