from enum import Enum


class Orientation(Enum):
    """Enum-like class for cardinal orientations.

    Provides values for North, East, South, and West, along with utility
    methods for navigation.
    """

    NORTH = "North"
    EAST = "East"
    SOUTH = "South"
    WEST = "West"

    @staticmethod
    def turn_left(orientation):
        """Calculates the new orientation after turning left.

        Args:
            orientation (Orientation): The current orientation.

        Returns:
            Orientation: The new orientation after a 90-degree left turn.
        """
        if orientation == Orientation.NORTH:
            return Orientation.WEST
        if orientation == Orientation.WEST:
            return Orientation.SOUTH
        if orientation == Orientation.SOUTH:
            return Orientation.EAST
        return Orientation.NORTH  # EAST

    @staticmethod
    def turn_right(orientation):
        """Calculates the new orientation after turning right.

        Args:
            orientation (Orientation): The current orientation.

        Returns:
            Orientation: The new orientation after a 90-degree right turn.
        """
        if orientation == Orientation.NORTH:
            return Orientation.EAST
        if orientation == Orientation.EAST:
            return Orientation.SOUTH
        if orientation == Orientation.SOUTH:
            return Orientation.WEST
        return Orientation.NORTH  # WEST

    @staticmethod
    def forward(orientation, x, y):
        """Calculates the new coordinates after moving one step forward.

        Args:
            orientation (Orientation): The current orientation.
            x (int): The current x-coordinate.
            y (int): The current y-coordinate.

        Returns:
            tuple[int, int]: The new (x, y) coordinates.
        """
        if orientation == Orientation.NORTH:
            return x, y + 1
        if orientation == Orientation.EAST:
            return x + 1, y
        if orientation == Orientation.SOUTH:
            return x, y - 1
        return x - 1, y  # WEST

    def __hash__(self):
        """Returns a hash value for the orientation."""
        return hash(self.value)

    def __lt__(self, other):
        """Less than comparison based on orientation value.

        Defines a specific ordering for orientations, useful for tie-breaking.
        The order is East < South < West < North.

        Args:
            other (Orientation): The other orientation to compare against.

        Returns:
            bool: True if this orientation is "less than" the other.
        """
        if self.value == other.value:
            return False

        if self.value == "East":
            return True
        if self.value == "South":
            return other.value in ["West", "North"]
        if self.value == "West":
            return other.value in ["North"]
        return False  # North

    def __sub__(self, other):
        """Calculates the "distance" between two orientations.

        The distance is defined as the number of 90-degree turns required to
        get from one orientation to the other.

        Args:
            other (Orientation): The other orientation.

        Returns:
            int: 0 for same orientation, 1 for adjacent, 2 for opposite.
        """
        if self.value == other.value:
            return 0
        if self.value in ["North", "East"]:
            return 1 if other.value in ["South", "West"] else 2
        return 1 if other.value in ["North", "East"] else 2  # South or West


class Position:
    """Class representing a position with coordinates and orientation.

    Attributes:
        x (int): The x-coordinate.
        y (int): The y-coordinate.
    """

    def __init__(
        self, x: int = 0, y: int = 0, orientation: Orientation = Orientation.EAST
    ):
        """Initializes a Position object.

        Args:
            x (int, optional): The x-coordinate. Defaults to 0.
            y (int, optional): The y-coordinate. Defaults to 0.
            orientation (Orientation, optional): The orientation. Defaults to Orientation.EAST.
        """
        self.x, self.y = x, y
        self.__orientation = orientation

    @property
    def location(self) -> tuple[int, int]:
        """The (x, y) coordinates of the position."""
        return self.x, self.y

    @location.setter
    def location(self, location: tuple[int, int]):
        """Sets the (x, y) coordinates of the position.

        Args:
            location (tuple[int, int]): The new location.
        """
        self.x, self.y = location

    def get_orientation(self) -> Orientation:
        """Returns the orientation of the position."""
        return self.__orientation

    def set_orientation(self, orientation: Orientation):
        """Sets the orientation of the position.

        Args:
            orientation (Orientation): The new orientation.
        """
        self.__orientation = orientation

    def __repr__(self) -> str:
        """Returns a string representation of the Position object."""
        return f"Position(x={self.x}, y={self.y}, orientation={self.__orientation})"

    def __eq__(self, other):
        """Checks if two Position objects are equal.

        Two positions are equal if they have the same location and orientation.

        Args:
            other (Position): The other position to compare.

        Returns:
            bool: True if the positions are equal, False otherwise.
        """
        if self.location != other.location:
            return False
        return self.get_orientation() == other.get_orientation()

    def __hash__(self):
        """Returns a hash value for the Position object."""
        return hash((self.x, self.y, self.get_orientation()))

    def __lt__(self, other):
        """Less than comparison for sorting and tie-breaking.

        Comparison is based first on orientation, then on location.

        Args:
            other (Position): The other position to compare.

        Returns:
            bool: True if this position is less than the other.
        """
        return (self.get_orientation(), self.location) < (
            other.get_orientation(),
            other.location,
        )

    def __sub__(self, other) -> tuple[int, int, int]:
        """Calculates the difference between two positions.

        The difference is a tuple containing the absolute difference in x,
        the absolute difference in y, and the "distance" between orientations.

        Args:
            other (Position): The other position.

        Returns:
            tuple[int, int, int]: A tuple of differences (dx, dy, d_orientation).
        """
        return (
            abs(self.x - other.x),
            abs(self.y - other.y),
            self.get_orientation() - other.get_orientation(),
        )


class Action(Enum):
    """Enum-like class for actions in the Wumpus World.

    Includes agent actions and special actions for the environment/Wumpus.
    """

    FORWARD = "Forward"
    TURN_LEFT = "TurnLeft"
    TURN_RIGHT = "TurnRight"
    GRAB = "Grab"
    SHOOT = "Shoot"
    CLIMB = "Climb"
    NOOP = "NoOp"  # No operation, used when no action is needed

    KILL = "Kill"  # Action to kill the Agent, used by SmartWumpus
    MOVE = "Move"  # Action to move the Wumpus, used by SmartWumpus

    @staticmethod
    def forward(position: Position) -> Position:
        """Returns a new position after moving forward from the given position.

        Args:
            position (Position): The current position.

        Returns:
            Position: The new position after moving forward.
        """
        x, y = position.location
        new_x, new_y = Orientation.forward(position.get_orientation(), x, y)
        return Position(new_x, new_y, position.get_orientation())

    @staticmethod
    def turn_left(position: Position) -> Position:
        """Returns a new position after turning left from the given position.

        The location remains the same, only the orientation changes.

        Args:
            position (Position): The current position.

        Returns:
            Position: The new position with the updated orientation.
        """
        new_orientation = Orientation.turn_left(position.get_orientation())
        return Position(position.x, position.y, new_orientation)

    @staticmethod
    def turn_right(position: Position) -> Position:
        """Returns a new position after turning right from the given position.

        The location remains the same, only the orientation changes.

        Args:
            position (Position): The current position.

        Returns:
            Position: The new position with the updated orientation.
        """
        new_orientation = Orientation.turn_right(position.get_orientation())
        return Position(position.x, position.y, new_orientation)
