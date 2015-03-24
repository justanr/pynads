from abc import ABCMeta, abstractmethod

class Functor(metaclass=ABCMeta):
    """Functors are data types that know how to be mapped over.

    To implement the functor protocol, all the subclass needs to do is implement
    fmap. fmap should return a new functor with the new data in it, preserving
    all other data.


        >>> class FMapDict(dict, Functor):
        >>>     def fmap(self, f):
        >>>         return FMapDict((k, f(v)) for k,v in self.items()))
    """
    __slots__ = ()
    @abstractmethod
    def fmap(self, f):
        return False
