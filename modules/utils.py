"""Utility classes and data structures for the Wumpus World Agent.

This module provides core data structures for representing positions,
orientations, and common utility functions used throughout the project.
"""

from enum import IntEnum
from typing import NamedTuple


class Position(NamedTuple):
    """Represents a coordinate position in the Wumpus World grid.

    This immutable class encapsulates a 2D grid position using zero-based
    indexing, where (0,0) represents the starting cell in the bottom-left
    corner of the Wumpus World grid.

    **Coordinate System**:
    - x-axis: Row index (0-based, increases southward/downward)
    - y-axis: Column index (0-based, increases eastward/rightward)
    - Origin (0,0): Bottom-left corner (agent starting position)

    **Grid Layout Example (4×4)**:
    ```
    (0,3) (0,2) (0,1) (0,0)  ← y=3 (top row)
    (1,3) (1,2) (1,1) (1,0)  ← y=2
    (2,3) (2,2) (2,1) (2,0)  ← y=1  
    (3,3) (3,2) (3,1) (3,0)  ← y=0 (bottom row)
      ↑     ↑     ↑     ↑
     x=3   x=2   x=1   x=0
    ```

    Attributes:
        x: Row index (0-based, increases southward).
        y: Column index (0-based, increases eastward).

    Example:
        >>> start = Position(0, 0)  # Bottom-left corner
        >>> center = Position(2, 2)  # Center of 4×4 grid
        >>> 
        >>> # Position arithmetic
        >>> delta = Position(1, 0)  # Move south
        >>> new_pos = Position(start.x + delta.x, start.y + delta.y)
    """
    x: int
    y: int


class Orientation(IntEnum):
    """Encodes agent orientation as integer constants.

    This enumeration represents the four cardinal directions the agent
    can face, with arithmetic support for rotation calculations.

    Attributes:
        UP: Facing north (towards decreasing x).
        RIGHT: Facing east (towards increasing y).
        DOWN: Facing south (towards increasing x).
        LEFT: Facing west (towards decreasing y).
    """
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3

    def turn_left(self) -> 'Orientation':
        """Return new orientation after turning left.

        Returns:
            New orientation after a 90-degree counterclockwise turn.
        """
        return Orientation((self - 1) % 4)

    def turn_right(self) -> 'Orientation':
        """Return new orientation after turning right.

        Returns:
            New orientation after a 90-degree clockwise turn.
        """
        return Orientation((self + 1) % 4)

    def to_vector(self) -> Position:
        """Convert orientation to movement vector for position calculations.

        Transforms the orientation into a displacement vector that can be
        added to a position to calculate the result of moving forward.

        **Vector Mappings**:
        - UP (North): (-1, 0) - decreases x coordinate
        - DOWN (South): (1, 0) - increases x coordinate  
        - LEFT (West): (0, -1) - decreases y coordinate
        - RIGHT (East): (0, 1) - increases y coordinate

        Returns:
            Position representing the displacement vector (dx, dy)
            for moving one step in this orientation.

        Raises:
            ValueError: If orientation value is invalid.

        Example:
            >>> pos = Position(2, 3)
            >>> direction = Orientation.RIGHT
            >>> new_pos = Position(pos.x + direction.to_vector().x,
            ...                   pos.y + direction.to_vector().y)
            >>> # new_pos is Position(2, 4) - moved east
        """
        if self == Orientation.UP:
            return Position(-1, 0)
        if self == Orientation.DOWN:
            return Position(1, 0)
        if self == Orientation.LEFT:
            return Position(0, -1)
        if self == Orientation.RIGHT:
            return Position(0, 1)
        raise ValueError(f"Invalid orientation: {self}")
