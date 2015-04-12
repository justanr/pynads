from functools import WRAPPER_ASSIGNMENTS
from pynads.utils import decorators, update_wrapper

def test_kwargs_deco_looks_like_wrapped():
    def my_deco(func, thing):
        "a doc string"
        return func
    
    wrapped = decorators.kwargs_decorator(my_deco)
    assert wrapped.__wrapped__ is my_deco
    assert all(getattr(my_deco, attr) == getattr(wrapped, attr) 
               for attr in WRAPPER_ASSIGNMENTS)


def test_kwargs_deco_actually_works():
    @decorators.kwargs_decorator
    def my_deco(func, thing):
        func.thing = thing
        return func

    @my_deco(thing=True)
    def tester():
        pass

    assert tester.thing


def test_kwargs_decorator_on_class():
    @decorators.kwargs_decorator
    class W(object):
        def __init__(self, f, thing):
            update_wrapper(self, f)
            self.thing = thing
            self.f = f

        def __call__(self, *a, **k):
            return self.f(*a, **k)

    wrapped_w = decorators.kwargs_decorator(W)

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
    @decorators.kwargs_decorator
    def test_deco(f, thing=True):
        f.thing = thing
        return f

    @test_deco
    def test():
        pass

    assert test.thing


def test_annotate():
    @decorators.annotate(type="(a -> b) -> [a] -> [b]")
    def my_map(f, xs):
        pass

    assert "my_map :: (a -> b) -> [a] -> [b]" in my_map.__doc__
