from pynads import Maybe, Just, Nothing
from pynads.concrete.maybe import _Nothing

add_two = lambda x: x+2
m_add_two = lambda x: Just(x+2)
n_add_two = lambda x: Nothing


def test_maybe_new():
    assert isinstance(Maybe(4), Just)
    assert Maybe(None) is Nothing
    assert Maybe(4, checker=lambda x: x&1) is Nothing


def test_truthiness():
    assert not bool(Nothing)
    assert bool(Just(1))
    assert Nothing == Nothing
    assert Just(1) == Just(1)


def test_nothing_singleton():
    assert _Nothing() is Nothing


def assert_just_fmap():
    assert Just(2).fmap(add_two) == Just(4)


def assert_just_apply():
    assert Just(add_two).apply(Just(2)) == Just(4)


def assert_bind():
    assert (Just(2) >> add_two) == Just(4)


def test_nothing_transforms():
    assert Nothing.fmap(add_two) is Nothing
    assert Nothing.apply(add_two) is Nothing
    assert (Nothing >> m_add_two) is Nothing


def test_Nothing_propagates():
    assert (Just(2) >> n_add_two >> add_two) is Nothing


def test_Nothing_proxy_is_false():
    assert not Nothing.proxy(lambda x: x%1)
    assert not Nothing.starproxy(lambda x, y: x%y)
