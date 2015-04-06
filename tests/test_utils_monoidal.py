from collections import Sequence, Mapping, Set
from decimal import Decimal
from numbers import Number
from operator import add, or_
from pynads import List, Map
from pynads.utils import monoidal as m, chain_dict_update
import pytest
from weakref import WeakSet

ints = (1,2,3)

list_of = lambda maker, stuff: [maker(x) for x in stuff]

class DummyMonoid(object):
    mempty = None
    mconcat = mappend = lambda s: s

@pytest.mark.parametrize('obj, type', [
    (Decimal('0'), Number),
    (set(), Set),
    (dict(), Mapping),
    (list(), Sequence),
    (str(), str),
    pytest.mark.xfail((WeakSet(), Set)) #surprise!
])
def test_get_generic_type(obj, type):
    assert m._get_generic_type(obj) is type


@pytest.mark.parametrize('generic, mappend', [
    (Sequence, m._seq_mappend), (Set, or_), 
    (str, add), (Number, add), (Decimal, None)
])
# note leading underscore!
def test__get_generic_mappend_from_generic_type(generic, mappend):
    assert m._get_generic_mappend(generic) is mappend


@pytest.mark.parametrize('obj, mappend', [
    ([], m._seq_mappend), ((), m._seq_mappend),
    (6, add), (6.0, add), (6+1j, add), ({4}, or_),
    (frozenset([2]), or_), ({1:1}, chain_dict_update),
    (Decimal('6'), add)
])
# note no leading underscore!
def test_get_generic_mappend_from_obj(obj, mappend):
    assert m.get_generic_mappend(obj) is mappend


@pytest.mark.parametrize('obj, mempty', [
    (6.0, 0.0), (1, 0), (6+1j, 0j), ('hello', ''),
    ([1,2,3], []), ((1,2,3), ()), ({4}, set()),
    (frozenset([1,2,3]), frozenset()), ({1:1}, {})
])
def test_get_generic_mempty(obj, mempty):
    assert m.get_generic_mempty(obj) == mempty


def test_get_generic_mempty_raises_with_unknown():
    with pytest.raises(TypeError) as error:
        m.get_generic_mempty(Decimal('5'))
    assert "No known" in str(error.value)


@pytest.mark.parametrize('objs, expected', [
    (ints, 6),
    (list_of(float, ints), 6.0),
    (list_of(complex, ints), 6+0j),
    (list_of(Decimal, ints), Decimal(6)),
    (list_of(lambda a: {a}, ints), set(ints)),
    (list_of(lambda a: frozenset([a]), ints), frozenset(ints)),
    (list_of(lambda a: [a], ints), list(ints)),
    (list_of(str, ints), '123'),
    (list_of(lambda a: {a:a}, ints), {1:1, 2:2, 3:3}),
    (list_of(lambda a: (a,), ints), list(ints))
])
def test_generic_mconcat(objs, expected):
    mappend = m.get_generic_mappend(objs[0])
    assert m.generic_mconcat(mappend, *objs) == expected


@pytest.mark.parametrize('obj, is_monoidal', [
    (Decimal(1), False), (List(), True),
    (1, True), ([], True), (object(), False),
    (Map(), True), (DummyMonoid(), True)
])
def test_is_monoid(obj, is_monoidal):
    assert m.is_monoid(obj) == is_monoidal
