from pynads import funcs, Just
from pynads.utils import iscallable

add_two = lambda x: x+2
curried_add = lambda x: lambda y: x+y
m_add_two = lambda x: Just(x+2)

def test_fmap_func():
    assert funcs.fmap(add_two, Just(2)) == Just(4)


def test_unit_func():
    assert funcs.unit(2, Just) == Just(2)


def test_multiapply():
    j = Just.unit(curried_add)
    js = [Just(2), Just(2)]
    assert funcs.multiapply(j, *js) == Just(4)


def test_lift_func():
    assert funcs.lift(add_two, 2, Just) == Just(4)


def test_multibind():
    j = Just.unit(2)
    assert funcs.multibind(j, m_add_two, m_add_two) == Just(6)


def test_identity():
    assert funcs.identity(2) == 2
    assert funcs.fmap(funcs.identity, Just(2)) == Just(2)


def test_const():
    def inc(x): return x+1
    c = funcs.const(inc)
    
    assert iscallable(c)
    assert c(4) is inc
    assert c()(4) == 5
    assert c.__name__ == 'inc'


def test_compose():
    def inc(x): return x+1
    def double(x): return x*2

    c = funcs.compose(inc, double)

    assert iscallable(c)
    assert c(1) == 3
    assert c.__doc__ == 'Composition of: inc, double'
