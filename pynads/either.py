from .functor import fmap
from .monad import Monad

class Either(Monad):
    """Enhanced version of Maybe. Represents a successful computation or
    a failed computation with an error msg.
    """
    def __bool__(self):
        return isinstance(self, Right)

    @staticmethod
    def unit(v):
        return Right(v)

class Left(Either):
    """Similar to Nothing in that it only returns itself when fmap, apply
    or bind is called. However, Left also carries an error message instead
    of representing a completely failed computation.
    """
    def __init__(self, v):
        self.v = v

    def __repr__(self):
        return "Left {}".format(self.v)

    def __eq__(self, other):
        return isinstance(other, Left) and self.v == other.v

    fmap = apply = bind = lambda self, _: self

class Right(Either):
    """Represents a result of a computation. Similar to Just except it is
    semantically a finished computation.
    """

    def __init__(self, v):
        self.v = v

    def __eq__(self, other):
        return isinstance(other, Right) and other.v == self.v
    
    def __repr__(self):
        return "Right {!r}".format(self.v)
    
    def fmap(self, f):
        return Right(f(self.v))

    def apply(self, applicative):
        return fmap(self.v, applicative)

    def bind(self, f):
        return f(self.v)


