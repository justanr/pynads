import pytest
from pynads import Either, Left, Right

add_two = lambda x: x+2
m_add_two = lambda x: Right(add_two(x))
l_add_two = lambda x: Left("failed")

def test_cant_make_either():
    with pytest.raises(TypeError) as excinfo:
        e = Either()


def test_truthiness():
    assert bool(Right(2))
    assert not bool(Left('failed'))
    assert Right(2) == Right(2)


def test_left_transforms():
    a = Left('failed')
    assert a.fmap(add_two) is a
    assert a.apply(Left('failure')) is a
    assert (a >> add_two) is a


def test_left_proxy_returns_false():
    a = Left('failed')
    assert not a.proxy(lambda x: x == 1)
    assert not a.starproxy(lambda x, y: x+y, 1)


def test_right_fmap():
    assert Right(2).fmap(add_two) == Right(4)


def test_right_apply():
    assert Right(add_two) * Right(2) == Right(4)


def test_right_bind():
    assert (Right(2) >> m_add_two) == Right(4)


def test_left_propagates():
    assert (Right(2) >> l_add_two >> add_two) == Left('failed')
