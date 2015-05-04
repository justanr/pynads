"""These are functions that don't expect interact with: Monoids, Functors,
Applicatives and Monads. Rather they act on just plain values. These
functions are exported by pynads under the `pynads.funcs` namespace.
"""

from ..utils.decorators import annotate
from ..utils.compat import wraps
from ..utils.internal import _get_name, _get_names


__all__ = ('const', 'identity', 'compose')


@annotate(type='a -> b -> a')
def const(value):
    """Returns a function that accepts any arguments but only returns a
    predetermined constant.
    >>> def inc(x): x+1
    >>> c = const(inc)
    >>> c(1)
    ... <function __main__.inc>

    See: pynads.concrete.reader.Reader for application.
    """
    @wraps(value)
    def constant(*_, **__):
        return value

    # extract *actual* name in case of partial or object
    constant.__name__ = _get_name(value)
    return constant


@annotate(type='a -> a')
def identity(v):
    """Always returns its initial value.

    >>> identity(4)
    ... 4

    Useful for proving that Functor, Applicative and Monad satsify certain
    required laws to be actual Functors, Applicatives and Monads.
    """
    return v


@annotate(type='(b -> c) -> (a -> b) -> (a -> c)')
def compose(*fs):
    """Composes several functions into one.

    Functions are applied right-to-left, with return values being passed
    up the chain. So: compose(f,g,h)(x) is the same as f(g(h(x))).

    If no functions are provided, the identity function is returned. If
    only one function is provided, only that function is returned.

    If the closure is actually generated, it's doc string lists the functions
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
