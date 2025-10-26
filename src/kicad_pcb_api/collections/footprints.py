"""
Footprint collection with specialized indexing and footprint-specific operations.

Extends IndexedCollection to provide footprint-specific features like
reference indexing, library ID grouping, net filtering, and bulk operations.

Based on kicad-sch-api's ComponentCollection pattern.
"""

import logging
from collections import defaultdict
from typing import Any, Dict, List, Optional

from ..core.types import Footprint
from .base import IndexedCollection

logger = logging.getLogger(__name__)


class FootprintCollection(IndexedCollection[Footprint]):
    """
    Collection class for efficient footprint management.

    Extends IndexedCollection with footprint-specific features:
    - Reference-based indexing for fast footprint lookup by reference
    - Library ID grouping for filtering by footprint type
    - Net indexing for finding footprints on specific nets
    - Layer filtering for finding components on specific layers
    - Bulk update operations
    - Advanced search capabilities
    """

    def __init__(self, footprints: Optional[List[Footprint]] = None):
        """
        Initialize footprint collection.

        Args:
            footprints: Initial list of footprints to add
        """
        # Additional indexes
        self._reference_index: Dict[str, int] = {}
        self._lib_id_index: Dict[str, List[int]] = defaultdict(list)
        self._layer_index: Dict[str, List[int]] = defaultdict(list)

        # Call parent init
        super().__init__(footprints)

        logger.debug(f"FootprintCollection initialized with {len(self._items)} footprints")

    # Abstract method implementations

    def _get_item_uuid(self, item: Footprint) -> str:
        """Extract UUID from footprint."""
        return item.uuid

    def _create_item(self, **kwargs) -> Footprint:
        """Create new footprint instance."""
        return Footprint(**kwargs)

    def _build_additional_indexes(self) -> None:
        """Build footprint-specific indexes."""
        # Build reference index
        self._reference_index = {
            fp.reference: i for i, fp in enumerate(self._items)
            if fp.reference  # Only index if reference exists
        }

        # Build library ID index
        self._lib_id_index = defaultdict(list)
        for i, fp in enumerate(self._items):
            if fp.library:
                self._lib_id_index[fp.library].append(i)

        # Build layer index
        self._layer_index = defaultdict(list)
        for i, fp in enumerate(self._items):
            if fp.layer:
                self._layer_index[fp.layer].append(i)

        logger.debug(
            f"Built indexes: {len(self._reference_index)} references, "
            f"{len(self._lib_id_index)} library IDs, "
            f"{len(self._layer_index)} layers"
        )

    # Footprint-specific access methods

    def get_by_reference(self, reference: str) -> Optional[Footprint]:
        """
        Get a footprint by reference designator.

        Args:
            reference: Reference designator (e.g., "R1", "C5", "U2")

        Returns:
            Footprint if found, None otherwise

        Example:
            fp = collection.get_by_reference("R1")
        """
        self._ensure_indexes_current()

        idx = self._reference_index.get(reference)
        if idx is not None:
            return self._items[idx]
        return None

    def filter_by_lib_id(self, library: str) -> List[Footprint]:
        """
        Filter footprints by library ID.

        Args:
            library: Library name (e.g., "Resistor_SMD", "Capacitor_SMD")

        Returns:
            List of footprints from the specified library

        Example:
            resistors = collection.filter_by_lib_id("Resistor_SMD")
        """
        self._ensure_indexes_current()

        indices = self._lib_id_index.get(library, [])
        return [self._items[i] for i in indices]

    def get_by_lib_id(self) -> Dict[str, List[Footprint]]:
        """
        Get footprints grouped by library ID.

        Returns:
            Dictionary mapping library IDs to lists of footprints

        Example:
            by_lib = collection.get_by_lib_id()
            for lib_id, footprints in by_lib.items():
                print(f"{lib_id}: {len(footprints)} footprints")
        """
        self._ensure_indexes_current()

        result = {}
        for lib_id, indices in self._lib_id_index.items():
            result[lib_id] = [self._items[i] for i in indices]
        return result

    def filter_by_net(self, net_name: str) -> List[Footprint]:
        """
        Filter footprints that have pads on a specific net.

        Args:
            net_name: Net name to filter by

        Returns:
            List of footprints with at least one pad on the specified net

        Example:
            gnd_footprints = collection.filter_by_net("GND")
        """
        def has_net(fp: Footprint) -> bool:
            for pad in fp.pads:
                if pad.net_name == net_name:
                    return True
            return False

        return self.find(has_net)

    def filter_by_layer(self, layer: str) -> List[Footprint]:
        """
        Filter footprints on a specific layer.

        Args:
            layer: Layer name (e.g., "F.Cu", "B.Cu")

        Returns:
            List of footprints on the specified layer

        Example:
            front_components = collection.filter_by_layer("F.Cu")
        """
        self._ensure_indexes_current()

        indices = self._layer_index.get(layer, [])
        return [self._items[i] for i in indices]

    # Bulk operations

    def bulk_update(self, criteria: Dict[str, Any], updates: Dict[str, Any]) -> int:
        """
        Bulk update footprints matching criteria.

        Args:
            criteria: Dictionary of attribute/value pairs to match
            updates: Dictionary of attribute/value pairs to update

        Returns:
            Number of footprints updated

        Example:
            # Update all 10k resistors to 20k
            count = collection.bulk_update(
                criteria={'value': '10k'},
                updates={'value': '20k'}
            )

            # Move all front components to back
            count = collection.bulk_update(
                criteria={'layer': 'F.Cu'},
                updates={'layer': 'B.Cu'}
            )
        """
        # Find matching footprints
        matching = self.filter(**criteria)

        # Update each matching footprint
        count = 0
        for fp in matching:
            for attr, value in updates.items():
                if hasattr(fp, attr):
                    setattr(fp, attr, value)
                    count += 1

        if count > 0:
            self._mark_modified()
            self._mark_indexes_dirty()

        logger.debug(f"Bulk updated {len(matching)} footprints ({count} attributes)")
        return len(matching)

    # Statistics and debugging

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get detailed collection statistics.

        Returns:
            Dictionary with collection statistics including footprint counts
            by library, layer, etc.
        """
        base_stats = super().get_statistics()

        self._ensure_indexes_current()

        # Add footprint-specific stats
        base_stats.update({
            "unique_libraries": len(self._lib_id_index),
            "unique_layers": len(self._layer_index),
            "footprints_by_library": {
                lib: len(indices) for lib, indices in self._lib_id_index.items()
            },
            "footprints_by_layer": {
                layer: len(indices) for layer, indices in self._layer_index.items()
            },
        })

        return base_stats
