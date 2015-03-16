from .monad import Monad

class Maybe(Monad):
    def __new__(self, value):
        return Just(value) if value is not None else Nothing()

    def __bool__(self):
        return isinstance(self, Just)

class Just(Monad):
    
    def __new__(self, value):
        return object.__new__(self)

    def __init__(self, val, *args, **kwargs):
        self.val = val

    def __repr__(self):
        return "Just {!r}".format(self.val)

    def bind(self, f):
        res = f(self.val)
        if not isinstance(res, Monad):
            raise TypeError("bind must return a monadic instance")
        return res

class Nothing(Maybe):
    def __new__(self, value=None):
        return object.__new__(self)

    def __repr__(self):
        return "Nothing"

    def bind(self, f):
        return self
