from .Maze.Mazes import Maze
from .Maze_config import MazeConfig
from .Algo.Algos import (
                   BackTracking,
                   BinaryTree,
                   HuntNKill,
                   Prims
                   )
from sys import stderr
from typing import Optional


class MazeGenerator:
    """apply the configs and apply"""
    ALGO_DICT = {
                "binarytree": BinaryTree,
                "backtracking": BackTracking,
                "huntnkill": HuntNKill,
                "prims": Prims
            }

    def __init__(self,
                 path_to_config: Optional[str] = None,
                 config_text: Optional[str] = None):
        if path_to_config:
            self.from_file(path_to_config)
        elif config_text:
            self.from_text(config_text)
        else:
            raise ValueError("MazeGeneratot must have a config")

    def from_text(self, text: str) -> None:
        """set the config"""
        self.config = MazeConfig.from_config(text)
        self.setup_config()

    def from_file(self, path_to_config: str) -> None:
        """set the config from a file"""
        with open(path_to_config, "r") as config_file:
            config_text = config_file.read()
        self.config = MazeConfig.from_config(config_text)
        self.setup_config()

    def setup_config(self) -> None:
        """set up the config"""
        self.maze: Maze = Maze(self.config)
        self.output_file = self.config.OUTPUT_FILE
        try:
            if self.config.ALGO is not None:
                self.algo = self.ALGO_DICT[self.config.ALGO](
                    self.maze)
            else:
                print("algo name not specified,"
                      " defaulting to backtracking algo", file=stderr)
                self.algo = BackTracking(self.maze)
        except KeyError:
            print("error while parsing algo name,"
                  " defaulting to backtracking algo", file=stderr)
            self.algo = BackTracking(self.maze)
        if not self.algo.perfect and self.config.PERFECT:
            print("chosen algo is not assured to create perfect maze,"
                  " defaulting to backtracking algo", file=stderr)
            self.algo = BackTracking(self.maze)

    @staticmethod
    def verify_config(config: str) -> bool:
        """args = config path.
        verify the config"""
        try:
            maze_config = MazeConfig.from_config(config)
        except Exception:
            return False
        if maze_config.ALGO not in MazeGenerator.ALGO_DICT:
            return False
        return True

    def launch_algo(self) -> None:
        """apply the modifications"""
        if self.maze.anim_finished:
            return
        elif self.maze.anim:
            try:
                self.algo.next_frame()
            except StopIteration:
                self.maze.parser_A()
                self.maze.anim_finished = True
        else:
            self.algo.full_create()
            self.maze.parser_A()
            self.maze.anim_finished = True
