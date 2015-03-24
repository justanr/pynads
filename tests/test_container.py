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


def test_Container_proxy():
    c = Container(1)
    assert c.proxy(lambda x: x==1)
    assert c.proxy(lambda x: not x%1)


def test_Container_starproxy():
    c = Container(2)
    assert c.starproxy(mod, 3) == 2
    assert c.starproxy(mod, 3, append=True) == 1
    assert c.starproxy(eq, 2) == True
