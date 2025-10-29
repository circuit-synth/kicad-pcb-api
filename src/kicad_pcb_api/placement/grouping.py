"""
Component grouping utilities for hierarchical placement.

Provides utilities for grouping components based on hierarchy.
"""

from dataclasses import dataclass
from typing import List

from ..core.types import Footprint


@dataclass
class ComponentGroup:
    """Represents a group of related components."""

    name: str
    components: List[Footprint]
    subgroups: List["ComponentGroup"]

    def __init__(self, name: str):
        """Initialize a component group."""
        self.name = name
        self.components = []
        self.subgroups = []


def group_by_hierarchy(components: List[Footprint]) -> List[ComponentGroup]:
    """
    Group components by their schematic hierarchy.

    Args:
        components: List of footprints to group

    Returns:
        List of component groups organized by hierarchy
    """
    # Simple implementation - group by sheetname
    groups = {}
    for component in components:
        sheet = component.sheetname if component.sheetname else "root"
        if sheet not in groups:
            groups[sheet] = ComponentGroup(sheet)
        groups[sheet].components.append(component)

    return list(groups.values())


def group_groups(groups: List[ComponentGroup]) -> List[ComponentGroup]:
    """
    Organize groups into a hierarchical structure.

    Args:
        groups: List of flat component groups

    Returns:
        List of hierarchically organized groups
    """
    # For now, just return the groups as-is
    return groups
