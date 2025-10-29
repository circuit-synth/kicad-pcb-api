"""
Metadata parser for KiCAD PCB files.

Handles parsing of metadata elements (nets, layers, general, etc).
"""

import logging
from typing import Any, Dict, List, Optional

from ...core.types import Net
from ..base import BaseElementParser

logger = logging.getLogger(__name__)


class NetParser(BaseElementParser):
    """Parser for net elements."""

    def __init__(self):
        """Initialize net parser."""
        super().__init__("net")

    def parse_element(self, element: List[Any]) -> Optional[Net]:
        """Parse a net definition."""
        if len(element) < 3:
            return None
        return Net(number=element[1], name=element[2])


class LayersParser(BaseElementParser):
    """Parser for layers section."""

    def __init__(self):
        """Initialize layers parser."""
        super().__init__("layers")

    def parse_element(self, element: List[Any]) -> List[Dict[str, Any]]:
        """Parse layers section."""
        layers = []
        for item in element[1:]:
            if self._is_sexp_list(item) and len(item) >= 3:
                layer = {
                    "number": item[0],
                    "canonical_name": item[1],
                    "type": item[2],
                }
                if len(item) > 3:
                    layer["user_name"] = item[3]
                layers.append(layer)
        return layers


class GeneralParser(BaseElementParser):
    """Parser for general section."""

    def __init__(self):
        """Initialize general parser."""
        super().__init__("general")

    def parse_element(self, element: List[Any]) -> Dict[str, Any]:
        """Parse general section."""
        general = {}
        general["thickness"] = self._get_value(element, "thickness", 1.6)
        general["legacy_teardrops"] = (
            self._get_value(element, "legacy_teardrops", "no") == "yes"
        )
        return general
