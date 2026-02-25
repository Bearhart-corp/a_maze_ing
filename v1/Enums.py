from enum import Enum


class Direction(Enum):
    NORTH = 0b1
    EAST = 0b10
    SOUTH = 0b100
    WEST = 0b1000

    def oppo(self) -> "Direction":
        return {
            Direction.NORTH: Direction.SOUTH,
            Direction.SOUTH: Direction.NORTH,
            Direction.EAST:  Direction.WEST,
            Direction.WEST:  Direction.EAST,
        }[self]

    def delta(self):
        return {
            Direction.NORTH: (-1, 0),
            Direction.SOUTH: (1, 0),
            Direction.EAST:  (0, 1),
            Direction.WEST:  (0, -1),
        }[self]

    def un_delta(self, delta: tuple[int, int]):
        return {
            (-1, 0): Direction.NORTH,
            (1, 0): Direction.SOUTH,
            (0, 1): Direction.EAST,
            (0, -1): Direction.WEST
        }[delta]


class Arrow(Enum):
    NORTH = "\033[92m ⬆\033[0m"
    EAST = "\033[92m ➡\033[0m"
    SOUTH = "\033[92m⬇ \033[0m"
    WEST = "\033[92m⬅ \033[0m"
    WIN = "👑"
    START = "\033[92m[]\033[0m"


class Redarrow(Enum):
    NORTH = "\033[91m ⬆\033[0m"
    EAST = "\033[91m ➡\033[0m"
    SOUTH = "\033[91m⬇ \033[0m"
    WEST = "\033[91m⬅ \033[0m"
    WIN = "👑"
    START = "\033[91m[]\033[0m"
