"""
Comprehensive tests for PCBFormatter class.
"""

import pytest
import sexpdata

from kicad_pcb_api.core.pcb_formatter import PCBFormatter
from kicad_pcb_api.core.types import (
    Footprint,
    Line,
    Net,
    Pad,
    Point,
    Property,
    Rectangle,
    Track,
    Via,
    Zone,
)


@pytest.fixture
def formatter():
    """Provide a PCBFormatter instance."""
    return PCBFormatter()


def test_formatter_initialization(formatter):
    """Test formatter initializes correctly."""
    assert formatter.indent_level == 0
    assert formatter.indent_str == "  "


def test_format_simple_symbol(formatter):
    """Test formatting a simple symbol."""
    symbol = sexpdata.Symbol("kicad_pcb")
    result = formatter.format(symbol)
    assert result == "kicad_pcb"


def test_format_string_unquoted_keyword(formatter):
    """Test formatting strings that are KiCad keywords (unquoted)."""
    # Keywords should be unquoted
    assert formatter.format("yes") == "yes"
    assert formatter.format("no") == "no"
    assert formatter.format("signal") == "signal"
    assert formatter.format("setup") == "setup"


def test_format_string_quoted(formatter):
    """Test formatting strings that should be quoted."""
    # Non-keywords should be quoted
    result = formatter.format("My Custom String")
    assert result == '"My Custom String"'

    result = formatter.format("Edge.Cuts")
    assert result == '"Edge.Cuts"'


def test_format_number(formatter):
    """Test formatting numbers."""
    assert formatter.format(42) == "42"
    assert formatter.format(3.14159) == "3.14159"
    assert formatter.format(-10.5) == "-10.5"


def test_format_boolean(formatter):
    """Test formatting boolean values."""
    assert formatter.format(True) == "yes"
    assert formatter.format(False) == "no"


def test_format_simple_list(formatter):
    """Test formatting a simple key-value list."""
    expr = [sexpdata.Symbol("version"), 20241229]
    result = formatter.format(expr)
    assert result == "(version 20241229)"


def test_format_inline_list(formatter):
    """Test formatting lists that should be inline."""
    # 'at' should be inline
    at_expr = [sexpdata.Symbol("at"), 100.0, 50.0, 90.0]
    result = formatter.format(at_expr)
    assert result == "(at 100.0 50.0 90.0)"

    # 'size' should be inline
    size_expr = [sexpdata.Symbol("size"), 1.0, 1.0]
    result = formatter.format(size_expr)
    assert result == "(size 1.0 1.0)"

    # 'layers' should be inline
    layers_expr = [sexpdata.Symbol("layers"), "F.Cu", "F.Paste", "F.Mask"]
    result = formatter.format(layers_expr)
    assert result == '(layers "F.Cu" "F.Paste" "F.Mask")'


def test_format_nested_list(formatter):
    """Test formatting nested lists with proper indentation."""
    # Create a nested structure
    expr = [
        sexpdata.Symbol("footprint"),
        "Resistor_SMD:R_0603",
        [sexpdata.Symbol("layer"), "F.Cu"],
        [sexpdata.Symbol("at"), 100, 50],
    ]

    result = formatter.format(expr)

    # Should have footprint on first line, nested items indented
    assert result.startswith("(footprint")
    assert "Resistor_SMD:R_0603" in result
    assert "(layer" in result
    assert "(at 100 50)" in result


def test_format_pcb_header(formatter):
    """Test formatting PCB header correctly."""
    pcb_expr = [
        sexpdata.Symbol("kicad_pcb"),
        [sexpdata.Symbol("version"), 20241229],
        [sexpdata.Symbol("generator"), "pcbnew"],
        [sexpdata.Symbol("generator_version"), "9.0"],
        [sexpdata.Symbol("general"), [sexpdata.Symbol("thickness"), 1.6]],
    ]

    result = formatter.format_pcb(pcb_expr)

    # Header elements should be on one line
    lines = result.split("\n")
    assert lines[0].startswith("(kicad_pcb (version 20241229)")
    assert "generator" in lines[0]
    assert "generator_version" in lines[0]


