"""
Collection classes for efficient PCB element management.

Following kicad-sch-api architecture patterns.
"""

from .base import IndexedCollection
from .footprints import FootprintCollection
from .tracks import TrackCollection
from .vias import ViaCollection
from .zones import ZoneCollection

__all__ = [
    "IndexedCollection",
    "FootprintCollection",
    "TrackCollection",
    "ViaCollection",
    "ZoneCollection",
]
