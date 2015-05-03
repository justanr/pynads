import pytest
from pynads import Either, Left, Right

add_two = lambda x: x+2
m_add_two = lambda x: Right(add_two(x))
l_add_two = lambda x: Left("failed")


def test_cant_make_either():
    with pytest.raises(TypeError):
        Either()


def test_truthiness():
    assert bool(Right(2))
    assert not bool(Left('failed'))
    assert Right(2) == Right(2)


def test_left_transformers():
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


def test_Right_get_or():
    assert Right(2).get_or(3) == 2


def test_Right_get_or_call():
    assert Right(2).get_or_call(lambda x: x, 3) == 2


def test_Right_or_else():
    assert Right(2).or_else(Right(3)) == Right(2)


def test_Right_or_call():
    assert Right(2).or_call(lambda: Right(3)) == Right(2)


def test_Right_filter():
    def even(x):
        return not x % 2

    assert Right(2).filter(even) == Right(2)
    assert Right(3).filter(even) == Left('even false with input 3')


def test_Right_chain_many():
    assert Right(2).fmap(add_two).bind(m_add_two).filter(lambda x: not x % 2) \
        .or_else(Right(3)) == Right(6)


def test_left_propagates():
    assert (Right(2) >> l_add_two >> add_two) == Left('failed')


def test_Left_get_or():
    assert Left('failure').get_or(2) == 2


def test_Left_get_or_call():
    assert Left('failure').get_or_call(lambda: 2) == 2


def test_Left_or_else():
    assert Left('failure').or_else(2) == Right(2)
    assert Left('failure').or_else(None) == Left('None provided')


def test_Left_or_call():
    def raise_if_odd(x):
        if not x % 2:
            return x
        else:
            raise TypeError("odd provided")

    assert Left('failure').or_call(raise_if_odd, 2) == Right(2)
    err = Left('failure').or_call(raise_if_odd, 3)
    assert isinstance(err, Left) and isinstance(err.v, TypeError) and \
        err.v.args == ('odd provided',)

def test_Either_as_wrapper():
    @Either.as_wrapper(expect=KeyError)
    def get_key(d, key):
        """Returns value from dict based on key"""
        return d[key]

    assert get_key.__doc__ == "Returns value from dict based on key"
    assert get_key({'a': 4}, 'a') == Right(4)

    err = get_key({}, 'a')
    assert isinstance(err.v, KeyError) and repr(err) == "Left KeyError('a',)"
