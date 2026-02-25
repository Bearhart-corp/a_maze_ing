from Enums import Direction


class Cell:
    BORDER_OFFSET = 4

    def __init__(self, x: int, y: int, walls_value: int = 15):
        self.x = x
        self.y = y
        self.path_str = "  "
        self.walls = walls_value
        self.need_update = True

    def wall_state(self, direction: Direction) -> int:
        if self.walls & (direction.value << self.BORDER_OFFSET):
            return 2
        if self.walls & direction.value:
            return 1
        return 0

    def get_pos(self):
        return (self.y, self.x)

    def is_border(self):
        return all(self.wall_state(direct) == 2 for direct in Direction)

    def is_open(self):
        return any(self.wall_state(d) == 0 for d in Direction)

    def add_wall(self, direction: Direction):
        self.walls |= direction.value
        self.need_update = True

    def remove_wall(self, direction: Direction):
        self.walls &= ~direction.value
        self.need_update = True

    def set_border(self, direction: Direction):
        self.walls |= direction.value
        self.walls |= direction.value << self.BORDER_OFFSET
        self.need_update = True

    def remove_border(self, direction: Direction):
        self.walls &= ~direction.value
        self.walls &= ~(direction.value << self.BORDER_OFFSET)
        self.need_update = True

    def wall_str(self, direction):
        if self.wall_state(direction) == 2:
            return "@@"
        elif self.wall_state(direction) == 1:
            return "[]"
        return "  "

    def corner_str(self, horizontal, vertical):
        if (self.wall_state(horizontal) == 2
                or self.wall_state(vertical) == 2):
            return '@@'
        else:
            return '[]'
        
    def update_str_rows(self):
        self.str_rows = [
            self.corner_str(Direction.WEST, Direction.NORTH)
            + self.wall_str(Direction.NORTH)
            + self.corner_str(Direction.EAST, Direction.NORTH),
            self.wall_str(Direction.WEST)
            + self.path_str
            + self.wall_str(Direction.EAST),
            self.corner_str(Direction.WEST, Direction.SOUTH)
            + self.wall_str(Direction.SOUTH)
            + self.corner_str(Direction.EAST, Direction.SOUTH)
        ]
        self.need_update = False

    def __str__(self):
        if self.need_update:
            self.update_str_rows()
        return "\n".join(self.str_rows)

    def __repr__(self) -> str:
        return "0123456789ABCDEF"[self.walls & 15]

    # def __str__(self):
    #     row1 = f"\\\\{'==' if self.north else '  '}//"
    #     row2 = f"{'||'if self.west else '  '}  {'||'if self.east else '  '}"
    #     row3 = f"//{'==' if self.south else '  '}\\\\"
    #     return "\n".join([row1, row2, row3]) + "\n"

