from decimal import Decimal
from pynads.funcs import monoid
from pynads import List
import pytest

def test_known_mempty():
    objs = (2, [1,2], {'a':1}, {4}, 'hello', 1.2, frozenset([4]), (4,), 1+0j)

    assert all(monoid.mempty(o) == type(o)() for o in objs)


def test_mempty_with_monoid():
    assert monoid.mempty(List) == List()


def test_mempty_raises_with_unknown():
    with pytest.raises(TypeError) as error:
        monoid.mempty(object())

    assert "No known mempty" in str(error.value)


def test_mappend():
    m = List(1)
    n = List(2)
    assert monoid.mappend(m, n) == List(1,2)


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

    assert monoid.mappend(*ints) == 3
    assert monoid.mappend(*floats) == 3.0
    assert monoid.mappend(*complexes) == 3+0j
    assert monoid.mappend(*decimals) == Decimal('3')
    assert monoid.mappend(*strs) == '12'
    assert monoid.mappend(*lists) == [1,2]
    assert monoid.mappend(*tuples) == [1,2]
    assert monoid.mappend(*sets) == {1,2}
    assert monoid.mappend(*frozensets) == frozenset(ints)
    assert monoid.mappend(*dicts) == {1:1, 2:2}


def test_mappend_raises_with_unknown():
    with pytest.raises(TypeError) as error:
        monoid.mappend(object(), object())

    assert "No known generic" in str(error.value)


def test_mconcat():
    ls = [List(x) for x in range(4)]
    assert monoid.mconcat(*ls) == List(0,1,2,3)


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

    assert monoid.mconcat(*ints) == 6
    assert monoid.mconcat(*floats) == 6.0
    assert monoid.mconcat(*complexes) == 6+0j
    assert monoid.mconcat(*decimals) == Decimal("6")
    assert monoid.mconcat(*strs) == '123'
    assert monoid.mconcat(*lists) == [1,2, 3]
    assert monoid.mconcat(*tuples) == [1,2, 3]
    assert monoid.mconcat(*sets) == {1,2, 3}
    assert monoid.mconcat(*frozensets) == frozenset(ints)
    assert monoid.mconcat(*dicts) == {1:1, 2:2, 3:3}
