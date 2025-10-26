"""Base manager class for PCB operations."""

from abc import ABC
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.pcb_board import PCBBoard


class BaseManager(ABC):
    """Base class for all PCB managers.

    Managers encapsulate complex operations and keep PCBBoard focused.
    Each manager has a reference to the parent board for accessing collections.
    """

    def __init__(self, board: "PCBBoard"):
        """Initialize manager with parent board reference.

        Args:
            board: The PCBBoard instance this manager operates on
        """
        self._board = board

    @property
    def board(self) -> "PCBBoard":
        """Get the parent board.

        Returns:
            The PCBBoard instance
        """
        return self._board
