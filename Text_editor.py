
class TypedText:
    """size of the elements"""
    WINDOW = 8
    MAX_LEN = 200
    TOP_MARGIN = 1      # line 2 visually
    BOTTOM_MARGIN = 3   # line 4 visually

    def __init__(self) -> None:
        self.__text: str = ""
        self.__text2: str = ""
        self.is_writing = False
        self.__blink = 0
        self.cursor_line = 0
        self.visual_cursor = 0

    @property
    def text(self) -> str:
        """format the two part of the text
        return the concatenated up to WINDOW line"""
        full_text = (self.__text
                     + ("_" if self.blink
                        and self.is_writing else " "
                        if self.is_writing else "")
                     + self.__text2)
        lines = full_text.splitlines(keepends=True)
        if len(lines) <= self.WINDOW:
            return ''.join(lines)
        self.cursor_line = self.__text.count("\n")
        if self.visual_cursor == self.cursor_line and self.visual_cursor > 0:
            self.visual_cursor = self.cursor_line - 1
        elif self.cursor_line > self.visual_cursor + self.BOTTOM_MARGIN:
            self.visual_cursor += + 1
        return ''.join(
            lines[self.visual_cursor:self.visual_cursor + self.WINDOW])

    @text.setter
    def text(self, other: str) -> None:
        """set the text to the given string"""
        cursor = len(self.__text)
        self.__text = other[0:cursor]
        self.__text2 = other[cursor:]

    @property
    def blink(self) -> bool:
        """used to periodiccaly shows a cursor """
        a = [i for i in range(1, 30)]
        a.append(0)
        self.__blink = a[self.__blink]
        return self.__blink >= 15

    def handle_input(self, key: int) -> None:
        """distribute key input to the righ function"""
        if key == 65288:  # delete key
            self.__text = self.__text[:-1]
        elif key == 65361:  # '⬅'
            self.move_left()
        elif key == 65362:  # '⬆'
            self.move_up()
        elif key == 65363:  # '➡'
            self.move_right()
        elif key == 65364:  # '⬇'
            self.move_down()
        elif self.text.__len__() < self.MAX_LEN and 31 < key < 128:
            self.__text += chr(key)
            if key == ord("/"):
                self.__text = self.__text[:-1] + "\n"

    def clean_text(self) -> str:
        """return the entire texxt without formating"""
        return (self.__text + self.__text2)

    def move_up(self) -> None:
        """moves the cursor up by one line"""
        col = len(self.__text) - self.__text.rfind("\n")
        for i in range(col):
            self.move_left()
        line_len = len(self.__text) - self.__text.rfind("\n")
        for i in range(line_len - col):
            self.move_left()

    def move_right(self) -> None:
        """move the cursor to the righ"""
        if self.__text2:
            self.__text += self.__text2[0]
            self.__text2 = self.__text2[1:]

    def move_down(self) -> None:
        """move down the cursor"""
        col = len(self.__text) - self.__text.rfind("\n")
        if col == -1:
            col = len(self.__text)
        nex = self.__text2.find("\n")
        if nex == -1:
            nex = len(self.__text2)
        for i in range(nex):
            self.move_right()
        for i in range(col):
            self.move_right()
            if self.__text2 and self.__text2[0] == "\n":
                break

    def move_left(self) -> None:
        """move the cursor to the left"""
        if self.__text:
            self.__text2 = self.__text[-1] + self.__text2
            self.__text = self.__text[:-1]
