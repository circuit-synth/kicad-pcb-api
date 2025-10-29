"""
Tests for the parser registry system.

Tests the modular parser architecture with element-specific parsers.
"""

import pytest

from kicad_pcb_api.core.types import Footprint, Line, Net, Point, Track, Via, Zone
from kicad_pcb_api.parsers import ParserRegistry
from kicad_pcb_api.parsers.elements import (
    FootprintParser,
    GraphicsLineParser,
    NetParser,
    TrackParser,
    ViaParser,
    ZoneParser,
)


def test_parser_registry_initialization():
    """Test basic registry initialization."""
    registry = ParserRegistry()
    assert registry is not None
    assert len(registry.get_registered_types()) == 0


def test_parser_registration():
    """Test registering parsers."""
    registry = ParserRegistry()

    # Register a parser
    net_parser = NetParser()
    registry.register("net", net_parser)

    assert registry.has_parser("net")
    assert "net" in registry.get_registered_types()
    assert not registry.has_parser("footprint")


def test_parser_registration_override():
    """Test overriding a parser registration."""
    registry = ParserRegistry()

    # Register a parser
    parser1 = NetParser()
    parser2 = NetParser()

    registry.register("net", parser1)
    registry.register("net", parser2)  # Should override

    assert registry.has_parser("net")
    assert len(registry.get_registered_types()) == 1


def test_parser_unregistration():
    """Test unregistering parsers."""
    registry = ParserRegistry()

    net_parser = NetParser()
    registry.register("net", net_parser)
    assert registry.has_parser("net")

    # Unregister
    result = registry.unregister("net")
    assert result is True
    assert not registry.has_parser("net")

    # Unregister non-existent
    result = registry.unregister("footprint")
    assert result is False


def test_parser_registry_clear():
    """Test clearing all parsers."""
    registry = ParserRegistry()

    registry.register("net", NetParser())
    registry.register("footprint", FootprintParser())
    registry.register("via", ViaParser())

    assert len(registry.get_registered_types()) == 3

    registry.clear()
    assert len(registry.get_registered_types()) == 0


def test_net_parser():
    """Test NetParser with registry."""
    registry = ParserRegistry()
    registry.register("net", NetParser())

    import sexpdata

    net_sexp = [sexpdata.Symbol("net"), 1, "GND"]
    result = registry.parse_element(net_sexp)

    assert result is not None
    assert isinstance(result, Net)
    assert result.number == 1
    assert result.name == "GND"


def test_track_parser():
    """Test TrackParser with registry."""
    registry = ParserRegistry()
    registry.register("segment", TrackParser())

    import sexpdata

    track_sexp = [
        sexpdata.Symbol("segment"),
        [sexpdata.Symbol("start"), 100.0, 100.0],
        [sexpdata.Symbol("end"), 150.0, 150.0],
        [sexpdata.Symbol("width"), 0.25],
        [sexpdata.Symbol("layer"), "F.Cu"],
        [sexpdata.Symbol("net"), 1],
        [sexpdata.Symbol("uuid"), "test-uuid"],
    ]
    result = registry.parse_element(track_sexp)

    assert result is not None
    assert isinstance(result, Track)
    assert result.start == Point(100.0, 100.0)
    assert result.end == Point(150.0, 150.0)
    assert result.width == 0.25
    assert result.layer == "F.Cu"
    assert result.net == 1


def test_via_parser():
    """Test ViaParser with registry."""
    registry = ParserRegistry()
    registry.register("via", ViaParser())

    import sexpdata

    via_sexp = [
        sexpdata.Symbol("via"),
        [sexpdata.Symbol("at"), 100.0, 100.0],
        [sexpdata.Symbol("size"), 0.8],
        [sexpdata.Symbol("drill"), 0.4],
        [sexpdata.Symbol("layers"), "F.Cu", "B.Cu"],
        [sexpdata.Symbol("net"), 1],
        [sexpdata.Symbol("uuid"), "test-uuid"],
    ]
    result = registry.parse_element(via_sexp)

    assert result is not None
    assert isinstance(result, Via)
    assert result.position == Point(100.0, 100.0)
    assert result.size == 0.8
    assert result.drill == 0.4
    assert result.layers == ["F.Cu", "B.Cu"]
    assert result.net == 1


