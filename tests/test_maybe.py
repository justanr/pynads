from pynads import Maybe, Just, Nothing
from pynads.concrete.maybe import _Nothing

add_two = lambda x: x+2
m_add_two = lambda x: Just(x+2)
n_add_two = lambda x: Nothing


def test_maybe_new():
    assert isinstance(Maybe(4), Just)
    assert Maybe(None) is Nothing
    assert Maybe(4, checker=lambda x: x & 1) is Nothing


def test_maybe_custom_check():
    c = lambda x: x & 1
    assert Maybe(1, checker=c) == Just(1)
    assert Maybe(2, checker=c) is Nothing


def test_truthiness():
    assert not bool(Nothing)
    assert bool(Just(1))
    assert Nothing == Nothing
    assert Just(1) == Just(1)


def test_nothing_singleton():
    assert _Nothing() is Nothing


def test_just_fmap():
    assert Just(2).fmap(add_two) == Just(4)


def test_just_apply():
    assert Just(add_two).apply(Just(2)) == Just(4)


def test_Just_bind():
    assert (Just(2) >> m_add_two) == Just(4)


def test_Just_get_or():
    assert Just(2).get_or(3) == 2


def test_Just_get_or_call():
    assert Just(2).get_or_call(add_two, 1) == 2


def test_Just_or_else():
    assert Just(2).or_else(Nothing) == Just(2)


def test_Just_or_call():
    assert Just(2).or_call(m_add_two, 1) == Just(2)


def test_Just_filter():
    assert Just(2).filter(lambda x: x % 2 == 0) == Just(2)


def test_Just_chain_many():
    x = Just(2).fmap(add_two).bind(m_add_two).filter(lambda x: not x % 3) \
        .or_else(Just(3))

    assert x == Just(6)


def test_Nothing_fmap():
    assert Nothing.fmap(add_two) is Nothing


def test_Nothing_apply():
    assert Nothing.apply(add_two) is Nothing


def test_Nothing_bind():
    assert (Nothing >> m_add_two) is Nothing


def test_Nothing_propagates():
    assert (Just(2) >> n_add_two >> add_two) is Nothing


def test_Nothing_filter():
    assert Nothing.filter(lambda x: x > 4) is Nothing


def test_Nothing_get_or():
    assert Nothing.get_or(3) == 3


def test_Nothing_get_or_call():
    assert Nothing.get_or_call(add_two, 2) == 4


def test_Nothing_or_else():
    assert Nothing.or_else(4) == Just(4)


def test_Nothing_or_call():
    assert Nothing.or_call(add_two, 2) == Just(4)


def test_Nothing_chain_many():
    x = Nothing.or_call(add_two, 2).filter(lambda x: x & 1)
    assert x is Nothing


def test_Maybe_wrap():
    @Maybe.as_wrapper(checker=lambda x: x % 2)
    def derp(x):
        'Subtract one from a number.'
        return x - 1

    assert derp.__name__ == 'derp'
    assert derp.__doc__ == 'Subtract one from a number.'
    assert derp(2) == Just(1)
    assert derp(3) == Nothing
    assert derp(12).fmap(lambda x: x//2).or_else(1) == Just(5)
