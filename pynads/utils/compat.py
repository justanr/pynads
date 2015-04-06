import sys
from functools import WRAPPER_ASSIGNMENTS, WRAPPER_UPDATES, partial


PY3 = sys.version_info[0] > 2

__all__ = ('update_wrapper', 'wraps', 'reduce', 'filter', 'filterfalse',
           'map', 'range', 'zip')

if PY3:
    map = map
    range = range
    zip = zip
    filter = filter
    from functools import reduce
    from itertools import filterfalse
else:
    range = xrange
    reduce = reduce
    from itertools import (imap as map, ifilter as filter,
                           izip as zip, ifilterfalse as filterfalse)


# backport Python 3.4's update_wrapper to avoid silliness
# has much smarter behavior than previous implementations of it
def update_wrapper(wrapper,
                   wrapped,
                   assigned=WRAPPER_ASSIGNMENTS,
                   updated=WRAPPER_UPDATES):
    """Makes a wrapper appear as the wrapped object.

    This is a backport of Python 3.4's `functools.update_wrapper`. This version
    is more intelligent than what's found in Python 2 as it uses a try-block
    when attempting to move attributes rather than just charitably assuming
    all of the attributes exist on the wrapped object.

    It also backports Python 3.3+'s `__wrapped__` attribute as well, which
    gives easy access to the original object.

    This function *always* modifies the wrapping object.
    """
    for attr in assigned:
        try:
            value = getattr(wrapped, attr)
        except AttributeError:
            pass
        else:
            setattr(wrapper, attr, value)

    for attr in updated:
        getattr(wrapper, attr, {}).update(getattr(wrapped, attr, {}))

    # store original object last so it isn't copied over
    wrapper.__wrapped__ = wrapped

    # return wrapper so this can be used as a decorator
    return wrapper


def wraps(wrapped, assigned=WRAPPER_ASSIGNMENTS, updated=WRAPPER_UPDATES):
    """Decorator form of update_wrapper.

    This is very useful for writing closure based decorators rather than
    using update_wrapper manually on the closure.

    Like update_wrapper, this decorator modifies what it's applied it.
    """
    return partial(update_wrapper,
                   wrapped=wrapped,
                   assigned=assigned,
                   updated=updated)
