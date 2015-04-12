from .exceptions import MonadReturn, MonadFinished


__all__ = ("mfinished", "mreturn")


def mreturn(v):
    """Flow control helper for do-notation style functions. This simply raises
    an exception containing the passed value.
    """
    raise MonadReturn(v)


def mfinished(monad):
    raise MonadFinished(monad)
