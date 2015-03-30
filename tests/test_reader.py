from operator import itemgetter
import pytest
from pynads import R #use Reader shortcut

#helpers
def inc(x):
    return x+1


def inc3(x):
    return x+3


def mul100(x):
    return x*100


#poor man's curry
def add_two(x):
    def adder(y):
        return x+y
    return adder


def madd(x):
    return R(add_two(x))


def mgetter(key):
    return R(itemgetter(key))


env = {'a':10, 'b':7}


#actual tests
def test_Reader_new_raises():    
    with pytest.raises(TypeError):
        R(None)


def test_Reader_call():
    r = R(inc)
    assert r(1) == r.v(1) == 2


def test_Reader_unit():
    r = inc & R
    assert r(None) is inc
    assert r(None)(1) == 2


def test_Reader_repr():
    r = R(inc)
    assert repr(r) == 'Reader(inc)'


def test_Reader_fmap():
    r = R(inc)
    rf = r.fmap(inc)
    assert rf(1) == 3


def test_Reader_apply():
    r = add_two & R
    s = r * R(inc3) * R(mul100)
    a = R(itemgetter('a'))
    b = R(itemgetter('b'))
    t = r * a * b
    assert s(5) == 508
    assert t(env) == 17


def test_Reader_apply_meta():
    r = add_two & R
    s = r * R(inc3)
    t = s * R(mul100)

    assert s.v.__name__ == 'add_two_o_inc3'
    assert s.v.__doc__  == 'Application of add_two, inc3'
    assert t.v.__name__ == 'add_two_o_inc3_o_mul100'
    assert t.v.__doc__  == 'Application of add_two_o_inc3, mul100'


def test_Reader_bind():
    r = R(inc)
    s = r >> madd
    t = s >> madd
    assert s(1) == 3
    assert t(1) == 4


def test_Reader_bind_meta():
    s = R(inc) >> madd
    t = s >> madd

    assert s.v.__name__ == 'inc_x_madd'
    assert s.v.__doc__  == 'Bind of inc, madd'
    assert t.v.__name__ == 'inc_x_madd_x_madd'
    assert t.v.__doc__  == 'Bind of inc_x_madd, madd'
