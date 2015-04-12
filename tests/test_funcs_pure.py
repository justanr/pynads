from pynads.funcs import pure
from pynads.utils import iscallable
from pynads import Just


def test_identity():
    assert pure.identity(2) == 2
    assert Just(2).fmap(pure.identity) == Just(2)


def test_const():
    def inc(x): return x+1
    c = pure.const(inc)
    
    assert iscallable(c)
    assert c(4) is inc
    assert c()(4) == 5
    assert c.__name__ == 'inc'


def test_compose():
    def inc(x): return x+1
    def double(x): return x*2

    c = pure.compose(inc, double)

    assert iscallable(c)
    assert c(1) == 3
    assert c.__doc__ == 'Composition of: inc, double'

