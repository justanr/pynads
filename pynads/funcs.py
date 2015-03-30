from functools import reduce, wraps
from operator import mul, rshift
from .utils import _get_names, _get_name

__all__ = ('fmap', 'unit', 'multiapply', 'lift', 'multibind', 'const',
           'identity', 'compose')

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


def const(f):
    """Returns a function that accepts any arguments but only returns a
    predetermined constant.
    >>> def inc(x): x+1
    >>> c = const(inc)
    >>> c(1)
    ... <function __main__.inc>

    See: pynads.concrete.reader.Reader for application.
    """
    # Note: Python 2 will raise errors if provided with a type that
    # doesn't have __name__, __module__ or __doc__
    # major issue with ``functools.partial`` which *is* a valid input
    # but doesn't define __name__ or __module__.
    # Fixes: backport Python 3.4's update_wrapper in utils?
    # or just include toolshed (and ergo toolz) as a requirement?
    @wraps(f)
    def constant(*a, **k):
        return f

    # extract *actual* name in case of partial or object
    constant.__name__ = _get_name(f)
    return constant


def identity(v):
    """Always returns its initial value.

    >>> identity(4)
    ... 4

    Useful for proving that Functor, Applicative and Monad satsify certain
    required laws to be actual Functors, Applicatives and Monads.
    """
    return v


def compose(*fs):
    """Composes several functions into one.

    Functions are applied right-to-left, with return values being passed
    up the chain. So: compose(f,g,h)(x) is the same as f(g(h(x))).

    If no functions are provided, the identity function is returned. If
    only one function is provided, only that function is returned.

    If the closure is actually generated, it's doc string lits the functions
    it composes.

    >>> def inc(x): return x+1
    >>> def double(x): return x*2
    >>> inc_then_double = compose(dobule, inc)
    >>> inc_then_double(2)
    ... 6
    >>> inc_then_double.__doc__
    ... Composition of: double, inc

    It's also possible to pass partialed callables and callable objects into
    compose as well and it will extract the proper names
    """

    if not fs:
        return identity
    elif len(fs) == 1:
        return fs[0]


    def composed(*a, **k):
        ret = fs[-1](*a, **k)
        for f in fs[-2::-1]:
            ret = f(ret)
        return ret

    docstring = "Composition of: {}".format(', '.join(_get_names(*fs)))
    composed.__doc__ = docstring
    composed.fs = fs

    return composed
