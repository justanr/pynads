from functools import reduce
from operator import mul, rshift
from ..concrete.list import List
from ..utils.decorators import annotate
from .monoid import mappend
from .pure import identity


__all__ = ('fmap', 'unit', 'lift', 'multiapply', 'multibind',
           'cons', 'mcons', 'sequence', 'mapM')


@annotate(type="Functor f => (a -> b) -> f a -> f b")
def fmap(f, functor):
    """Functional form of fmap.
    """
    return functor.fmap(f)


@annotate(type="Applicative f => a -> f a")
def unit(v, applicative):
    """Puts a value in the minimum necessary context to form an Applicative.
    """
    return applicative.unit(v)


@annotate(type="Applicative f => f (a -> b) -> [f a] -> f b")
def multiapply(initial, *args):
    """Shorthand for stringing many applicatives together.

    This is designed for use with a curried function that will gradually
    build until it reaches the correct number of arguments to call itself.
    """
    return reduce(mul, args, initial)


@annotate(type="Applicative f => (a -> b) -> a -> f -> f b")
def lift(f, v, applicative):
    """Applies a function to a value and puts it into an applicative context.
    """
    return unit(f(v), applicative)


@annotate(type="Monad m => m a -> [a -> m a] -> m a")
def multibind(monad, *binds):
    """Shortcut function for composing many monadic binds together.

    >>> add_two = lambda x: Just(x+2)
    >>> multibind(Just(2), *repeat(add_two, 3))
    ... Just 8

    """
    return reduce(rshift, binds, monad)


@annotate(type="a -> [a] -> [a]")
def cons(x, xs):
    """Prepends a value to a pynads.List of existing values.

    .. code-block:: Python
        from pynads import List
        from pynads.funcs import cons

        cons(1, List(2,3)) # List(1,2,3)
        cons(1, cons(2, cons(3, List()))) # List(1,2,3)
    """
    return mappend(List(x), xs)


@annotate(type="Monad m => m a -> m [a] -> m [a]")
def mcons(p, q):
    """Prepends a monadic value to a pynads.List of values inside of a monad.

    .. code-block:: python
        from pynads import Just
        from pynads.funcs import mcons

        mcons(Just(1), Just(List(2,3)))   # Just(List(1,2,3))
        mcons(Nothing, Just(List(1,2,3))) # Nothing
    """
    return p >> (lambda x:
                 q >> (lambda xs:
                       p.unit(cons(x, xs))))


@annotate(type="Monad m => [m a] -> m [a]")
def sequence(*monads):
    """Folds a list of monads into a monad containing a list of the
    monadic values.

    .. code-block:: python
        justs = List(*[Just(x) for x in range(5)])
        sequence(*justs)
        # In: List(Just 0, Just 2, Just 3, Just 4)
        # Just List(0, 1, 2, 3, 4)
    """
    return reduce(lambda q, p: mcons(p, q),
                  reversed(monads),
                  monads[0].unit(List()))


@annotate(type="Moand m => (a -> m b) -> [a] -> m [b]")
def mapM(func, *xs):
    """Maps a monadic function over an iterable of plain values, lifting
    each into a monadic context then uses sequence to convert the iterable
    of monads into a monad containing a pynads.List of values.
    """
    return sequence(*map(func, xs))
