from abc import ABCMeta, abstractmethod

class MonadMeta(ABCMeta):
    
    def unit(self, value):
        return self(value)

    def __lt__(self, value):
        return self.unit(value)

def Monad(metaclass=MonadMeta):
    
    @abstractmethod
    def bind(self, f):
        return NotImplemented

    @staticmethod
    def ignore_self(f):
        return f()

    def __ge__(self, f):
        return self.bind(f)

    def __rshift__(self, f):
        return self.ignore_self(f)
