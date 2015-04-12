from pynads.do import utils, MonadReturn, MonadFinished
import pytest


def test_mreturn_raises():
    with pytest.raises(MonadReturn) as mr:
        utils.mreturn(4)

    assert mr.value.v == 4


def test_mfinished_raises():
    with pytest.raises(MonadFinished) as mf:
        utils.mfinished(4)

    assert mf.value.v == 4
