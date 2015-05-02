from functools import WRAPPER_ASSIGNMENTS
from pynads.utils import decorators, update_wrapper


def generate_test_class():
    class Test(object):
        @decorators.method_optional_kwargs
        def instm(self, f, **notes):
            """Instance Method"""
            f.notes = notes
            return f

        @decorators.method_optional_kwargs
        @classmethod
        def clsm(cls, f, **notes):
            """Class Method"""
            f.notes = notes
            return f

        @decorators.method_optional_kwargs
        @staticmethod
        def statm(f, **notes):
            """Static Method"""
            f.notes = notes
            return f

    return Test


def test_kwargs_deco_looks_like_wrapped():
    def my_deco(func, thing):
        "a doc string"
        return func

    wrapped = decorators.optional_kwargs(my_deco)
    assert wrapped.__wrapped__ is my_deco
    assert all(getattr(my_deco, attr) == getattr(wrapped, attr)
               for attr in WRAPPER_ASSIGNMENTS)


def test_kwargs_deco_actually_works():
    @decorators.optional_kwargs
    def my_deco(func, thing):
        func.thing = thing
        return func

    @my_deco(thing=True)
    def tester():
        pass

    assert tester.thing


def test_optional_kwargs_on_class():
    @decorators.optional_kwargs
    class W(object):
        def __init__(self, f, thing):
            update_wrapper(self, f)
            self.thing = thing
            self.f = f

        def __call__(self, *a, **k):
            return self.f(*a, **k)

    wrapped_w = decorators.optional_kwargs(W)

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


def test_optional_kwargs_with_defaults():
    @decorators.optional_kwargs
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


def test_method_optional_kwargs_wraps_descriptors():
    Test = generate_test_class()
    assert "Instance Method" == Test.instm.__doc__
    assert "Class Method" == Test.clsm.__doc__
    assert "Static Method" == Test.statm.__doc__


def test_method_optional_kwargs_works():
    Test = generate_test_class()
    t = Test()

    @t.instm(test=True)
    def test1(*args, **kwargs):
        """Wrapped by instance"""
        return 1

    @Test.clsm(test=True)
    def test2(*args, **kwargs):
        """Wrapped by classmethod"""
        return 2

    @Test.statm(test=True)
    def test3(*args, **kwargs):
        """Wrapped by staticmethod"""
        return 3

    assert all(f.notes['test'] for f in [test1, test2, test3])
    assert "Wrapped by instance" == test1.__doc__
    assert test1() == 1
    assert "Wrapped by classmethod" == test2.__doc__
    assert test2() == 2
    assert "Wrapped by staticmethod" == test3.__doc__
    assert test3() == 3
