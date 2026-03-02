from time import time
from functools import wraps
from typing import Callable


def spell_timer(func: Callable) -> Callable:
    @wraps(func)
    def func_timer(*args, **kwargs):
        start = time()
        try:
            result = func(*args, **kwargs)
            end = time()
        except Exception as error:
            end = time()
            print(f"{func.__name__} crashed after {end - start:.5f} seconds"
                  f"\nerror :'{error}'\n")
            raise error
        return (result, end - start)
    return func_timer
