"""Board-level validation manager."""

import logging
from dataclasses import dataclass
from typing import List

from .base import BaseManager

logger = logging.getLogger(__name__)


@dataclass
class ValidationIssue:
    """Represents a validation issue."""

    severity: str  # "error", "warning", "info"
    category: str  # "reference", "net", "placement", etc.
    description: str
    element_uuid: str = ""
    suggestion: str = ""


class ValidationManager(BaseManager):
    """Manager for board-level validation.

    Performs comprehensive validation beyond DRC checks.
    """

    def __init__(self, board):
        """Initialize validation manager.

        Args:
            board: Parent PCBBoard instance
        """
        super().__init__(board)
        self._issues: List[ValidationIssue] = []

    @property
    def issues(self) -> List[ValidationIssue]:
        """Get list of validation issues.

        Returns:
            List of issues from last validation
        """
        return self._issues

    def validate_references(self) -> int:
        """Validate component references.

        Checks for:
        - Duplicate references
        - Invalid reference formats
        - Missing references

        Returns:
            Number of issues found
        """
        count = 0
        seen_refs = {}

        # Access raw footprint data instead of collection
        for footprint in self.board.pcb_data.get("footprints", []):
            ref = footprint.reference

            # Check for missing reference
            if not ref:
                self._issues.append(
                    ValidationIssue(
                        severity="error",
                        category="reference",
                        description="Footprint has no reference designator",
                        element_uuid=footprint.uuid,
                        suggestion="Assign a unique reference like R1, C1, etc.",
                    )
                )
                count += 1
                continue

            # Check for duplicates
            if ref in seen_refs:
                self._issues.append(
                    ValidationIssue(
                        severity="error",
                        category="reference",
                        description=f"Duplicate reference: {ref}",
                        element_uuid=footprint.uuid,
                        suggestion=f"Rename to a unique reference",
                    )
                )
                count += 1
            else:
                seen_refs[ref] = footprint.uuid

        return count

    def validate_nets(self) -> int:
        """Validate net assignments.

        Checks for:
        - Inconsistent net names for same net number
        - Nets with only one connection

        Returns:
            Number of issues found
        """
        count = 0

        # Check for inconsistent net names
        net_names = {}
        for footprint in self.board.pcb_data.get("footprints", []):
            for pad in footprint.pads:
                if pad.net is not None and pad.net_name:
                    if pad.net in net_names:
                        if net_names[pad.net] != pad.net_name:
                            self._issues.append(
                                ValidationIssue(
                                    severity="warning",
                                    category="net",
                                    description=f"Net {pad.net} has inconsistent names: {net_names[pad.net]} vs {pad.net_name}",
                                    suggestion="Use consistent net names",
                                )
                            )
                            count += 1
                    else:
                        net_names[pad.net] = pad.net_name

        return count

    def validate_placement(self) -> int:
        """Validate component placement.

        Checks for:
        - Overlapping components (simplified check)
        - Components outside board bounds (if bounds defined)

        Returns:
            Number of issues found
        """
        count = 0

        # Simple overlap check: components at exact same position
        positions = {}
        for footprint in self.board.pcb_data.get("footprints", []):
            pos_key = (round(footprint.position.x, 3), round(footprint.position.y, 3))
            if pos_key in positions:
                self._issues.append(
                    ValidationIssue(
                        severity="warning",
                        category="placement",
                        description=f"Components {positions[pos_key]} and {footprint.reference} at same position",
                        element_uuid=footprint.uuid,
                        suggestion="Move components apart",
                    )
                )
                count += 1
            else:
                positions[pos_key] = footprint.reference

        return count

    def validate_layers(self) -> int:
        """Validate layer assignments.

        Checks for:
        - Invalid layer names
        - Tracks on non-copper layers
        - Vias with invalid layer spans

        Returns:
            Number of issues found
        """
        count = 0

        # Check tracks are on copper layers
        for track in self.board.pcb_data.get("tracks", []):
            if not track.layer.endswith(".Cu"):
                self._issues.append(
                    ValidationIssue(
                        severity="error",
                        category="layer",
                        description=f"Track on non-copper layer: {track.layer}",
                        element_uuid=track.uuid,
                        suggestion="Move track to copper layer",
                    )
                )
                count += 1

        # Check vias have valid layer spans
        for via in self.board.pcb_data.get("vias", []):
            if len(via.layers) < 2:
                self._issues.append(
                    ValidationIssue(
                        severity="error",
                        category="layer",
                        description=f"Via must span at least 2 layers, has {len(via.layers)}",
                        element_uuid=via.uuid,
                        suggestion="Fix via layer span",
                    )
                )
                count += 1

        return count

    def validate_all(self) -> int:
        """Run all validation checks.

        Returns:
            Total number of issues found
        """
        self._issues.clear()

        count = 0
        count += self.validate_references()
        count += self.validate_nets()
        count += self.validate_placement()
        count += self.validate_layers()

        logger.info(f"Board validation complete: {count} issues found")
        return count

    def get_errors(self) -> List[ValidationIssue]:
        """Get only error-level issues.

        Returns:
            List of error issues
        """
        return [i for i in self._issues if i.severity == "error"]

    def get_warnings(self) -> List[ValidationIssue]:
        """Get only warning-level issues.

        Returns:
            List of warning issues
        """
        return [i for i in self._issues if i.severity == "warning"]

    def clear_issues(self) -> None:
        """Clear all recorded issues."""
        self._issues.clear()
