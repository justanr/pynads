from functools import partial
from .exceptions import MonadReturn, MonadFinished
from ..utils.compat import update_wrapper, wraps


__all__  = ("kwargs_decorator", "mfinished", "mreturn")


def kwargs_decorator(deco):
    """This is a decorator-decorator (a metadecorator if you will) that allows
    creating decorators that accept keyword arguments. It's a relatively
    simple trick of checking if the wrapper -- which stands in for the actual
    decorator -- has received the func parameter.and if not, a partial of
    the wrapper (decorator) is returned instead. This will continue to
    happen until the func param is filled.

    .. code-block:: python
        @kwargs_decorator
        def kwarg_deco(f, pre, post):
            def wrapper(*a, **k):
                print(pre)
                r = f(*a, **k)
                print(post)
                return r
            return wrapper

    Using the created decorator and the function it wraps is the same as
    any other decorator and wrapped function:

    .. code-block:: python
        @kwarg_deco(pre="Hello!", post="Goodbye!")
        def greet(name):
            print(name)

    And...

    .. code-block:: python
        >>> greet('Alec')
        Hello!
        Alec
        Goodbye!

    The created decorator, however, is not reentrant, meaning they can't
    be stacked like this:

    .. code-block:: Python
        @kwarg_deco(pre="Hello!")
        @kwarg_deco(post='Goodbye!')
        def greet(name):
            print(name)

        TypeError: kwarg_deco() missing 1 required positional argument: 'pre'

    But by providing default arguments, it can be made to appear reentrant:

    .. code-block:: Python
        @kwargs_decorator
        def my_kwarg_deco(f, pre='', post=''):
            # as before

        @my_kwarg_deco(pre='Hello!')
        @my_kwarg_deco(post='Goodbye!')
        def greet(name):
            print(name)

    Note the extra white space that results from calling this version::

        Hello!

        Alec
        Goodbye!

    Because the created decorator isn't truly reentrant, the created decorator
    is actually run twice.

    This decorator can be used on classes as well:

    .. code-block:: Python
        @kwarg_decorator
        class pre_post_print(object):
            def __init__(self, f, pre='', post=''):
                self.f = f
                self.pre = pre
                self.post = post

            def __call__(self, *a, **k):
                print(self.pre)
                r = self.f(*a, **k)
                print(self.post)
                return r

        @pre_post_print(pre='hello', post='goodbye')
        def greet(name):
            print(name)

    Calling greet results in:

        .. code-block:: Python
            hello
            alec
            goodbye

    However, to use it as a class decorator requires Python 2,6+.
    """
    @wraps(deco)
    def wrapper(func=None, **kwargs):
        if func is None:
            return partial(wrapper, **kwargs)
        return deco(func, **kwargs)
    return wrapper


def mreturn(v):
    """Flow control helper for do-notation style functions. This simply raises
    an exception containing the passed value.
    """
    raise MonadReturn(v)


def mfinished(monad):
    raise MonadFinished(monad)
