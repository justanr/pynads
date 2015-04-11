from ..funcs import fmap
from ..abc import Monad
from ..utils import _propagate_self


class Either(Monad):
    """Enhanced version of Maybe. Represents a successful computation or
    a failed computationi with an error message. Either's unit method returns
    an instance of Right, which is the minimal needed context for a possible
    computation.

    Compare to Haskell's implementation of Either:

    .. code-block:: Haskell
       data Either a b = Left a | Right b

       instance Functor (Either a) where
           fmap f (Left a)      = Left a
           fmap f (Right b)     = Right (f b)

        instance Applicative (Either a) where
            pure            = Right
            (Left a)  <*> f = Left a
            (Right b) <*> f = fmap b f

       instance Monad (Either a) where
           return           = Right
           (Left e)  >>= _  = Left e
           (Right a) >>= f  = f a

    As said before, Either is like a Maybe that carries an error message when
    a computation fails. Just like Nothing, (Left a) propagates when it is
    mapped, applied or bound. And like Just, mapping, applying or binding a
    (Right b) simply takes the value stored in Right and does the appropriate
    action.

    Either is more useful than Maybe when you not only expect to encounter
    a None (or other failure) but you also want to know why you got that
    bad result.

    .. code-block:: Python
       from random import randint
       def reporting_none_safe_inc(x):
           if x is None:
               print("x was None when incrementing")
               return None
           else:
               return x+1

       def reporting_none_safe_sq(x):
           if x is None:
               print("x was None when squareing")
               return None
           else:
               return x*x

       def bad_get_int():
           x = randint(1,10)
           return x if x%2 else None

       x = bad_get_int()
       y = reporting_none_safe_inc(reporting_none_safe_sq(x))

    Instead, using the Either monad would all you to rewrite this as:

    .. code-block:: Python
       def bad_get_int():
           x = randint(1,10)
           if x%2:
              return Right(x)
           else:
              return Left("bad integer returned")

       def inc(x): return Right(x+1)
       def sqr(x): return Right(x*x)

       y = bad_get_int() >> sqr >> inc

    Unlike Maybe, Either doesn't have a default checker. You must provide a
    Left with a message or a Right with a value to be returned, as well as
    the condition which causes that result. Other than that, it acts like
    Maybe in all respects.

    If a Left is mapped, applied or bound, the Left simply propagates itself
    until the end of the chain. But a Right will allow the computations to
    still run.
    """
    __slots__ = ()

    def __bool__(self):
        return isinstance(self, Right)

    __nonzero__ = __bool__

    @staticmethod
    def unit(v):
        return Right(v)


class Left(Either):
    """Similar to Nothing in that it only returns itself when fmap, apply
    or bind is called. However, Left also carries an error message instead
    of representing an unknown failed computation
    """
    __slots__ = ()

    def __repr__(self):
        return "Left {}".format(self.v)

    def __eq__(self, other):
        return isinstance(other, Left) and self.v == other.v

    fmap = apply = bind = _propagate_self


class Right(Either):
    """Represents a result of a computation. Similar to Just except it is
    semantically a finished computation.
    """
    __slots__ = ()

    def __eq__(self, other):
        return isinstance(other, Right) and other.v == self.v

    def __repr__(self):
        return "Right {!r}".format(self.v)

    def fmap(self, func):
        return Right(func(self.v))

    def apply(self, applicative):
        return fmap(self.v, applicative)

    def bind(self, bindee):
        return bindee(self.v)
