"""The State monad is all about defining and passing a shared state on your
terms rather than relying on things scoping and global mutation.
"""
from ..abc import Monad, Container
from ..utils import iscallable, _get_names, wraps


class State(Monad):
    r"""A monadic wrapper around some sort of state. Superficially it
    resembles pynads.concrete.reader.Reader in that it wraps a function.
    However, instead of thinking of State as storing a function, imagine
    it holding a transition from state a to state b.

    Haskell implementation for comparison:

    .. code-block:: Haskell
       newtype State s a = State { runState :: s -> (a,s) }

       instance Monad (State s) where
           return x        = State $ \s -> (x, s)
           (State f) >>= g = State $ \s -> let (v, s') = f s
                                           in runState (g v) s'

    Curiously similar to Reader's monadic instance. However, instead of just
    allowing an environment to pass through a series of functions, it
    handles maintaining the state needed by each of those functions.

    The "All About Monads" section on State gives an example
    of this with and without the state Monad.

    <https://wiki.haskell.org/All_About_Monads#The_State_monad>

    .. code-block:: Haskell
       data MyType = MT Int Bool Char Int deriving Show

       makeRandomValue :: StdGen -> (MyType, StdGen)
       makeRandomValue g = let (n, g1) = randomR (1,1000) g
                               (b, g2) = random g1
                               (c, g3) = randomR ('a', 'z') g2
                               (m, g4) = randomR (-n, n) g3
                           in (MT n b c m, g4)

    All About Monads notes that this *works* but it's an eyesore, messy,
    hard to maintain and possibly error prone (what if you pass the wrong
    state further along?). After introducing the State monad a little more,
    the text goes on to give a revised implementation of the above...

    .. code-block:: Haskell
       getAny :: (Random a) => State StdGen a
       getAny = do g <- get
                   (x, g') <- return $ random g
                   put g'
                   return x

       getOne :: (Random a) => (a,a) -> State StdGen a
       getOne bounds = do g <- get
                          (x, g') <- return randomR bounds g
                          put g'
                          return x

       makeRandomValueSt :: StdGen -> (MyType, StdGen)
       makeRandomValueSt = runState ( do n <- getOne (1,100)
                                         b <- getAny
                                         c <- getOne ('a', 'z')
                                         m <- getOne (-n, n)
                                        return (MT  n b c m))

    Desugaring it is a little messy and requires looking at the definition of
    get (put is included for completion's sake):

    .. code-block:: Haskell
       class MonadState m s | m -> s where
           get :: m -> s
           put :: s -> m ()

       instance MonadState (State s) s where
           get      = State $ \s -> (s,s)
           put s    = State $ \_ -> ((), s)

    get retrieves the current state by copying it to the output value
    (the result of a stateful computation). put overwrites the current
    state and has no meaningful output value.
    """
    # TODO: Finish docstring.
    def __new__(cls, v):
        if not iscallable(v):
            raise TypeError("excepted callable type to be passed.")
        return Container.__new__(cls)

    def __call__(self, state):
        r"""In Haskell, State is defined with a selector function used to
        extract in stored transistion function and call it...

            .. code-block:: Haskell
                newtype State s a = State { runState :: s -> (a,s) }

        State is pretty much a wrapper around a transition from some state
        to some result, state pair. ``runState`` actually retrieves the
        transistion function from the monad. Doing ``runState (myState) s``
        actually outputs a (result, state) pair.
        """
        return self.v(state)

    def __repr__(self):
        return "{}({!s})".format(*_get_names(self, self.v))

    @classmethod
    def unit(cls, v):
        """Putting a value in the context of a stateful transition just means
        we want it to also accept some state and then return the value and
        the state together.
        """
        return cls(lambda s: (v, s))

    def fmap(self, func):
        r"""Mapping a function over a stateful computation is similar, in
        a fashion to function composition. Rather than compose the stateful
        computation with the function, first, we'll run the stateful
        computation and retrieve the result and state, and then apply the
        function to the result in the computation.

        In Haskell, the instance resembles:

            .. code-block:: Haskell
                instance Functor (State s) where
                    fmap f st = State $ \s -> let (a, s') = runState st s
                                              in (f a, s')
        """
        @wraps(self.v)
        def state_mapper(state, func=func, runner=self):
            result, new_state = runner(state)
            return (func(result), state)

        return State(state_mapper)

    def apply(self, applicative):
        r"""Using Applicative State instances is interesting. The first
        State instance needs to return a ``((r -> a), s)`` result pair.
        and the following State instances return values to feed into the
        returned function. However, we also need to pass the changed
        state from the previous ``runState`` invocation along as well:

            .. code-block:: Haskell
                instance Applicative (State s) where
                    pure a = State $ \s -> (a, s)
                    stateF <*> stateV = State $ \s ->
                            let (f, s') = runState stateF s
                                (v, s'') = runState stateV s'
                            in (f v, s'')
        """
        def state_applier(state, state_f=self, state_v=applicative):
            func, func_state = state_f(state)
            result, res_state = state_v(func_state)
            return (func(result), res_state)
        return State(state_applier)

    def bind(self, bindee):
        r"""Binding a State monad to a function is actually very similar
        to binding a function to a reader monad. Except the "environment"
        is modified along the way.

        We begin with a stateful computation wrapped up in a State. The
        computation is invoked with some initial state. From that, we get
        a value and some modified state. We take that value and feed it to
        a function that outputs another stateful computation based on the
        input. After that we feed the new stateful computation some state.

        This entire operation is wrapped in a function and placed inside
        a State monad.

            .. code-block:: Haskell
                instance Monad (State s) where
                    return a = State $ \s -> (a, s)
                    st >>= f = State $ s ->
                        let (a, s') = runState st s
                        in runState (f a) s'

        Consider a simple stack manipulation routine:

        >>> from pynads import State
        >>> from pynads.funcs import mappend
        >>> pop = State(lambda s: (s[0], s[1:]))
        >>> push = lambda a: State(lambda s: ((), mappend([a], s )))
        >>> # lambda _: pop emulates Haskell's >> operator
        >>> stack_manip = push(1) >> (lambda _: pop) >> (lambda _: pop)
        >>> stack_manip([2,3])
        ... (2, [3])

        This function can be bound to another function since it returns
        a stateful computation:

        >>> g = lambda a: push(5) if a == 5 else push(3) >> (lambda _: push(8))
        >>> s = stack_manip >> g
        >>> s([9,0,2,10])
        ... ((), [8,3,0,2,1,0])
        """
        def state_binder(state, runner=self, maker=bindee):
            value, runner_state = runner(state)
            return maker(value)(runner_state)
        return State(state_binder)
