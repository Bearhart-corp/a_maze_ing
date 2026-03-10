from mazegen.Enums import Direction


class DrawDir:
    """get the proportion of the given direction"""
    _DRAW = {
        Direction.NORTH: (0, 0, 1, 0.1),
        Direction.SOUTH: (0, 0.9, 1, 0.1),
        Direction.EAST:  (0.9, 0, 0.1, 1),
        Direction.WEST:  (0, 0, 0.1, 1),
    }

    _SMALL_DRAW = {
        Direction.NORTH: (0.2, 0, 0.6, 0.2),
        Direction.SOUTH: (0.2, 0.8, 0.6, 0.2),
        Direction.EAST:  (0.8, 0.2, 0.2, 0.6),
        Direction.WEST:  (0, 0.2, 0.2, 0.6),
    }

    @classmethod
    def draw(cls, direction: Direction) -> tuple:
        """return proportion that can be drawn on screen
        , including corner"""
        return cls._DRAW[direction]

    @classmethod
    def small_draw(cls, direction: Direction) -> tuple:
        """return proportion that can be drawn on screen
        , excluding corner"""
        return cls._SMALL_DRAW[direction]
