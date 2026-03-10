from typing import List
from ..Enums import Direction
from random import Random
from .Cell import Cell
import sys
from ..Maze_config import MazeConfig


class Maze():
    """A maze is a list of closed cells at a coordonate, he has a size
    an entry and an exit, a seed and some config"""
    def __init__(self, config: MazeConfig):
        self.rng: Random = Random(config.SEED)
        self.context: dict = {}
        self.width = config.WIDTH
        self.height = config.HEIGHT
        self.start = config.ENTRY
        self.end = config.EXIT
        self.output_file = config.OUTPUT_FILE
        self.perfect = config.PERFECT
        self.cells = [[Cell() for y in range(self.height)]
                      for x in range(self.width)]  # flipped x and y
        self.anim_finished = False
        self.anim = config.ANIM
        self.solution_pos: List[tuple[int, int]] = []
        self.solution_direct: List[Direction] = []
        self.patern_42((self.height - 5) // 2, (self.width - 8) // 2)

    def get_cell(self, coord: tuple[int, int]) -> Cell:
        """args = position.
        get the cell with his position in the maze
        return a cell"""
        x, y = coord
        return self.cells[x][y]

    def get_valid_neighbords(self, act_pos: tuple) -> list[Direction]:
        """args = current position.
        get all the valid neigbords
        return the list of the directions to the valid neighbord"""
        neighbords = []
        for dir in Direction:
            pos = self.add_pos(dir.delta(), act_pos)
            if self.is_in_bound(pos):
                cell = self.get_cell(pos)
                if not cell.is_visited and not cell.blocked:
                    neighbords.append(dir)
        return neighbords

    def patern_42(self, off_y, off_x):
        """args = 2 offsets.
        apply an offset on the pattern"""
        fourthy = [(0, 0), (1, 0), (2, 0), (2, 1), (2, 2), (3, 2), (4, 2)]
        two = [(0, 0), (0, 1), (0, 2), (1, 2), (2, 2), (2, 1), (2, 0), (3, 0),
               (4, 0), (4, 1), (4, 2)]
        fourthy_offset = [(off_x + pos[1], off_y + pos[0]) for pos in fourthy]
        two_offset = [(off_x + pos[1] + 5, off_y + pos[0]) for pos in two]
        final_patern = fourthy_offset + two_offset
        min_width = max(final_patern, key=lambda item: item[0])[0] + 2
        min_height = max(final_patern, key=lambda item: item[1])[1] + 2
        if self.width >= min_width and self.height >= min_height:
            self.apply_pattern(final_patern)
        else:
            print("maze too small for the 42 pattern", file=sys.stderr)

    def apply_pattern(self, coords: list[tuple[int, int]]):
        """args = a list of the positions of the 42
        set the cells at blocked"""
        for coord in coords:
            self.get_cell(coord).blocked = True

    def hexa(self):
        """write the hexadecimal representation of the maze"""
        return "\n".join(
            "".join("0123456789ABCDEF"[self.cells[col][row].walls & 15] for
                    col in range(self.width))
            for row in range(self.height)
        )

    @staticmethod
    def abs_dist(pos1: tuple[int, int], pos2: tuple[int, int]) -> int:
        """args = position 1 and position 2
        we get the manhatan distance ( number of the cells we have to parcours to 
        reach the destination)
        return the manhatan distance"""
        x1, y1 = pos1
        x2, y2 = pos2
        return abs(x1 - x2) + abs(y1 - y2)

    @staticmethod
    def add_pos(pos1: tuple[int, int], pos2: tuple[int, int]) -> tuple:
        """args = 2 positions we wanna add
        unpack and add the position
        ret the new position"""
        return tuple(a + b for a, b in zip(pos1, pos2))

    def is_in_bound(self, pos: tuple[int, int]):
        """arg = a position
        return true if the cell is inside of the maze"""
        x, y = pos
        return 0 <= x < self.width and 0 <= y < self.height

    def get_neighbors(self, act_pos: tuple) -> List[tuple[tuple, Direction]]:
        """Args = current position as a tuple and the maze
        Get the possible directions, conditions for possible are:
        inside of the maze and not in the 42 pattern
        Return a list of the possible directions and they positions"""
        neighbords: list = []
        for dir in Direction:
            pos = self.add_pos(dir.delta(), act_pos)
            if self.is_in_bound(pos):
                cell = self.get_cell(pos)
                if not cell.blocked:
                    neighbords.append((pos, dir))
        return neighbords

    def parser_A(self) -> None:
        """Use the DFS AND maximize the efficiency with the manhatan distance"""
        rank: List[List[int]] = [[-1 for y in range(self.height)]
                                 for x in range(self.width)]
        sx, sy = self.start
        rank[sx][sy] = 0
        queue = [self.start]
        while queue:
            base_x, base_y = min(
                queue, key=lambda pos: self.abs_dist(
                    pos, self.end) + rank[pos[0]][pos[1]]
            )
            base = self.get_cell((base_x, base_y))
            queue.remove((base_x, base_y))
            if (base_x, base_y) == self.end:
                break
            for neighbor, direct in self.get_neighbors((base_x, base_y)):
                nx, ny = neighbor
                if (base.wall_state(direct) == 0
                    and (rank[nx][ny] > rank[base_x][base_y] + 1
                         or rank[nx][ny] == -1)):
                    rank[nx][ny] = rank[base_x][base_y] + 1
                    queue.append((nx, ny))
        solution = [self.end]
        solution_dir = []
        while rank[solution[-1][0]][solution[-1][1]]:
            current = solution[-1]
            current_rank = rank[current[0]][current[1]]
            for neighbor, direct in self.get_neighbors(current):
                nx, ny = neighbor
                if (self.get_cell(current).wall_state(direct) == 0
                        and rank[nx][ny] == current_rank - 1):
                    solution.append(neighbor)
                    solution_dir.append(direct.oppo())
                    break
        solution.reverse()
        solution_dir.reverse()
        solution_dir.append(None)
        self.solution_pos = solution
        self.solution_direct = solution_dir
