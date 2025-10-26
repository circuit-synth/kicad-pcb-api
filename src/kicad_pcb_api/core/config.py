"""Configuration system for kicad-pcb-api.

Provides centralized configuration for validation thresholds, default values,
and DRC rules. Can be customized per-project.
"""

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class TrackConfig:
    """Configuration for track/trace specifications."""

    # Default track width in mm
    default_width: float = 0.25

    # Minimum allowed track width in mm
    min_width: float = 0.1

    # Maximum allowed track width in mm
    max_width: float = 10.0

    # Default clearance between tracks in mm
    default_clearance: float = 0.2

    # Net class widths (overrides for specific nets)
    net_class_widths: Dict[str, float] = field(default_factory=dict)


@dataclass
class ViaConfig:
    """Configuration for via specifications."""

    # Default via pad size in mm
    default_size: float = 0.8

    # Default via drill size in mm
    default_drill: float = 0.4

    # Minimum via pad size in mm
    min_size: float = 0.2

    # Maximum via pad size in mm
    max_size: float = 10.0

    # Minimum drill size in mm
    min_drill: float = 0.1

    # Minimum annular ring (size - drill) / 2
    min_annular_ring: float = 0.15


@dataclass
class FootprintConfig:
    """Configuration for footprint specifications."""

    # Default rotation snap angle in degrees
    rotation_snap: float = 90.0

    # Default grid snap in mm
    grid_snap: float = 0.5

    # Minimum clearance between footprints in mm
    min_clearance: float = 0.5


@dataclass
class ValidationConfig:
    """Configuration for validation rules."""

    # Check for duplicate references
    check_duplicate_references: bool = True

    # Check for missing references
    check_missing_references: bool = True

    # Check for invalid net assignments
    check_invalid_nets: bool = True

    # Check for overlapping components
    check_overlapping_components: bool = True

    # Tolerance for position comparisons in mm
    position_tolerance: float = 0.001

    # Tolerance for angle comparisons in degrees
    angle_tolerance: float = 0.01


@dataclass
class DRCConfig:
    """Configuration for Design Rule Check."""

    # Minimum clearance between copper in mm
    min_copper_clearance: float = 0.2

    # Minimum clearance for different nets in mm
    min_different_nets_clearance: float = 0.2

    # Minimum clearance for same net in mm
    min_same_net_clearance: float = 0.0

    # Minimum hole-to-hole clearance in mm
    min_hole_to_hole: float = 0.25

    # Minimum edge clearance (copper to board edge) in mm
    min_edge_clearance: float = 0.3

    # Minimum silkscreen width in mm
    min_silkscreen_width: float = 0.12

    # Minimum silkscreen text height in mm
    min_silkscreen_text_height: float = 0.8


@dataclass
class PlacementConfig:
    """Configuration for component placement."""

    # Default component spacing in grid placement in mm
    default_spacing_x: float = 5.0
    default_spacing_y: float = 5.0

    # Default grid columns
    default_grid_columns: int = 10

    # Snap to grid
    snap_to_grid: bool = True

    # Grid size in mm
    grid_size: float = 0.5


@dataclass
class RoutingConfig:
    """Configuration for routing."""

    # Prefer Manhattan (90-degree) routing
    prefer_manhattan: bool = True

    # Default routing layer for autorouter
    default_layer: str = "F.Cu"

    # Via placement strategy: 'minimal', 'balanced', 'aggressive'
    via_strategy: str = "balanced"

    # Maximum route detour ratio (route_length / direct_distance)
    max_detour_ratio: float = 2.0


@dataclass
class PCBConfig:
    """Main configuration class for PCB operations.

    Holds all sub-configurations and provides centralized access to settings.
    Can be customized per-project by modifying the global instance or creating
    project-specific instances.
    """

    track: TrackConfig = field(default_factory=TrackConfig)
    via: ViaConfig = field(default_factory=ViaConfig)
    footprint: FootprintConfig = field(default_factory=FootprintConfig)
    validation: ValidationConfig = field(default_factory=ValidationConfig)
    drc: DRCConfig = field(default_factory=DRCConfig)
    placement: PlacementConfig = field(default_factory=PlacementConfig)
    routing: RoutingConfig = field(default_factory=RoutingConfig)

    def to_dict(self) -> Dict:
        """Convert configuration to dictionary.

        Returns:
            Dictionary representation of configuration
        """
        return {
            "track": self.track.__dict__,
            "via": self.via.__dict__,
            "footprint": self.footprint.__dict__,
            "validation": self.validation.__dict__,
            "drc": self.drc.__dict__,
            "placement": self.placement.__dict__,
            "routing": self.routing.__dict__,
        }


# Global default configuration instance
# Can be modified: config.track.default_width = 0.5
# Or replaced: config = PCBConfig(track=TrackConfig(default_width=0.5))
config = PCBConfig()
