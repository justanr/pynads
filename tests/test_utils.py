import pytest
from functools import partial
from pynads import utils

def test_check_utils_iter():
    assert utils._iter_but_not_str_or_map([])
    assert utils._iter_but_not_str_or_map(set())
    assert utils._iter_but_not_str_or_map(())
    assert not utils._iter_but_not_str_or_map('')
    assert not utils._iter_but_not_str_or_map({})


def test_propagate_self():
    class Test(object):
        def __init__(self, v):
            self.v = v

        # intended use of utils._propagate_self
        __call__ = utils._propagate_self

    t = Test(4)

    assert t() is t


def test_with_metaclass():
    
    class MyMeta(type):
        pass

    class Test(utils.with_metaclass(MyMeta)):
        pass

    assert isinstance(Test, MyMeta)

def test_single_value_iter():
    i = utils._single_value_iter(1)
    j = utils._single_value_iter(2)

    assert next(i) == 1
    with pytest.raises(StopIteration):
        next(i)
    assert list(j) == [2]

def test_iscallable():
    class PassTest(object):
        def __call__(self):
            pass

    class FailTest(object):
        pass

    
    def funcpass():
        pass

    assert utils.iscallable(funcpass)
    assert utils.iscallable(lambda x: x)
    assert utils.iscallable(PassTest())
    assert not utils.iscallable(FailTest())
    assert not utils.iscallable('failure')


def test_get_name():
    def inc(x): x+1

    class Test(object):
        pass

    f = partial(inc, 1)

    assert utils._get_name(inc) == 'inc'
    assert utils._get_name(f) == 'partialed inc'
    assert utils._get_name(Test()) == 'Test'


def test_get_names():
    def inc(x): x+1
    f = partial(inc, 1)

    class Test(object):
        pass

    fs = [inc, f, Test()]

    def dummy(*fs):
        pass

    dummy.fs = fs

    assert utils._get_names(*fs) == ['inc', 'partialed inc', 'Test']
    assert utils._get_names(dummy) == ['inc', 'partialed inc', 'Test']
    assert utils._get_names(inc, dummy) == ['inc', 'inc', 'partialed inc', 'Test']