def test_format_empty_list(formatter):
    """Test formatting empty list."""
    result = formatter.format([])
    assert result == "()"


def test_format_net(formatter):
    """Test formatting net S-expressions."""
    net_expr = [sexpdata.Symbol("net"), 1, "GND"]
    result = formatter.format(net_expr)
    assert result == '(net 1 "GND")'


def test_format_stroke(formatter):
    """Test formatting stroke element (should be inline)."""
    stroke_expr = [
        sexpdata.Symbol("stroke"),
        [sexpdata.Symbol("width"), 0.15],
        [sexpdata.Symbol("type"), sexpdata.Symbol("solid")],
    ]

    result = formatter.format(stroke_expr)
    assert "(stroke" in result
    assert "(width 0.15)" in result
    assert "(type solid)" in result


def test_format_symbol_vs_string():
    """Test that symbols and strings are formatted differently."""
    formatter = PCBFormatter()

    # Symbols should never be quoted
    symbol = sexpdata.Symbol("F.Cu")
    assert formatter.format(symbol) == "F.Cu"

    # Strings that are not keywords should be quoted
    string = "F.Cu"
    assert formatter.format(string) == '"F.Cu"'


def test_format_effects(formatter):
    """Test formatting effects element."""
    effects_expr = [
        sexpdata.Symbol("effects"),
        [
            sexpdata.Symbol("font"),
            [sexpdata.Symbol("size"), 1.0, 1.0],
            [sexpdata.Symbol("thickness"), 0.15],
        ],
    ]

    result = formatter.format(effects_expr)
    assert "(effects" in result
    assert "(font" in result
    assert "(size 1.0 1.0)" in result
    assert "(thickness 0.15)" in result


def test_format_pad(formatter):
    """Test formatting pad element."""
    pad_expr = [
        sexpdata.Symbol("pad"),
        "1",
        sexpdata.Symbol("smd"),
        sexpdata.Symbol("rect"),
        [sexpdata.Symbol("at"), -0.875, 0],
        [sexpdata.Symbol("size"), 1.05, 0.95],
        [sexpdata.Symbol("layers"), "F.Cu", "F.Paste", "F.Mask"],
        [sexpdata.Symbol("net"), 1, "GND"],
        [sexpdata.Symbol("uuid"), "test-uuid"],
    ]

    result = formatter.format(pad_expr)

    # Check all elements are present
    assert "(pad" in result
    assert "smd" in result
    assert "rect" in result
    assert "(at -0.875 0)" in result
    assert "(size 1.05 0.95)" in result
    assert "F.Cu" in result
    assert '"GND"' in result


def test_format_property(formatter):
    """Test formatting property element."""
    property_expr = [
        sexpdata.Symbol("property"),
        "Reference",
        "R1",
        [sexpdata.Symbol("at"), 0, 0, 0],
        [sexpdata.Symbol("layer"), "F.SilkS"],
        [sexpdata.Symbol("uuid"), "prop-uuid"],
        [
            sexpdata.Symbol("effects"),
            [
                sexpdata.Symbol("font"),
                [sexpdata.Symbol("size"), 1.0, 1.0],
                [sexpdata.Symbol("thickness"), 0.15],
            ],
        ],
    ]

    result = formatter.format(property_expr)

    assert "(property" in result
    assert '"Reference"' in result
    assert '"R1"' in result
    assert "(at 0 0 0)" in result
    assert "(layer" in result


