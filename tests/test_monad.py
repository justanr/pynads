import pytest
from pynads.monad import Monad
from pynads.funcs import multibind

class MyMonad(Monad):
    
    def __init__(self, v):
        self.v = v

    @classmethod
    def unit(cls, v):
        return cls(v)

    def fmap(self, v):
        return MyMonad(f(self.v))

    def apply(self, applicative):
        return fmap(self.v, applicative)

    def bind(self, f):
        return f(self.v)

    def __eq__(self, other):
        return isinstance(other, MyMonad) and self.v == other.v

add_two = lambda x: MyMonad(x+2)

def test_bind():
    assert MyMonad.unit(2).bind(add_two) == MyMonad.unit(4)

def test_rshift_bind():
    assert (MyMonad.unit(2) >> add_two) == MyMonad.unit(4)

def test_lshift_assign_bind():
    a = MyMonad.unit(2)
    b = a
    a <<= lambda x: MyMonad(x+2)

    assert a is not b
    assert a == MyMonad.unit(4)

def test_multibind():
    assert multibind(MyMonad.unit(2), add_two, add_two) == MyMonad.unit(6)
