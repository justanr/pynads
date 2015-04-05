from decimal import Decimal
import pytest
from pynads import funcs, Just, List
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


def test_known_mempty():
    objs = (2, [1,2], {'a':1}, {4}, 'hello', 1.2, frozenset([4]), (4,), 1+0j)

    assert all(funcs.mempty(o) == type(o)() for o in objs)


def test_mempty_with_monoid():
    assert funcs.mempty(List) == ()


def test_mempty_raises_with_unknown():
    with pytest.raises(TypeError) as error:
        funcs.mempty(object())

    assert "No known mempty" in str(error.value)


def test_mappend():
    m = List(1)
    n = List(2)
    assert funcs.mappend(m, n) == List(1,2)


def test_known_mappend():
    ints = (1,2)
    floats = [float(x) for x in ints]
    complexes = [complex(x) for x in ints]
    # Decimal is an "unknown" type, but can be determined to a Number instance
    decimals = [Decimal(str(x)) for x in ints]
    strs = [str(x) for x in ints]
    lists = [[x] for x in ints]
    tuples = [(x,) for x in ints]
    sets = [{x} for x in ints]
    frozensets = [frozenset([x]) for x in ints]
    dicts = [{x:x} for x in ints]

    assert funcs.mappend(*ints) == 3
    assert funcs.mappend(*floats) == 3.0
    assert funcs.mappend(*complexes) == 3+0j
    assert funcs.mappend(*decimals) == Decimal('3')
    assert funcs.mappend(*strs) == '12'
    assert funcs.mappend(*lists) == [1,2]
    assert funcs.mappend(*tuples) == [1,2]
    assert funcs.mappend(*sets) == {1,2}
    assert funcs.mappend(*frozensets) == frozenset(ints)
    assert funcs.mappend(*dicts) == {1:1, 2:2}


def test_mappend_raises_with_unknown():
    with pytest.raises(TypeError) as error:
        funcs.mappend(object(), object())

    assert "No known generic" in str(error.value)


def test_mconcat():
    ls = [List(x) for x in range(4)]
    assert funcs.mconcat(*ls) == List(0,1,2,3)

def test_known_mconcat():
    ints = (1,2,3)
    floats = [float(x) for x in ints]
    complexes = [complex(x) for x in ints]
    decimals = [Decimal(str(x)) for x in ints]
    strs = [str(x) for x in ints]
    lists = [[x] for x in ints]
    tuples = [(x,) for x in ints]
    sets = [{x} for x in ints]
    frozensets = [frozenset([x]) for x in ints]
    dicts = [{x:x} for x in ints]

    assert funcs.mconcat(*ints) == 6
    assert funcs.mconcat(*floats) == 6.0
    assert funcs.mconcat(*complexes) == 6+0j
    assert funcs.mconcat(*decimals) == Decimal("6")
    assert funcs.mconcat(*strs) == '123'
    assert funcs.mconcat(*lists) == [1,2, 3]
    assert funcs.mconcat(*tuples) == [1,2, 3]
    assert funcs.mconcat(*sets) == {1,2, 3}
    assert funcs.mconcat(*frozensets) == frozenset(ints)
    assert funcs.mconcat(*dicts) == {1:1, 2:2, 3:3}
