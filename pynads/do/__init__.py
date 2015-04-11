"""This module enables uses a bastardized version of Haskell's do notation by
writing do-notation style code as coroutines and then stepping through the
coroutine by sending and receiving monads to bind and work with.

Much of the inspiration for this module came from a blog post by Peter Thatcher
on his blog Valued Lessons (link below), where he explored the idea of using
coroutines to emulate this notation back in 2008 in Python 2.5 with a style
of monads that are remarkably similar to the ones found in pynads and in
pynads' inspirational projects 

<http://www.valuedlessons.com/2008/01/monads-in-python-with-nice-syntax.html>
"""

from .doer import *
from .utils import *
from .exceptions import *
