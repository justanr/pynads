from pynads import State
from pynads.funcs import mappend, multiapply, multibind
from pynads.utils.internal import iscallable
import pytest


pop = State(lambda s: (s[0], s[1:]))
push = lambda a: State(lambda s: ((), mappend([a], s)))


def test_State_new_raises():
    with pytest.raises(TypeError):
        State(4)


def test_State_unit():
    s = State.unit(1)
    assert iscallable(s.v)
    assert s(4) == (1,4)


def test_State_repr():
    def test():
        pass

    assert repr(State(test)) == 'State(test)'


def test_State_fmap():
    a = str.upper % State.unit('a')
    assert a(None) == ('A', None)


def test_State_apply():
    F = State(lambda s: (lambda x: x+1, s))
    V = State(lambda s: (s+1, s-1))
    applied = F * V
    assert applied(1) == (3,0)


def test_State_multiapply():
    F = State(lambda s: (lambda x: lambda y: x+y, s))
    X = State.unit(1)
    Y = State.unit(2)
    applied = F * X * Y
    assert applied(1) == (3, 1)
    assert multiapply(F, X, Y)(1) == (3,1)


def test_simply_State_bind():
    pop_push = pop >> push
    assert pop_push([1,2,3]) == ((), [1,2,3])


def test_complex_State_bind():
    def find_factor(got, divisor):
        while got > divisor:
            got //= divisor
        return got

    push_if = lambda a: push(find_factor(a, 5)) if not a%5 \
                        else push(3) >> (lambda _: push(8))

    assert (pop >> push_if)([10, 4, 3]) == ((), [2, 4, 3])
    assert (pop >> push_if)([4, 3]) == ((), [8,3,3])


def test_multibind_with_State():
    pops = [lambda _: pop] * 3
    f = multibind(push(1), *pops)
    assert f([1,2,3,4]) == (2, [3,4])
