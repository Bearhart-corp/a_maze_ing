from pydantic import BaseModel, Field, model_validator
from typing import Optional


class Doublons(Exception):
    def __init__(self, msg):
        super().__init__(msg)


class MazeConfig(BaseModel):
    WIDTH: int = Field(ge=0, le=4000)
    HEIGHT: int = Field(ge=0, le=4000)
    ENTRY: tuple[int, int]
    EXIT: tuple[int, int]
    OUTPUT_FILE: str = Field(min_length=0, max_length=200)
    PERFECT: bool
    SEED: int
    ALGO: Optional[str] = Field(Default=None, min_length=0, max_length=200)
    DIS_MODE: Optional[bool]
    ANIM: Optional[bool]

    @model_validator(mode="after")
    def validate_and_initialize(self):
        self.validate_coor()
        # self.initialize()
        return self

    def validate_coor(self):
        (a, b) = self.EXIT
        (x, y) = self.ENTRY
        if x >= self.HEIGHT or y >= self.WIDTH:
            raise ValueError(
                "Entry is outside of the maze !"
            )
        if a >= self.HEIGHT or b >= self.WIDTH:
            raise ValueError(
                "Exit is outside of the maze !"
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
        mandatory = [
                "WIDTH",
                "HEIGHT",
                "ENTRY",
                "EXIT",
                "OUTPUT_FILE",
                "PERFECT"
        ]
        data = {
                "WIDTH": None,
                "HEIGHT": None,
                "ENTRY": None,
                "EXIT": None,
                "OUTPUT_FILE": None,
                "PERFECT": None,
                "SEED": None,
                "ALGO": None,
                "DIS_MODE": None,
                "ANIM": None
        }
        with open(path, "r") as file:
            for line in file:
                if not line or line.startswith("#") \
                        or line.startswith("\n") or line.startswith(" "):
                    continue
                key, value = line.strip().split("=")
                key = key.upper()
                if data.get(key, None) is not None:
                    raise Doublons("Insert only once the parameter")
                elif data.get(key, KeyError) is KeyError:
                    raise KeyError("Bad key Entries")
                if key in {"ENTRY", "EXIT"}:
                    value = tuple(map(int, value.split(",")))
                elif key in {"WIDTH", "HEIGHT", "SEED"}:
                    value = int(value)
                elif key == {"PERFECT", "DIS_MODE", "ANIM"}:
                    value = value.lower() == "true"
                data[key] = value
            for key in mandatory:
                if data[key] is None:
                    raise IOError("Miss some mandatory Entries")
            return cls(**data)  # return l'instance
