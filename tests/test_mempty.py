from decimal import Decimal
from pynads import Mempty, List, Map
from pynads.concrete.mempty import _Mempty
from pynads.funcs import mconcat, mappend
import pytest


def test_Mempty_is_singleton():
    assert Mempty is _Mempty()


def test_Mempty_mempty_is_Mempty():
    assert Mempty.mempty is Mempty


@pytest.mark.parametrize('monoid', [
    [4], [{1,2}], [List(1,2)], [Map({'a': 10})],
    [True], pytest.mark.xfail([Decimal('0')])
])
def test_Mempty_mappend(monoid):
    assert Mempty.mappend(monoid) == monoid


@pytest.mark.parametrize('monoids, result', [
    ((1,2,3), 6), ((1, Mempty, 2, 3), 6),
    ([[1], [2],[3]], [1,2,3]), ([Mempty, [1], [2], [3]], [1,2,3])

])
def test_Mempty_mconcat(monoids, result):
    assert Mempty.mconcat(*monoids) == result


def test_Mempty_mconcat_with_all_mempties():
    assert Mempty.mconcat(Mempty, Mempty) is Mempty


@pytest.mark.parametrize('monoid', [
    [List(1,2,3)], [{1,2}], [3], [True]
])
def test_Mempty_reflect_mappend(monoid):
    assert Mempty._reflected_mappend(monoid) == monoid
    assert mappend(monoid, Mempty) == monoid


@pytest.mark.parametrize('monoids, result', [
    ((1,2,3, Mempty), 6), ((List(1,2,3), Mempty, List(4)), List(1,2,3,4)),
    ((True, Mempty, True, False), True), ((Mempty, 1, 2, 3), 6),
    (({'a':10}, Mempty, {'b':7}), {'a':10, 'b':7})
])
def test_Mempty_reflected_mappend_in_mconcat(monoids, result):
    assert mconcat(*monoids) == result
