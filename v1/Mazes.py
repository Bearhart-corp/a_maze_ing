from typing import List, Tuple, Callable
from Cells import Cell
from Enums import Direction, Arrow
from random import Random
from time import sleep, time


class Maze:
    def __init__(self, seed: float | None = None) -> None:
        self.cells: List[List[Cell]] = []
        self.solution: List[tuple[int, int]] = []
        if seed is None:
            self.seed = time()
        else:
            self.seed = seed
        self.rng = Random(self.seed)
        self.context = {}
        self.start = (0, 0)
        self.end = (0, 0)

    def get_cell(self, coord: tuple[int, int]) -> Cell:
        return self.cells[coord[0]][coord[1]]

    def create(self, height: int, width: int) -> None:
        self.width = width
        self.height = height
        if width <= 1 and height <= 1:
            raise ValueError("a maze cannot be 1 cell alone")
        for y in range(height):
            self.cells.append([Cell(x, y) for x in range(width)])
        self.create_exterior_wall()

    def create_exterior_wall(self):
        for x in range(self.width):
            self.cells[0][x].set_border(Direction.NORTH)
            self.cells[-1][x].set_border(Direction.SOUTH)
        for y in range(self.height):
            self.cells[y][0].set_border(Direction.WEST)
            self.cells[y][-1].set_border(Direction.EAST)

    def add_pos(self, pos1: tuple[int, int],
                pos2: tuple[int, int]) -> tuple:
        return tuple(a + b for a, b in zip(pos1, pos2))

    def is_in_grid(self, pos: tuple[int, int]):
        return (pos[0] >= 0 and pos[0] < self.height
                and pos[1] >= 0 and pos[1] < self.width)

    def backtrack_algo(self, start: tuple[int, int] | None = None):
        if start is None:
            self.start = self.random_cell(predicate=Cell.is_border).get_pos()
        self.end = self.random_cell(predicate=Cell.is_border).get_pos()
        move_list = [self.start]
        while move_list:
            possible = [a for a in Direction]
            while possible:
                goal = self.rng.choice(possible)
                actual_cell = self.get_cell(move_list[-1])
                next_pos = self.add_pos(move_list[-1], goal.delta())
                if (self.is_in_grid(next_pos)
                        and not self.get_cell(next_pos).is_open()
                        and not actual_cell.wall_state(goal) == 2):
                    actual_cell.remove_wall(goal)
                    self.get_cell(next_pos).remove_wall(goal.oppo())
                    move_list.append(next_pos)
                    break
                else:
                    possible.remove(goal)
            if not possible:
                move_list.pop()
        for row in self.cells:
            for cell in row:
                cell.update_str_rows()

    def binary_tree(self, start: tuple[int, int] | None = None):
        for i in range(self.height):
            for j in range(self.width):
                if j == 0:
                    rand = Direction.NORTH
                elif i == 0:
                    rand = Direction.WEST
                else:
                    rand = self.rng.choice((Direction.NORTH, Direction.WEST))
                goal = Direction.delta(rand)
                actual_cell = self.get_cell((i, j))
                next_pos = self.add_pos((i, j), goal)
                next_cell = self.get_cell(next_pos)
                actual_cell.remove_wall(rand)
                next_cell.remove_wall(Direction.oppo(rand))
        for row in self.cells:
            for cell in row:
                cell.update_str_rows()

    def show_path(self, wait_per_frame):
        print("\33[2J")
        self.get_cell(self.solution[0]).path_str = Arrow.START.value
        self.get_cell(self.solution[0]).need_update = True
        self.get_cell(self.solution[-1]).path_str = Arrow.WIN.value
        self.get_cell(self.solution[-1]).need_update = True
        if len(self.solution) <= 2:
            print(self)
        for pos, pos_next in zip(self.solution[1:], self.solution[2:]):
            diff = (pos_next[0] - pos[0], pos_next[1] - pos[1])
            direction = next(d for d in Direction if d.delta() == diff)
            self.cells[pos[0]][pos[1]].path_str = Arrow[direction.name].value
            self.cells[pos[0]][pos[1]].need_update = True
            if wait_per_frame:
                sleep(wait_per_frame)
                print("\33[H", self, sep="")
        if not wait_per_frame:
            print(self)
        for pos in self.solution:
            self.get_cell(pos).path_str = "  "

    def reset_maze(self):
        for row in self.cells:
            for cell in row:
                cell.walls = 15
        self.start = (0, 0)
        self.end = (0, 0)
        self.rng = Random(self.rng.randint(0, 1000))
        self.cells.clear()
        self.create_exterior_wall()

    def get_neighbors(self, cell: Cell) -> List[Tuple[Cell, Direction]]:
        neighbors = []
        y, x = cell.y, cell.x
        for direction in Direction:
            dy, dx = direction.delta()
            ny, nx = y + dy, x + dx

            if 0 <= ny < self.height and 0 <= nx < self.width:
                neighbors.append((self.cells[ny][nx], direction))
        return neighbors

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

    def apply_pattern(self, coords):
        coord_set = set(coords)

        for y, x in coord_set:
            cell = self.cells[y][x]
            cell.path_str = "@@"
            for direction in Direction:
                cell.set_border(direction)
            for neighbor, direction in self.get_neighbors(cell):
                if (neighbor.y, neighbor.x) not in coord_set:
                    neighbor.set_border(direction.oppo())

    def random_cell(self, predicate: None | Callable = None):
        candidate = self.rng.choice(self.rng.choice(self.cells))
        if predicate is None:
            return candidate
        else:
            while predicate(candidate):
                candidate = self.rng.choice(self.rng.choice(self.cells))
            return (candidate)

    # def __str__(self) -> str:
    #     final = ""
    #     for y in range(self.height):
    #         row = ["", "", ""]
    #         for x in range(self.width):
    #             curr_cell = str(self.cells[y][x]).splitlines()
    #             for i, cell_row in enumerate(curr_cell):
    #                 row[i] += cell_row
    #         final += "\n".join(row) + "\n"
    #     return (final)

    def __str__(self) -> str:
        lines = []
        for y in range(self.height):
            row_lines = ["", "", ""]
            for x in range(self.width):
                curr_cell_lines = str(self.cells[y][x]).splitlines()
                for i in range(3):
                    row_lines[i] += curr_cell_lines[i]
            lines.extend(row_lines)
        return "\n".join(lines)

    def __repr__(self) -> str:
        return (f"width = {self.width}\n"
                f"height = {self.height}\n"
                f"start = {self.start}\n"
                f"end = {self.end}\n"
                f"solution = {self.solution} len = {len(self.solution)}\n"
                f"seed = {self.seed}\n"
                f"context ={self.context}\n" +
                '\n'.join(' '.join(f'{repr(cell)}'for cell in row)
                          for row in self.cells))

    def hexa(self):
        return '\n'.join(' '.join(f'{repr(cell)}'for cell in row)
                         for row in self.cells)

    def abs_dist(self, pos1: tuple[int, int], pos2: tuple[int, int]):
        return (abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1]))

    def parser_bfs(self):
        rank: List[List[int]] = [[1000 for width in range(self.width)]
                                 for height in range(self.height)]
        rank[self.start[0]][self.start[1]] = 0
        queue = [self.add_pos(self.start, direct.delta())
                 for direct in Direction
                 if self.get_cell(self.start).wall_state(direct) == 0]
        while True:
            y, x = min(queue,
                       key=lambda pos: self.abs_dist(
                           pos, self.end) + rank[pos[0]][pos[1]])
            base = self.get_cell((y, x))
            valid_neighbor = [self.add_pos((y, x), direct.delta())
                              for direct in Direction
                              if base.wall_state(direct) == 0]
            prec = rank[y][x]
            maxi = min(valid_neighbor,
                       key=lambda neigbor: rank[neigbor[0]][neigbor[1]])
            rank[y][x] = max(0, rank[maxi[0]][maxi[1]]) + 1
            queue.remove((y, x))
            if prec != rank[y][x]:
                queue.extend([valid for valid
                              in valid_neighbor
                              if (rank[valid[0]][valid[1]] > rank[y][x] + 1
                                  or rank[valid[0]][valid[1]] == -1)])
            # print("\33[2J")
            # print("\33[H", "\n\n".join(" ".join(f'{cell:5}'for cell in row)
            #       for row in rank), sep="")
            # sleep(0.2)
            if rank[self.end[0]][self.end[1]] != 1000:
                break
        pos = self.end
        solution = [pos]

        while (rank[pos[0]][pos[1]]):
            pos = [self.add_pos(pos, direct.delta()) for direct in Direction
                   if self.get_cell(pos).wall_state(direct) == 0
                   and rank[self.add_pos(pos, direct.delta())[0]][self.add_pos(
                       pos, direct.delta())[1]] == rank[pos[0]][pos[1]] - 1][0]
            solution.append(pos)
        solution.reverse()
        return solution

    def parser_A(self):
        rank: List[List[int]] = [[-1 for width in range(self.width)]
                                 for height in range(self.height)]
        rank[self.start[0]][self.start[1]] = 0
        queue = [self.start]
        while queue:
            base_y, base_x = min(queue,
                                 key=lambda pos: self.abs_dist(
                                    pos, self.end) + rank[pos[0]][pos[1]])
            base = self.get_cell((base_y, base_x))
            queue.remove((base_y, base_x))
            if (base_y, base_x) == self.end:
                break
            for neighbor, direct in self.get_neighbors(base):
                neighbor_y, neighbor_x = neighbor.get_pos()
                if (base.wall_state(direct) == 0
                        and (rank[neighbor_y][neighbor_x] >
                             rank[base_y][base_x] + 1
                             or rank[neighbor_y][neighbor_x] == -1)):
                    rank[neighbor_y][neighbor_x] = rank[base_y][base_x] + 1
                    queue.append((neighbor_y, neighbor_x))
            # print("\33[2J")
            # print("\33[H", "\n\n".join(" ".join(f'{cell:5}'for cell in row)
            #       for row in rank), sep="")
            # sleep(wait_per_frame)
        solution = [self.end]
        while (rank[solution[-1][0]][solution[-1][1]]):
            current = self.get_cell(solution[-1])
            current_rank = rank[solution[-1][0]][solution[-1][1]]
            for neighbor, direct in self.get_neighbors(current):
                neighbor_y, neighbor_x = neighbor.get_pos()
                neighbor_rank = rank[neighbor_y][neighbor_x]
                if (current.wall_state(direct) == 0
                        and neighbor_rank == current_rank - 1):
                    solution.append(neighbor.get_pos())
                    break
        solution.reverse()
        # print("\33[2J")
        # print("\33[H", "\n\n".join(" ".join(f'{cell:5}'for cell in row)
        #       for row in rank), sep="")
        # for row in self.cells:
        #     for cell in row:
        # cell.path_str = f"{rank[cell.get_pos()[0]][cell.get_pos()[1]]:2d}"
        #         cell.need_update = True
        return solution

    def parser(self, pos, end, dist_traveled, min_known, prec):
        path = [pos]
        best_subpath = []
        while (pos != end and dist_traveled <= min_known
                and self.abs_dist(pos, end) <= min_known - dist_traveled):
            possible = [direct for direct in Direction
                        if self.get_cell(pos).wall_state(direct) == 0
                        and direct != prec]
            if len(possible) == 0:
                return None
            elif len(possible) == 1:
                dist_traveled += 1
                pos = self.add_pos(pos, possible[0].delta())
                path.append(pos)
                prec = possible[0].oppo()
            else:
                dist_traveled += 1
                for sub_path in possible:
                    child_path = self.parser(self.add_pos(
                                             pos, sub_path.delta()
                                             ),
                                             end,
                                             dist_traveled,
                                             min_known,
                                             sub_path.oppo())
                    if (child_path is not None
                            and min_known >= dist_traveled + len(child_path)):
                        min_known = len(child_path) + dist_traveled
                        best_subpath = child_path
                break
        if path[-1] == end or (best_subpath and best_subpath[-1] == end):
            return path + best_subpath
        else:
            return None
