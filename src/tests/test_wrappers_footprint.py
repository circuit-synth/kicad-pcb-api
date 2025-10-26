"""
Tests for FootprintWrapper validation and functionality.

Tests:
- Reference validation and duplicate detection
- Value and position updates
- Rotation and layer changes
- Parent collection index updates
- Convenience methods (move_by, rotate_by, flip)
"""

import pytest

from kicad_pcb_api.collections.footprints import FootprintCollection
from kicad_pcb_api.core.exceptions import ReferenceError, ValidationError
from kicad_pcb_api.core.types import Footprint, Point
from kicad_pcb_api.wrappers.footprint import FootprintWrapper


def create_test_footprint(ref: str = "R1", x: float = 0.0, y: float = 0.0) -> Footprint:
    """Helper to create a test footprint."""
    return Footprint(
        reference=ref,
        value="10k",
        library="Resistor_SMD",
        name="R_0603_1608Metric",
        position=Point(x, y),
        rotation=0.0,
        layer="F.Cu",
        pads=[],
        uuid=f"test-uuid-{ref}",
    )


class TestFootprintWrapperValidation:
    """Test validation in FootprintWrapper."""

    def test_reference_validation_invalid_format(self):
        """Test that invalid reference formats are rejected."""
        collection = FootprintCollection()
        footprint = create_test_footprint("R1")
        collection.add(footprint)

        wrapper = collection.get_by_reference("R1")

        # Invalid formats should raise ReferenceError
        with pytest.raises(ReferenceError, match="Invalid reference format"):
            wrapper.reference = "123"  # No letters

        with pytest.raises(ReferenceError, match="Invalid reference format"):
            wrapper.reference = "R-1"  # Invalid character

        with pytest.raises(ReferenceError, match="Reference cannot be empty"):
            wrapper.reference = ""

    def test_reference_validation_duplicate(self):
        """Test that duplicate references are rejected."""
        collection = FootprintCollection()
        collection.add(create_test_footprint("R1"))
        collection.add(create_test_footprint("R2"))

        wrapper = collection.get_by_reference("R1")

        # Trying to change R1 to R2 should fail
        with pytest.raises(ReferenceError, match="already exists"):
            wrapper.reference = "R2"

    def test_reference_update_valid(self):
        """Test that valid reference updates work and update indexes."""
        collection = FootprintCollection()
        footprint = create_test_footprint("R1")
        collection.add(footprint)

        wrapper = collection.get_by_reference("R1")
        wrapper.reference = "R100"

        # Old reference should not be found
        assert collection.get_by_reference("R1") is None

        # New reference should be found
        new_wrapper = collection.get_by_reference("R100")
        assert new_wrapper is not None
        assert new_wrapper.uuid == wrapper.uuid

    def test_layer_validation(self):
        """Test that invalid layers are rejected."""
        collection = FootprintCollection()
        collection.add(create_test_footprint("R1"))

        wrapper = collection.get_by_reference("R1")

        # Only F.Cu and B.Cu are valid for footprints
        with pytest.raises(ValidationError, match="must be 'F.Cu' or 'B.Cu'"):
            wrapper.layer = "In1.Cu"

        with pytest.raises(ValidationError, match="must be 'F.Cu' or 'B.Cu'"):
            wrapper.layer = "F.SilkS"

    def test_position_validation(self):
        """Test that invalid positions are rejected."""
        collection = FootprintCollection()
        collection.add(create_test_footprint("R1"))

        wrapper = collection.get_by_reference("R1")

        # Position must be a Point instance
        with pytest.raises(ValidationError, match="must be a Point instance"):
            wrapper.position = (10.0, 20.0)  # type: ignore


class TestFootprintWrapperProperties:
    """Test FootprintWrapper property access and updates."""

    def test_property_getters(self):
        """Test that property getters return correct values."""
        collection = FootprintCollection()
        footprint = create_test_footprint("R1", 50.0, 75.0)
        footprint.rotation = 90.0
        collection.add(footprint)

        wrapper = collection.get_by_reference("R1")

        assert wrapper.reference == "R1"
        assert wrapper.value == "10k"
        # lib_id property returns library:name
        assert wrapper.lib_id == "Resistor_SMD:R_0603_1608Metric"
        assert wrapper.position.x == 50.0
        assert wrapper.position.y == 75.0
        assert wrapper.rotation == 90.0
        assert wrapper.layer == "F.Cu"

    def test_value_update(self):
        """Test value property update and modification tracking."""
        collection = FootprintCollection()
        collection.add(create_test_footprint("R1"))

        wrapper = collection.get_by_reference("R1")
        collection._modified = False  # Reset flag after add

        wrapper.value = "22k"

        assert wrapper.value == "22k"
        assert collection.is_modified

    def test_position_update(self):
        """Test position property update and modification tracking."""
        collection = FootprintCollection()
        collection.add(create_test_footprint("R1", 10.0, 20.0))

        wrapper = collection.get_by_reference("R1")
        collection._modified = False  # Reset

        wrapper.position = Point(50.0, 75.0)

        assert wrapper.position.x == 50.0
        assert wrapper.position.y == 75.0
        assert collection.is_modified

    def test_rotation_update(self):
        """Test rotation normalization and modification tracking."""
        collection = FootprintCollection()
        collection.add(create_test_footprint("R1"))

        wrapper = collection.get_by_reference("R1")
        collection._modified = False

        # Rotation should be normalized to 0-360
        wrapper.rotation = 450.0
        assert wrapper.rotation == 90.0
        assert collection.is_modified

        wrapper.rotation = -90.0
        assert wrapper.rotation == 270.0

    def test_layer_update(self):
        """Test layer update and modification tracking."""
        collection = FootprintCollection()
        collection.add(create_test_footprint("R1"))

        wrapper = collection.get_by_reference("R1")
        collection._modified = False

        wrapper.layer = "B.Cu"

        assert wrapper.layer == "B.Cu"
        assert collection.is_modified


