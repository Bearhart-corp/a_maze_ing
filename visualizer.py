from .mlx_CLXV.mlx.python.src.mlx.mlx import Mlx
from mazegen.Enums import Direction
from mazegen.MazeGenerator import MazeGenerator
from time import time
from typing import Iterator
from window.direction_translator import DrawDir
from window.font import Ascii
from window.Text_editor import TypedText
from typing import Optional, Callable


class Color:
    """set all the color values"""
    def __init__(self, value: int) -> None:
        """
        value: either an int (ARGB) or a callable returning int
        """
        self.value: int | Iterator[int] = value

    @staticmethod
    def rainbow(var: int) -> Iterator[int]:   # 0x00ff00 best start with green
        """create a fade of RGB"""
        end = 0  # to prevent norme error
        while True:
            for j in range(256):
                mask = (j % 3) << 3
                for i in range(256):
                    end = var ^ (i << mask)
                    yield end + 0xff_00_00_00
                var = end

    def get(self) -> int:
        """return the next color value"""
        if isinstance(self.value, int):
            return self.value
        return next(self.value)

    def __int__(self) -> int:
        """return the next color value"""
        return self.get()

    def __call__(self) -> int:
        """return the next color value"""
        return self.get()

    def __repr__(self) -> str:
        """return the color representation"""
        return f"Color({self.get()})"


