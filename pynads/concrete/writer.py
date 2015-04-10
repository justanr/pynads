from ..utils import _iter_but_not_str_or_map
from ..abc import Monad
from ..funcs import fmap, mappend
from ..utils import is_monoid
from .list import List
from .mempty import Mempty


class Writer(Monad):
    """The Writer monad stores both a value and some side output, commonly
    referred to as a log because its usually used to track transformations
    on the stored value. However, Haskell and ``pynads`` allows using any
    monoid as the log value.

    Since the Functor and Applicative instances aren't that interesting,
    I'm just going to show the Haskell Monad instance as that's where the
    real magic happens!

        .. code-block:: Haskell
            data Writer w a = Writer { runWriter :: (a,w) }

            instance Monad (Writer w) where
                return x = Writer (x, mempty)
                (Writer (v, l)) >>= f = let (Writer (v', l')) = f v
                                        in Writer (v', l `mappend` l')

    The `return` operation just places a value in a Writer with a Mempty as
    the log value place holder. Bind however, not only expects to get a log
    from the function it binds to, it creates a third Writer which has the
    value from the second Writer and combines the logs from both previous
    Writers into a single cohesive log.

    ``pynads`` emulates this behavior, including allowing any monoidal value
    as the log with one cavaet: if the initial log value *isn't* a monoid,
    it's stuffed into a List monad which is. The definition of what is and
    isn't considered a monoid is determined by
    ``pynads.utils.monoidal.is_monoid`` so that's worth checking up on to
    see how to write (heh) binding functions for Writer.

    >>> w = Writer.unit(1)
    >>> w.v, w.log
    ... (4, Mempty)
    >>> w <<= lambda x: Writer(x+1, 'added one')
    >>> w.v, w.log
    ... (5, 'added one')

    However, Writer can be used for more than simply keeping a log of events.
    It can be used for keeping track of any secondary output a function
    that would otherwise become messy and bug prone.

    For example, you can add values to a dictionary on the side...

    >>> w = Writer(4, Mempty)
    >>> f = lambda x: Writer(x+1, {'a': x})
    >>> g = lambda x: Writer(x+2, {'b': x})
    >>> w >> f >> g
    ... Writer(7, {'a': 4, 'b': 5})

    Of course, Writer monad isn't really building some state to pass around,
    that's the job of another monad. Rather, it's about keep tracking of the
    status of something as it passes through transformations.
    """
    __slots__ = ()

    def __init__(self, v, log=Mempty):

        if not is_monoid(log):
            log = List.unit(log)

        super(Writer, self).__init__((v, log))

    @property
    def log(self):
        return self.v[1]

    @classmethod
    def unit(cls, v):
        """The most minimal context for a value in a Writer is a Writer with
        that value and a Mempty as the default value for the log.
        """
        return cls(v, Mempty)

    def fmap(self, f):
        """Call a function with the stored value as the input. Nothing fancy
        here.
        """
        return self.__class__(f(self.v[0]), self.v[1])

    def apply(self, applicative):
        """Take a function stored in this Writer and apply it to the next
        writer in the sequence. Nothing fancy here either.
        """
        return fmap(self.v[0], applicative)

    def bind(self, func):
        """As explained in the class docstring, bind takes the value stored
        in an instance of Writer and feeds it to a function that accepts
        that value and outputs a Writer as well. A new Writer is created
        which contains the new value and the combined logs of both
        previous Writers.

        >>> w = Writer.unit(4)
        >>> f = lambda x: Writer(x//2, ['divided by two'])
        >>> g = lambda x: Writer(str(x), ['converted to str'])
        >>> w >> f >> f
        ... Writer(1, ['divided by two', 'divided by two'])
        >>> w >> f >> g
        ... Writer('2', ['divided by two', 'converted to string'])

        The writer monad could also be used to track the values that
        pass through the transformations, as well...

        >>> w = Writer.unit(4)
        >>> f = lambda x: Writer(x//2, [x])
        >>> g = lambda x: Writer(str(x), [x])
        >>> w >> f >> g
        ... Writer('2', [4, 2])

        This bind operation will work with any compatible monads. which
        is either determined by their `mappend` method or by
        `pynads.utils.monoidal.get_generic_mappend`. Suffice to say,
        if your log is a boolean and you attempt merge them, you'll get a
        TypeError.
        """
        w = func(self.v[0])
        return self.__class__(w.v[0], mappend(self.v[1], w.v[1]))

    def __repr__(self):
        return "Writer({!r}, {!r})".format(self.v, self.log)
