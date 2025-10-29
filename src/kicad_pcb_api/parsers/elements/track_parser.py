"""
Track (segment) parser for KiCAD PCB files.

Handles parsing of track/segment elements.
"""

import logging
import uuid
from typing import Any, List, Optional

from ...core.types import Point, Track
from ..base import BaseElementParser

logger = logging.getLogger(__name__)


class TrackParser(BaseElementParser):
    """Parser for track (segment) elements."""

    def __init__(self):
        """Initialize track parser."""
        super().__init__("segment")

    def parse_element(self, element: List[Any]) -> Optional[Track]:
        """Parse a track (segment) element."""
        start_elem = self._find_element(element, "start")
        end_elem = self._find_element(element, "end")

        if not start_elem or not end_elem:
            return None

        start = Point(float(start_elem[1]), float(start_elem[2]))
        end = Point(float(end_elem[1]), float(end_elem[2]))

        width_elem = self._find_element(element, "width")
        width = float(width_elem[1]) if width_elem else 0.25

        layer_elem = self._find_element(element, "layer")
        layer = self._to_string(layer_elem[1]) if layer_elem else "F.Cu"

        track = Track(start=start, end=end, width=width, layer=layer)

        net_elem = self._find_element(element, "net")
        if net_elem:
            track.net = net_elem[1]

        uuid_elem = self._find_element(element, "uuid")
        track.uuid = uuid_elem[1] if uuid_elem else str(uuid.uuid4())

        return track
