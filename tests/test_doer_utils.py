from functools import WRAPPER_ASSIGNMENTS
from pynads.do import utils, MonadReturn, MonadFinished
import pytest


def test_kwargs_deco_looks_like_wrapped():
    def my_deco(func, thing):
        "a doc string"
        return func
    
    wrapped = utils.kwargs_decorator(my_deco)
    assert wrapped.__wrapped__ is my_deco
    assert all(getattr(my_deco, attr) == getattr(wrapped, attr) 
               for attr in WRAPPER_ASSIGNMENTS)


def test_kwargs_deco_actually_works():
    @utils.kwargs_decorator
    def my_deco(func, thing):
        func.thing = thing
        return func

    @my_deco(thing=True)
    def tester():
        pass

    assert tester.thing


def test_kwargs_decorator_on_class():
    @utils.kwargs_decorator
    class W(object):
        def __init__(self, f, thing):
            utils.update_wrapper(self, f)
            self.thing = thing
            self.f = f

        def __call__(self, *a, **k):
            return self.f(*a, **k)

    wrapped_w = utils.kwargs_decorator(W)

    @wrapped_w(thing=True)
    def tester(x):
        "a doc string"
        return x

    assert wrapped_w.__wrapped__ is W
    assert all(getattr(W, attr) == getattr(wrapped_w, attr) 
               for attr in WRAPPER_ASSIGNMENTS)
    assert tester.thing
    assert tester.__doc__ == "a doc string"
    assert tester.__name__ == 'tester'


def test_kwargs_decorator_with_defaults():
    @utils.kwargs_decorator
    def test_deco(f, thing=True):
        f.thing = thing
        return f

    @test_deco
    def test():
        pass

    assert test.thing

def test_mreturn_raises():
    with pytest.raises(MonadReturn) as mr:
        utils.mreturn(4)

    assert mr.value.v == 4


def test_mfinished_raises():
    with pytest.raises(MonadFinished) as mf:
        utils.mfinished(4)

    assert mf.value.v == 4