class TestFootprintWrapperMethods:
    """Test FootprintWrapper convenience methods."""

    def test_move_by(self):
        """Test move_by method."""
        collection = FootprintCollection()
        collection.add(create_test_footprint("R1", 10.0, 20.0))

        wrapper = collection.get_by_reference("R1")
        wrapper.move_by(5.0, 10.0)

        assert wrapper.position.x == 15.0
        assert wrapper.position.y == 30.0
        assert collection.is_modified

    def test_rotate_by(self):
        """Test rotate_by method."""
        collection = FootprintCollection()
        collection.add(create_test_footprint("R1"))

        wrapper = collection.get_by_reference("R1")
        wrapper.rotation = 45.0
        collection._modified = False

        wrapper.rotate_by(90.0)

        assert wrapper.rotation == 135.0
        assert collection.is_modified

    def test_flip_to_other_side(self):
        """Test flip_to_other_side method."""
        collection = FootprintCollection()
        collection.add(create_test_footprint("R1"))

        wrapper = collection.get_by_reference("R1")
        assert wrapper.layer == "F.Cu"

        wrapper.flip_to_other_side()
        assert wrapper.layer == "B.Cu"

        wrapper.flip_to_other_side()
        assert wrapper.layer == "F.Cu"

    def test_is_on_layer(self):
        """Test is_on_layer query method."""
        collection = FootprintCollection()
        collection.add(create_test_footprint("R1"))

        wrapper = collection.get_by_reference("R1")

        assert wrapper.is_on_layer("F.Cu")
        assert not wrapper.is_on_layer("B.Cu")


class TestFootprintWrapperIndexUpdates:
    """Test that wrapper updates properly update parent collection indexes."""

    def test_reference_change_updates_index(self):
        """Test that changing reference updates the reference index."""
        collection = FootprintCollection()
        collection.add(create_test_footprint("R1"))
        collection.add(create_test_footprint("R2"))

        wrapper = collection.get_by_reference("R1")
        wrapper.reference = "R100"

        # Old reference should not be found
        assert collection.get_by_reference("R1") is None

        # New reference should be found
        assert collection.get_by_reference("R100") is not None

        # Other references should still work
        assert collection.get_by_reference("R2") is not None

    def test_layer_change_updates_index(self):
        """Test that changing layer updates the layer index."""
        collection = FootprintCollection()
        collection.add(create_test_footprint("R1"))

        wrapper = collection.get_by_reference("R1")
        wrapper.layer = "B.Cu"

        # Should be found in back copper layer
        back_footprints = collection.filter_by_layer("B.Cu")
        assert len(back_footprints) == 1
        assert back_footprints[0].reference == "R1"

        # Should not be in front copper layer
        front_footprints = collection.filter_by_layer("F.Cu")
        assert len(front_footprints) == 0


class TestFootprintWrapperEdgeCases:
    """Test edge cases and error handling."""

    def test_wrapper_equality(self):
        """Test wrapper equality based on UUID."""
        collection = FootprintCollection()
        collection.add(create_test_footprint("R1"))

        wrapper1 = collection.get_by_reference("R1")
        wrapper2 = collection.get_by_reference("R1")

        assert wrapper1 == wrapper2
        assert hash(wrapper1) == hash(wrapper2)

    def test_wrapper_repr(self):
        """Test wrapper string representation."""
        collection = FootprintCollection()
        collection.add(create_test_footprint("R1", 10.0, 20.0))

        wrapper = collection.get_by_reference("R1")
        repr_str = repr(wrapper)

        assert "R1" in repr_str
        assert "10k" in repr_str
        assert "10.00" in repr_str
        assert "20.00" in repr_str
        assert "F.Cu" in repr_str
