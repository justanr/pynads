class Container(object):
    """Basic container object to serve as a base for Functor, Applicative
    and Monad, as most derived classes need only one argument. However,
    subclasses may override ``Container.__init__`` to accept multiple
    arguments (see ``pynads.conrete.writer.Writer``) but these classes
    should pass back to ``Container.__init__`` via super.

    This class is the endpoint for any super() calls relating to ``_new__``,
    ``__init__`` and ``_get_val`` unless multiple inheritance is used,
    in which another class may also be called with these
    methods (including ``object``).

    The value contained in this class is a *strong* reference by default.
    Using a weakreference is possible, but untested.

    It also creates a property -- ``Container.v`` -- which invokes a method
    to return the contained value. If a subclass needs to return from a
    different source, or return multiple values, it can override the
    default implementation of ``Container._get_val``

    In many cases, ``Container.__init__`` is sufficient for its subclasses,
    which often are only concerned with one value being passed it. However,
    feel free to override it to accept multiple values or to perform
    special initialization.

    If multiple values need to be returned by ``Container.v`` in a subclass,
    then override ``Container._get_val`` to return them instead of overriding
    the ``Container.v`` property.
    """
    __slots__ = ('_v', '__weakref__')

    # provide stop point for __new__
    def __new__(cls, *a, **k):
        return object.__new__(cls)

    def __init__(self, v=None, *a, **k):
        self._v = v

    def _get_val(self):
        return self._v

    @property
    def v(self):
        return self._get_val()
