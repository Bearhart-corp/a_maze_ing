from enum import Enum
import random
import time

class Dir(Enum):
    N = 0b00001
    E = 0b00010
    S = 0b00100
    W = 0b01000
    # V = 0b10000

def dir_oppo(dir: Dir) -> Dir:
    return {
        Dir.S: Dir.N,
        Dir.W: Dir.E,
        Dir.N: Dir.S,
        Dir.E: Dir.W
    }[dir]

def take_dir(dir: Dir, pos: tuple) -> tuple:
    delta = {
        Dir.N: (-1, 0),
        Dir.E: (0, 1),
        Dir.S: (1, 0),
        Dir.W: (0, -1)
    }
    x, y = delta[dir]
    return (pos[0] + x, pos[1] + y)

def in_grid(pos: tuple, width: int, height: int) -> bool:
    x, y = pos
    if x < 0 or y < 0:
        return False
    if x >= height or y >= width:
        return False
    return True

def init_maze(width: int, height: int) -> list:
    array = []
    for i in range(width):
        array.append([])
        for j in range(height):
            array[i].append(0xf)
    return array

def is_visited(maze: list[list[tuple]], pos: tuple) -> bool:
    return (get_cell(maze, pos) & 16)

def rm_wall(maze, dir: Dir, pos: tuple) -> None:
    maze[pos[0]][pos[1]] &= ~dir.value

def set_visited(pos: tuple, maze: list[list[tuple]]) -> None:
    maze[pos[0]][pos[1]] |= 16

def add_wall(cell: int, dir: Dir) -> int:
    return (cell | Dir.value)

def get_neighbords(pos: tuple, maze: list[list[tuple]], w, h) -> list[Dir]:
    neighbords = []
    for dir in Dir:
        x = take_dir(dir, pos)
        if in_grid(x, w, h):
            if not is_visited(maze, x):
                neighbords.append(dir)
    return neighbords

def get_cell(maze: list[list[int]], pos: tuple) -> int:
    return maze[pos[0]][pos[1]]

def print_maze(maze, width: int, height: int, entry: tuple) -> None:
    t = [
        "  ",
        "  ",
        "  ",#2
        "←↓",
        "  ",#4
        "←→",
        "←↑",#6
        "← ",
        "  ",#8
        "↓→",
        "↑↓",#10
        " ↓",
        "↑→",#12
        "→ ",
        " ↑",
        "O "
    ]
    for i in range(height):
        for j in range(width):
            print(t[(maze[i][j]) & 0xf], end=" | ")
        print()

def print_hexa(maze, w, h):
    for i in range(h):
        for j in range(w):
            print(hex(maze[i][j]), end=" | ")
        print()

def create_maze(maze: list[list[int]], cur_coor: tuple, seed: int, w:int, h:int):
    rng = random.Random(seed)
    stack = []
    neig: list[Dir] = get_neighbords(cur_coor, maze, w, h)
    while len(neig) > 0:
        set_visited(cur_coor, maze)
        stack.append(cur_coor)
        neig: list[Dir] = get_neighbords(cur_coor, maze, w, h)
        if len(neig) > 0:
            next_dir: Dir = rng.choice(neig)
        else:
            while len(stack) > 0:
                cur_coor = stack.pop()
                neig: list[Dir] = get_neighbords(cur_coor, maze, w, h)
                if len(neig) > 0:
                    next_dir: Dir = rng.choice(neig)
                    break
        next_coor: tuple = take_dir(next_dir, cur_coor)
        rm_wall(maze, next_dir, cur_coor)
        rm_wall(maze, dir_oppo(next_dir), next_coor)
        cur_coor = next_coor

def backtrack(maze: list[list[int]], cell: tuple, rng: random, w:int, h:int) -> None:
    set_visited(cell, maze)
    directions = get_neighbords(cell, maze, w, h)
    rng.shuffle(directions)
    for d in directions:
        next_cell = take_dir(d, cell)
        if not is_visited(maze, next_cell):
            rm_wall(maze, d, cell)
            rm_wall(maze, dir_oppo(d), next_cell)
        backtrack(maze, next_cell, rng, w, h)

def printok(maze, w, h):
    arr = []
    j = 0
    for line in maze:
        for i in range(2):
            arr.append([])
            for cell in line:
                if i == 0:
                    arr[i + j].append("⬛")
                    if (cell & 1):
                        arr[i + j].append("⬛")
                    else:
                        arr[i + j].append("⬜")
                if i == 1:
                    if (cell & 8):
                        arr[i + j].append("⬛")
                    else:
                        arr[i + j].append("⬜")
                    arr[i + j].append("⬜")
            arr[i + j].append("⬛")
        j += 2
    for line in arr:
        for col in line:
            print(col, end="")
        print()   
    print("⬛" * ((2 * w) + 1))      

def main():
    seed = 41
    w = h = 20
    #maze = init_maze(w, h)
    #create_maze(maze, (0, 0), seed, w, h)
    rng = random.Random(seed)
    maze = init_maze(w, h)
    if w <= 1 or h <= 1:
        return
    backtrack(maze, (0, 0), rng, w, h)
    print_hexa(maze, w, h)
    printok(maze, w, h)


if __name__ == "__main__":
    main()
