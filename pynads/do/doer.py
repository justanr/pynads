from functools import partial
from .exceptions import MonadReturn, MonadFinished
from ..utils import kwargs_decorator, update_wrapper


__all__ = ('do',)


@kwargs_decorator
class do(object):
    """Class based decorator that faciliates do-notation by using coroutines.
    It accepts a keyword argument ``monad`` that used to create the final
    return value via its unit method.

    Haskell's do notation is often thought of as a "loop" where each operation
    is executed in sequence. In Python, this can emulate this by writing the
    do notation as a coroutine (see following examples).

    With pynads, ``var = yield monadic_function(...)`` is equlivalent to
    Haskell's ``var <- monadic_function ...``. similarly, Haskell's do
    version of ``>>``/then/ignore, which is simply ``monadic_function ...``
    is just `yield monadic_function(...)`` in pynads, simply don't assign it
    to a name.

    To maintain compatibility with Python 2.7, a function that raises an
    exception is used to extract the value from the do-notation function
    rather than using the Python 3.3+ return from generators feature --
    which would be both slicker and slightly more complicated.

    .. code-block:: python
        from pynads import Left, Right, Either
        from pynads.do import do, mreturn

        def safediv(a,b):
            if b == 0:
                return Left("Divide by zero error!")
            else:
                return Right(a/b)

        @do(monad=Either)
        def either_doer_safe_div(first):
            a = yield safe_div(2, first)
            b = yield safe_div(3, 4)
            c = yield safe_div(a, b)
            mreturn(c)

    The desugared version would look like this:

    .. code-block:: python
        def either_binding_safe_div(first):
            return safe_div(2, first) >> (lambda a:
                   safe_div(3, 4)     >> (lambda b:
                   safe_div(a, b)                ))

    Calling the decoratored function is the same as any other:

    .. code-block:: Python
        >>> either_doer_safe_div(1)
        ... Right 2.6666666666666665
        >>> either_doer_safe_div(0)
        ... Left 'Divide by zero error!'

    Even though the final ``c = yield safe_div(a, b)`` looks extraneous,
    it serves purpose. Without, the final result would actually be:
    ``Right Right 2.6666666666666665`` because when this catches an
    ``mreturn`` it wraps the resulting value with the unit method of the
    initial monad (Either in this case, which puts a value into a Right
    instance).

    In addition to ``mreturn``, there is also ``mfinished`` which signals to
    the do notation handler that the final output is actually a monad which
    should be propagate directly the caller.

    With that in mind, the do-notation example could be written as:

    .. code-block:: python
        @do(monad=Either)
        def either_mfinished_example(first):
            a = yield safe_div(2, first)
            b = yield safe_div(3, 4)
            mfinished(safe_div(a, b))

    And the result is the same as the first. Both styles are provided for
    stylistic concerns, but sometimes it is neccessary to distinguish a
    value that should be wrapped in a unit method and an explicit monadic
    result.
    """
    def __init__(self, do_func, monad):
        update_wrapper(self, do_func)
        self._do_func = do_func
        self._monad = monad

    def __call__(self, *a, **k):
        do_loop = self._do_func(*a, **k)
        return self._send(None, do_loop)

    def _send(self, val, gen):
        """Haskell's do notation is often thought of as a loop that calls
        each step in sequence, making it look like imperative code rather than
        functional.

        With pynads this is accomplished by writing the do-notation style
        functions as coroutines and sending the yielded results back into
        the coroutine with the ``send`` method and stepping through the
        coroutine in that manner. Each yielded result is bound to the next
        monad in the sequence.

        Slightly confusingly, there are two exceptions that look remarkably
        similar to each other and serve, at a practical level, the same
        function: extracting a value from the do coroutine. However, they
        represent different things:

            * MonadReturn (used with mreturn) signals to this method that
            the resulting value should be wrapped in the unit method of
            the initial monad.
            * MonadFinished (used with mfinished) signals to this method
            the the resulting value itself if a monad itself and should
            be returned to the caller as is.

        Unlike Haskell, using either of these *is* a final statement.
        """
        try:
            monad = gen.send(val)
            return monad.bind(partial(self._send, gen=gen))
        except MonadReturn as mr:
            return self._monad.unit(mr.v)
        except MonadFinished as mf:
            return mf.v
