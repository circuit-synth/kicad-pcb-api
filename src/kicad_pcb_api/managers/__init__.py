"""Manager classes for complex PCB operations.

Managers separate concerns and prevent PCBBoard from becoming bloated.
Each manager handles a specific domain of functionality.
"""

from .base import BaseManager
from .drc import DRCManager
from .net import NetManager
from .placement import PlacementManager
from .routing import RoutingManager
from .validation import ValidationManager

__all__ = [
    "BaseManager",
    "DRCManager",
    "NetManager",
    "PlacementManager",
    "RoutingManager",
    "ValidationManager",
]