def test_format_zone(formatter):
    """Test formatting zone element."""
    zone_expr = [
        sexpdata.Symbol("zone"),
        [sexpdata.Symbol("net"), 1],
        [sexpdata.Symbol("net_name"), "GND"],
        [sexpdata.Symbol("layer"), "F.Cu"],
        [sexpdata.Symbol("uuid"), "zone-uuid"],
        [sexpdata.Symbol("hatch"), sexpdata.Symbol("edge"), 0.5],
        [
            sexpdata.Symbol("polygon"),
            [
                sexpdata.Symbol("pts"),
                [sexpdata.Symbol("xy"), 10, 10],
                [sexpdata.Symbol("xy"), 90, 10],
                [sexpdata.Symbol("xy"), 90, 50],
                [sexpdata.Symbol("xy"), 10, 50],
            ],
        ],
    ]

    result = formatter.format(zone_expr)

    assert "(zone" in result
    assert "(net 1)" in result
    assert '"GND"' in result
    assert "(polygon" in result
    assert "(xy 10 10)" in result


def test_format_complete_pcb(formatter):
    """Test formatting a complete minimal PCB."""
    pcb_expr = [
        sexpdata.Symbol("kicad_pcb"),
        [sexpdata.Symbol("version"), 20241229],
        [sexpdata.Symbol("generator"), "pcbnew"],
        [sexpdata.Symbol("generator_version"), "9.0"],
        [
            sexpdata.Symbol("general"),
            [sexpdata.Symbol("thickness"), 1.6],
            [sexpdata.Symbol("legacy_teardrops"), sexpdata.Symbol("no")],
        ],
        [sexpdata.Symbol("paper"), "A4"],
        [
            sexpdata.Symbol("layers"),
            [0, "F.Cu", sexpdata.Symbol("signal")],
            [31, "B.Cu", sexpdata.Symbol("signal")],
        ],
        [sexpdata.Symbol("net"), 0, ""],
        [sexpdata.Symbol("net"), 1, "GND"],
        [sexpdata.Symbol("embedded_fonts"), sexpdata.Symbol("no")],
    ]

    result = formatter.format_pcb(pcb_expr)

    # Verify structure
    assert result.startswith("(kicad_pcb")
    assert result.endswith(")")
    assert "(version 20241229)" in result
    assert "(generator" in result
    assert "(general" in result
    assert "(paper" in result
    assert "(layers" in result
    assert "(net 0" in result
    assert "(net 1" in result

    # Should have proper line breaks
    lines = result.split("\n")
    assert len(lines) > 5  # Multiple lines


def test_format_indentation_reset(formatter):
    """Test that indentation resets properly between calls."""
    # Format first expression
    expr1 = [
        sexpdata.Symbol("footprint"),
        "Test",
        [sexpdata.Symbol("layer"), "F.Cu"],
    ]
    formatter.format(expr1)

    # Indentation should be reset
    assert formatter.indent_level == 0

    # Format second expression - should not be affected
    expr2 = [sexpdata.Symbol("net"), 0, ""]
    result = formatter.format(expr2)
    assert result == '(net 0 "")'


def test_format_preserves_precision(formatter):
    """Test that floating point precision is preserved."""
    # Test various precisions
    expr = [sexpdata.Symbol("at"), 100.123456, 50.987654, 45.5]
    result = formatter.format(expr)

    # Should preserve decimal values
    assert "100.123456" in result
    assert "50.987654" in result
    assert "45.5" in result


def test_format_special_characters_in_strings(formatter):
    """Test formatting strings with special characters."""
    # Strings with spaces should be quoted
    result = formatter.format("My Component")
    assert result == '"My Component"'

    # Strings with parentheses should be quoted
    result = formatter.format("Test (A)")
    assert result == '"Test (A)"'


