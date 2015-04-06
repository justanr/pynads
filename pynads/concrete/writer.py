from ..utils import _iter_but_not_str_or_map
from ..abc import Monad
from ..funcs import fmap, mappend
from ..utils import is_monoid
from .list import List


class Writer(Monad):
    """Stores a value as well as a log of events that have transpired
    with the value.
    """
    __slots__ = ('log',)

    def __init__(self, v, log=None):
        super(Writer, self).__init__(v)

        if log is None:
            log = List()
        elif not is_monoid(log):
            log = List.unit(log)
        self.log = log

    @classmethod
    def unit(cls, v):
        return cls(v, List())

    def fmap(self, f):
        return Writer(f(self.v), self.log)

    def apply(self, applicative):
        return fmap(self.v, applicative)

    def bind(self, f):
        v, entry = f(self.v)
        return Writer(v, mappend(self.log, entry))

    def __repr__(self):
        return "Writer({!r}, {!r})".format(self.v, self.log)
