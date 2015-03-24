from pynads.writer import Writer

add_two = lambda x: x+2
m_add_two = lambda x: (x+2, 'added two')
f_id = lambda x: x

def test_writer_unit():
    w = Writer.unit(2)
    assert w.v == 2 and w.log == []


def test_fmap_id():
    w = Writer.unit(2)
    assert w.v == 2 and w.log == []


def test_writer_fmap():
    w = Writer.unit(2).fmap(add_two)
    assert w.v == 4 and w.log == []


def test_writer_apply():
    w = (Writer.unit(add_two)) * (Writer.unit(2))
    assert w.v == 4 and w.log == []


def test_writer_bind():
    w = Writer.unit(2) >> m_add_two
    assert w.v == 4 and w.log == ['added two']
