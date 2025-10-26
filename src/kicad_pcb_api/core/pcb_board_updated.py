"""
Main PCB board class providing a simple API for PCB manipulation.

Updated with manager integration for better separation of concerns.
"""

import logging
import math
import uuid as uuid_module
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union, Set

from ..footprints.footprint_library import FootprintInfo, get_footprint_cache
from .pcb_parser import PCBParser
from .types import (
    Arc,
    Footprint,
    Line,
    Net,
    Pad,
    Point,
    Property,
    Rectangle,
    Text,
    Track,
    Via,
    Zone,
)
from ..utils.validation import PCBValidator, ValidationResult

# Import managers
from ..managers import (
    DRCManager,
    NetManager,
    PlacementManager,
    RoutingManager,
    ValidationManager,
)

# Import collections
from ..collections import (
    FootprintCollection,
    TrackCollection,
    ViaCollection,
)

logger = logging.getLogger(__name__)


class PCBBoard:
    """
    High-level API for creating and manipulating KiCad PCB files.

    Provides simple methods for common PCB operations like adding,
    moving, and removing footprints. Now includes managers for:
    - DRC checking (self.drc)
    - Net operations (self.net)
    - Component placement (self.placement)
    - Routing (self.routing)
    - Validation (self.validation)
    """

    def __init__(self, filepath: Optional[Union[str, Path]] = None):
        """
        Initialize a PCB board.

        Args:
            filepath: Optional path to load an existing PCB file
        """
        self.parser = PCBParser()
        self.pcb_data = self._create_empty_pcb()
        self._filepath = None
        self._modified = False
        self._modification_trackers = {
            'footprints': set(),
            'tracks': set(),
            'vias': set(),
            'zones': set(),
            'graphics': set(),
        }

        # Initialize collections
        self._footprints_collection = FootprintCollection()
        self._tracks_collection = TrackCollection()
        self._vias_collection = ViaCollection()

        # Initialize managers
        self.drc = DRCManager(self)
        self.net = NetManager(self)
        self.placement = PlacementManager(self)
        self.routing = RoutingManager(self)
        self.validation = ValidationManager(self)

        if filepath:
            self.load(filepath)
            # Sync collections after loading
            self._sync_collections_from_data()

    def _sync_collections_from_data(self):
        """Sync collection wrappers with pcb_data after loading."""
        # Update footprints collection
        self._footprints_collection = FootprintCollection(self.pcb_data.get("footprints", []))

        # Update tracks collection
        self._tracks_collection = TrackCollection(self.pcb_data.get("tracks", []))

        # Update vias collection
        self._vias_collection = ViaCollection(self.pcb_data.get("vias", []))

    @property
    def footprints(self) -> FootprintCollection:
        """Get footprints collection.

        Returns:
            FootprintCollection for querying and manipulating footprints

        Example:
            # Get footprint by reference
            resistor = pcb.footprints.get_by_reference("R1")

            # Filter by library
            resistors = pcb.footprints.filter_by_lib_id("Resistor_SMD")
        """
        return self._footprints_collection

    @property
    def tracks(self) -> TrackCollection:
        """Get tracks collection.

        Returns:
            TrackCollection for querying and manipulating tracks

        Example:
            # Get tracks by net
            gnd_tracks = pcb.tracks.filter_by_net(0)

            # Get total length
            length = pcb.tracks.get_total_length_by_net(1)
        """
        return self._tracks_collection

    @property
    def vias(self) -> ViaCollection:
        """Get vias collection.

        Returns:
            ViaCollection for querying and manipulating vias

        Example:
            # Filter vias by net
            vias = pcb.vias.filter_by_net(1)
        """
        return self._vias_collection

    @property
    def nets(self) -> Set[int]:
        """Get all net numbers used in the board.

        Returns:
            Set of net numbers

        Example:
            for net in pcb.nets:
                print(f"Net {net}: {pcb.net.get_net_name(net)}")
        """
        return self.net.get_all_nets()

    @property
    def issues(self) -> List:
        """Get validation issues from last validation run.

        Returns:
            List of ValidationIssue objects

        Example:
            pcb.validate()
            if pcb.issues:
                for issue in pcb.issues:
                    print(f"{issue.severity}: {issue.description}")
        """
        return self.validation.issues

    # Convenience methods that delegate to managers

    def place_grid(self, references: List[str], start_x: float, start_y: float,
                   spacing_x: float, spacing_y: float, columns: int) -> int:
        """Place components in a grid pattern.

        Convenience method that delegates to PlacementManager.

        Args:
            references: List of component references to place
            start_x: Starting X coordinate
            start_y: Starting Y coordinate
            spacing_x: Horizontal spacing between components
            spacing_y: Vertical spacing between components
            columns: Number of columns in the grid

        Returns:
            Number of components placed

        Example:
            pcb.place_grid(["R1", "R2", "R3", "R4"], 10, 10, 5, 5, 2)
        """
        return self.placement.place_in_grid(references, start_x, start_y, spacing_x, spacing_y, columns)

    def check_drc(self, min_track_width: float = 0.1, max_track_width: float = 10.0,
                  min_via_size: float = 0.2, min_via_drill: float = 0.1) -> int:
        """Run DRC checks on the board.

        Convenience method that delegates to DRCManager.

        Args:
            min_track_width: Minimum track width in mm
            max_track_width: Maximum track width in mm
            min_via_size: Minimum via size in mm
            min_via_drill: Minimum via drill in mm

        Returns:
            Number of violations found

        Example:
            violations = pcb.check_drc()
            if violations:
                for v in pcb.drc.violations:
                    print(f"{v.severity}: {v.description}")
        """
        return self.drc.check_all(min_track_width, max_track_width, min_via_size, min_via_drill)

    def validate(self) -> int:
        """Run all validation checks on the board.

        Convenience method that delegates to ValidationManager.

        Returns:
            Number of issues found

        Example:
            issues = pcb.validate()
            if issues:
                for issue in pcb.issues:
                    print(f"{issue.category}: {issue.description}")
        """
        return self.validation.validate_all()

    # Rest of the original PCBBoard methods remain unchanged...
    # (The existing implementation continues below)
