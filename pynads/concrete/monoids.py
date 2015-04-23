from operator import add, mul
from .maybe import Nothing
from ..abc import Monoid
from ..funcs.pure import identity, compose
from ..utils.compat import filter


__all__ = ('First', 'Last', 'Product', 'Sum')


class First(Monoid):
    """Monoid helper for Maybe which finds the first Just value in a sequence
    when mappending or mconcatting.
    """
    mempty = Nothing

    @staticmethod
    def mappend(first, second):
        if first:
            return first
        elif second:
            return second
        else:
            return Nothing

    @staticmethod
    def mconcat(*monoids):
        """Since First looks for the first Just instance in a sequence,
        there's no point in running the sequence to completion when a short
        circuit can be used to bailout when a Just is found.
        """
        return next(filter(bool, monoids), Nothing)


class Last(First):
    """Monoid helper for Maybe which finds the last Just value in a sequence
    when mappending or mconcatting.
    """
    @staticmethod
    def mappend(first, second):
        return super(Last, Last).mappend(second, first)

    @staticmethod
    def mconcat(*monoids):
        return super(Last, Last).mconcat(*reversed(monoids))


class Sum(Monoid):
    """Monoid helper for Number objects that performs addition over the
    numbers.
    """
    mempty = 0
    mappend = staticmethod(add)

    @staticmethod
    def mconcat(*monoids):
        return sum(monoids)


class Product(Monoid):
    """Monoid helper for Number objects that performs multiplication over
    the numbers.
    """
    mempty = 1
    mappend = staticmethod(mul)


class Endo(Monoid):
    """Functions form a monoid under composition if they receive and output
    a value of the same type, i.e. they are ``a -> a``. The mempty for the
    function monoid is identity, which just outputs its input.

    Since the pynads implementation of compose accepts any number of functions
    as its arguments, it's trivial to assign it to both mappend and mconcat
    by wrapping it in staticmethod.
    """
    mempty = identity
    mappend = mconcat = staticmethod(compose)
