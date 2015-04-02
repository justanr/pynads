from functools import reduce
from operator import mul, rshift


__all__ = ('fmap', 'unit', 'lift', 'multiapply', 'multibind',
           'mempty', 'mappend', 'mconcat')


_KNOWN_MEMPTIES = {
    int: 0,
    list: [],
    dict: {},
    set: set(),
    str: '',
    float: 0.0,
    frozenset: frozenset(),
    tuple: ()
}


def fmap(f, functor):
    """Callable form of fmap."""
    return functor.fmap(f)


def unit(v, applicative):
    """Puts a value in the minimum necessary context to form an Applicative.
    """
    return applicative.unit(v)


def mempty(monoid):
    """Returns the mempty value of a Monoid. If the passed object/class isn't
    a monoid, this function will return an empty value for a small subset of
    Python types.
    """

    if hasattr(monoid, 'mempty'):
        return monoid.mempty
    elif type(monoid) in _KNOWN_MEMPTIES:
        return _KNOWN_MEMPTIES[type(monoid)]
    else:
        raise TypeError("No known mempty value for {!r}".format(type(monoid)))


def mappend(existing, other):
    """Joins a monoid with another monoid by using the first monoid's mappend
    method. This function propagates exceptions if any occur.
    """
    return existing.mappend(other)


def mconcat(*monoids):
    """Joins together a sequence of monoids into a single monoid by grabbing
    the mconcat method off the first monoid and applying it to every monoid
    in the iterable.
    """
    mconcat_ = monoids[0].mconcat
    return mconcat_(*monoids)


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
