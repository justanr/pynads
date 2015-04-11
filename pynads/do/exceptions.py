__all__ = ("MonadFinished", "MonadReturn")

class MonadReturn(Exception):
    def __init__(self, v, *args):
        self.v = v
        super().__init__(v, *args)


class MonadFinished(Exception):
    def __init__(self, v, *args):
        self.v = v
        super().__init__(v, *args)
