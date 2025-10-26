#!/usr/bin/env python3
"""
Patch script to integrate managers and collections into PCBBoard.
"""

import re

def patch_pcb_board():
    """Apply patches to pcb_board.py"""

    file_path = "kicad_pcb_api/core/pcb_board.py"

    with open(file_path, 'r') as f:
        content = f.read()

    # Patch 1: Add imports
    imports_to_add = '''
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
'''

    # Find the position after the ValidationResult import
    import_pattern = r'(from \.\.utils\.validation import PCBValidator, ValidationResult\n)'
    content = re.sub(import_pattern, r'\1' + imports_to_add, content)

    # Patch 2: Update __init__ method
    init_addition = '''
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

'''

    # Find __init__ method and add after modification_trackers
    init_pattern = r"(        self\._modification_trackers = \{[^}]+\}\n\n)"
    content = re.sub(init_pattern, r'\1' + init_addition, content)

    # Patch 3: Update load method to sync collections
    load_pattern = r'(        if filepath:\n            self\.load\(filepath\))'
    load_replacement = r'''\1
            # Sync collections after loading
            self._sync_collections_from_data()'''
    content = re.sub(load_pattern, load_replacement, content)

    # Patch 4: Add sync method and properties after __init__
    new_methods = '''
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
        """Get footprints collection."""
        return self._footprints_collection

    @property
    def tracks(self) -> TrackCollection:
        """Get tracks collection."""
        return self._tracks_collection

    @property
    def vias(self) -> ViaCollection:
        """Get vias collection."""
        return self._vias_collection

    @property
    def nets(self):
        """Get all net numbers used in the board."""
        return self.net.get_all_nets()

    @property
    def issues(self):
        """Get validation issues from last validation run."""
        return self.validation.issues

    # Convenience methods that delegate to managers

    def place_grid(self, references, start_x, start_y, spacing_x, spacing_y, columns):
        """Place components in a grid pattern."""
        return self.placement.place_in_grid(references, start_x, start_y, spacing_x, spacing_y, columns)

    def check_drc(self, min_track_width=0.1, max_track_width=10.0, min_via_size=0.2, min_via_drill=0.1):
        """Run DRC checks on the board."""
        return self.drc.check_all(min_track_width, max_track_width, min_via_size, min_via_drill)

    def validate(self):
        """Run all validation checks on the board."""
        return self.validation.validate_all()

'''

    # Find _create_empty_pcb method and add new methods before it
    create_empty_pattern = r'(\n    def _create_empty_pcb\(self\))'
    content = re.sub(create_empty_pattern, '\n' + new_methods + r'\1', content)

    # Write back
    with open(file_path, 'w') as f:
        f.write(content)

    print("✓ Successfully patched pcb_board.py")
    print("  - Added manager imports")
    print("  - Added collection imports")
    print("  - Initialized managers in __init__")
    print("  - Initialized collections in __init__")
    print("  - Added _sync_collections_from_data method")
    print("  - Added property accessors for collections and data")
    print("  - Added convenience methods")

if __name__ == "__main__":
    patch_pcb_board()
