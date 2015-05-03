import pytest
from pynads import List
from pynads.funcs import multiapply, multibind


add_two = lambda x: x+2
minus_or_plus_two = lambda x: [x-2, x+2]
plus_other = lambda x: lambda y: x+y


def test_List_bool():
    assert List(1,2)
    assert not List()


def test_List_mempty():
    assert List.mempty  == List()


def test_List_mappend():
    m = List(1,2,3)
    n = List(4)
    assert m.mappend(n) == List(1,2,3,4)


def test_List_add_other_iters():
    control = List(1,2,3,4)
    m = List(1,2,3)
    n = iter([4])
    o = (4, )
    p = {4}

    assert all(control == (m+x) for x in [n,o,p])


def test_List_add_raises_with_str():
    l = List()

    with pytest.raises(TypeError) as error:
        l + 'a'

    assert 'str' in str(error.value)


def test_List_add_raises_with_mapping():
    l = List()

    with pytest.raises(TypeError) as error:
        l + {'a':10}

    assert 'dict' in str(error.value)


def test_List_monoidal_add():
    l =  List.unit(1)
    assert l + (List.unit(2)) == List(1,2)
    assert l + (2,) == List(1,2)


def test_List_mconcat():
    ls = [List.unit(x) for x in range(4)]
    final = List.mconcat(*ls)
    assert final == List(0,1,2,3)


def test_List_is_monoidal():
    ls = [List.unit(x) for x in [1,2,3]]
    assert List.mappend(ls[0], List.mappend(ls[1], ls[2])) == \
           List.mappend(List.mappend(ls[0], ls[1]), ls[2])


def test_List_repr():
    assert repr(List(1,2,3)) == "List(1, 2, 3)"
    assert "...5 more..." in repr(List(*range(15)))


def test_List_unit():
    assert List.unit(1).v == (1,)
    assert List.unit('fred').v == ('fred',)
    assert List.unit([1,2,3]).v == ([1,2,3],)


def test_List_fmap():
    l = List(1,2,3)
    assert l.fmap(add_two).v == (3,4,5)


def test_List_apply():
    l = List(add_two) * List(1,2,3)
    assert l.v == (3,4,5)


def test_List_apply_two_funcs():
    l = List(add_two, add_two) * List(1,2,3)
    assert l.v == (3,4,5,3,4,5)


def test_List_multi_apply():
    ls = [List(*x) for x in ([1,2,3], [1,2,3])]
    l = multiapply(List(plus_other), *ls)
    assert l.v == (2,3,4,3,4,5,4,5,6)


def test_List_bind():
    l = List(1,2,3) >> minus_or_plus_two
    assert l.v == (-1,3,0,4,1,5)


def test_build_chessboard():
    # shamelessly stolen from:
    # https://github.com/dustingetz/pymonads/blob/master/list.py
    ranks = 'abcdefg'
    files = range(1,9)

    l = List(*ranks) >> (lambda r:
        List(*files) >> (lambda f:
        List.unit((r,f))        ))

    hardway = tuple((r,f) for r in ranks for f in files)
    sliced = List(('a', 1), ('a', 2), ('a', 3))

    assert l.v == hardway
    assert l[:3] == sliced


def test_ignore_second_bind():
    l = List(1,2,3) >> (lambda a:
        List(1,2)   >> (lambda _:
        minus_or_plus_two(a)   ))

    assert l.v == (-1, 3, -1, 3, 0, 4, 0, 4, 1, 5, 1, 5)


def test_list_multibind():
    l = multibind(List(1,2), minus_or_plus_two, minus_or_plus_two)
    assert l.v == (-3, 1, 1, 5, -2, 2, 2, 6)


def test_List_filter():
    assert List(1,2,3,4).filter(lambda x: not x % 2) == List(2,4)


def test_List_cons():
    l = List(2,3)
    n = l.cons(1)

    assert n == List(1,2,3)


def test_List_append():
    l = List(1,2)
    n = l.append(3)

    assert n == List(1,2,3)


def test_List_extend():
    l = List(1, 2)
    n = List(3, 4)

    assert l.extend(n) == List(1, 2, 3, 4)


# test boring list stuff to make sure it's proxied correctly...
def test_List_getitem():
    assert List(1,2,3)[0] == 1


def test_List_slice_makes_List():
    assert List(1,2,3)[:] == List(1,2,3)


def test_List_eq():
    assert List(1,2,3) == List(1,2,3)
    assert List.unit(1) != List(1,2)


def test_List_iter():
    tuple_iter_type = type(iter(tuple()))
    List_monad_iter = iter(List())
    assert isinstance(List_monad_iter, tuple_iter_type)


def test_List_contains():
    assert 1 in List(1,2,3)


def test_List_len():
    assert len(List(1,2,3)) == 3


def test_List_iadd():
    l1 = l2 = List.unit(1)
    l1 += List.unit(2)
    assert l1 == List(1,2)
    assert l1 is not l2


def test_List_index():
    assert List(1,2,3).index(3) == 2


def test_List_count():
    assert List(1,1,3).count(1) == 2


def test_List_reversed():
    assert reversed(List(1,2,3)) == List(3,2,1)
