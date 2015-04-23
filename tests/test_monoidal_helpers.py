from pynads.concrete import monoids
from pynads import Maybe, Just, Nothing
import pytest


checker = lambda x: not x % 3
inc = lambda x: x+1
double = lambda x: x*2
square = lambda x: x**2


@pytest.mark.parametrize('pair, result', [
    ((Just(4), Just(5)), Just(4)),
    ((Nothing, Nothing), Nothing),
    ((Nothing, Just(4)), Just(4)),
    ((Just(4), Nothing), Just(4))
])
def test_First_mappend(pair, result):
    assert monoids.First.mappend(*pair) == result


def test_First_mconcat():
    maybes = [Maybe(x, checker) for x in range(1, 4)]
    assert monoids.First.mconcat(*maybes) == Just(3)


@pytest.mark.parametrize('pair, result', [
    ((Just(4), Just(5)), Just(5)),
    ((Nothing, Nothing), Nothing),
    ((Nothing, Just(4)), Just(4)),
    ((Just(4), Nothing), Just(4))
])
def test_Last_mappend(pair, result):
    assert monoids.Last.mappend(*pair) == result


def test_Last_mconcat():
    maybes = [Maybe(x, checker) for x in range(1, 4)]
    assert monoids.Last.mconcat(*maybes) == Just(3)


def test_Sum_mappend():
    assert monoids.Sum.mappend(4, 6) == 10


def test_Sum_mconcat():
    assert monoids.Sum.mconcat(1, 2, 3) == sum([1, 2, 3]) == 6


def test_Product_mappend():
    assert monoids.Product.mappend(2, 3) == 6


def test_Product_mconcat():
    assert monoids.Product.mconcat(*range(1, 7)) == 720


def test_Endo_mappend():
    assert monoids.Endo.mappend(inc, double)(1) == (lambda x: x*2+1)(1) == 3


def test_Endo_mconcat():
    assert monoids.Endo.mconcat(inc, double, square)(2) == \
        (lambda x: x**2 * 2 + 1)(2) == \
        9
