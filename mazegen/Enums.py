from enum import Enum


class Direction(Enum):
    NORTH = 0b1
    EAST = 0b10
    SOUTH = 0b100
    WEST = 0b1000

    def oppo(self) -> "Direction":
        """get the opposite direction"""
        return {
            Direction.NORTH: Direction.SOUTH,
            Direction.SOUTH: Direction.NORTH,
            Direction.EAST:  Direction.WEST,
            Direction.WEST:  Direction.EAST,
        }[self]

    def delta(self) -> tuple:
        """get the delta for direction changing"""
        return {
            Direction.NORTH: (0, -1),
            Direction.SOUTH: (0, 1),
            Direction.EAST:  (1, 0),
            Direction.WEST:  (-1, 0),
        }[self]

    def to_text(self) -> str:
        """get the char representation of directions"""
        return {
            Direction.NORTH: 'N',
            Direction.SOUTH: 'S',
            Direction.EAST:  'E',
            Direction.WEST:  'W',
        }[self]
