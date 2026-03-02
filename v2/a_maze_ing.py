# from random import randint
# from Enums import Direction, Redarrow
# from sys import stderr
# from Utils import spell_timer
from visualizer import Window
from Maze_config import MazeConfig
from Mazes import Maze
from time import sleep
import random
import sys


def wall_break(maze):
    pass


def main() -> None:
    if len(sys.argv) <= 1:
        print("put the path of the configuration\n \
For exemple: config.txt")
        exit(1)
    path = sys.argv[1]
    try:
        config = MazeConfig.get_arg(path)
        visualizer = Window(1000, 1080, "maze", config)
        visualizer.start()
    except Exception as e:
        print(e)
    # for i in range(102):
    #     print("\33[2J")
    #     print(maze.hexa())
    #     maze.launch_algo()
    #     sleep(0.2)
    # window = Window(1000, 1050, "maze")
    # args = Parser.get_arg()
    # for i in range(100):
    #     maze = Maze(window, seed=randint(0, 1000000))
    #     maze.patern_42()
    #     maze.backtrack_algo()
    #     if maze.window.is_dead:
    #         print("Window died")
    #     else:
    #         window.print_maze(maze.cells)
    #         window.wait_loop()


if __name__ == "__main__":
    main()
