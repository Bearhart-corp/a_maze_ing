from abc import ABC, abstractmethod
from ..Enums import Direction
from typing import Generator
from ..Maze.Mazes import Maze


class Algo(ABC):
    def __init__(self, maze: Maze) -> None:
        self.algo = self.algo_generator(maze)
        self.perfect = False

    def next_frame(self) -> None:
        next(self.algo)

    def full_create(self) -> None:
        for _ in self.algo:
            continue

    @abstractmethod
    def algo_generator(self, maze: Maze) -> Generator[None, None, None]:
        pass


class BackTracking(Algo):
    """args = maze
    carve the walls of the cells with a backtrack strategy
    return None"""
    def __init__(self, maze: Maze) -> None:
        super().__init__(maze)
        self.perfect = True

    def algo_generator(self, maze: Maze) -> Generator[None, None, None]:
        yield None
        stack = [maze.start]
        while stack:
            act_pos = stack[-1]
            available_dir = []
            for direct in Direction:
                pos = maze.add_pos(direct.delta(), act_pos)
                if (maze.is_in_bound(pos)):
                    neighbord = maze.get_cell(pos)
                    if (not neighbord.is_visited
                            and not neighbord.blocked):
                        available_dir.append(direct)
            if available_dir:
                goal = maze.rng.choice(available_dir)
                maze.get_cell(act_pos).remove_wall(goal)
                stack.append(maze.add_pos(act_pos, goal.delta()))
                maze.get_cell(stack[-1]).remove_wall(goal.oppo())
                yield None
            else:
                stack.pop()


class BinaryTree(Algo):
    """args = maze
    carve the walls of the cells with a binary strategy
    Ret None"""
    def __init__(self, maze: Maze) -> None:
        super().__init__(maze)
        self.perfect = True

    def algo_generator(self, maze: Maze) -> Generator[None, None, None]:
        yield None
        for x in range(maze.height):
            for y in range(maze.width):
                if maze.get_cell((x, y)).blocked:
                    continue
                possibility = self.get_possibility((x, y), maze)
                if (x == ((maze.height - 5) // 2) + 3
                        and y == ((maze.width - 8) // 2) + 8):
                    maze.get_cell((x, y - 1)).remove_wall(Direction.EAST)
                    maze.get_cell((x, y)).remove_wall(Direction.WEST)
                    maze.get_cell((x, y)).remove_wall(Direction.NORTH)
                    maze.get_cell((x - 1, y)).remove_wall(Direction.SOUTH)
                    yield None
                    continue
                if possibility:
                    d = maze.rng.choice(possibility)
                    prev_cell__coor = maze.add_pos((x, y), d.delta())
                    prev_cell = maze.get_cell(prev_cell__coor)
                    cell = maze.get_cell((x, y))
                    cell.is_visited = True
                    cell.remove_wall(d)
                    prev_cell.remove_wall(d.oppo())
                    yield None

    def get_possibility(self, act_pos: tuple, maze: Maze) -> list[Direction]:
        """Args = current position as a tuple and the maze
            Get the directions N or/and W if the cell in the choosen direction
            is in the maze and not in the 42
            return a list of directions"""
        neighbords = []
        dir = [Direction.NORTH, Direction.WEST]
        for d in dir:
            pos = maze.add_pos(d.delta(), act_pos)
            cell = maze.get_cell(pos)
            if (maze.is_in_bound(pos)
                    and not cell.blocked):
                neighbords.append(d)
        return neighbords


class HuntNKill(Algo):
    """args = maze
    carve the walls of the cells with a hunter strategy
    Return None"""
    def __init__(self, maze: Maze) -> None:
        super().__init__(maze)
        self.perfect = True

    def algo_generator(self, maze: Maze) -> Generator[None, None, None]:
        yield None
        act_pos = maze.start
        maze.get_cell(act_pos).is_visited = True
        flag = True
        while flag:
            dir = maze.get_valid_neighbords(act_pos)
            if dir:
                d: Direction = maze.rng.choice(dir)
                next_pos = maze.add_pos(act_pos, d.delta())
                maze.get_cell(act_pos).remove_wall(d)
                maze.get_cell(next_pos).remove_wall(d.oppo())
                yield None
                act_pos = next_pos
            else:
                flag = False
                for x in range(maze.width):
                    for y in range(maze.height):
                        if (not maze.get_cell((y, x)).blocked
                                and not maze.get_cell((y, x)).is_visited):
                            neig = self.hunt_the_next((y, x), maze)
                            if neig:
                                flag = True
                                next_cell = maze.get_cell(
                                    maze.add_pos((y, x), neig.delta()))
                                next_cell.remove_wall(neig.oppo())
                                maze.get_cell((y, x)).remove_wall(neig)
                                act_pos = (y, x)
                                break
                    if flag:
                        break

    def hunt_the_next(self, act_pos: tuple, maze: Maze) -> Direction | None:
        """Args = current position as a tuple and the maze
        if the cell is in the maze, visited and not in the 42 pattern
        we pick it up
        Return a direction if he found one"""
        for dir in Direction:
            pos = maze.add_pos(dir.delta(), act_pos)
            if maze.is_in_bound(pos):
                if (maze.get_cell(pos).is_visited
                        and not maze.get_cell(pos).blocked):
                    return dir
        return None

    def get_possibility(self, act_pos: tuple, maze: Maze) -> list[Direction]:
        """Args = current position as a tuple and the maze
        Get the possible directions, conditions for possible are:
        inside of the maze and not in the 42 pattern
        Return a list of the possible directions"""
        neighbords = []
        dir = [Direction.NORTH, Direction.WEST]
        for d in dir:
            pos = maze.add_pos(d.delta(), act_pos)
            cell = maze.get_cell(pos)
            if (maze.is_in_bound(pos)
                    and not cell.blocked):
                neighbords.append(d)
        return neighbords


class Prims(Algo):
    """args = maze
    carve the walls of the cells with a wave strategy
    return None"""
    def __init__(self, maze: Maze):
        super().__init__(maze)
        self.perfect = True

    def algo_generator(self, maze: Maze) -> Generator[None, None, None]:
        yield None
        act_pos = maze.start
        frontier = {}
        maze.get_cell(act_pos).is_visited = True
        dirs = maze.get_valid_neighbords(act_pos)
        for d in dirs:
            neig = maze.add_pos(act_pos, d.delta())
            frontier[neig] = True
        while frontier:
            pos = maze.rng.choice(list(frontier.keys()))
            maze.get_cell(pos).is_visited = True
            dirs = maze.get_valid_neighbords(pos)
            for d in dirs:
                neig = maze.add_pos(pos, d.delta())
                frontier[neig] = True
            dir = self.get_frontier(pos, maze)
            if dir:
                maze.get_cell(pos).remove_wall(dir)
                pos2: tuple = maze.add_pos(pos, dir.delta())
                maze.get_cell(pos2).remove_wall(dir.oppo())
                yield None
            del frontier[pos]

    def get_frontier(self, act_pos: tuple, maze: Maze) -> Direction | None:
        """Args = current position as a tuple and the maze.
        Get the visited neigbords with a wall in commune with the 
        current cell
        Return a direction if he found one"""
        possibility = []
        for d in Direction:
            pos = maze.add_pos(d.delta(), act_pos)
            if maze.is_in_bound(pos):
                cell = maze.get_cell(pos)
                if (not cell.blocked and cell.is_visited):
                    possibility.append(d)
        if possibility:
            return maze.rng.choice(possibility)
        return None
