from pynads.utils import _iter_but_not_str_or_map

def test_check_iter():
    assert _iter_but_not_str_or_map([])
    assert _iter_but_not_str_or_map(set())
    assert _iter_but_not_str_or_map(())
    assert not _iter_but_not_str_or_map('')
    assert not _iter_but_not_str_or_map({})
