"""
Via parser for KiCAD PCB files.

Handles parsing of via elements.
"""

import logging
import uuid
from typing import Any, List, Optional

from ...core.types import Point, Via
from ..base import BaseElementParser

logger = logging.getLogger(__name__)


class ViaParser(BaseElementParser):
    """Parser for via elements."""

    def __init__(self):
        """Initialize via parser."""
        super().__init__("via")

    def parse_element(self, element: List[Any]) -> Optional[Via]:
        """Parse a via element."""
        at_elem = self._find_element(element, "at")
        if not at_elem or len(at_elem) < 3:
            return None

        position = Point(float(at_elem[1]), float(at_elem[2]))

        size_elem = self._find_element(element, "size")
        size = float(size_elem[1]) if size_elem else 0.8

        drill_elem = self._find_element(element, "drill")
        drill = float(drill_elem[1]) if drill_elem else 0.4

        layers_elem = self._find_element(element, "layers")
        layers = (
            [str(l) for l in layers_elem[1:]] if layers_elem else ["F.Cu", "B.Cu"]
        )

        via = Via(position=position, size=size, drill=drill, layers=layers)

        net_elem = self._find_element(element, "net")
        if net_elem:
            via.net = net_elem[1]

        uuid_elem = self._find_element(element, "uuid")
        via.uuid = uuid_elem[1] if uuid_elem else str(uuid.uuid4())

        return via
