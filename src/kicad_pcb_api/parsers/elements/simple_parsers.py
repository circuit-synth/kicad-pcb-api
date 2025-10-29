"""
Simple element parsers for metadata and configuration.

Handles parsing of simple scalar and configuration elements like
version, generator, paper size, setup, and embedded fonts.
"""

import logging
from typing import Any, Dict, List, Optional

from ..base import BaseElementParser

logger = logging.getLogger(__name__)


class VersionParser(BaseElementParser):
    """Parser for version element."""

    def __init__(self):
        """Initialize version parser."""
        super().__init__("version")

    def parse_element(self, element: List[Any]) -> Optional[Dict[str, Any]]:
        """Parse version element: (version 20241229)"""
        if len(element) < 2:
            return None

        return {
            "type": "version",
            "value": int(element[1])
        }


class GeneratorParser(BaseElementParser):
    """Parser for generator element."""

    def __init__(self):
        """Initialize generator parser."""
        super().__init__("generator")

    def parse_element(self, element: List[Any]) -> Optional[Dict[str, Any]]:
        """Parse generator element: (generator "pcbnew") or (generator "pcbnew" "9.0")"""
        if len(element) < 2:
            return None

        result = {
            "type": "generator",
            "name": str(element[1])
        }

        # Optional version
        if len(element) > 2:
            result["version"] = str(element[2])

        return result


class PaperParser(BaseElementParser):
    """Parser for paper element."""

    def __init__(self):
        """Initialize paper parser."""
        super().__init__("paper")

    def parse_element(self, element: List[Any]) -> Optional[Dict[str, Any]]:
        """Parse paper element: (paper "A4")"""
        if len(element) < 2:
            return None

        return {
            "type": "paper",
            "size": str(element[1])
        }


class SetupParser(BaseElementParser):
    """Parser for setup element."""

    def __init__(self):
        """Initialize setup parser."""
        super().__init__("setup")

    def parse_element(self, element: List[Any]) -> Optional[Dict[str, Any]]:
        """
        Parse setup element containing board setup configuration.

        Example: (setup
                   (pad_to_mask_clearance 0)
                   (grid_origin 100 100)
                   ...)
        """
        setup_data = {
            "type": "setup",
            "raw": element  # Store raw for exact format preservation
        }

        # Parse common setup parameters
        for sub_elem in element[1:]:
            if not self._is_sexp_list(sub_elem):
                continue

            param_name = self._get_symbol_name(sub_elem[0])
            if not param_name:
                continue

            # Store each parameter
            if len(sub_elem) == 2:
                # Simple value: (param value)
                setup_data[param_name] = sub_elem[1]
            elif len(sub_elem) > 2:
                # Multiple values or nested: store as list
                setup_data[param_name] = list(sub_elem[1:])

        return setup_data


class EmbeddedFontsParser(BaseElementParser):
    """Parser for embedded_fonts element."""

    def __init__(self):
        """Initialize embedded_fonts parser."""
        super().__init__("embedded_fonts")

    def parse_element(self, element: List[Any]) -> Optional[Dict[str, Any]]:
        """Parse embedded_fonts element: (embedded_fonts yes)"""
        if len(element) < 2:
            return None

        value_str = str(element[1]).lower()
        value = value_str in ("yes", "true", "1")

        return {
            "type": "embedded_fonts",
            "enabled": value
        }
