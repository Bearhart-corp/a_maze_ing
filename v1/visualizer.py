from mlx import Mlx
from Mazes import Maze
from Enums import Direction

def draw_line(mlx: tuple[Mlx, int, int], x, y, width, color):
    for x_offset in range(width):
        # print(f"drawing pixel at {x+x_offset} {y}")
        mlx[0].mlx_pixel_put(mlx[1], mlx[2], x + x_offset, y,color)

def draw_rectangle(mlx: tuple[Mlx, int, int], x, y, width, height, color):
    for y_offset in range(height):
        draw_line(mlx, x, y + y_offset, width, color)

def draw_cell(mlx: tuple[Mlx, int, int], walls, x, y):
    cell = mlx[0].mlx_new_image(mlx[1], 200, 200)

    addr, bpp, line_len, endian = mlx[0].mlx_get_data_addr(cell)
    print("\n".join([str(addr), str(bpp), str(line_len), str(endian)]))
    # Draw white square
    for y__ in range(0, 200):
        for x__ in range(0, 200):
            offset = y__ * line_len + x__ * (bpp // 8)
            color = 0x00
            for a in range(4):
                addr[offset + a] = color
    for y__ in range(0, 50):
        for x__ in range(0, 50):
            offset = y__ * line_len + x__ * (bpp // 8)
            color = 0xFF
            for a in range(4):
                addr[offset + a] = color
    mlx[0].mlx_put_image_to_window(mlx[1], mlx[2], cell, x, y)

def quit(mlx):
    mlx[0].mlx_destroy_window(mlx[1], mlx[2])
    mlx[0].mlx_loop_exit(mlx[1])


def mouse_handler(button, x, y, mystuff):
    print(f"mouse is at {x}, {y}")

def key_handler(key, args):
    mlx = args[1]
    if key == 32:
        quit(mlx)

def print_maze(maze: Maze):
    m = Mlx()
    mlx_ptr = m.mlx_init()
    win_ptr = m.mlx_new_window(mlx_ptr, 500, 500, "toto")
    # draw_cell((m, mlx_ptr, win_ptr), 15, 5, 5)
    draw_cell((m, mlx_ptr, win_ptr), 50, 200, 200)
    m.mlx_mouse_hook(win_ptr, mouse_handler, "")
    m.mlx_key_hook(win_ptr, key_handler, ((m.mlx_mouse_get_pos, mlx_ptr), (m, mlx_ptr, win_ptr)))
    m.mlx_hook(win_ptr, 33, 0, quit, (m, mlx_ptr, win_ptr))
    m.mlx_loop(mlx_ptr)
    print("hi")

if __name__ == "__main__":
    print_maze("a")
