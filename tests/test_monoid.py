import pytest
from pynads import Monoid


def test_Monoid_raises_with_no_mempty():
    class Test(Monoid):
        # dummy out to avoid potential ABC errors
        def mappend():
            pass

    with pytest.raises(TypeError) as err:
        Test()

    assert "abstract property mempty" in str(err.value)


def test_Monoid_searches_mro():
    class Base(Monoid):
        mempty = None
        def mappend(self, other):
            pass

    class Test(Base):
        pass

    assert Test()
    assert Test.mempty is None


def test_Monoid_default_mappend():
    class Test(Monoid):
        mempty = 0

        def mappend(self, other):
            return Test(self.v + other.v)

    assert Test.mconcat(Test(1), Test(2)).v == Test(3).v
