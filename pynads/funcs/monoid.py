"""Helper functions for making it easier to deal with types in Python that
*are* monoidal but exist as basic types in Python.
"""


from ..utils.monoidal import (get_generic_mappend, get_generic_mempty,
                              generic_mconcat, is_monoid)


__all__ = ('mempty', 'mappend', 'mconcat', 'is_monoid')


def mempty(monoid, **kwargs):
    """Returns the mempty value of a Monoid.

    If the object passed is an implementation of pynads.abc.Monoid, then the
    mempty attribute found there is returned. Otherwise, if it fulfills certain
    criteria, then a generic mempty is returned instead. This criteria is
    determined by pynads.utils.get_generic_mempty. If neither case is true,
    then a TypeError is raised (propagated from get_generic_mempty).

    It's possible to pass optional keyword arguments to get_generic_mempty
    by using kwargs.

    See:
        pynads.utils.monoidal.get_generic_mempty
    """

    if hasattr(monoid, 'mempty'):
        return monoid.mempty
    else:
        return get_generic_mempty(monoid, **kwargs)


def mappend(existing, other, **kwargs):
    """Joins together two monoids.

    If the first value is an implementation of pynads.abc.Monoid, then it
    uses the mappend method on the object. Otherwise, if it fulfills certain
    criteria, then a generic mappend can be determined and that is used
    instead. This criteria is determined by pynads.utils.get_generic_mappend.

    Sequences -- e.g. lists and tuples -- that aren't strings are returned as
    lists.

    If neither case is true, then a TypeError is raised (propagated from
    get_generic_mappend).

    It is possible to pass optional keyword arguments to get_generic_mappend
    by using kwargs.

    See:
        pynads.utils.monoidal.get_generic_mappend
    """
    if hasattr(existing, 'mappend'):
        return existing.mappend(other)
    else:
        mappend = get_generic_mappend(existing)
        return mappend(existing, other)


def mconcat(*monoids, **kwargs):
    """Joins together a sequence of monoids into a single monoid.

    If the passed object is an implementation of pynads.abc.Monoid, then
    the mconcat from the first monoid is used, as it may be more efficient
    than a generic mconcat implementation. Otherwise, if certain criteria are
    fulfilled, then a generic mconcat is used instead. This criteria is
    determined by pynads.utils.get_generic_mappend.

    Sequences -- e.g. lists and tuples -- that aren't strings are returned as
    lists.

    If neither case is true,
    then a TypeError is raised (propagated from get_generic_mappend.

    It is possible to pass optional keyword arguments to generic_mappend
    by using kwargs.

    See:
        pynads.utils.monoidal.get_generic_mappend
        pynads.utils.monoidal.generic_mconcat
    """
    if hasattr(monoids[0], 'mconcat'):
        mconcat_ = monoids[0].mconcat
        return mconcat_(*monoids)
    else:
        return generic_mconcat(*monoids, **kwargs)
