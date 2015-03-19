from abc import abstractmethod
from functools import reduce
from operator import mul
from .functor import Functor

class Applicative(Functor):
    """Applicative Functors are data types that can store potential 
    computations. Since Applicative Functors are also functors, they are also
    mappable and must implement the `fmap` method.

    Applicative offers two abstract methods and one concrete method.

    ``apply`` is the way applicative interactive with each other. The initial
    Applicative needs to be a function that will accept all following
    Applicatives as arguments. It's possible to chain multiple calls to
    apply together if the initial function accepts 

    >>> S_mul_two  Something.unit(curry(lambda x, y: x*y))
    >>> S_mul_two.apply(Something(4)).apply(Something(5))
    ... Something 20

    ``unit`` puts a value in the most minimal context needed to form the
    Applicative. In most cases, it will simply be `self.__class__(v)` However,
    it is possible to store multiple values in an Applicative, so no default
    implementation is provided.

    ``__mul__`` (*) is short hand for apply and allows quickly stringing
    together Applicatives.

    >>> S_mul_two  Something.unit(curry(lambda x, y: x*y))
    >>> S_mul_two * Something(4) * Something(5)
    ... Something 20
    """
    def __mul__(self, f):
        """Shortcut to Applicative.apply for quickly stringing
        Applicatives together.
        """
        return self.apply(f)

    @abstractmethod
    def apply(self, functor):
        return False

    @abstractmethod
    def unit(v):
        return NotImplemented

def unit(v, applicative):
    """Puts a value in the minimum necessary context to form an Applicative.
    """
    return applicative.unit(v)

def multiapply(initial, *args):
    """Shorthand for stringing many applicatives together.

    This is designed for use with a curried function that will gradually
    build until it reaches the correct number of arguments to call itself.
    """
    return reduce(mul, args, initial)
