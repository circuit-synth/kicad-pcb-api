"""
Footprint parser for KiCAD PCB files.

Handles parsing of footprint elements and their sub-elements (pads, graphics, etc).
"""

import logging
import uuid
from typing import Any, List, Optional

from ...core.types import (
    Arc,
    Footprint,
    Line,
    Pad,
    Point,
    Property,
    Rectangle,
    Text,
)
from ..base import BaseElementParser

logger = logging.getLogger(__name__)


class FootprintParser(BaseElementParser):
    """Parser for footprint elements."""

    def __init__(self):
        """Initialize footprint parser."""
        super().__init__("footprint")

    def parse_element(self, element: List[Any]) -> Optional[Footprint]:
        """Parse a footprint from S-expression."""
        try:
            # Get library ID (e.g., "Resistor_SMD:R_0603_1608Metric")
            lib_id = element[1]
            if ":" in lib_id:
                library, name = lib_id.split(":", 1)
            else:
                library = ""
                name = lib_id

            # Get layer
            layer_elem = self._find_element(element, "layer")
            layer = self._to_string(layer_elem[1]) if layer_elem else "F.Cu"

            # Get UUID
            uuid_elem = self._find_element(element, "uuid")
            fp_uuid = uuid_elem[1] if uuid_elem else str(uuid.uuid4())

            # Get position
            at_elem = self._find_element(element, "at")
            if not at_elem or len(at_elem) < 3:
                return None

            position = Point(float(at_elem[1]), float(at_elem[2]))
            rotation = float(at_elem[3]) if len(at_elem) > 3 else 0.0

            # Create footprint
            footprint = Footprint(
                library=library,
                name=name,
                position=position,
                rotation=rotation,
                layer=layer,
                uuid=fp_uuid,
            )

            # Parse description and tags
            footprint.descr = self._get_value(element, "descr", "")
            footprint.tags = self._get_value(element, "tags", "")

            # Parse attributes
            attr_elem = self._find_element(element, "attr")
            if attr_elem:
                footprint.attr = " ".join(str(a) for a in attr_elem[1:])

            # Parse properties
            for prop_elem in self._find_all_elements(element, "property"):
                prop = self._parse_property(prop_elem)
                if prop:
                    footprint.properties.append(prop)
                    # Set reference and value
                    if prop.name == "Reference":
                        footprint.reference = prop.value
                    elif prop.name == "Value":
                        footprint.value = prop.value

            # Parse path info
            path_elem = self._find_element(element, "path")
            if path_elem:
                footprint.path = path_elem[1]
            sheetname_elem = self._find_element(element, "sheetname")
            if sheetname_elem:
                footprint.sheetname = sheetname_elem[1]
            sheetfile_elem = self._find_element(element, "sheetfile")
            if sheetfile_elem:
                footprint.sheetfile = sheetfile_elem[1]

            # Parse graphical elements
            for line_elem in self._find_all_elements(element, "fp_line"):
                line = self._parse_line(line_elem)
                if line:
                    footprint.lines.append(line)

            for arc_elem in self._find_all_elements(element, "fp_arc"):
                arc = self._parse_arc(arc_elem)
                if arc:
                    footprint.arcs.append(arc)

            for text_elem in self._find_all_elements(element, "fp_text"):
                text = self._parse_text(text_elem)
                if text:
                    footprint.texts.append(text)

            for rect_elem in self._find_all_elements(element, "fp_rect"):
                rect = self._parse_rectangle(rect_elem)
                if rect:
                    footprint.rectangles.append(rect)

            # Parse pads
            for pad_elem in self._find_all_elements(element, "pad"):
                pad = self._parse_pad(pad_elem)
                if pad:
                    footprint.pads.append(pad)

            # Parse 3D model
            model_elem = self._find_element(element, "model")
            if model_elem:
                footprint.model_path = model_elem[1]
                # Parse offset, scale, rotate if present

            return footprint

        except Exception as e:
            logger.error(f"Error parsing footprint: {e}")
            return None

    def _parse_property(self, element: List[Any]) -> Optional[Property]:
        """Parse a property element."""
        if len(element) < 3:
            return None

        name = element[1]
        value = element[2]

        # Get position
        at_elem = self._find_element(element, "at")
        if at_elem and len(at_elem) >= 3:
            position = Point(float(at_elem[1]), float(at_elem[2]))
        else:
            position = Point(0, 0)

        # Get layer
        layer_elem = self._find_element(element, "layer")
        layer = self._to_string(layer_elem[1]) if layer_elem else "F.SilkS"

        # Get UUID
        uuid_elem = self._find_element(element, "uuid")
        prop_uuid = uuid_elem[1] if uuid_elem else str(uuid.uuid4())

        prop = Property(
            name=name, value=value, position=position, layer=layer, uuid=prop_uuid
        )

        # Parse effects
        effects_elem = self._find_element(element, "effects")
        if effects_elem:
            font_elem = self._find_element(effects_elem, "font")
            if font_elem:
                size_elem = self._find_element(font_elem, "size")
                if size_elem and len(size_elem) >= 3:
                    prop.size = (float(size_elem[1]), float(size_elem[2]))
                thickness_elem = self._find_element(font_elem, "thickness")
                if thickness_elem:
                    prop.thickness = float(thickness_elem[1])

        return prop

    def _parse_pad(self, element: List[Any]) -> Optional[Pad]:
        """Parse a pad element."""
        if len(element) < 4:
            return None

        number = str(element[1])
        pad_type = self._to_string(element[2])
        shape = self._to_string(element[3])

        # Get position
        at_elem = self._find_element(element, "at")
        if at_elem and len(at_elem) >= 3:
            position = Point(float(at_elem[1]), float(at_elem[2]))
        else:
            position = Point(0, 0)

        # Get size
        size_elem = self._find_element(element, "size")
        if size_elem and len(size_elem) >= 3:
            size = (float(size_elem[1]), float(size_elem[2]))
        else:
            size = (1.0, 1.0)

        # Get layers
        layers_elem = self._find_element(element, "layers")
        if layers_elem:
            layers = [str(l) for l in layers_elem[1:]]
        else:
            layers = []

        pad = Pad(
            number=number,
            type=pad_type,
            shape=shape,
            position=position,
            size=size,
            layers=layers,
        )

        # Get drill if present
        drill_elem = self._find_element(element, "drill")
        if drill_elem:
            if len(drill_elem) >= 4 and str(drill_elem[1]) == "oval":
                # Oval drill
                pad.drill = {
                    "shape": "oval",
                    "width": float(drill_elem[2]),
                    "height": float(drill_elem[3]),
                }
            else:
                # Circular drill
                pad.drill = float(drill_elem[1])

        # Get net
        net_elem = self._find_element(element, "net")
        if net_elem and len(net_elem) >= 3:
            pad.net = net_elem[1]
            pad.net_name = net_elem[2]

        # Get roundrect ratio
        rratio_elem = self._find_element(element, "roundrect_rratio")
        if rratio_elem:
            pad.roundrect_rratio = float(rratio_elem[1])

        # Get UUID
        uuid_elem = self._find_element(element, "uuid")
        pad.uuid = uuid_elem[1] if uuid_elem else str(uuid.uuid4())

        return pad

    def _parse_line(self, element: List[Any]) -> Optional[Line]:
        """Parse a line element."""
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

    def _parse_arc(self, element: List[Any]) -> Optional[Arc]:
        """Parse an arc element."""
        start_elem = self._find_element(element, "start")
        mid_elem = self._find_element(element, "mid")
        end_elem = self._find_element(element, "end")

        if not start_elem or not mid_elem or not end_elem:
            return None

        start = Point(float(start_elem[1]), float(start_elem[2]))
        mid = Point(float(mid_elem[1]), float(mid_elem[2]))
        end = Point(float(end_elem[1]), float(end_elem[2]))

        layer_elem = self._find_element(element, "layer")
        layer = layer_elem[1] if layer_elem else "F.SilkS"

        arc = Arc(start=start, mid=mid, end=end, layer=layer)

        # Parse stroke
        stroke_elem = self._find_element(element, "stroke")
        if stroke_elem:
            width_elem = self._find_element(stroke_elem, "width")
            if width_elem:
                arc.width = float(width_elem[1])
            type_elem = self._find_element(stroke_elem, "type")
            if type_elem:
                arc.type = type_elem[1]

        # Get UUID
        uuid_elem = self._find_element(element, "uuid")
        arc.uuid = uuid_elem[1] if uuid_elem else str(uuid.uuid4())

        return arc

    def _parse_rectangle(self, element: List[Any]) -> Optional[Rectangle]:
        """Parse a rectangle element."""
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

    def _parse_text(self, element: List[Any]) -> Optional[Text]:
        """Parse a text element."""
        if len(element) < 3:
            return None

        text_type = element[1]  # "reference", "value", "user"
        text_value = element[2]

        at_elem = self._find_element(element, "at")
        if at_elem and len(at_elem) >= 3:
            position = Point(float(at_elem[1]), float(at_elem[2]))
        else:
            position = Point(0, 0)

        layer_elem = self._find_element(element, "layer")
        layer = layer_elem[1] if layer_elem else "F.SilkS"

        text = Text(text=text_value, position=position, layer=layer)

        # Parse effects
        effects_elem = self._find_element(element, "effects")
        if effects_elem:
            font_elem = self._find_element(effects_elem, "font")
            if font_elem:
                size_elem = self._find_element(font_elem, "size")
                if size_elem and len(size_elem) >= 3:
                    text.size = (float(size_elem[1]), float(size_elem[2]))
                thickness_elem = self._find_element(font_elem, "thickness")
                if thickness_elem:
                    text.thickness = float(thickness_elem[1])

        # Get UUID
        uuid_elem = self._find_element(element, "uuid")
        text.uuid = uuid_elem[1] if uuid_elem else str(uuid.uuid4())

        return text
