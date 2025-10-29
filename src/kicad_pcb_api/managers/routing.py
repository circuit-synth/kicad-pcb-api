"""Routing and trace management."""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from ..core.types import Point, Track, Via
from ..routing.dsn_exporter import DSNExporter
from ..routing.freerouting_runner import FreeroutingConfig, FreeroutingRunner
from ..routing.ses_importer import SESImporter
from .base import BaseManager

logger = logging.getLogger(__name__)


class RoutingManager(BaseManager):
    """Manager for routing operations.

    Handles trace routing, length matching, and routing optimization.
    """

    def add_track(
        self,
        start: Point,
        end: Point,
        width: float,
        layer: str,
        net: Optional[int] = None,
        net_name: Optional[str] = None,
    ) -> str:
        """Add a new track to the board.

        Args:
            start: Track start point
            end: Track end point
            width: Track width in mm
            layer: Layer name (e.g., 'F.Cu')
            net: Optional net number
            net_name: Optional net name

        Returns:
            UUID of created track
        """
        import uuid

        track = Track(
            start=start,
            end=end,
            width=width,
            layer=layer,
            net=net,
            net_name=net_name,
            uuid=str(uuid.uuid4()),
        )

        self.board.tracks.add(track)
        logger.debug(f"Added track on {layer}, net={net}")

        return track.uuid

    def route_manhattan(
        self,
        start: Point,
        end: Point,
        width: float,
        layer: str,
        net: Optional[int] = None,
        net_name: Optional[str] = None,
    ) -> List[str]:
        """Route using Manhattan (90-degree) routing.

        Creates two track segments: horizontal then vertical, or vice versa.

        Args:
            starting: Starting point
            end: Ending point
            width: Track width in mm
            layer: Layer name
            net: Optional net number
            net_name: Optional net name

        Returns:
            List of track UUIDs created
        """
        import uuid

        uuids = []

        # Route horizontally first, then vertically
        mid_point = Point(end.x, start.y)

        # First segment (horizontal)
        if start.x != end.x:
            track1 = Track(
                start=start,
                end=mid_point,
                width=width,
                layer=layer,
                net=net,
                net_name=net_name,
                uuid=str(uuid.uuid4()),
            )
            self.board.tracks.add(track1)
            uuids.append(track1.uuid)

        # Second segment (vertical)
        if start.y != end.y:
            track2 = Track(
                start=mid_point,
                end=end,
                width=width,
                layer=layer,
                net=net,
                net_name=net_name,
                uuid=str(uuid.uuid4()),
            )
            self.board.tracks.add(track2)
            uuids.append(track2.uuid)

        logger.info(f"Created Manhattan route with {len(uuids)} segments")
        return uuids

    def get_total_track_length_by_net(self, net: int) -> float:
        """Get total track length for a specific net.

        Args:
            net: Net number

        Returns:
            Total length in mm
        """
        tracks = [t for t in self.board.tracks if t.net == net]
        return sum(t.length for t in tracks)

    def get_length_statistics_by_net(self) -> Dict[int, Dict[str, float]]:
        """Get track length statistics grouped by net.

        Returns:
            Dictionary mapping net numbers to statistics:
            - total_length: Total track length in mm
            - track_count: Number of track segments
            - average_length: Average segment length
        """
        stats = {}

        # Group tracks by net
        nets = {}
        for track in self.board.tracks:
            if track.net is not None:
                if track.net not in nets:
                    nets[track.net] = []
                nets[track.net].append(track)

        # Calculate statistics for each net
        for net, tracks in nets.items():
            lengths = [t.length for t in tracks]
            stats[net] = {
                "total_length": sum(lengths),
                "track_count": len(tracks),
                "average_length": sum(lengths) / len(lengths) if lengths else 0.0,
                "min_length": min(lengths) if lengths else 0.0,
                "max_length": max(lengths) if lengths else 0.0,
            }

        return stats

    def find_stubs(self, min_stub_length: float = 0.1) -> List[str]:
        """Find track stubs (dead-end tracks).

        Args:
            min_stub_length: Minimum length to consider a stub

        Returns:
            List of track UUIDs that are stubs
        """
        # This is a simplified implementation
        # A proper implementation would analyze connectivity
        stubs = []

        for track in self.board.tracks:
            if track.length < min_stub_length:
                stubs.append(track.uuid)

        return stubs

    def optimize_track_order(self) -> None:
        """Optimize track storage order for rendering performance.

        Groups tracks by layer and net for better rendering performance.
        """
        # Sort tracks by layer, then net
        def sort_key(track):
            return (track.data.layer, track.data.net or 0)

        sorted_tracks = sorted(self.board.tracks, key=sort_key)

        # Replace collection items with sorted list
        self.board.tracks._items = [t.data for t in sorted_tracks]
        self.board.tracks._dirty_indexes = True

        logger.info("Optimized track storage order")

    def route_point_to_point(
        self,
        start: Point,
        end: Point,
        width: float,
        layer: str,
        net: Optional[int] = None,
        net_name: Optional[str] = None,
        style: str = "direct",
    ) -> List[str]:
        """Route between two points.

        Args:
            start: Starting point
            end: Ending point
            width: Track width in mm
            layer: Layer name (e.g., 'F.Cu')
            net: Optional net number
            net_name: Optional net name
            style: Routing style ('direct', 'manhattan', 'auto')

        Returns:
            List of track UUIDs created
        """
        if style == "direct":
            # Direct routing (straight line)
            return [self.add_track(start, end, width, layer, net, net_name)]
        elif style == "manhattan":
            # Manhattan routing (90-degree angles)
            return self.route_manhattan(start, end, width, layer, net, net_name)
        elif style == "auto":
            # Auto-route using best available method
            # For now, default to manhattan
            return self.route_manhattan(start, end, width, layer, net, net_name)
        else:
            raise ValueError(
                f"Unknown routing style '{style}'. Use 'direct', 'manhattan', or 'auto'"
            )

    def route_multi_point(
        self,
        points: List[Point],
        width: float,
        layer: str,
        net: Optional[int] = None,
        net_name: Optional[str] = None,
    ) -> List[str]:
        """Route through multiple points.

        Args:
            points: List of points to route through
            width: Track width in mm
            layer: Layer name
            net: Optional net number
            net_name: Optional net name

        Returns:
            List of track UUIDs created
        """
        if len(points) < 2:
            logger.warning("Need at least 2 points to route")
            return []

        uuids = []
        for i in range(len(points) - 1):
            start = points[i]
            end = points[i + 1]
            uuid = self.add_track(start, end, width, layer, net, net_name)
            uuids.append(uuid)

        logger.info(f"Created multi-point route with {len(uuids)} segments")
        return uuids

    def add_via(
        self,
        position: Point,
        size: float = 0.8,
        drill: float = 0.4,
        layers: Optional[List[str]] = None,
        net: Optional[int] = None,
        net_name: Optional[str] = None,
    ) -> str:
        """Add a via at the specified position.

        Args:
            position: Via position
            size: Via diameter in mm
            drill: Drill diameter in mm
            layers: List of layers the via connects (default: all copper layers)
            net: Optional net number
            net_name: Optional net name

        Returns:
            UUID of created via
        """
        import uuid as uuid_module

        if layers is None:
            layers = ["F.Cu", "B.Cu"]  # Default to through-hole via

        via = Via(
            position=position,
            size=size,
            drill=drill,
            layers=layers,
            net=net,
            uuid=str(uuid_module.uuid4()),
        )

        self.board.vias.add(via)
        logger.debug(f"Added via at ({position.x}, {position.y}), net={net}")

        return via.uuid

    def connect_pads(
        self,
        ref1: str,
        pad1: str,
        ref2: str,
        pad2: str,
        width: float = 0.25,
        layer: str = "F.Cu",
        style: str = "manhattan",
        add_vias: bool = False,
    ) -> Tuple[List[str], List[str]]:
        """Connect two pads with routing.

        Args:
            ref1: First component reference
            pad1: First pad number
            ref2: Second component reference
            pad2: Second pad number
            width: Track width in mm
            layer: Layer to route on
            style: Routing style ('direct', 'manhattan', 'auto')
            add_vias: Whether to add vias if components are on different layers

        Returns:
            Tuple of (track_uuids, via_uuids)
        """
        # Get footprints
        fp1 = self.board.footprints.get_by_reference(ref1)
        fp2 = self.board.footprints.get_by_reference(ref2)

        if fp1 is None:
            raise ValueError(f"Footprint {ref1} not found")
        if fp2 is None:
            raise ValueError(f"Footprint {ref2} not found")

        # Find pads
        pad1_obj = None
        for pad in fp1.pads:
            if str(pad.number) == str(pad1):
                pad1_obj = pad
                break

        pad2_obj = None
        for pad in fp2.pads:
            if str(pad.number) == str(pad2):
                pad2_obj = pad
                break

        if pad1_obj is None:
            raise ValueError(f"Pad {pad1} not found on {ref1}")
        if pad2_obj is None:
            raise ValueError(f"Pad {pad2} not found on {ref2}")

        # Calculate absolute pad positions
        pad1_pos = Point(
            fp1.position.x + pad1_obj.position.x,
            fp1.position.y + pad1_obj.position.y,
        )
        pad2_pos = Point(
            fp2.position.x + pad2_obj.position.x,
            fp2.position.y + pad2_obj.position.y,
        )

        # Get net info from pads
        net = pad1_obj.net
        net_name = pad1_obj.net_name

        # Route between pads
        track_uuids = self.route_point_to_point(
            pad1_pos, pad2_pos, width, layer, net, net_name, style
        )

        via_uuids = []

        # Add vias if needed (different layers)
        if add_vias and fp1.layer != fp2.layer:
            # Add via at midpoint
            mid_x = (pad1_pos.x + pad2_pos.x) / 2
            mid_y = (pad1_pos.y + pad2_pos.y) / 2
            via_uuid = self.add_via(
                Point(mid_x, mid_y),
                net=net,
                net_name=net_name,
                layers=[fp1.layer, fp2.layer],
            )
            via_uuids.append(via_uuid)

        logger.info(
            f"Connected {ref1}:{pad1} to {ref2}:{pad2} with {len(track_uuids)} tracks and {len(via_uuids)} vias"
        )
        return track_uuids, via_uuids

    def auto_route_freerouting(
        self,
        dsn_file: Optional[str] = None,
        ses_file: Optional[str] = None,
        effort: str = "medium",
        optimization_passes: int = 10,
        timeout_seconds: Optional[int] = 3600,
        keep_temp_files: bool = False,
    ) -> bool:
        """Auto-route the board using Freerouting.

        Args:
            dsn_file: Path to DSN file (None = generate from board)
            ses_file: Path to SES file (None = auto-generate)
            effort: Routing effort ('fast', 'medium', 'high')
            optimization_passes: Number of optimization passes
            timeout_seconds: Timeout in seconds
            keep_temp_files: Whether to keep temporary DSN/SES files

        Returns:
            True if routing successful, False otherwise
        """
        import tempfile

        # Generate DSN file if not provided
        if dsn_file is None:
            temp_dir = tempfile.mkdtemp()
            dsn_file = str(Path(temp_dir) / "board.dsn")
            logger.info(f"Generating DSN file: {dsn_file}")

            exporter = DSNExporter(self.board)
            exporter.export(Path(dsn_file))

        # Generate SES file path if not provided
        if ses_file is None:
            ses_file = str(Path(dsn_file).with_suffix(".ses"))

        # Create Freerouting config
        config = FreeroutingConfig(
            effort=effort,
            optimization_passes=optimization_passes,
            timeout_seconds=timeout_seconds,
        )

        # Run Freerouting
        logger.info("Starting Freerouting auto-router...")
        runner = FreeroutingRunner(config)
        success, result = runner.route(dsn_file, ses_file)

        if not success:
            logger.error(f"Freerouting failed: {result}")
            return False

        # Import SES file back into board
        logger.info(f"Importing routing from {ses_file}")
        try:
            # Clear existing routing
            self.board.tracks.clear()
            self.board.vias.clear()

            # Import new routing
            importer = SESImporter(str(self.board.file_path), ses_file)
            importer.import_routing()

            logger.info("Freerouting completed successfully")

            # Clean up temp files if requested
            if not keep_temp_files:
                try:
                    Path(dsn_file).unlink()
                    Path(ses_file).unlink()
                    logger.debug("Cleaned up temporary files")
                except Exception as e:
                    logger.warning(f"Could not clean up temp files: {e}")

            return True

        except Exception as e:
            logger.error(f"Failed to import routing: {e}")
            return False

    def validate_routing(
        self,
        check_clearances: bool = True,
        check_connectivity: bool = True,
        min_clearance: float = 0.2,
    ) -> Dict[str, List[str]]:
        """Validate routing for errors.

        Args:
            check_clearances: Whether to check track clearances
            check_connectivity: Whether to check net connectivity
            min_clearance: Minimum clearance between tracks in mm

        Returns:
            Dictionary of validation errors by type
        """
        errors: Dict[str, List[str]] = {
            "clearance_violations": [],
            "unrouted_nets": [],
            "layer_violations": [],
        }

        # Check track clearances
        if check_clearances:
            tracks = list(self.board.tracks)
            for i, track1 in enumerate(tracks):
                for track2 in tracks[i + 1 :]:
                    # Skip if same net
                    if track1.net == track2.net:
                        continue

                    # Check if tracks are on same layer
                    if track1.layer != track2.layer:
                        continue

                    # Simple clearance check (could be more sophisticated)
                    # Check if track endpoints are too close
                    points1 = [track1.start, track1.end]
                    points2 = [track2.start, track2.end]

                    for p1 in points1:
                        for p2 in points2:
                            distance = (
                                (p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2
                            ) ** 0.5
                            if distance < min_clearance:
                                errors["clearance_violations"].append(
                                    f"Clearance violation between nets {track1.net} and {track2.net}: {distance:.3f}mm < {min_clearance}mm"
                                )

        # Check connectivity
        if check_connectivity:
            # Get all nets that have pads
            nets_with_pads = set()
            for fp in self.board.footprints.values():
                for pad in fp.pads:
                    if pad.net is not None and pad.net > 0:
                        nets_with_pads.add(pad.net)

            # Get all nets that have tracks
            nets_with_tracks = set()
            for track in self.board.tracks:
                if track.net is not None and track.net > 0:
                    nets_with_tracks.add(track.net)

            # Find unrouted nets
            unrouted = nets_with_pads - nets_with_tracks
            if unrouted:
                for net in unrouted:
                    errors["unrouted_nets"].append(f"Net {net} has no routing")

        # Check layer validity
        valid_layers = {"F.Cu", "B.Cu", "In1.Cu", "In2.Cu", "In3.Cu", "In4.Cu"}
        for track in self.board.tracks:
            if track.layer not in valid_layers:
                errors["layer_violations"].append(
                    f"Track on invalid layer: {track.layer}"
                )

        # Log summary
        total_errors = sum(len(v) for v in errors.values())
        if total_errors == 0:
            logger.info("Routing validation passed")
        else:
            logger.error(f"Routing validation found {total_errors} error(s)")
            for error_type, error_list in errors.items():
                if error_list:
                    logger.error(f"  {error_type}: {len(error_list)} errors")

        return errors

    def get_net_routing_stats(self, net: int) -> Dict[str, any]:
        """Get routing statistics for a specific net.

        Args:
            net: Net number

        Returns:
            Dictionary with routing statistics
        """
        tracks = [t for t in self.board.tracks if t.net == net]
        vias = [v for v in self.board.vias if v.net == net]

        total_length = sum(t.length for t in tracks)
        layers_used = set(t.layer for t in tracks)

        return {
            "net": net,
            "track_count": len(tracks),
            "via_count": len(vias),
            "total_length": total_length,
            "layers_used": list(layers_used),
            "average_track_width": (
                sum(t.width for t in tracks) / len(tracks) if tracks else 0
            ),
        }
