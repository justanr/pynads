from pynads import Identity

inc = lambda x: x+1
minc = lambda x: Identity(x+1)


def test_Identity_fmap():
    i = Identity.unit(1).fmap(inc)
    assert i.v == 2 and isinstance(i, Identity)


def test_Identity_apply():
    i, j = Identity(inc), Identity(4)
    h = i.apply(j)
    assert h.v == 5 and isinstance(h, Identity)


def test_Identity_bind():
    i = Identity(1)
    j = i.bind(minc).bind(minc)
    assert j.v == 3 and isinstance(j, Identity)