def test_format_multiline_footprint(formatter):
    """Test formatting a footprint with proper multiline structure."""
    footprint_expr = [
        sexpdata.Symbol("footprint"),
        "Resistor_SMD:R_0603",
        [sexpdata.Symbol("layer"), "F.Cu"],
        [sexpdata.Symbol("uuid"), "test-uuid"],
        [sexpdata.Symbol("at"), 100, 50, 0],
        [
            sexpdata.Symbol("property"),
            "Reference",
            "R1",
            [sexpdata.Symbol("at"), 0, 0, 0],
            [sexpdata.Symbol("layer"), "F.SilkS"],
            [sexpdata.Symbol("uuid"), "ref-uuid"],
        ],
        [
            sexpdata.Symbol("pad"),
            "1",
            sexpdata.Symbol("smd"),
            sexpdata.Symbol("rect"),
            [sexpdata.Symbol("at"), 0, 0],
            [sexpdata.Symbol("size"), 1.0, 1.0],
            [sexpdata.Symbol("layers"), "F.Cu"],
        ],
    ]

    result = formatter.format(footprint_expr)

    # Should be multiline
    assert "\n" in result

    # Should have proper structure
    assert "(footprint" in result
    assert "(property" in result
    assert "(pad" in result


def test_format_via(formatter):
    """Test formatting via element."""
    via_expr = [
        sexpdata.Symbol("via"),
        [sexpdata.Symbol("at"), 50, 50],
        [sexpdata.Symbol("size"), 0.8],
        [sexpdata.Symbol("drill"), 0.4],
        [sexpdata.Symbol("layers"), "F.Cu", "B.Cu"],
        [sexpdata.Symbol("net"), 1],
        [sexpdata.Symbol("uuid"), "via-uuid"],
    ]

    result = formatter.format(via_expr)

    assert "(via" in result
    assert "(at 50 50)" in result
    assert "(size 0.8)" in result
    assert "(drill 0.4)" in result
    assert "F.Cu" in result
    assert "B.Cu" in result


def test_format_segment(formatter):
    """Test formatting segment (track) element."""
    segment_expr = [
        sexpdata.Symbol("segment"),
        [sexpdata.Symbol("start"), 10, 20],
        [sexpdata.Symbol("end"), 30, 40],
        [sexpdata.Symbol("width"), 0.25],
        [sexpdata.Symbol("layer"), "F.Cu"],
        [sexpdata.Symbol("net"), 1],
        [sexpdata.Symbol("uuid"), "track-uuid"],
    ]

    result = formatter.format(segment_expr)

    assert "(segment" in result
    assert "(start 10 20)" in result
    assert "(end 30 40)" in result
    assert "(width 0.25)" in result


def test_format_gr_line(formatter):
    """Test formatting graphics line."""
    gr_line_expr = [
        sexpdata.Symbol("gr_line"),
        [sexpdata.Symbol("start"), 0, 0],
        [sexpdata.Symbol("end"), 100, 0],
        [
            sexpdata.Symbol("stroke"),
            [sexpdata.Symbol("width"), 0.15],
            [sexpdata.Symbol("type"), sexpdata.Symbol("solid")],
        ],
        [sexpdata.Symbol("layer"), "Edge.Cuts"],
        [sexpdata.Symbol("uuid"), "line-uuid"],
    ]

    result = formatter.format(gr_line_expr)

    assert "(gr_line" in result
    assert "(start 0 0)" in result
    assert "(end 100 0)" in result
    assert "(stroke" in result


def test_format_gr_rect(formatter):
    """Test formatting graphics rectangle."""
    gr_rect_expr = [
        sexpdata.Symbol("gr_rect"),
        [sexpdata.Symbol("start"), 10, 10],
        [sexpdata.Symbol("end"), 90, 50],
        [
            sexpdata.Symbol("stroke"),
            [sexpdata.Symbol("width"), 0.1],
            [sexpdata.Symbol("type"), sexpdata.Symbol("default")],
        ],
        [sexpdata.Symbol("fill"), sexpdata.Symbol("no")],
        [sexpdata.Symbol("layer"), "Dwgs.User"],
        [sexpdata.Symbol("uuid"), "rect-uuid"],
    ]

    result = formatter.format(gr_rect_expr)

    assert "(gr_rect" in result
    assert "(start 10 10)" in result
    assert "(end 90 50)" in result
    assert "(fill no)" in result
