"""Design Rule Check (DRC) manager."""

import logging
from dataclasses import dataclass
from typing import List

from .base import BaseManager

logger = logging.getLogger(__name__)


@dataclass
class DRCViolation:
    """Represents a DRC violation."""

    type: str  # "clearance", "track_width", "via_size", etc.
    severity: str  # "error", "warning"
    description: str
    element1_uuid: str = ""
    element2_uuid: str = ""  # For clearance violations
    location_x: float = 0.0
    location_y: float = 0.0


class DRCManager(BaseManager):
    """Manager for Design Rule Checking.

    Validates board against design rules and reports violations.
    """

    def __init__(self, board):
        """Initialize DRC manager.

        Args:
            board: Parent PCBBoard instance
        """
        super().__init__(board)
        self._violations: List[DRCViolation] = []

    @property
    def violations(self) -> List[DRCViolation]:
        """Get list of DRC violations.

        Returns:
            List of violations from last check
        """
        return self._violations

    def check_track_widths(self, min_width: float = 0.1, max_width: float = 10.0) -> int:
        """Check track widths against design rules.

        Args:
            min_width: Minimum allowed track width in mm
            max_width: Maximum allowed track width in mm

        Returns:
            Number of violations found
        """
        count = 0

        # Access raw track data instead of collection
        for track in self.board.pcb_data.get("tracks", []):
            if track.width < min_width:
                self._violations.append(
                    DRCViolation(
                        type="track_width",
                        severity="error",
                        description=f"Track width {track.width}mm below minimum {min_width}mm",
                        element1_uuid=track.uuid,
                        location_x=track.start.x,
                        location_y=track.start.y,
                    )
                )
                count += 1
            elif track.width > max_width:
                self._violations.append(
                    DRCViolation(
                        type="track_width",
                        severity="warning",
                        description=f"Track width {track.width}mm exceeds maximum {max_width}mm",
                        element1_uuid=track.uuid,
                        location_x=track.start.x,
                        location_y=track.start.y,
                    )
                )
                count += 1

        return count

    def check_via_sizes(
        self, min_size: float = 0.2, max_size: float = 10.0, min_drill: float = 0.1
    ) -> int:
        """Check via sizes against design rules.

        Args:
            min_size: Minimum via pad size in mm
            max_size: Maximum via pad size in mm
            min_drill: Minimum drill size in mm

        Returns:
            Number of violations found
        """
        count = 0

        # Access raw via data instead of collection
        for via in self.board.pcb_data.get("vias", []):
            if via.size < min_size:
                self._violations.append(
                    DRCViolation(
                        type="via_size",
                        severity="error",
                        description=f"Via size {via.size}mm below minimum {min_size}mm",
                        element1_uuid=via.uuid,
                        location_x=via.position.x,
                        location_y=via.position.y,
                    )
                )
                count += 1

            if via.drill < min_drill:
                self._violations.append(
                    DRCViolation(
                        type="via_drill",
                        severity="error",
                        description=f"Via drill {via.drill}mm below minimum {min_drill}mm",
                        element1_uuid=via.uuid,
                        location_x=via.position.x,
                        location_y=via.position.y,
                    )
                )
                count += 1

            if via.drill >= via.size:
                self._violations.append(
                    DRCViolation(
                        type="via_drill",
                        severity="error",
                        description=f"Via drill {via.drill}mm must be smaller than pad size {via.size}mm",
                        element1_uuid=via.uuid,
                        location_x=via.position.x,
                        location_y=via.position.y,
                    )
                )
                count += 1

        return count

    def check_all(
        self,
        min_track_width: float = 0.1,
        max_track_width: float = 10.0,
        min_via_size: float = 0.2,
        min_via_drill: float = 0.1,
    ) -> int:
        """Run all DRC checks.

        Args:
            min_track_width: Minimum track width in mm
            max_track_width: Maximum track width in mm
            min_via_size: Minimum via size in mm
            min_via_drill: Minimum via drill in mm

        Returns:
            Total number of violations found
        """
        self._violations.clear()

        count = 0
        count += self.check_track_widths(min_track_width, max_track_width)
        count += self.check_via_sizes(min_via_size, min_drill=min_via_drill)

        logger.info(f"DRC check complete: {count} violations found")
        return count

    def get_errors(self) -> List[DRCViolation]:
        """Get only error-level violations.

        Returns:
            List of error violations
        """
        return [v for v in self._violations if v.severity == "error"]

    def get_warnings(self) -> List[DRCViolation]:
        """Get only warning-level violations.

        Returns:
            List of warning violations
        """
        return [v for v in self._violations if v.severity == "warning"]

    def clear_violations(self) -> None:
        """Clear all recorded violations."""
        self._violations.clear()
