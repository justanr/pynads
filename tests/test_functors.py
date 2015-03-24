import pytest
from pynads.functor import Functor
from pynads.funcs import fmap

class MyFunctor(Functor):
    def __init__(self, v):
        self.v = v

    def fmap(self, f):
        return MyFunctor(f(self.v))

def test_functor_not_instantiable():
    with pytest.raises(TypeError):
        Functor()

def test_fmap_calls_functor_fmap():
    x = fmap(lambda x: + 2, MyFunctor(0))
    assert isinstance(x, MyFunctor) and x.v == 2
