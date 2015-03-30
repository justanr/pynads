from ..utils import _iter_but_not_str_or_map
from ..abc import Monad
from ..funcs import fmap
from .list import List


class Writer(Monad):
    """Stores a value as well as a log of events that have transpired
    with the value.
    """
    __slots__ = ('log',)

    def __init__(self, v, log):
        super(Writer, self).__init__(v)

        if _iter_but_not_str_or_map(log):
            self.log = List.unit([l for l in log])
        else:
            self.log = List.unit(log)

    @classmethod
    def unit(cls, v):
        return cls(v, [])

    def fmap(self, f):
        return Writer(f(self.v), self.log)

    def apply(self, applicative):
        return fmap(self.v, applicative)

    def bind(self, f):
        v, msg = f(self.v)
        return Writer(v, self.log + (msg,))

    def __repr__(self):
        return "Writer({!r}, {!r})".format(self.v, self.log)
