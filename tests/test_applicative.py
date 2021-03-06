import pytest
from pynads import Applicative
from pynads.funcs import fmap, multiapply, unit


class MyApplicative(Applicative):
    @classmethod
    def unit(cls, v):
        return cls(v)

    def fmap(self, f):
        return MyApplicative(f(self.v))

    def apply(self, applicative):
        return fmap(self.v, applicative)

    def __eq__(self, other):
        return isinstance(other, MyApplicative) and self.v == other.v

id = lambda x: x

fake_curry = lambda x: lambda y: x+y


def test_class_unit():
    a = MyApplicative.unit(id)
    assert a.v is id and isinstance(a, Applicative)


def test_apply():
    a = MyApplicative.unit(id)
    b = MyApplicative.unit('b')
    c = a.apply(b)

    assert c == b


def test_fmap_infix_to_chain_apply():
    a = MyApplicative('a')
    b = MyApplicative('b')
    ab = fake_curry % a * b

    assert ab == MyApplicative('ab')


def test_mul_apply():
    a = MyApplicative.unit(id)
    b = MyApplicative.unit('b')
    c = a * b

    assert c == b

def test_chain_apply():
    a = MyApplicative.unit(fake_curry)
    b = MyApplicative.unit(2)

    c = a * b * b

    assert c == MyApplicative.unit(4)

def test_function_unit():
    assert unit(4, MyApplicative) == MyApplicative.unit(4)

def test_multi_apply():
    a = MyApplicative.unit(fake_curry)
    b = MyApplicative.unit(2)
    c = multiapply(a, b, b)

    assert c == MyApplicative.unit(4)
