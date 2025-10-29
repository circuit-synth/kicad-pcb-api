"""
Graphics parser for KiCAD PCB files.

Handles parsing of board graphics elements (lines, rectangles, etc).
"""

import logging
import uuid
from typing import Any, List, Optional, Union

from ...core.types import Line, Point, Rectangle
from ..base import BaseElementParser

logger = logging.getLogger(__name__)


class GraphicsLineParser(BaseElementParser):
    """Parser for graphics line elements."""

    def __init__(self):
        """Initialize graphics line parser."""
        super().__init__("gr_line")

    def parse_element(self, element: List[Any]) -> Optional[Line]:
        """Parse a graphics line element."""
        start_elem = self._find_element(element, "start")
        end_elem = self._find_element(element, "end")

        if not start_elem or not end_elem:
            return None

        start = Point(float(start_elem[1]), float(start_elem[2]))
        end = Point(float(end_elem[1]), float(end_elem[2]))

        layer_elem = self._find_element(element, "layer")
        layer = layer_elem[1] if layer_elem else "F.SilkS"

        line = Line(start=start, end=end, layer=layer)

        # Parse stroke
        stroke_elem = self._find_element(element, "stroke")
        if stroke_elem:
            width_elem = self._find_element(stroke_elem, "width")
            if width_elem:
                line.width = float(width_elem[1])
            type_elem = self._find_element(stroke_elem, "type")
            if type_elem:
                line.type = type_elem[1]

        # Get UUID
        uuid_elem = self._find_element(element, "uuid")
        line.uuid = uuid_elem[1] if uuid_elem else str(uuid.uuid4())

        return line


class GraphicsRectParser(BaseElementParser):
    """Parser for graphics rectangle elements."""

    def __init__(self):
        """Initialize graphics rectangle parser."""
        super().__init__("gr_rect")

    def parse_element(self, element: List[Any]) -> Optional[Rectangle]:
        """Parse a graphics rectangle element."""
        start_elem = self._find_element(element, "start")
        end_elem = self._find_element(element, "end")

        if not start_elem or not end_elem:
            return None

        start = Point(float(start_elem[1]), float(start_elem[2]))
        end = Point(float(end_elem[1]), float(end_elem[2]))

        layer_elem = self._find_element(element, "layer")
        layer = layer_elem[1] if layer_elem else "F.SilkS"

        rect = Rectangle(start=start, end=end, layer=layer)

        # Parse stroke
        stroke_elem = self._find_element(element, "stroke")
        if stroke_elem:
            width_elem = self._find_element(stroke_elem, "width")
            if width_elem:
                rect.width = float(width_elem[1])

        # Parse fill
        fill_elem = self._find_element(element, "fill")
        if fill_elem and len(fill_elem) > 1:
            # Handle both "no" and "none" as False
            # Convert to string in case it's a Symbol object
            fill_value = str(fill_elem[1])
            rect.fill = fill_value not in ["no", "none"]

        # Get UUID
        uuid_elem = self._find_element(element, "uuid")
        rect.uuid = uuid_elem[1] if uuid_elem else str(uuid.uuid4())

        return rect
