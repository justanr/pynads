from pynads import Map
from pynads.funcs import identity

def test_Map_unit():
    m = Map.unit(('a', 4))
    assert m.v == {'a': 4}


def test_Map_fromkeys():
    m = Map.fromkeys(['a', 'b', 'c'], 1)
    assert isinstance(m, Map)
    assert m.v == {'a': 1, 'b': 1, 'c': 1}
    assert Map.fromkeys(['a']).v == {'a': None}


def test_Map_fmap():
    f = lambda x: x+1
    m = Map({'a': 1, 'b': 2, 'c': 3})
    assert m.fmap(f).v == {'a': 2, 'b': 3, 'c': 4}
    assert m.fmap(identity).v == {'a': 1, 'b': 2, 'c': 3}


def test_Map_apply():
    m = Map.fromkeys('abc', lambda x: x+1)
    n = Map({'a': 1, 'b': 2, 'c': 3})
    o = m * n
    assert o.v == {'a': 2, 'b': 3, 'c': 4}


def test_Map_apply_only_matches():
    f = lambda x: x+1
    g = lambda x: x-1
    h = lambda x: x*x

    m = Map({'a': f, 'b': g, 'c': h})
    n = Map({'a': 1, 'b': 2, 'c': 3})
    o = m * n
    assert o.v == {'a': 2, 'b': 1, 'c': 9}


def test_Map_apply_multiple_args():
    f = lambda x: lambda y: x+y
    m = Map({'a': f})
    n = Map({'a': 1})
    o = Map({'a': 2})
    p = m * n * o
    assert p.v == {'a': 3}


def test_Map_apply_multiple_args_with_miss():
    f = lambda x: lambda y: x+y
    m = Map({'a': f})
    n = Map({'a': 1})
    o = Map({'b': 2})
    p = Map({'a': 2})
    q = m * n * o * p
    assert q.v == {}
