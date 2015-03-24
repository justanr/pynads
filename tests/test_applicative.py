import pytest
from pynads import fmap, multiapply, unit, Applicative


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


def test_unit_shortcut():
    assert (2 & MyApplicative) == MyApplicative.unit(2)


def test_myapplicative_instance_doesnt_have_rand():
    assert not hasattr(MyApplicative(None), '__rand__')


def test_apply():
    a = MyApplicative.unit(id)
    b = MyApplicative.unit('b')
    c = a.apply(b)

    assert c == b


def test_mul_apply():
    a = MyApplicative.unit(id)
    b = MyApplicative.unit('b')
    c = a * b

    assert c == b

def test_chain_apply():
    a = MyApplicative.unit(fake_curry)
    b = MyApplicative.unit(2)

    c = a * b *b

    assert c == MyApplicative.unit(4)

def test_function_unit():
    assert unit(4, MyApplicative) == MyApplicative.unit(4)

def test_multi_apply():
    a = MyApplicative.unit(fake_curry)
    b = MyApplicative.unit(2)
    c = multiapply(a, b, b)

    assert c == MyApplicative.unit(4)
