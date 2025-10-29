"""
Zone parser for KiCAD PCB files.

Handles parsing of zone/copper pour elements.
"""

import logging
from typing import Any, List, Optional

from ...core.types import Point, Zone
from ..base import BaseElementParser

logger = logging.getLogger(__name__)


class ZoneParser(BaseElementParser):
    """Parser for zone elements."""

    def __init__(self):
        """Initialize zone parser."""
        super().__init__("zone")

    def parse_element(self, element: List[Any]) -> Optional[Zone]:
        """Parse a zone element."""
        zone = Zone(layer="F.Cu")  # Default layer

        # Parse attributes
        for item in element[1:]:
            if not self._is_sexp_list(item):
                continue

            item_type = self._get_symbol_name(item[0])

            if item_type == "net":
                if len(item) >= 2:
                    zone.net = item[1]
                if len(item) >= 3:
                    zone.net_name = item[2]
            elif item_type == "net_name":
                zone.net_name = item[1]
            elif item_type == "layers":
                # Can be multiple layers
                zone.layer = " ".join(str(l) for l in item[1:])
            elif item_type == "uuid":
                zone.uuid = item[1]
            elif item_type == "hatch":
                if len(item) >= 3:
                    zone.hatch_thickness = float(item[2])
                if len(item) >= 4:
                    zone.hatch_gap = float(item[3])
            elif item_type == "connect_pads":
                connect_elem = self._find_element(item, "clearance")
                if connect_elem:
                    zone.thermal_relief_gap = float(connect_elem[1])
            elif item_type == "min_thickness":
                zone.min_thickness = float(item[1])
            elif item_type == "filled_areas_thickness":
                zone.filled = item[1] != "no"
            elif item_type == "fill":
                thermal_gap = self._find_element(item, "thermal_gap")
                if thermal_gap:
                    zone.thermal_relief_gap = float(thermal_gap[1])
                thermal_bridge = self._find_element(item, "thermal_bridge_width")
                if thermal_bridge:
                    zone.thermal_relief_bridge = float(thermal_bridge[1])
            elif item_type == "polygon":
                pts_elem = self._find_element(item, "pts")
                if pts_elem:
                    for pt in pts_elem[1:]:
                        if (
                            self._is_sexp_list(pt)
                            and self._get_symbol_name(pt[0]) == "xy"
                        ):
                            zone.polygon.append(Point(float(pt[1]), float(pt[2])))

        return zone
