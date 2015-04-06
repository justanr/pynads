"""A transient mempty value to serve as a placeholder when any monoidal value
can be used.
"""
from ..abc import Monoid
from ..utils.compat import filter
from ..funcs.monoid import is_monoid, mconcat, mempty, mappend


__all__ = ('Mempty',)


class _Mempty(Monoid):
    """A class that acts as a transient mempty value, similar to the Haskell
    implementation. This class should be used as a singleton, placeholder
    value for operations that can expect any Monoidal value. However, Python
    isn't intuitive in the same ways as Haskell is and needs some help
    understanding. Mempty isn't so much the *absence* of a value as just
    sitting around waiting for a monoid to be provided.
    """
    __slots__ = ()
    # _Mempty is its own mempty value
    mempty = __inst = None

    def __new__(cls):
        if cls.__inst is None:
            cls.mempty = cls.__inst = Monoid.__new__(cls)
        return cls.__inst

    def __repr__(self):
        return 'Mempty'

    def mappend(self, other):
        """When mempty is used to mappend something, it simply becomes
        the other value if it is monoidal. Otherwise, a TypeError is raised.
        In doing so, the transient mempty disappears.
        """
        return other

    @staticmethod
    def mconcat(*monoids, **kwargs):
        """Rather than rely on the mconcat provided by Monoid, the transient
        mempty will attempt to construct a mconcat call via the
        pynads.funcs.mconcat function. This implementation of mconcat
        will also filter all instances of mempty out instead of relying
        on the _Mempty._reflected_mappend method.
        """
        monoids = list(filter(lambda x: not isinstance(x, _Mempty), monoids))
        if not monoids:
            return Mempty
        return mconcat(*monoids, **kwargs)

    def _reflected_mappend(self, other):
        """It's possible that a Mempty will end up in the middle of a list
        of monoids. Rather than blowing up, Mempty will attempt to discover
        the appropriate mempty value to return. If a mempty can't be
        determined, a TypeError is raised instead. Unlike other calls
        that delegate to pynads.utils.monoid.get_generic_mempty in some way,
        there's not a good way to provide optional keyword arguments
        since this method will actually be invoked by dunder method calls
        like __add__ or __or__.
        """
        return mappend(other, mempty(other))

    __add__ = __iadd__ = __radd__ = \
        __or__ = __ior__ = __ror__ = _reflected_mappend

    # should work for mappends on sequences and mappings
    __iter__ = lambda _: iter(())


Mempty = _Mempty()
