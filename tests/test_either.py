import pytest
from gonads.either import Either, Left, Right

add_two = lambda x: x+2
m_add_two = lambda x: Right(add_two(x))
l_add_two = lambda x: Left("failed")

def test_cant_make_either():
    with pytest.raises(TypeError) as excinfo:
        e = Either()

    assert "Instantiate Left or Right directly." == str(excinfo.value)
    assert 'e' not in locals()


def test_truthiness():
    assert bool(Right(2))
    assert not bool(Left('failed'))
    assert Right(2) == Right(2)
    assert Left('failed') == Left('failed')


def test_Left_immutability():
    with pytest.raises(AttributeError):
        Left(2).msg = 'failure'


def test_Right_immutability():
    with pytest.raises(AttributeError):
        Right(2).v = 4


def test_left_transforms():
    a = Left('failed')
    assert a.fmap(add_two) is a
    assert a.apply(Left('failure')) is a
    assert (a >> add_two) is a


def test_right_fmap():
    assert Right(2).fmap(add_two) == Right(4)


def test_right_apply():
    assert Right(add_two) * Right(2) == Right(4)


def test_right_bind():
    assert (Right(2) >> m_add_two) == Right(4)


def test_left_propagates():
    assert (Right(2) >> l_add_two >> add_two) == Left('failed')
