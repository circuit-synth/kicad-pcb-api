"""
Parser module for KiCAD PCB files.

Provides a registry-based parser architecture for modular and extensible parsing.
"""

from .base import BaseElementParser
from .registry import ParserRegistry
from .utils import (
    find_all_elements,
    find_element,
    get_symbol_name,
    get_value,
    is_sexp_list,
    to_string,
)

__all__ = [
    "BaseElementParser",
    "ParserRegistry",
    "find_all_elements",
    "find_element",
    "get_symbol_name",
    "get_value",
    "is_sexp_list",
    "to_string",
]
