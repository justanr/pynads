from ..abc import Monad


class Identity(Monad):
    """The simplest Monad. Acts as merely a wrapper around a value,

    Identity, in and of itself, is not very interesting or useful.
    However, the Identity monad becomes integral when working with
    Monad Transformers (essentially nested monads) to derive the
    non-transformer variant of the monad.

        .. code-block:: Haskell
            data Identity a = Identity a

            instance Functor Identity where
                fmap f (Identity a) = Identity (f a)

            instance Applicative Identity where
                pure = Identity
                (Identity f) <*> (Identity a) = Identity (f a)

            instance Monad Identity where
                return = Identity
                (Identity a) >>= f = Identity (f a)

    Not terribly difficult, but just like the very unintersting identity
    function (why would we ever need a function that just spits back its
    input?), when combined with other things it becomes a nice tool.
    """
    def __repr__(self):
        return "Identity({!r})".format(self.v)

    @classmethod
    def unit(cls, v):
        return cls(v)

    def fmap(self, func):
        """Fmapping over an Identity monad is the same as applying the
        function being mapped and then wrapping the result in an
        Identity monad.
        """
        return Identity(func(self.v))

    def apply(self, other):
        """Applying a function stored in an Identity monad in the same as
        fmapping the function over the next Identity monad which is the same
        as just applying the stored function to the stored value and returning
        the result wrapped up in an Identity monad.
        """
        return Identity(self.v(other.v))

    def bind(self, bindee):
        """Binding a function to an Identity monad is the same as fmapping the
        function over the contained value.
        """
        return bindee(self.v)
