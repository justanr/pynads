from pynads import Just, List, Nothing
from pynads.funcs import lifted

add_two = lambda x: x+2
curried_add = lambda x: lambda y: x+y
m_add_two = lambda x: Just(x+2)

def test_fmap_func():
    assert lifted.fmap(add_two, Just(2)) == Just(4)


def test_unit_func():
    assert lifted.unit(2, Just) == Just(2)


def test_multiapply():
    j = Just.unit(curried_add)
    js = [Just(2), Just(2)]
    assert lifted.multiapply(j, *js) == Just(4)


def test_lift_func():
    assert lifted.lift(add_two, 2, Just) == Just(4)


def test_multibind():
    j = Just.unit(2)
    assert lifted.multibind(j, m_add_two, m_add_two) == Just(6)


def test_cons():
    assert lifted.cons(1, List(2,3)) == List(1,2,3)
    assert lifted.cons(1, 
               lifted.cons(2, 
                   lifted.cons(3, 
                       lifted.cons(4, List())))) == List(1,2,3,4)


def test_mcons():
    assert lifted.mcons(Just(0), Just(List(1,2,3))) == Just(List(0,1,2,3))
    assert lifted.mcons(Nothing, Just(List(0))) is Nothing


def test_sequence():
    justs = [Just(x) for x in range(5)]
    assert lifted.sequence(*justs) == Just(List(0,1,2,3,4))
    assert lifted.sequence(Nothing, *justs) is Nothing


def test_mapM():
    assert lifted.mapM(m_add_two, *range(5)) == Just(List(2,3,4,5,6))
