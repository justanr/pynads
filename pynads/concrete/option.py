from abc import abstractmethod
from ..abc import Container, Functor
from ..utils.compat import wraps
from ..utils.decorators import method_optional_kwargs
from ..utils.internal import _propagate_self


class Option(Functor):
    """Option is similar to Maybe and Either in that its members represent
    both a successful computation or a failure. However, Option provides
    a means to recover from a bad computation through its or methods:

        - get_or: If called on a Full value, this returns the value stored,
        but if called on an Empty, it returns the provided value instead.
        - get_or_call: If called on a Full value, the value stored in Full
        is returned, but if called on an Empty value the provided function
        is called with the provided arguments and the result is returned
        - or_else: When called on a Full value, the Full simply propagates,
        but when called on an Empty value, the provided default is wrapped in
        Option and returned instead.
        - or_call: When called on a Full value, the Full simply propagates
        but when called on an Empty value the provided function is called
        with the provided arguments and the result is wrapped in Option and
        returned.

    Option is also a Haskell style functor, meaning it can be fmapped over. It
    follows the same rules as Maybe and Either: Fulls can be mapped over,
    changing their value; while Empty will simple return itself from the fmap.

    Option also provides the filter method, which essentially allows a check
    against the potentially stored value. On Full, if the check is successful
    the Full is returned, otherwise Empty pops out. Filtering on Empty always
    results in an Empty.

    Option also provides a decorator method to place values inside either a Full
    or replacing them with an Empty immediately based on an arbitrary check. By
    default, the check is ``lambda x: x is not None`` but can be overriden if
    needed.

    This class is inspired by both Scala's Option (obviously) and fn.py's
    implementation of Option as well.
    """
    __slots__ = ()

    def __new__(cls, v, checker=lambda x: x is not None):
        return Full(v) if checker(v) else Empty

    def __bool__(self):
        return isinstance(self, Full)

    __nonzero__ = __bool__

    @method_optional_kwargs
    @classmethod
    def as_wrapper(cls, func, checker=lambda x: x is not None):
        @wraps(func)
        def optioner(*args, **kwargs):
            return cls(func(*args, **kwargs), checker=checker)
        return optioner

    @abstractmethod
    def filter(self, predicate):
        pass

    @abstractmethod
    def get_or(self, default):
        pass

    @abstractmethod
    def get_or_call(self, func, *args, **kwargs):
        pass

    @abstractmethod
    def or_else(self, default):
        pass

    @abstractmethod
    def or_call(self, func, args, **kwargs):
        pass


class Full(Option):
    """Value ready for more processing through the fmap and filter methods.
    """
    __slots__ = ()

    def __new__(cls, v):
        return Container.__new__(cls)

    def __repr__(self):
        return "Full({!r})".format(self.v)

    def __eq__(self, other):
        return isinstance(other, Full) and self.v == other.v

    def fmap(self, func):
        return Full(func(self.v))

    def filter(self, predicate):
        return self if predicate(self.v) else Empty

    def get_or(self, default):
        return self.v

    def get_or_call(self, func, *args, **kwargs):
        return self.v

    or_else = or_call = _propagate_self


class _Empty(Option):
    """A recoverable failure in a processing line through get_or, get_or_call,
    or_else and or_call. _Empty is implemented as a singleton as it stores
    no data.
    """
    __slots__ = ()
    _inst = None

    def __new__(cls, *args, **kwargs):
        if cls._inst is None:
            cls._inst = Container.__new__(cls)
        return cls._inst

    def __repr__(self):
        return "Empty"

    def __eq__(self, other):
        return self is other or isinstance(other, _Empty)

    @staticmethod
    def _get_val():
        return Empty

    fmap = filter = _propagate_self

    @staticmethod
    def get_or(default):
        """Returns the default value provided as Empty posseses no value.
        """
        return default

    @staticmethod
    def get_or_call(func, *args, **kwargs):
        """Calls the provided function with the provided arguments as Empty
        possess no values.
        """
        return func(*args, **kwargs)

    @staticmethod
    def or_else(default):
        """Returns the provided default wrapped in an Option.
        """
        return Option(default)

    @staticmethod
    def or_call(func, *args, **kwargs):
        """Returns the provided function with the provided arguments and the
        result is wrapped in an Option.
        """
        return Option(func(*args, **kwargs))

Empty = _Empty()
