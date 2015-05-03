from .option import Option, Full, _Empty
from ..funcs import fmap
from ..abc import Monad, Container
from ..utils.compat import wraps
from ..utils.decorators import method_optional_kwargs
from ..utils.internal import _propagate_self


class Either(Monad, Option):
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
    Left with an error or a Right with a value to be returned, as well as
    the condition which causes that result. Other than that, it acts like
    Maybe in all respects.

    If a Left is mapped, applied or bound, the Left simply propagates itself
    until the end of the chain. But a Right will allow the computations to
    still run.

    Either is also combined with the Option class, allowing for a recovering
    of a potentially failed computation through the get_or, get_or_call,or_else
    and or_call methods. Recovery is only possible on a Left, as a Right is
    already a successful computation.

    Either also provides a decorator: ``Either.as_wrapper`` which will attempt
    to call the wrapped function. If no errors are raised, then the result
    is returned wrapped in a Right. If the expected error (by default
    Exception) is raised, then the exception is wrapped in a Left and returned
    instead. However, if any other errors are encountered, then the exception
    is propagate until caught or the program exits.
    """
    __slots__ = ()

    def __new__(cls, *args):
        raise TypeError("Instantiate Left or Right directly.")

    def __bool__(self):
        return isinstance(self, Right)

    __nonzero__ = __bool__

    @method_optional_kwargs
    @staticmethod
    def as_wrapper(func, expect=Exception):
        """Either based decorator. Tries to call the wrapped function and
        if successful returns the value wrapped in a Right. If the expected
        exception occurs, the exception is wrapped in a Left.
        """
        @wraps(func)
        def tryer(*args, **kwargs):
            try:
                return Right(func(*args, **kwargs))
            except expect as e:
                return Left(e)
        return tryer

    @staticmethod
    def unit(v):
        return Right(v)


class Left(Either, _Empty):
    """Similar to Nothing in that it only returns itself when fmap, apply
    or bind is called. However, Left also carries an error message instead
    of representing an unknown failed computation
    """
    __slots__ = ()

    # needed to override _Empty.__new__
    def __new__(cls, v):
        return Container.__new__(cls)

    def __repr__(self):
        return "Left {!r}".format(self.v)

    def __eq__(self, other):
        return isinstance(other, Left) and self.v == other.v

    fmap = apply = bind = _propagate_self

    def _get_val(self):
        return self._v

    @staticmethod
    def or_else(default):
        return Right(default) if (default is not None) \
            else Left("None provided")

    @staticmethod
    def or_call(func, *args, **kwargs):
        return Either.as_wrapper(func)(*args, **kwargs)


class Right(Either, Full):
    """Represents a result of a computation. Similar to Just except it is
    semantically a finished computation.
    """
    __slots__ = ()

    def __new__(cls, v):
        return Container.__new__(cls)

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

    def filter(self, predicate):
        msg = "{!s} false with input {!r}".format(predicate.__name__, self.v)
        return self if predicate(self.v) else Left(msg)
