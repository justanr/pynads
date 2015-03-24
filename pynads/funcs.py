from functools import reduce
from operator import mul, rshift

__all__ = ('fmap', 'unit', 'multiapply', 'lift', 'multibind')

def fmap(f, functor):
    """Callable form of fmap."""
    return functor.fmap(f)


def unit(v, applicative):
    """Puts a value in the minimum necessary context to form an Applicative.
    """
    return applicative.unit(v)


def multiapply(initial, *args):
    """Shorthand for stringing many applicatives together.

    This is designed for use with a curried function that will gradually
    build until it reaches the correct number of arguments to call itself.
    """
    return reduce(mul, args, initial)


def lift(f, v, monad):
    """Applies a function to a value and puts it into a monadic context.
    """
    return unit(f(v), monad)


def multibind(monad, *binds):
    """Shortcut function for composing many monadic binds together.

    >>> add_two = lambda x: Just(x+2)
    >>> multibind(Just(2), *repeat(add_two, 3))
    ... Just 8

    """
    return reduce(rshift, binds, monad)
