import pytest
from pynads import List, multiapply


add_two = lambda x: x+2
plus_or_minus_two = lambda x: [x-2, x+2]
plus_other = lambda x: lambda y: x+y


def test_List_mempty():
    assert List.mempty == ()


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


def test_List_mondoial_add():
    l =  List.unit(1)
    assert l + (List.unit(2)) == List.unit([1,2])
    assert l + (2,) == List.unit([1,2])


def test_List_mconcat():
    ls = [List.unit(x) for x in range(4)]
    final = List.mconcat(*ls)
    assert final == List(0,1,2,3)


def test_List_is_monoidal():
    ls = [List.unit(x) for x in [1,2,3]]
    assert List.mappend(ls[0], List.mappend(ls[1], ls[2])) == \
           List.mappend(List.mappend(ls[0], ls[1]), ls[2])


def test_List_handles_str():
    l = List("fred")
    assert l.v == ("fred",)


def test_List_handles_map():
    assert List({1,2,3}).v == ({1,2,3},)


def test_List_handles_seq():
    assert List(*range(3)).v == (0,1,2)


def test_List_handles_gen():
    gen_list = List.unit(iter([1,2,3]))
    assert gen_list.v == (1,2,3)


def test_List_repr():
    assert repr(List(1,2,3)) == "List(1,2,3)"
    assert "...5 more..." in repr(List(*range(15)))


def test_List_unit():
    assert List.unit(1).v == (1,)
    assert List.unit('fred').v == ('fred',)
    assert List.unit([1,2,3]).v == (1,2,3)


def test_List_fmap():
    l = List.unit(range(1,4))
    assert l.fmap(add_two).v == (3,4,5)


def test_List_apply():
    l = List.unit(add_two)
    l2 = l * List.unit([1,2,3])
    assert l2.v == (3,4,5)


def test_List_apply_two_funcs():
    l = List.unit([add_two, add_two])
    l2 = l * List.unit([1,2,3]) 
    assert l2.v == (3,4,5,3,4,5)


def test_List_multi_apply(): 
    ls = [List.unit(x) for x in  (plus_other, [1,2,3], [1,2,3])]
    l = multiapply(*ls)
    assert l.v == (2,3,4,3,4,5,4,5,6)


def test_List_bind():
    l = List.unit([1,2,3]) >> plus_or_minus_two
    assert l.v == (-1,3,0,4,1,5)


# test boring list stuff to make sure it's proxied correctly...
def test_List_getitem():
    assert List.unit([1,2,3])[0] == 1


def test_List_slice_makes_List():
    assert List.unit([1,2,3])[:] == List.unit([1,2,3])


def test_List_eq():
    assert List.unit([1,2,3]) == List.unit([1,2,3])
    assert List.unit(1) != List.unit([1,2])


def test_List_iter():
    assert isinstance(iter(List()), type(iter(())))


def test_List_contains():
    assert 1 in List.unit([1,2,3])


def test_List_len():
    assert len(List.unit([1,2,3])) == 3


def test_List_iadd():
    l1 = l2 = List.unit(1)
    l1 += List.unit(2)
    assert l1 == List.unit([1,2])
    assert l1 is not l2


def test_List_index():
    assert List.unit([1,2,3]).index(3) == 2


def test_List_count():
    assert List.unit([1,1,3]).count(1) == 2
