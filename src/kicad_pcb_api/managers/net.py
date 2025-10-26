"""Net management operations."""

import logging
from typing import Dict, List, Optional, Set

from .base import BaseManager

logger = logging.getLogger(__name__)


class NetManager(BaseManager):
    """Manager for net operations.

    Handles net classes, net connectivity, and net-based queries.
    """

    def get_all_nets(self) -> Set[int]:
        """Get all unique net numbers in the board.

        Returns:
            Set of net numbers
        """
        nets: Set[int] = set()

        # First, collect all nets defined in the board's net list
        for net in self.board.pcb_data.get("nets", []):
            nets.add(net.number)

        # Also collect nets from footprint pads
        # Access raw data list instead of iterating over collection
        for footprint_data in self.board.pcb_data.get("footprints", []):
            for pad in footprint_data.pads:
                if pad.net is not None:
                    nets.add(pad.net)

        # Collect nets from tracks
        for track_data in self.board.pcb_data.get("tracks", []):
            if track_data.net is not None:
                nets.add(track_data.net)

        # Collect nets from vias
        for via_data in self.board.pcb_data.get("vias", []):
            if via_data.net is not None:
                nets.add(via_data.net)

        return nets

    def get_net_name(self, net: int) -> Optional[str]:
        """Get the name for a net number.

        Args:
            net: Net number

        Returns:
            Net name if found, None otherwise
        """
        # Try to find net name from footprint pads
        for footprint_data in self.board.pcb_data.get("footprints", []):
            for pad in footprint_data.pads:
                if pad.net == net and pad.net_name:
                    return pad.net_name

        # Try tracks
        for track_data in self.board.pcb_data.get("tracks", []):
            if track_data.net == net and hasattr(track_data, 'net_name') and track_data.net_name:
                return track_data.net_name

        # Try vias
        for via_data in self.board.pcb_data.get("vias", []):
            if via_data.net == net and hasattr(via_data, 'net_name') and via_data.net_name:
                return via_data.net_name

        return None

    def get_net_statistics(self) -> Dict[int, Dict[str, any]]:
        """Get comprehensive statistics for all nets.

        Returns:
            Dictionary mapping net numbers to statistics including:
            - name: Net name
            - track_count: Number of tracks on this net
            - via_count: Number of vias on this net
            - pad_count: Number of pads on this net
            - total_track_length: Total length of tracks in mm
        """
        stats: Dict[int, Dict[str, any]] = {}

        for net in self.get_all_nets():
            name = self.get_net_name(net)
            tracks = [t for t in self.board.pcb_data.get("tracks", []) if t.net == net]
            vias = [v for v in self.board.pcb_data.get("vias", []) if v.net == net]

            pad_count = 0
            for footprint_data in self.board.pcb_data.get("footprints", []):
                for pad in footprint_data.pads:
                    if pad.net == net:
                        pad_count += 1

            # Calculate track length
            total_length = 0
            for track in tracks:
                import math
                dx = track.end.x - track.start.x
                dy = track.end.y - track.start.y
                total_length += math.sqrt(dx * dx + dy * dy)

            stats[net] = {
                "name": name,
                "track_count": len(tracks),
                "via_count": len(vias),
                "pad_count": pad_count,
                "total_track_length": total_length,
            }

        return stats

    def find_unconnected_pads(self) -> List[tuple]:
        """Find all pads that are not connected (net = 0 or None).

        Returns:
            List of (footprint_reference, pad_number) tuples
        """
        unconnected = []

        for footprint_data in self.board.pcb_data.get("footprints", []):
            for pad in footprint_data.pads:
                if pad.net is None or pad.net == 0:
                    unconnected.append((footprint_data.reference, pad.number))

        return unconnected

    def rename_net(self, old_net: int, new_name: str) -> int:
        """Rename a net (update net_name on all connected elements).

        Args:
            old_net: Net number to rename
            new_name: New name for the net

        Returns:
            Number of elements updated
        """
        count = 0

        # Update footprint pads
        for footprint_data in self.board.pcb_data.get("footprints", []):
            for pad in footprint_data.pads:
                if pad.net == old_net:
                    pad.net_name = new_name
                    count += 1

        # Update tracks
        for track_data in self.board.pcb_data.get("tracks", []):
            if track_data.net == old_net:
                if hasattr(track_data, 'net_name'):
                    track_data.net_name = new_name
                count += 1

        # Update vias
        for via_data in self.board.pcb_data.get("vias", []):
            if via_data.net == old_net:
                if hasattr(via_data, 'net_name'):
                    via_data.net_name = new_name
                count += 1

        if count > 0:
            logger.info(f"Renamed net {old_net} to '{new_name}' on {count} elements")

        return count
