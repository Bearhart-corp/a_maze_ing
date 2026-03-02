from mlx import Mlx
from Enums import Direction
from Mazes import Maze
from Maze_config import MazeConfig
from time import time
from typing import Iterator
from font import Ascii

class Color:
    def __init__(self, value):
        """
        value: either an int (ARGB) or a callable returning int
        """
        # if not (callable(value) or isinstance(value, int)):
        #     raise TypeError("Color must be an int or a callable returning int")
        self.value: int | Iterator = value

    def get(self) -> int:
        if isinstance(self.value, int):
            return self.value
        return next(self.value)

    def __int__(self):
        return self.get()

    def __call__(self):
        return self.get()

    def __repr__(self):
        return f"Color({self.get()})"


class Image:
    def __init__(self, image, mlx: Mlx, color: Color) -> None:
        self.mlx = mlx
        self.image = image
        self.addr, self.bpp, self.line_len, self.endian = (
            mlx.mlx_get_data_addr(image))
        self.u_addr = self.addr.cast('I')
        self.height = len(self.u_addr) // (self.line_len / (self.bpp / 8))
        self.width = len(self.u_addr) // self.height
        self.fill_image(color)

    
    def update_cell_size(self, x, y):
        self.hpc = self.height // y
        self.wpc = self.width // x
        # print("\033[32m", f"{self.height=}, {len(self.u_addr)=}in update size")
        # print(f"{self.width=}, {len(self.u_addr)=}in update size")
        # print(f"{y=}, {x=}, {self.wpc=}, {self.hpc=}, in update size", "\033[0m")

    def fill_image(self, color: Color):
        for i in range(len(self.u_addr)):
            self.u_addr[i] = color.get()

    def put_pixel(self, x, y, color: Color):
        self.u_addr[(y * self.line_len //
                    (self.bpp // 8)) + x] = color.get()

    def draw_line(self, x, y, width, color: Color):
        offset = (y * self.line_len //
                  (self.bpp // 8)) + x
        for x_offset in range(width):
            self.u_addr[offset + x_offset] = color.get()

    def draw_rectangle(self, x, y, width, height, color: Color):
        for y_offset in range(height):
            self.draw_line(x, y + y_offset, width, color)

    def draw_char(self, x, y, char, color: Color, scale=1):
        glyph = Ascii.get(ord(char))
        if not glyph:
            return
        for row in range(8):
            bits = glyph[row]
            for col in range(8):
                if bits & (1 << (7 - col)):
                    for dy in range(scale):
                        for dx in range(scale):
                            self.put_pixel(
                                x + col * scale + dx,
                                y + row * scale + dy,
                                color
                            )


class Window:
    FPS = 15

    def __init__(self, width: int, height: int,
                 name: str, generator: MazeConfig):
        self.mlx = Mlx()
        self.mlx_ptr = self.mlx.mlx_init()
        self.win_ptr = self.mlx.mlx_new_window(
            self.mlx_ptr, width, height, name)
        self.maze_image = Image(
            self.mlx.mlx_new_image(self.mlx_ptr, width, height - 80),
            self.mlx,
            Color(0xff_00_00_00))
        self.text_image = Image(
            self.mlx.mlx_new_image(self.mlx_ptr, width, 80),
            self.mlx,
            Color(0xff_80_80_80))
        self.rain = rainbow(0x80_80_80)
        self.color = next(self.rain) + 0xff_00_00_00
        self.height = height
        self.width = width
        self.generator = generator
        self.last_frame = 0
        self.typed_text = ""
        self.paused = False
        self.init_hook()

    def init_hook(self):
        self.mlx.mlx_key_hook(self.win_ptr, self.key_handler, None)
        self.mlx.mlx_hook(self.win_ptr, 33, 0, self.quit, None)
        self.mlx.mlx_loop_hook(self.mlx_ptr, self.step, None)

    def start(self):
        self.start_maze()
        # self.last_frame = time()
        self.forced_step()
        self.mlx.mlx_loop(self.mlx_ptr)

    def start_maze(self):
        self.maze: Maze = Maze(self.generator.get_arg("config.txt"))
        self.prec_maze = ("\n".join("".join("_" for i in range(self.maze.width))
                                    for j in range(
                                        self.maze.height))).splitlines()

    def step(self, *_):
        if (time() > self.last_frame + (1 / self.FPS)
            and not self.maze.anim_finished
                and not self.paused):
            self.maze.launch_algo()
            self.update_display()


    def forced_step(self):
        if self.paused:
            self.paused = False
            self.step()
            self.paused = True

    def update_display(self):
        self.text_image.fill_image(Color(0xff_80_80_80))
        self.draw_maze()
        self.draw_text(
            0,
            0,
            "\n".join(["press escape to leave",
                        "press space to pause",
                        "press 'n' to go to next maze",
                        "faefaf",
                        "aadasad"]),
            Color(0xff_00_00_00),
            scale=2)
        self.draw_text(600, 0, self.typed_text, Color(0xff_00_00_00), scale=2)
        self.last_frame = time()
    ###########################################

    def quit(self, *_):
        self.mlx.mlx_destroy_image(self.mlx_ptr, self.text_image.image)
        self.mlx.mlx_destroy_image(self.mlx_ptr, self.maze_image.image)
        self.mlx.mlx_destroy_window(self.mlx_ptr, self.win_ptr)
        self.mlx.mlx_loop_exit(self.mlx_ptr)
        # if not self.maze.anim_finished:
        #     self.maze.anim = False
        #     self.maze.launch_algo()
        with open("output.txt", "w") as output:
            output.write(self.maze.hexa())

    def change_color(self):
        for i in range(325):
            next(self.rain)
        self.color = next(self.rain) + 0xff_00_00_00
        self.prec_maze = ("\n".join("".join("_" for i in range(self.maze.width))
                                    for j in range(
                                        self.maze.height))).splitlines()
        self.update_display()

    def key_handler(self, key, *_):
        if key == 65307:  # 'echap'
            self.quit()
        elif key == 110:  # 'n'
            self.start_maze()
            self.typed_text = ""
            self.forced_step()
        elif key == 65363:  # '➡'
            self.forced_step()
        elif key == 32:  # 'espace'
            self.paused = [True, False][self.paused]
        elif key == 99:
            self.change_color()
        else:
            if self.paused:
                if self.typed_text.__len__() < 50:
                    self.typed_text += (str(key))
                    self.draw_text(
                        600,
                        0,
                        self.typed_text,
                        Color(0xff_00_00_00),
                        scale=2)
            else:
                print(key)
    ###########################################

    def draw_maze(self):
        self.maze_image.update_cell_size(self.maze.height,
                                         self.maze.width)
        maze_hexa = self.maze.hexa().splitlines()
        for y in range(self.maze.height):
            for x in range(self.maze.width):
                if self.prec_maze[y][x] != maze_hexa[y][x]:
                    self.draw_cell(
                               x,
                               y,
                               Color(self.color),
                               Color(0xff_00_00_00))
        self.prec_maze = maze_hexa
        self.mlx.mlx_put_image_to_window(self.mlx_ptr, self.win_ptr,
                                         self.maze_image.image, 0, 0)

    def draw_cell(self, x, y, cell_color, background_color):
        if self.maze.cells[y][x].blocked:
            self.maze_image.draw_rectangle(
                round(x * self.maze_image.wpc),
                round(y * self.maze_image.hpc),
                round(self.maze_image.wpc),
                round(self.maze_image.hpc),
                cell_color)
            return None

        for direct in Direction:
            if not self.maze.cells[y][x].walls & direct.value:
                x_off, y_off, width, height = direct.draw()
                x_off, y_off, width, height = (
                    round(x_off * self.maze_image.wpc),
                    round(y_off * self.maze_image.hpc),
                    round(width * self.maze_image.wpc),
                    round(height * self.maze_image.hpc)
                )
                self.maze_image.draw_rectangle(
                    round(x * self.maze_image.wpc) + x_off,
                    round(y * self.maze_image.hpc) + y_off,
                    width,
                    height,
                    background_color)

        for direct in Direction:
            if self.maze.cells[y][x].walls & direct.value:
                x_off, y_off, width, height = direct.draw()
                x_off, y_off, width, height = (
                    round(x_off * self.maze_image.wpc),
                    round(y_off * self.maze_image.hpc),
                    round(width * self.maze_image.wpc),
                    round(height * self.maze_image.hpc)
                )
                self.maze_image.draw_rectangle(
                    round(x * self.maze_image.wpc) + x_off,
                    round(y * self.maze_image.hpc) + y_off,
                    width, height, cell_color)

    def draw_text(self, x, y, text: str, color: Color, scale=1):
        original_x = x
        for ch in text:
            if y + (8 * scale) > self.text_image.height:
                break
            self.text_image.draw_char(x, y, ch, color, scale)
            x += 8 * scale
            if x + (8 * scale) > self.text_image.width or ch == "\n":
                x = original_x
                y += 10*scale
        self.mlx.mlx_put_image_to_window(
            self.mlx_ptr,
            self.win_ptr,
            self.text_image.image, 
            0,
            self.height - 80)
    ###########################################


def rainbow(var):   # 0x00ff00 best start with green
    """create a fade of RGB"""
    for j in range(256):
        mask = (j % 3) << 3
        for i in range(256):
            end = var ^ (i << mask)
            yield end
        var = end


