import inspect
from os.path import join, dirname, abspath
from typing import Callable, Set

assets_dir = join(dirname(abspath(__file__)), "assets")


# TODO make async using aiofiles?
def read_asset(filename: str) -> str:
    with open(join(assets_dir, filename), "r") as f:
        return f.read()


def overrides(original: Callable) -> Callable:
    def decorate(func):
        func.__doc__ = original.__doc__
        return func

    return decorate


class cached_property:
    # A property that is only computed once.

    def __init__(self, getter):
        self.getter = getter

    def __get__(self, obj, cls):
        if obj is None:
            return self

        value = obj.__dict__[self.getter.__name__] = self.getter(obj)
        return value
