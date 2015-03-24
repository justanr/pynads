from itertools import chain

class Container(object):
    """Basic container object to serve as a base for Functor, Applicative
    and Monad, as most derived classes need only one argument. However,
    subclasses may override ``Container.__init__`` to accept multiple
    arguments (see ``pynads.conrete.writer.Writer``) but these classes
    should pass back to ``Container.__init__`` via super.

    This class is the endpoint for any super() calls relating to
    ``__init__``, ``_get_val``, ``proxy`` and ``starproxy`` (see below)
    unless multiple inheritance is used, in which another class may also
    be called with these methods (including ``object``).

    The value contained in this class is a *strong* reference by default.
    Using a weakreference is possible, but untested.

    It also creates a property -- ``Container.v`` -- which invokes a method
    to return the contained value. If a subclass needs to return from a
    different source, or return multiple values, it can override the
    default implementation of ``Container._get_val``

    There is also two special methods: proxy and starproxy, which allow
    functions to operate directly on the stored attribute. Generally, methods 
    from derived classes should be used to *change* the stored value;
    however, operations such as boolean comparisons, arithmetic checks, etc
    are likely faster when operating directly on the value.

    ``Container.proxy`` accepts a function with a sole argument which is the
    stored value.

    ``Container.starproxy`` accepts a function with multiple arguments as well
    as the container's value. By default, it preprends the container's value,
    but there is an optional keyword ``append`` which places it at the end.

    Subclasses may override these methods to provide more specialized behavior
    such as in ``pynads.concrete.maybe._Nothing`` which returns False for these
    methods.
    """
    
    __slots__ = ('_v', '__weakref__')

    # accept *args, **kwargs for co-op inheritance with super
    # note: Container is the endpoint for 
    def __init__(self, v=None, *a, **k):
        self._v = v

    def _get_val(self):
        return self._v

    @property
    def v(self):
        return self._get_val()

    def proxy(self, f):
        """Proxies a function which accepts a single argument to the stored
        value. 
        
        This proxy method shouldn't preform any mutation of the
        stored value. Trust is in your hands.
        """
        return f(self.v)

    def starproxy(self, f, *a, append=False):
        """Proxies a function which accepts multiple arguments to the stored
        value. By default, the stored value is preprended to the arguments,
        but optionally it can be appended by setting `append=True`.

        The proxied function shouldn't preform any mutation on the stored
        value. Trust is in your hands.
        """
        if append:
            a = chain(a, [self.v])
        else:
            a = chain([self.v], a)
        return f(*a)
