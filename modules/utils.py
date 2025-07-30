from enum import Enum


class Orientation(Enum):
    """Enum-like class for orientations."""
    NORTH = "North"
    EAST = "East"
    SOUTH = "South"
    WEST = "West"

    @staticmethod
    def turn_left(orientation):
        if orientation == Orientation.NORTH:
            return Orientation.WEST
        if orientation == Orientation.WEST:
            return Orientation.SOUTH
        if orientation == Orientation.SOUTH:
            return Orientation.EAST
        return Orientation.NORTH  # EAST

    @staticmethod
    def turn_right(orientation):
        if orientation == Orientation.NORTH:
            return Orientation.EAST
        if orientation == Orientation.EAST:
            return Orientation.SOUTH
        if orientation == Orientation.SOUTH:
            return Orientation.WEST
        return Orientation.NORTH  # WEST

    @staticmethod
    def forward(orientation, x, y):
        if orientation == Orientation.NORTH:
            return x, y + 1
        if orientation == Orientation.EAST:
            return x + 1, y
        if orientation == Orientation.SOUTH:
            return x, y - 1
        return x - 1, y  # WEST

    def __sub__(self, other):
        """Subtracts another orientation from this one, returning a tuple of differences."""
        if self.value == other.value:
            return 0
        if self.value == "North" or self.value == "East":
            return 1 if other.value in ["South", "West"] else 2
        return 1 if other.value in ["North", "East"] else 2  # South or West


class Position:
    """Class representing a position with coordinates and orientation."""

    def __init__(self, x: int = 0, y: int = 0, orientation: Orientation = Orientation.WEST):
        self.x = x
        self.y = y
        self.__orientation = orientation

    @property
    def location(self) -> tuple[int, int]:
        return self.x, self.y

    @location.setter
    def location(self, location: tuple[int, int]):
        self.x, self.y = location

    def get_orientation(self) -> Orientation:
        return self.__orientation

    def set_orientation(self, orientation: Orientation):
        self.__orientation = orientation

    def __eq__(self, other):
        if self.location != other.location:
            return False
        return self.get_orientation() == other.get_orientation()

    def __lt__(self, other):
        """Less than comparison based on coordinates and orientation."""
        return (self.get_orientation(), self.location) < (other.get_orientation(), other.location)

    def __sub__(self, other) -> tuple[int, int, int]:
        """Subtracts another position from this one, returning a tuple of differences."""
        return abs(self.x - other.x), abs(self.y - other.y), self.get_orientation() - other.get_orientation()