class Image:
    """temporary buffer that can be pushed to window"""
    def __init__(self, image: int, mlx: Mlx, color: Color) -> None:
        self.mlx = mlx
        self.image = image
        self.addr, self.bpp, self.line_len, self.endian = (
            mlx.mlx_get_data_addr(image))
        self.u_addr = self.addr.cast('I')
        self.height = len(self.u_addr) // (self.line_len // (self.bpp // 8))
        self.width = len(self.u_addr) // self.height
        self.fill_image(color)

    def update_cell_size(self, x: int, y: int) -> None:
        """update the pixel ratio"""
        self.hpc = self.height // y
        self.wpc = self.width // x

    def fill_image(self, color: Color) -> None:
        """filled the buffer with the given color"""
        for i in range(len(self.u_addr)):
            self.u_addr[i] = color.get()

    def put_pixel(self, x: int, y: int, color: Color) -> None:
        """set up a given pixel,
        extremely expansive due to coordinate calculation"""
        self.u_addr[(y * self.line_len //
                    (self.bpp // 8)) + x] = color.get()

    def draw_line(self, x: int, y: int, width: int, color: Color) -> None:
        """draw horizontal line between (x, y) + a width offset,
         with the given color"""
        offset = (y * self.line_len //
                  (self.bpp // 8)) + x
        for x_offset in range(width):
            self.u_addr[offset + x_offset] = color.get()

    def draw_rectangle(self, x: int, y: int, width: int,
                       height: int, color: Color) -> None:
        """draw a rectangle at the given coordinates"""
        for y_offset in range(height):
            self.draw_line(x, y + y_offset, width, color)

    def draw_char(self, x: int, y: int, char: str, color: Color,
                  scale: int = 1) -> None:
        """args = position, char and its colors,
        draw into the buffer the bitmap of the given char"""
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
    """window manager"""
    FPS = 60
    MENU_TEXT = (
        "'escape' to leave\n"
        "'space' to pause and edit config\n"
        "   (right enter to step)\n"
        "'n' to go to the configured maze\n"
        "'c' to toggle color\n"
        "'.' to finish maze animation\n\n")
    BLACK = Color(0xff_00_00_00)
    PATERN_COLOR = Color(0xff_30_30_FF)
    WIN_COLOR = Color(0xff_30_A0_30)

    def __init__(self, width: int, height: int,
                 name: str,
                 path_to_config: str) -> None:
        if width < 20 or height < 20:
            raise ValueError("a window cannot be that smaller "
                             "than 20 pixel in any direction")
        self.mlx = Mlx()
        self.mlx_ptr = self.mlx.mlx_init()
        self.win_ptr = self.mlx.mlx_new_window(
            self.mlx_ptr, width, height+160, name)
        self.maze_image = Image(
            self.mlx.mlx_new_image(self.mlx_ptr, width, height),
            self.mlx,
            Color(0xff_00_00_00))
        self.text_image = Image(
            self.mlx.mlx_new_image(self.mlx_ptr, width, 160),
            self.mlx,
            Color(0xff_80_80_80))
        self.generator = MazeGenerator(path_to_config)
        self.config_path = path_to_config
        ############
        self.rain = Color.rainbow(0x00_ff_00)
        self.rainbow = False
        self.maze_color = Color(0xff_80_80_80)
        self.text_color = Color(0xff_80_80_80)
        self.height = height + 160
        self.width = width
        self.paused = False
        self.show_path = True
        self.typed_text: TypedText = TypedText()
        self.last_frame: float = 0.0
        self.frame_count = 0
        self.start_time: float = 0.0
        self.prec_maze = ""
        self.init_hook()

    def init_hook(self) -> None:
        """uses mlx function to listen to some x11 event and call fuction accordingly""" 
        self.mlx.mlx_mouse_hook(self.win_ptr, self.mouse_handler, None)
        self.mlx.mlx_key_hook(self.win_ptr, self.key_handler, None)
        self.mlx.mlx_hook(self.win_ptr, 33, 0, self.quit, None)
        self.mlx.mlx_loop_hook(self.mlx_ptr, self.step, None)

    def start(self) -> None:
        """launch the window display"""
        self.start_time = time()
        self.start_maze()
        self.mlx.mlx_loop(self.mlx_ptr)

    def start_maze(self, config_text: Optional[str] = None) -> None:
        """start a new maze, either by an optionale
         config_text or using the config_path set at window initialisation"""
        if config_text:
            if MazeGenerator.verify_config(config_text):
                self.generator.from_text(config_text)
                with (open(self.config_path, "w")
                      as config_file):
                    config_file.write(config_text)
            else:
                try:
                    self.generator.from_text(config_text)
                except Exception as error:
                    print(error)
        else:
            try:
                self.generator.from_file(self.config_path)
            except Exception as error:
                print(error)
            with open(self.config_path, "r") as config_file:
                self.typed_text.text = config_file.read()
        self.maze_image.update_cell_size(self.generator.maze.width,
                                         self.generator.maze.height)
        self.maze_image.fill_image(Color(0xff_00_00_00))
        self.full_update = True

    def step(self, *_: tuple) -> None:
        """called periodicaly by mlx, used to launch animation
         step by step using time() to cap at a given fps"""
        if (time() > self.last_frame + (1 / self.FPS)):
            suplement = []
            if not self.paused:
                a = self.generator.maze.anim_finished
                self.generator.launch_algo()
                if (not a
                    and self.generator.maze.anim_finished
                        and self.show_path):
                    suplement.append(self.draw_path)
            self.update_display(*suplement)

    def forced_step(self) -> None:
        """force an animation step without checking if time passed"""
        if self.paused:
            suplement = []
            a = self.generator.maze.anim_finished
            self.generator.launch_algo()
            if not a and self.generator.maze.anim_finished and self.show_path:
                suplement.append(self.draw_path)
            self.update_display(*suplement)

    def quit(self, *_: tuple) -> None:
        """used to close mlx properly and write the config file at window closure"""
        self.mlx.mlx_destroy_image(self.mlx_ptr, self.text_image.image)
        self.mlx.mlx_destroy_image(self.mlx_ptr, self.maze_image.image)
        self.mlx.mlx_destroy_window(self.mlx_ptr, self.win_ptr)
        self.mlx.mlx_loop_exit(self.mlx_ptr)
        if not self.generator.maze.anim_finished:
            self.generator.algo.full_create()
            self.generator.maze.parser_A()
        with open(self.generator.output_file, "w") as output:
            output.write(self.generator.maze.hexa())
            output.write("\n\n")
            output.write(str(
                self.generator.config.ENTRY)[1:-1].replace(" ", "") + "\n")
            output.write(str(
                self.generator.config.EXIT)[1:-1].replace(" ", "") + "\n")
            output.write("".join(direct.to_text() for direct in
                         self.generator.maze.solution_direct
                         if direct is not None) + " \n")

    ###########################################
    def update_display(self, *suplement: Callable) -> None:
        """call all function needed to update the display, 
         can call suplement renderer passed as function argument if necessary"""
        self.last_frame = time()
        self.frame_count += 1
        self.text_image.fill_image(self.text_color)
        self.draw_maze()
        # self.draw_circle()
        self.draw_text(
            0, 0, self.MENU_TEXT +
            "fps counter : "
            f"{self.frame_count / (time() - self.start_time):.3f}",
            self.BLACK, scale=2)
        self.draw_text(
            600, 0,
            self.typed_text.text,
            self.BLACK,
            scale=(2))
        self.mlx.mlx_put_image_to_window(
            self.mlx_ptr,
            self.win_ptr,
            self.text_image.image,
            0,
            self.height - 160)
        for addition in suplement:
            addition()

    def change_color(self, how_much: int) -> Color:
        """used to change slithly the cursor color while in colored mode"""
        for i in range(how_much):
            next(self.rain)
        return Color(next(self.rain))

    def mouse_handler(self, button_pressed: int, *_: tuple) -> None:
        """catch x11 mouse related event,
         used to toggle the shortest path appearence"""
        # print(button_pressed)
        if button_pressed == 1:
            self.show_path = [True, False][self.show_path]
            self.draw_path()

    def key_handler(self, key: int, *_: tuple) -> None:
        """catch x11 keyboard press event,
         dispatch to according function based on keycode"""
        if key == 32:  # 'espace'
            self.paused = [True, False][self.paused]
            self.typed_text.is_writing = self.paused
        elif key == 65307:  # 'echap'
            self.quit()
        elif key == 65421:  # 'right enter'
            self.forced_step()
        elif self.paused:  # ecriture
            self.typed_text.handle_input(key)
        elif key == 65439:  # '.'
            self.generator.maze.anim = False
            self.forced_step()
        elif key == 110:  # 'n'
            self.start_maze(config_text=self.typed_text.clean_text())
            self.forced_step()
        elif key == 99:  # 'c'
            self.rainbow = [True, False][self.rainbow]
            if not self.rainbow:
                self.maze_color = Color(0xff_80_80_80)
            else:
                self.maze_color = self.change_color(2)
            self.start_maze()
        else:
            print(key)
    ###########################################

    def draw_maze(self) -> None:
        """update the render of each cell that 
        are different from the precedent frame, 
        if self.full_update is true, redraw the entire maze"""
        maze_hexa = self.generator.maze.hexa()
        a = self.generator.maze.width + 1
        for y in range(self.generator.maze.height):
            for x in range(self.generator.maze.width):
                if (self.full_update
                        or self.prec_maze[x + (y*a)] != maze_hexa[x + (y*a)]):
                    if self.rainbow:
                        self.maze_color = self.change_color(2)
                    self.draw_cell(
                               x,
                               y,
                               self.maze_color,
                               self.BLACK)
        self.prec_maze = maze_hexa
        self.full_update = False
        self.mlx.mlx_put_image_to_window(self.mlx_ptr, self.win_ptr,
                                         self.maze_image.image, 0, 0)

    def draw_path(self) -> None:
        """update the shortet path apearence based on self.show_path"""
        past_direct = None
        for pos, direct in zip(
                self.generator.maze.solution_pos,
                self.generator.maze.solution_direct):
            x1 = round((pos[0] + 0.2) * self.maze_image.wpc)
            y1 = round((pos[1] + 0.2) * self.maze_image.hpc)
            x2 = round((pos[0] + 0.8) * self.maze_image.wpc)
            y2 = round((pos[1] + 0.8) * self.maze_image.hpc)
            width = x2 - x1
            height = y2 - y1
            self.maze_image.draw_rectangle(
                x1, y1, width, height,
                self.WIN_COLOR if self.show_path else self.BLACK)
            if direct is not None:
                self.draw_cell_direct(
                    direct, pos[0], pos[1],
                    self.WIN_COLOR
                    if self.show_path else self.BLACK, small=True)
            if past_direct:
                self.draw_cell_direct(
                    past_direct.oppo(), pos[0], pos[1],
                    self.WIN_COLOR
                    if self.show_path else self.BLACK, small=True)
            past_direct = direct

    def draw_cell(self, x: int, y: int, cell_color: Color,
                  background_color: Color) -> None:
        """draw a cell at an x, y position in the maze"""
        if self.generator.maze.cells[x][y].blocked:
            self.maze_image.draw_rectangle(
                x * self.maze_image.wpc,
                y * self.maze_image.hpc,
                self.maze_image.wpc,
                self.maze_image.hpc,
                self.PATERN_COLOR)
            return None

        for direct in Direction:
            if not self.generator.maze.cells[x][y].walls & direct.value:
                self.draw_cell_direct(direct, x, y, background_color)

        for direct in Direction:
            if self.generator.maze.cells[x][y].walls & direct.value:
                self.draw_cell_direct(direct, x, y, cell_color)

    def draw_cell_direct(self, direct: Direction,
                         x: int, y: int,
                         color: Color, small: bool = False) -> None:
        """draw the wall of cell x,y in the given direction,
         if small = True it wont draw corner"""
        x_off, y_off, w, h = (-
            DrawDir.small_draw(direct) if small
            else DrawDir.draw(direct))
        x1 = round((x + x_off) * self.maze_image.wpc)
        y1 = round((y + y_off) * self.maze_image.hpc)
        x2 = round((x + x_off + w) * self.maze_image.wpc)
        y2 = round((y + y_off + h) * self.maze_image.hpc)
        width = x2 - x1
        height = y2 - y1
        self.maze_image.draw_rectangle(
            x1,
            y1,
            width,
            height,
            color)

    def draw_text(self, x: int, y: int,
                  text: str, color: Color, scale: int = 1) -> None:
        """draw the text starting at a given x,y coordinate,
        go to next line when going over the right border of the buffer,
        stop drawing text if it goes beneath the bottom of the buffer"""
        original_x = x
        for ch in text:
            if y + (8 * scale) > self.text_image.height:
                break
            if x + (8 * scale) > self.text_image.width:
                break
            self.text_image.draw_char(x, y, ch, color, scale)
            x += 8 * scale
            if x + (8 * scale) > self.text_image.width or ch == "\n":
                x = original_x
                y += 10*scale

    # def draw_circle(self) -> None:
    #     cx, cy = 400, 400
    #     r = 150
    #     x = 0
    #     y = r

    #     prec_y = y
    #     while x <= y:
    #         if (sqrt(float(x * x) + float(y * y)) > r):
    #             y -= 1
    #         if prec_y != y:
    #             prec_y = y
    #             self.maze_image.draw_line(
    #                 cx - x - 1, cy - y + 1, (x * 2) + 1, self.WIN_COLOR)
    #             self.maze_image.draw_line(
    #                 cx - x, cy + y, (x * 2), self.WIN_COLOR)
    #         self.maze_image.draw_line(
    #             cx - y, cy - x, (y * 2), self.WIN_COLOR)   # Upper sides
    #         self.maze_image.draw_line(
    #             cx - y, cy + x, (y * 2), self.WIN_COLOR)   # Lower sides
    #         x += 1
    #         self.mlx.mlx_put_image_to_window(
    #           self.mlx_ptr, self.win_ptr, self.maze_image.image, 0, 0)
    ###########################################
