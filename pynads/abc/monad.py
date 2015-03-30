from abc import abstractmethod
from .applicative import Applicative


class Monad(Applicative):
    """Base Monad class. Provides an abstract bind method
    as well as two concrete methods: >> and <<=. These are
    in addition to the abstract and concrete methods provided
    by Applicative.

    ``bind`` should provide a value (or values) from the Monad
    to a function that returns a Monad. However, there's no way
    to reasonably enforce this in Python, so it's a contract.

    ``>>`` and ``<<=`` are helper operators to bind.

    * ``>>`` is essentially Haskell's `>>=`
    """
    __slots__ = ()

    @abstractmethod
    def bind(self, f):
        """Pushes a value into a monadic transformer function.

        :param callable f: A callable the accepts a single plain value
        and returns a monad.

        >>> Just(4).bind(lambda x: Just(x+2) if x > 4 else Nothing())
        ... Nothing

        Since the result of bind should be an instance of Monad, it's
        possible to chain multiple calls together:

        >>> add_two = lambda x: Just(x+2)
        >>> Just(2).bind(add_two).bind(add_two)
        """
        return False

    def __rshift__(self, f):
        """Pushes a value into a monadic transformer function.

        :param callable f: A callable that accepts a single plain value
        and returns a monad.

        >>> Just(4) >> (lambda x: Just(x+2) if x > 4 else Nothing())
        ... Nothing

        It's also possible to chain multiple transforms together:

        >>> add_two = lambda x: Just(x+2)
        >>> Just(2) >> add_two >> add_two
        ... Just 6

        """
        return self.bind(f)

    def __ilshift__(self, f):
        """Helper operator. The same as using bind or >> but
        as an assignment operator. The return value is *new* monad
        not an altered one.

        >>> m = Right(4)
        >>> m <<= lambda x: Right(x+2) if x < 1 else Left("greater than 1")
        >>> print(m)
        Left greater than 1

        """
        return self.bind(f)
