from typing import List, Tuple, Callable
from Enums import Direction
from random import Random
from Cell import Cell
from time import sleep, time
import sys
from Maze_config import MazeConfig


class Maze():
    def __init__(self, config: MazeConfig):
        self.solution: List[tuple[int, int]] = []
        self.rng: Callable = Random(config.SEED)
        self.context = {}
        self.width = config.WIDTH
        self.height = config.HEIGHT
        self.start = config.ENTRY
        self.end = config.EXIT
        self.output_file = config.OUTPUT_FILE
        self.perfect = config.PERFECT
        self.cells = [[Cell() for x in range(self.width)]
                      for y in range(self.height)]
        self.algo_name = ""
        self.algo = {
                "backtrack": self.backtrack_algo(),
                "tree": self.tree_algo(),
            }.get(self.algo_name, self.backtrack_algo())
        if self.perfect:
            self.algo = self.backtrack_algo()
        self.anim_finished = False
        self.anim = True
        self.patern_42(1, 1)

    def get_cell(self, coord: tuple[int, int]) -> Cell:
        return self.cells[coord[0]][coord[1]]

    def launch_algo(self):
        if self.anim and not self.anim_finished:
            try:
                next(self.algo)
            except StopIteration:
                self.anim_finished = True
        elif not self.anim_finished:
            for _ in self.algo:
                continue
            self.anim_finished = True
        else:
            print("already finished")

    def backtrack_algo(self):
        yield None
        stack = [self.start]
        while stack:
            act_pos = stack[-1]
            available_dir = []
            for direct in Direction:
                pos = self.add_pos(direct.delta(), act_pos)
                if (self.is_in_bound(pos)):
                    neighbord = self.get_cell(pos)
                    if (not neighbord.is_visited
                            and not neighbord.blocked):
                        available_dir.append(direct)
            if available_dir:
                goal = self.rng.choice(available_dir)
                self.get_cell(act_pos).remove_wall(goal)
                stack.append(self.add_pos(act_pos, goal.delta()))
                self.get_cell(stack[-1]).remove_wall(goal.oppo())
                yield None
            else:
                stack.pop()

    # def backtrack(cell: tuple, rng: random, w:int, h:int) -> None:
    # set_visited(cell, maze)
    # directions = get_neighbords(cell, maze, w, h)
    # rng.shuffle(directions)
    # for d in directions:
    #     next_cell = take_dir(d, cell)
    #     if not is_visited(maze, next_cell):
    #         rm_wall(maze, d, cell)
    #         rm_wall(maze, dir_oppo(d), next_cell)
    #     backtrack(maze, next_cell, rng, w, h)

    def tree_algo(self):
        for i in range(40):
            yield

    def patern_42(self, off_y, off_x):
        fourthy = [(0, 0), (1, 0), (2, 0), (2, 1), (2, 2), (3, 2), (4, 2)]
        two = [(0, 0), (0, 1), (0, 2), (1, 2), (2, 2), (2, 1), (2, 0), (3, 0),
               (4, 0), (4, 1), (4, 2)]
        fourthy_offset = [(off_y + pos[0], off_x + pos[1]) for pos in fourthy]
        two_offset = [(off_y + pos[0], off_x + pos[1] + 5) for pos in two]
        final_patern = fourthy_offset + two_offset
        min_height = max(final_patern, key=lambda item: item[0])[0] + 2
        min_width = max(final_patern, key=lambda item: item[1])[1] + 2
        if self.width >= min_width and self.height >= min_height:
            self.apply_pattern(final_patern)
        else:
            print("maze too small for the 42 pattern", file=sys.stderr)

    def apply_pattern(self, coords: list[tuple[int, int]]):
        for coord in coords:
            self.get_cell(coord).blocked = True

    def parser_A(self):
        pass

    def hexa(self):
        return "\n".join(
            "".join("0123456789ABCDEF"[cell.walls & 15] for cell in row)
            for row in self.cells)

        # helper func
    def abs_dist(self, pos1: tuple[int, int], pos2: tuple[int, int]):
        pass

    def add_pos(self, pos1: tuple[int, int],
                pos2: tuple[int, int]) -> tuple:
        return tuple(a + b for a, b in zip(pos1, pos2))

    def is_in_bound(self, pos: tuple[int, int]):
        return (True if 0 <= pos[0] < self.height
                and 0 <= pos[1] < self.width else False)

    def get_neighbors(self, x, y) -> List[Tuple[Cell, Direction]]:
        pass
