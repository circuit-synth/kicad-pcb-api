"""Component placement manager."""

import logging
import math
from typing import List, Optional

from ..core.types import Point
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
