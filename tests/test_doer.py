from __future__ import division # Py2 compat
from pynads.do import do, mreturn, mfinished
from pynads import Either, Left, Right
from pynads import Maybe, Just, Nothing


def safe_div(a, b):
    if b == 0:
        return Left("divided by zero error")
    else:
        return Right(a/b)


def test_do_with_either():
    @do(monad=Either)
    def safe_div_test(first):
        a = yield safe_div(2, first)
        b = yield safe_div(3, 4)
        c = yield safe_div(a, b)
        mreturn(c)

    computed = safe_div_test(1)
    failed = safe_div_test(0)

    assert type(failed) is Left
    assert failed.v == 'divided by zero error'
    assert type(computed) is Right
    assert computed.v == (2/1)/(3/4)


def test_do_with_maybe():
    @do(monad=Maybe)
    def always_nothing():
        x = yield Just(1-3)
        y = yield Nothing
        mreturn(x-y)

    assert always_nothing() is Nothing
