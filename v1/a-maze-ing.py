from random import randint
from typing import Any
from Mazes import Maze
from Enums import Direction, Redarrow
from sys import stderr
from Utils import spell_timer
# from visualizer import print_maze


def wall_break(maze):
    for j in range(30):
        cell = maze.random_cell()
        direct = maze.rng.choice([d for d in Direction])
        if cell.wall_state(direct) == 1:
            cell.remove_wall(direct)
            cell.path_str = Redarrow[direct.name].value
            cell = maze.get_cell(maze.add_pos(cell.get_pos(),
                                              direct.delta()))
            direct = direct.oppo()
            cell.remove_wall(direct)
            cell.path_str = Redarrow[direct.name].value


def main() -> None:
    maze = ""
    try:
        timer = {
            "create": 0,
            "patern": 0,
            "backtrack": 0,
            "binary_tree": 0,
            "wall_break": 0,
            "A*": 0,
            "show_path": 0
                }
        if True:
        #  for i in range(100):
            # maze = Maze(seed=870111)
            maze = Maze(seed=randint(0, 1000000))
            timer["create"] += spell_timer(maze.create)(
                maze.rng.randint(5, 20), maze.rng.randint(5, 20))[1]
            timer["patern"] += spell_timer(maze.patern_42)(
                int(maze.height / 3), int(maze.width / 3))[1]
            timer["binary_tree"] += spell_timer(maze.binary_tree)()[1]
            # timer["backtrack"] += spell_timer(maze.backtrack_algo)()[1]
            # timer["wall_break"] += spell_timer(wall_break)(maze)[1]
            solution = spell_timer(maze.parser_A)()
            timer["A*"] += solution[1]
            maze.solution = solution[0]
            print(repr(maze))
            timer["show_path"] += spell_timer(maze.show_path)(0)[1]
            # print_maze(maze)
        print(timer, file=stderr)
    except Exception:
        print(repr(maze))
        raise

    # print(maze)


if __name__ == "__main__":
    main()

