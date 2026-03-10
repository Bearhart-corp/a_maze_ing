from pydantic import BaseModel, Field, model_validator
from typing import Optional
from random import randint


class Doublons(Exception):
    """duplicate error"""
    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class MazeConfig(BaseModel):
    """Fill and verify the parameters"""
    WIDTH: int = Field(ge=1, le=4000)
    HEIGHT: int = Field(ge=1, le=4000)
    ENTRY: tuple[int, int]
    EXIT: tuple[int, int]
    OUTPUT_FILE: str = Field(min_length=1, max_length=200)
    PERFECT: bool
    SEED: int
    ALGO: Optional[str] = Field(min_length=0, max_length=200)
    ANIM: Optional[bool]

    @model_validator(mode="after")
    def validate_and_initialize(self) -> "MazeConfig":
        self.validate_coor()
        return self

    def validate_coor(self) -> None:
        """Apply more checking points
        entry and exit cannot be the same
        entry and exit cannot be inside of 
        the 42 pattern and have to be inside of the maze"""
        ft = [(0, 0), (0, 1), (0, 2), (1, 2), (2, 2), (2, 3), (2, 4),
              (5, 0), (6, 0), (7, 0), (7, 1),
              (7, 2), (6, 2), (5, 2), (5, 3),
              (5, 4), (5, 4), (7, 4)]
        off_x, off_y = ((self.WIDTH - 8) // 2, (self.HEIGHT - 5) // 2)
        ft_offset = [(off_x + pos[0], off_y + pos[1]) for pos in ft]
        (a, b) = self.EXIT
        (x, y) = self.ENTRY
        if x >= self.WIDTH or y >= self.HEIGHT:
            raise ValueError(
                "Entry is outside of the maze !"
            )
        if a >= self.WIDTH or b >= self.HEIGHT:
            raise ValueError(
                "Exit is outside of the maze !"
            )
        if (a, b) in ft_offset:
            raise ValueError(
                "Exit cannot be inside of the 42"
            )
        if (x, y) in ft_offset:
            raise ValueError(
                "Entry cannot be inside of the 42"
            )
        if a == x and b == y:
            raise ValueError(
                "Entry and exit cannot be the same"
            )
        if any(x < 0 for x in [a, b, x, y]):
            raise ValueError(
                "coordinates cannot be negatives"
            )

    @classmethod
    def get_arg(cls, path: str) -> "MazeConfig":
        """parser, get the args in a file, return a config class"""
        width: Optional[int] = None
        height: Optional[int] = None
        entry: Optional[tuple[int, int]] = None
        exit: Optional[tuple[int, int]] = None
        output_file: Optional[str] = None
        perfect: Optional[bool] = None
        seed: Optional[int] = None
        algo: Optional[str] = None
        anim: Optional[bool] = None

        seen: set[str] = set()

        with open(path, "r") as file:
            for line in file:
                if not line.strip() or line.startswith("#"):
                    continue
                k, v = line.strip().split("=")
                k = k.upper()
                if k in seen:
                    raise Doublons("Insert only once the parameter")
                seen.add(k)
                if k == "WIDTH":
                    width = int(v)
                elif k == "HEIGHT":
                    height = int(v)
                elif k == "ENTRY":
                    x, y = map(int, v.split(","))
                    entry = (x, y)
                elif k == "EXIT":
                    x, y = map(int, v.split(","))
                    exit = (x, y)
                elif k == "OUTPUT_FILE":
                    output_file = v
                elif k == "PERFECT":
                    perfect = v.lower() == "true"
                elif k == "SEED":
                    seed = int(v)
                elif k == "ALGO":
                    algo = v
                elif k == "ANIM":
                    anim = v.lower() == "true"
                else:
                    raise KeyError(f"Bad key: {k}")
        if None in (width, height, entry, exit, output_file, perfect):
            raise IOError("Missing mandatory entries")
        assert width is not None
        assert height is not None
        assert entry is not None
        assert exit is not None
        assert output_file is not None
        assert perfect is not None
        return cls(
            WIDTH=width,
            HEIGHT=height,
            ENTRY=entry,
            EXIT=exit,
            OUTPUT_FILE=output_file,
            PERFECT=perfect,
            SEED=seed if seed is not None else randint(0, 10000000),
            ALGO=algo,
            ANIM=anim,
        )

    @classmethod
    def from_config(cls, config: str) -> "MazeConfig":
        """parser, get the args in a file, return a config class"""
        width: Optional[int] = None
        height: Optional[int] = None
        entry: Optional[tuple[int, int]] = None
        exit: Optional[tuple[int, int]] = None
        output_file: Optional[str] = None
        perfect: Optional[bool] = None
        seed: Optional[int] = None
        algo: Optional[str] = None
        anim: Optional[bool] = None

        seen: set[str] = set()
        for line in config.splitlines(keepends=True):
            if not line.strip() or line.startswith("#"):
                continue
            k, v = line.strip().split("=")
            k = k.upper()
            if k in seen:
                raise Doublons("Insert only once the parameter")
            seen.add(k)
            if k == "WIDTH":
                width = int(v)
            elif k == "HEIGHT":
                height = int(v)
            elif k == "ENTRY":
                x, y = map(int, v.split(","))
                entry = (x, y)
            elif k == "EXIT":
                x, y = map(int, v.split(","))
                exit = (x, y)
            elif k == "OUTPUT_FILE":
                output_file = v
            elif k == "PERFECT":
                perfect = v.lower() == "true"
            elif k == "SEED":
                seed = int(v)
            elif k == "ALGO":
                algo = v
            elif k == "ANIM":
                anim = v.lower() == "true"
            else:
                raise KeyError(f"Bad key: {k}")
        if None in (width, height, entry, exit, output_file, perfect):
            raise IOError("Missing mandatory entries")
        assert width is not None
        assert height is not None
        assert entry is not None
        assert exit is not None
        assert output_file is not None
        assert perfect is not None
        return cls(
            WIDTH=width,
            HEIGHT=height,
            ENTRY=entry,
            EXIT=exit,
            OUTPUT_FILE=output_file,
            PERFECT=perfect,
            SEED=seed if seed is not None else randint(0, 10000000),
            ALGO=algo,
            ANIM=anim,
        )