def test_graphics_line_parser():
    """Test GraphicsLineParser with registry."""
    registry = ParserRegistry()
    registry.register("gr_line", GraphicsLineParser())

    import sexpdata

    line_sexp = [
        sexpdata.Symbol("gr_line"),
        [sexpdata.Symbol("start"), 0.0, 0.0],
        [sexpdata.Symbol("end"), 100.0, 100.0],
        [
            sexpdata.Symbol("stroke"),
            [sexpdata.Symbol("width"), 0.15],
            [sexpdata.Symbol("type"), sexpdata.Symbol("solid")],
        ],
        [sexpdata.Symbol("layer"), "Edge.Cuts"],
        [sexpdata.Symbol("uuid"), "test-uuid"],
    ]
    result = registry.parse_element(line_sexp)

    assert result is not None
    assert isinstance(result, Line)
    assert result.start == Point(0.0, 0.0)
    assert result.end == Point(100.0, 100.0)
    assert result.width == 0.15
    assert result.layer == "Edge.Cuts"


def test_zone_parser():
    """Test ZoneParser with registry."""
    registry = ParserRegistry()
    registry.register("zone", ZoneParser())

    import sexpdata

    zone_sexp = [
        sexpdata.Symbol("zone"),
        [sexpdata.Symbol("net"), 1, "GND"],
        [sexpdata.Symbol("layer"), "F.Cu"],
        [sexpdata.Symbol("uuid"), "test-uuid"],
        [sexpdata.Symbol("hatch"), sexpdata.Symbol("edge"), 0.5],
        [
            sexpdata.Symbol("connect_pads"),
            [sexpdata.Symbol("clearance"), 0.5],
        ],
        [sexpdata.Symbol("min_thickness"), 0.25],
        [sexpdata.Symbol("filled_areas_thickness"), sexpdata.Symbol("yes")],
    ]
    result = registry.parse_element(zone_sexp)

    assert result is not None
    assert isinstance(result, Zone)
    assert result.net == 1
    assert result.net_name == "GND"
    assert result.layer == "F.Cu"
    assert result.filled is True


def test_parse_multiple_elements():
    """Test parsing multiple elements at once."""
    registry = ParserRegistry()
    registry.register("net", NetParser())
    registry.register("segment", TrackParser())

    import sexpdata

    elements = [
        [sexpdata.Symbol("net"), 1, "GND"],
        [sexpdata.Symbol("net"), 2, "VCC"],
        [
            sexpdata.Symbol("segment"),
            [sexpdata.Symbol("start"), 0.0, 0.0],
            [sexpdata.Symbol("end"), 10.0, 10.0],
            [sexpdata.Symbol("width"), 0.25],
            [sexpdata.Symbol("layer"), "F.Cu"],
        ],
    ]

    results = registry.parse_elements(elements)

    assert len(results) == 3
    assert isinstance(results[0], Net)
    assert isinstance(results[1], Net)
    assert isinstance(results[2], Track)


def test_parser_with_invalid_element():
    """Test parser with invalid element."""
    registry = ParserRegistry()
    registry.register("net", NetParser())

    # Invalid element (not a list)
    result = registry.parse_element("invalid")
    assert result is None

    # Empty list
    result = registry.parse_element([])
    assert result is None


def test_parser_with_unknown_element():
    """Test parser with unknown element type."""
    registry = ParserRegistry()
    registry.register("net", NetParser())

    import sexpdata

    # Unknown element type
    unknown_sexp = [sexpdata.Symbol("unknown_type"), "data"]
    result = registry.parse_element(unknown_sexp)

    # Should return None as no parser is registered
    assert result is None


def test_footprint_parser_basic():
    """Test basic footprint parsing with registry."""
    registry = ParserRegistry()
    registry.register("footprint", FootprintParser())

    import sexpdata

    footprint_sexp = [
        sexpdata.Symbol("footprint"),
        "Resistor_SMD:R_0603_1608Metric",
        [sexpdata.Symbol("layer"), "F.Cu"],
        [sexpdata.Symbol("uuid"), "test-uuid"],
        [sexpdata.Symbol("at"), 100.0, 100.0, 0.0],
        [sexpdata.Symbol("property"), "Reference", "R1", [sexpdata.Symbol("at"), 100.0, 98.0], [sexpdata.Symbol("layer"), "F.SilkS"], [sexpdata.Symbol("uuid"), "prop-uuid"]],
        [sexpdata.Symbol("property"), "Value", "10k", [sexpdata.Symbol("at"), 100.0, 102.0], [sexpdata.Symbol("layer"), "F.Fab"], [sexpdata.Symbol("uuid"), "prop-uuid-2"]],
    ]

    result = registry.parse_element(footprint_sexp)

    assert result is not None
    assert isinstance(result, Footprint)
    assert result.library == "Resistor_SMD"
    assert result.name == "R_0603_1608Metric"
    assert result.position == Point(100.0, 100.0)
    assert result.layer == "F.Cu"
    assert result.reference == "R1"
    assert result.value == "10k"
