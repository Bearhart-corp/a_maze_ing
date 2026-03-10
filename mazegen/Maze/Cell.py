from ..Enums import Direction


class Cell:
    def __init__(self, walls: int = 15) -> None:
        self.__walls = walls
        self.is_visited = False
        self.blocked = False

    #   Getters:

    @property
    def walls(self) -> int:
        return self.__walls

    def wall_state(self, dir: Direction) -> bool:
        """test the state of a specific wall"""
        if (self.__walls & dir.value):
            return True
        return False

    #   setters:

    def add_wall(self, dir: Direction) -> None:
        """args = a direction (cardinals)
        add a wall by concatenation OR logic
        return nothing"""
        self.__walls |= dir.value

    def remove_wall(self, dir: Direction) -> None:
        """args = a direction (cardinals)
        remove a wall by setting it up at zero with an
        inverted mask (NAND logic).
        return nothing"""
        self.__walls &= ~dir.value
        self.is_visited = True
