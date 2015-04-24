from decimal import Decimal
from pynads.funcs import monoid
from pynads import List
import pytest


ints = (1, 2, 3)

def list_of(maker, stuff):
    return [maker(x) for x in stuff]


@pytest.mark.parametrize('o, expected', [
    (2, 0),
    ([1, 2], []),
    ({'a': 1}, {}),
    ({4}, set()),
    ('hello', ''),
    (1.2, 0),
    (frozenset([4]), set()),
    ((4,), []),
    (1+0j, 0)
])
def test_known_mempty(o, expected):
    assert monoid.mempty(o) == expected


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


@pytest.mark.parametrize('ms, res', [
    (ints, 6),
    (list_of(float, ints), 6.0),
    (list_of(complex, ints), 6.0+0j),
    (list_of(lambda a: {a}, ints), set(ints)),
    (list_of(lambda a: frozenset([a]), ints), frozenset(ints)),
    (list_of(lambda a: [a], ints), list(ints)),
    (list_of(str, ints), '123'),
    (list_of(lambda a: {a: a}, ints), {1: 1, 2: 2, 3: 3}),
    (list_of(lambda a: (a, ), ints), [1, 2, 3,])
])
def test_known_mconcat(ms, res):
    assert monoid.mconcat(*ms) == res
