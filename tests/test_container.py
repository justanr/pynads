import pytest
from pynads import Container
from weakref import ref
from operator import mod, eq

def test_Container_get_val():
    c = Container(1)
    assert c._get_val() == 1
    assert c.v == 1


def test_Container_weakref():
    c = Container(1)

    try:
        w = ref(c)
    except TypeError:
        pytest.fail("Can't create weakref.")
    else:
        assert c.__weakref__ is w, "__weakref__ miscreated"
