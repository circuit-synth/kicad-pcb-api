"""Component placement manager."""

import logging
import math
from typing import Dict, List, Optional, Tuple

from ..core.types import Point
from ..placement.base import ComponentWrapper, PlacementAlgorithm
from ..placement.bbox import BoundingBox
from ..placement.courtyard_collision import CourtyardCollisionDetector
from ..placement.hierarchical_placement import HierarchicalPlacer
from ..placement.spiral_placement import SpiralPlacer
from .base import BaseManager

logger = logging.getLogger(__name__)


class PlacementManager(BaseManager):
    """Manager for component placement operations.

    Handles automatic placement, alignment, and distribution of components.
    """

    def place_in_grid(
        self,
        references: List[str],
        start_x: float,
        start_y: float,
        spacing_x: float,
        spacing_y: float,
        columns: int,
    ) -> int:
        """Place components in a grid pattern.

        Args:
            references: List of component references to place
            start_x: Starting X coordinate
            start_y: Starting Y coordinate
            spacing_x: Horizontal spacing between components
            spacing_y: Vertical spacing between components
            columns: Number of columns in the grid

        Returns:
            Number of components placed
        """
        count = 0

        for i, ref in enumerate(references):
            footprint = self.board.footprints.get_by_reference(ref)
            if footprint is None:
                logger.warning(f"Footprint {ref} not found, skipping")
                continue

            row = i // columns
            col = i % columns

            x = start_x + (col * spacing_x)
            y = start_y + (row * spacing_y)

            footprint.position = Point(x, y)
            count += 1

        logger.info(f"Placed {count} components in grid pattern")
        return count

    def place_in_circle(
        self, references: List[str], center_x: float, center_y: float, radius: float
    ) -> int:
        """Place components in a circular pattern.

        Args:
            references: List of component references to place
            center_x: Circle center X coordinate
            center_y: Circle center Y coordinate
            radius: Circle radius in mm

        Returns:
            Number of components placed
        """
        count = len(references)
        if count == 0:
            return 0

        angle_step = (2 * math.pi) / count

        for i, ref in enumerate(references):
            footprint = self.board.footprints.get_by_reference(ref)
            if footprint is None:
                logger.warning(f"Footprint {ref} not found, skipping")
                continue

            angle = i * angle_step
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)

            footprint.position = Point(x, y)
            # Optionally rotate to face center
            footprint.rotation = math.degrees(angle + math.pi / 2)

        logger.info(f"Placed {count} components in circular pattern")
        return count

    def align_horizontally(self, references: List[str], y: Optional[float] = None) -> int:
        """Align components horizontally.

        Args:
            references: List of component references to align
            y: Y coordinate to align to (uses first component's Y if None)

        Returns:
            Number of components aligned
        """
        if not references:
            return 0

        # Get target Y coordinate
        if y is None:
            first = self.board.footprints.get_by_reference(references[0])
            if first is None:
                return 0
            y = first.position.y

        count = 0
        for ref in references:
            footprint = self.board.footprints.get_by_reference(ref)
            if footprint is None:
                continue

            footprint.position = Point(footprint.position.x, y)
            count += 1

        logger.info(f"Aligned {count} components horizontally at Y={y}")
        return count

    def align_vertically(self, references: List[str], x: Optional[float] = None) -> int:
        """Align components vertically.

        Args:
            references: List of component references to align
            x: X coordinate to align to (uses first component's X if None)

        Returns:
            Number of components aligned
        """
        if not references:
            return 0

        # Get target X coordinate
        if x is None:
            first = self.board.footprints.get_by_reference(references[0])
            if first is None:
                return 0
            x = first.position.x

        count = 0
        for ref in references:
            footprint = self.board.footprints.get_by_reference(ref)
            if footprint is None:
                continue

            footprint.position = Point(x, footprint.position.y)
            count += 1

        logger.info(f"Aligned {count} components vertically at X={x}")
        return count

    def distribute_horizontally(
        self, references: List[str], start_x: float, end_x: float
    ) -> int:
        """Distribute components evenly in horizontal span.

        Args:
            references: List of component references to distribute
            start_x: Starting X coordinate
            end_x: Ending X coordinate

        Returns:
            Number of components distributed
        """
        count = len(references)
        if count < 2:
            return 0

        spacing = (end_x - start_x) / (count - 1)

        placed = 0
        for i, ref in enumerate(references):
            footprint = self.board.footprints.get_by_reference(ref)
            if footprint is None:
                continue

            x = start_x + (i * spacing)
            footprint.position = Point(x, footprint.position.y)
            placed += 1

        logger.info(f"Distributed {placed} components horizontally")
        return placed

    def distribute_vertically(self, references: List[str], start_y: float, end_y: float) -> int:
        """Distribute components evenly in vertical span.

        Args:
            references: List of component references to distribute
            start_y: Starting Y coordinate
            end_y: Ending Y coordinate

        Returns:
            Number of components distributed
        """
        count = len(references)
        if count < 2:
            return 0

        spacing = (end_y - start_y) / (count - 1)

        placed = 0
        for i, ref in enumerate(references):
            footprint = self.board.footprints.get_by_reference(ref)
            if footprint is None:
                continue

            y = start_y + (i * spacing)
            footprint.position = Point(footprint.position.x, y)
            placed += 1

        logger.info(f"Distributed {placed} components vertically")
        return placed

    def auto_place(
        self,
        references: Optional[List[str]] = None,
        algorithm: str = "hierarchical",
        board_width: float = 100.0,
        board_height: float = 100.0,
        component_spacing: float = 0.5,
        group_spacing: float = 2.5,
        check_collisions: bool = True,
    ) -> int:
        """Auto-place components using the specified algorithm.

        Args:
            references: List of component references to place (None = all unlocked)
            algorithm: Placement algorithm ('hierarchical' or 'spiral')
            board_width: Board width in mm
            board_height: Board height in mm
            component_spacing: Spacing between components in mm
            group_spacing: Spacing between groups in mm (hierarchical only)
            check_collisions: Whether to check for collisions

        Returns:
            Number of components placed
        """
        # Get components to place
        if references is None:
            # Place all unlocked components
            components_to_place = [
                fp for fp in self.board.footprints.values() if not fp.locked
            ]
        else:
            components_to_place = []
            for ref in references:
                fp = self.board.footprints.get_by_reference(ref)
                if fp is None:
                    logger.warning(f"Component {ref} not found, skipping")
                    continue
                if fp.locked:
                    logger.warning(f"Component {ref} is locked, skipping")
                    continue
                components_to_place.append(fp)

        if not components_to_place:
            logger.warning("No unlocked components to place")
            return 0

        # Wrap components
        wrapped_components = [ComponentWrapper(fp) for fp in components_to_place]

        # Create placer instance
        placer: PlacementAlgorithm
        if algorithm == "hierarchical":
            placer = HierarchicalPlacer(
                component_spacing=component_spacing, group_spacing=group_spacing
            )
        elif algorithm == "spiral":
            placer = SpiralPlacer(center_x=board_width / 2, center_y=board_height / 2)
        else:
            raise ValueError(
                f"Unknown algorithm '{algorithm}'. Use 'hierarchical' or 'spiral'"
            )

        # Run placement
        logger.info(
            f"Auto-placing {len(wrapped_components)} components using {algorithm} algorithm"
        )
        positions = placer.place(
            wrapped_components,
            connections=[],  # TODO: Extract from netlist
            board_width=board_width,
            board_height=board_height,
        )

        # Validate placements if requested
        if check_collisions:
            collision_count = self.check_collisions(list(positions.keys()))
            if collision_count > 0:
                logger.warning(
                    f"Found {collision_count} collisions after auto-placement"
                )

        logger.info(f"Auto-placed {len(positions)} components")
        return len(positions)

    def check_collisions(
        self, references: Optional[List[str]] = None, spacing: float = 0.0
    ) -> int:
        """Check for collisions between components using courtyard geometry.

        Args:
            references: List of component references to check (None = all)
            spacing: Additional spacing to add between courtyards in mm

        Returns:
            Number of collisions detected
        """
        # Get components to check
        if references is None:
            components = list(self.board.footprints.values())
        else:
            components = []
            for ref in references:
                fp = self.board.footprints.get_by_reference(ref)
                if fp is not None:
                    components.append(fp)

        if len(components) < 2:
            return 0

        # Create collision detector
        detector = CourtyardCollisionDetector(spacing=spacing)

        # Check all pairs
        collision_count = 0
        for i, fp1 in enumerate(components):
            for fp2 in components[i + 1 :]:
                if detector.check_collision(fp1, fp2):
                    logger.warning(
                        f"Collision detected between {fp1.reference} and {fp2.reference}"
                    )
                    collision_count += 1

        if collision_count == 0:
            logger.info("No collisions detected")
        else:
            logger.error(f"Found {collision_count} collision(s)")

        return collision_count

    def snap_to_grid(
        self, references: List[str], grid_size: float = 1.0, origin: Point = Point(0, 0)
    ) -> int:
        """Snap components to a grid.

        Args:
            references: List of component references to snap
            grid_size: Grid size in mm
            origin: Grid origin point

        Returns:
            Number of components snapped
        """
        count = 0

        for ref in references:
            footprint = self.board.footprints.get_by_reference(ref)
            if footprint is None:
                logger.warning(f"Footprint {ref} not found, skipping")
                continue

            if footprint.locked:
                logger.warning(f"Footprint {ref} is locked, skipping")
                continue

            # Calculate snapped position
            dx = footprint.position.x - origin.x
            dy = footprint.position.y - origin.y

            snapped_x = origin.x + round(dx / grid_size) * grid_size
            snapped_y = origin.y + round(dy / grid_size) * grid_size

            footprint.position = Point(snapped_x, snapped_y)
            count += 1

        logger.info(f"Snapped {count} components to {grid_size}mm grid")
        return count

    def validate_placements(
        self,
        references: Optional[List[str]] = None,
        board_outline: Optional[BoundingBox] = None,
        check_collisions: bool = True,
        min_edge_clearance: float = 2.0,
    ) -> Dict[str, List[str]]:
        """Validate component placements.

        Args:
            references: List of component references to validate (None = all)
            board_outline: Board outline bounding box (None = auto-detect)
            check_collisions: Whether to check for collisions
            min_edge_clearance: Minimum clearance from board edge in mm

        Returns:
            Dictionary of validation errors by component reference
        """
        # Get components to validate
        if references is None:
            components = list(self.board.footprints.values())
        else:
            components = []
            for ref in references:
                fp = self.board.footprints.get_by_reference(ref)
                if fp is not None:
                    components.append(fp)

        # Auto-detect board outline if not provided
        if board_outline is None:
            # Try to extract from Edge.Cuts layer
            # For now, use a default
            board_outline = BoundingBox(0, 0, 100, 100)
            logger.warning(
                "No board outline provided, using default 100x100mm for validation"
            )

        errors: Dict[str, List[str]] = {}

        # Check each component
        for fp in components:
            component_errors = []

            # Check if within board bounds
            if (
                fp.position.x < board_outline.min_x + min_edge_clearance
                or fp.position.x > board_outline.max_x - min_edge_clearance
                or fp.position.y < board_outline.min_y + min_edge_clearance
                or fp.position.y > board_outline.max_y - min_edge_clearance
            ):
                component_errors.append(
                    f"Component too close to board edge (min clearance: {min_edge_clearance}mm)"
                )

            # Check rotation is valid
            if fp.rotation < 0 or fp.rotation >= 360:
                component_errors.append(
                    f"Invalid rotation: {fp.rotation} (should be 0-360)"
                )

            if component_errors:
                errors[fp.reference] = component_errors

        # Check collisions
        if check_collisions:
            detector = CourtyardCollisionDetector(spacing=0.0)
            for i, fp1 in enumerate(components):
                for fp2 in components[i + 1 :]:
                    if detector.check_collision(fp1, fp2):
                        if fp1.reference not in errors:
                            errors[fp1.reference] = []
                        errors[fp1.reference].append(
                            f"Collision with {fp2.reference}"
                        )

        if errors:
            logger.error(
                f"Validation failed for {len(errors)} component(s): {list(errors.keys())}"
            )
        else:
            logger.info("All placements validated successfully")

        return errors

    def find_valid_position(
        self,
        reference: str,
        ideal_position: Point,
        search_radius: float = 50.0,
        search_step: float = 0.5,
        board_outline: Optional[BoundingBox] = None,
    ) -> Optional[Point]:
        """Find a valid position near the ideal position using spiral search.

        Args:
            reference: Component reference
            ideal_position: Ideal position to place near
            search_radius: Maximum search radius in mm
            search_step: Step size for spiral search in mm
            board_outline: Optional board outline to constrain placement

        Returns:
            Valid position if found, None otherwise
        """
        footprint = self.board.footprints.get_by_reference(reference)
        if footprint is None:
            logger.error(f"Footprint {reference} not found")
            return None

        # Get all other footprints
        other_footprints = [
            fp for fp in self.board.footprints.values() if fp.reference != reference
        ]

        # Create collision detector
        detector = CourtyardCollisionDetector(spacing=0.5)

        # Convert board outline to polygon if provided
        board_polygon = None
        if board_outline:
            from ..placement.courtyard_collision import Polygon

            vertices = [
                (board_outline.min_x, board_outline.min_y),
                (board_outline.max_x, board_outline.min_y),
                (board_outline.max_x, board_outline.max_y),
                (board_outline.min_x, board_outline.max_y),
            ]
            board_polygon = Polygon(vertices)

        # Use courtyard collision detector's spiral search
        result = detector.find_valid_position(
            footprint,
            ideal_position.x,
            ideal_position.y,
            other_footprints,
            board_outline=board_polygon,
            search_radius=search_radius,
            search_step=search_step,
        )

        if result:
            return Point(result[0], result[1])
        else:
            logger.warning(
                f"Could not find valid position for {reference} near ({ideal_position.x}, {ideal_position.y})"
            )
            return None
