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


def test_List_mondoial_add():
    l = 1 & List
    assert l + (2 & List) == [1,2] & List
    assert l + (2,) == [1,2] & List


def test_List_mconcat():
    ls = [x & List for x in range(4)]
    final = List.mconcat(*ls)
    assert final == List(0,1,2,3)


def test_List_is_monoidal():
    ls = [x & List for x in [1,2,3]]
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
    gen_list = iter([1,2,3]) & List
    assert gen_list.v == (1,2,3)


def test_List_repr():
    assert repr(List(1,2,3)) == "List(1,2,3)"
    assert "...5 more..." in repr(List(*range(15)))


def test_List_unit():
    assert List.unit(1).v == (1,)
    assert List.unit('fred').v == ('fred',)
    assert List.unit([1,2,3]).v == (1,2,3)


def test_List_fmap():
    l = (range(1,4) & List)
    assert l.fmap(add_two).v == (3,4,5)


def test_List_apply():
    l = add_two & List
    l2 = l * ([1,2,3] & List)
    assert l2.v == (3,4,5)


def test_List_apply_two_funcs():
    l = [add_two, add_two] & List
    l2 = l * ([1,2,3] & List) 
    assert l2.v == (3,4,5,3,4,5)


def test_List_multi_apply(): 
    ls = [(plus_other & List), ([1,2,3] & List), ([1,2,3] & List)]
    l = multiapply(*ls)
    assert l.v == (2,3,4,3,4,5,4,5,6)


def test_List_bind():
    l = ([1,2,3] & List) >> plus_or_minus_two
    assert l.v == (-1,3,0,4,1,5)


# test boring list stuff to make sure it's proxied correctly...
def test_List_getitem():
    assert ([1,2,3] & List)[0] == 1


def test_List_slice_makes_List():
    assert ([1,2,3] & List)[:] == ([1,2,3] & List)


def test_List_eq():
    assert ([1,2,3] & List) == ([1,2,3] & List)
    assert (1 & List) != ([1,2] & List)


def test_List_iter():
    assert isinstance(iter(List()), type(iter(())))


def test_List_contains():
    assert 1 in ([1,2,3] & List)


def test_List_len():
    assert len(([1,2,3] & List)) == 3


def test_List_iadd():
    l1 = l2 = 1 & List
    l1 += 2 & List
    assert l1 == [1,2] & List
    assert l1 is not l2


def test_List_index():
    assert ([1,2,3] & List).index(3) == 2


def test_List_count():
    assert ([1,1,3] & List).count(1) == 2
