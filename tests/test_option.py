from pynads import Option, Full, Empty
from pynads.concrete.option import _Empty


def even(x): return not x % 2


def test_Option_new():
    assert Option(4) == Full(4)
    assert Option(None) == Empty


def test_Option_custom_checker():
    assert Option(2, checker=even) == Full(2)
    assert Option(3, checker=even) == Empty


def test_Option_truthiness():
    assert Full(1)
    assert not Empty


def test_Empty_singleton():
    assert Empty is _Empty()


def test_Full_fmap():
    assert Full(2).fmap(lambda x: x + 1) == Full(3)


def test_Full_filter():
    assert Full(2).filter(even) == Full(2)
    assert Full(3).filter(even) == Empty


def test_Full_get_or():
    assert Full(2).get_or(5) == 2


def test_Full_get_or_call():
    assert Full(2).get_or_call(lambda: 5) == 2


def test_Full_or_else():
    assert Full(2).or_else(Full(5)) == Full(2)


def test_Full_or_call():
    assert Full(2).or_call(lambda: Full(5)) == Full(2)


def test_Empty_fmap():
    assert Empty.fmap(lambda x: x + 1) == Empty


def test_Empty_filter():
    assert Empty.filter(even) == Empty


def test_Empty_get_or():
    assert Empty.get_or(5) == 5


def test_Empty_get_or_call():
    assert Empty.get_or_call(lambda: 5) == 5


def test_Empty_or_else():
    assert Empty.or_else(5) == Full(5)


def test_Empty_or_call():
    assert Empty.or_call(lambda: 5) == Full(5)


def test_Option_as_wrapper():
    @Option.as_wrapper(checker=even)
    def test(x):
        """identity"""
        return x

    assert test.__doc__ == 'identity'
    assert test.__name__ == 'test'
    assert test(2) == Full(2)
    assert test(3) == Empty
