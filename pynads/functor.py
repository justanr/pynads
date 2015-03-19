from abc import ABC, abstractmethod

class Functor(ABC):
    """Functors are data types that know how to be mapped over.

    To implement the functor protocol, all the subclass needs to do is implement
    fmap. fmap should return a new functor with the new data in it, preserving
    all other data.


        >>> class FMapDict(dict, Functor):
        >>>     def fmap(self, f):
        >>>         return FMapDict((k, f(v)) for k,v in self.items()))
    """
    @abstractmethod
    def fmap(self, f):
        return False


def fmap(f, functor):
    """Callable form of fmap."""
    return functor.fmap(f)