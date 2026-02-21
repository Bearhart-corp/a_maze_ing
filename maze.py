from enum import Enum


class maze:
    maze_cells = []

    def __init__(
            self,
            width: int,
            height: int,
            entry: tuple,
            exit: tuple,
            perfect: bool
    ):
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit
        self.perfect = perfect

    def gen_maze(self):
        for _ in range(self.width):
            for _ in range(self.height):
                self.maze_cells.append((1, 1, 1, 1))

    def print_maze(self):
        for dir in [0, 1, 2, 3]:
            for cel in self.maze_cells:
                if cel[dir] == 1:
                    if dir == 0:
                        print('@@', end="")
                    if dir == 1:
                        print('|', end="")
                        print(' ', end="")
            print("")

    class cell:
        def __init__(self) -> None:
            self.config = {
                'NORTH': 1,
                'EAST': 1,
                'SOUTH': 1,
                'WEST': 1
            }


class Pos(Enum):
    NORTH = 0b0001
    EAST = 0b0010
    SOUTH = 0b0100
    WEST = 0b1000


def main():
    laberinto = maze(3, 3, (0, 0), (2, 2), True)
    laberinto.gen_maze()
    laberinto.print_maze()


if __name__ == "__main__":
    main()
