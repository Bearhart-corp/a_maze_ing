from Enums import Direction


class Cell:
    def __init__(self, walls: int = 15) -> None:
        self.__walls = walls
        self.is_visited = False
        self.blocked = False

    #   Getters:

    @property
    def walls(self) -> bool:
        return self.__walls

    def wall_state(self, dir: Direction) -> bool:
        """test the state of a specific wall"""
        if (self.__walls & dir.value):
            return True
        return False

    #   setters:

    def add_wall(self, dir: Direction) -> None:
        self.__walls |= dir.value

    def remove_wall(self, dir: Direction) -> None:
        self.__walls &= ~dir.value
        self.is_visited = True
